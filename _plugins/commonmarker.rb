# frozen_string_literal: true

require 'commonmarker'
require 'rouge'

module Jekyll
  module Converters
    class Markdown
      class Commonmarker
        def initialize(config)
          @config = config
          Jekyll.logger.debug "Commonmarker:", "Initializing converter with Rouge"
          
          # Get commonmarker configuration from _config.yml
          commonmarker_config = config.fetch('commonmarker', {})
          
          # Build options hash with parse, render, and extension options
          @options = build_options(commonmarker_config)
          
          # Disable built-in syntax highlighting - we'll use Rouge instead
          @plugins = { syntax_highlighter: nil }
          
          # Get Rouge configuration
          @rouge_config = commonmarker_config.fetch('rouge', {})
          
          Jekyll.logger.debug "Commonmarker:", "Options: #{@options.inspect}"
          Jekyll.logger.debug "Commonmarker:", "Rouge config: #{@rouge_config.inspect}"
        end

        def convert(content)
          # Convert markdown to HTML with Commonmarker (no syntax highlighting)
          html = ::Commonmarker.to_html(content, options: @options, plugins: @plugins)
          
          # Apply Rouge syntax highlighting to code blocks
          highlight_code_blocks(html)
        end

        private

        def build_options(config)
          options = {}
          
          # Parse options
          if config['parse']
            options[:parse] = symbolize_keys(config['parse'])
          end
          
          # Render options
          if config['render']
            options[:render] = symbolize_keys(config['render'])
          end
          
          # Extension options
          if config['extension']
            options[:extension] = symbolize_keys(config['extension'])
          end
          
          options
        end

        def highlight_code_blocks(html)
          # Match code blocks: <pre><code class="language-xxx">...</code></pre>
          # or <pre lang="xxx"><code>...</code></pre> (github_pre_lang style)
          html.gsub(%r{<pre(?:\s+lang="([^"]*)")?\s*><code(?:\s+class="language-([^"]*)")?>(.+?)</code></pre>}m) do
            lang = $1 || $2
            code = $3
            
            # Decode HTML entities in the code
            code = CGI.unescapeHTML(code)
            
            if lang && !lang.empty?
              highlight_with_rouge(code, lang)
            else
              # No language specified, return as-is with highlight class
              css_class = @rouge_config['css_class'] || 'highlight'
              %(<div class="#{css_class}"><pre><code>#{CGI.escapeHTML(code)}</code></pre></div>)
            end
          end
        end

        def highlight_with_rouge(code, lang)
          # Get Rouge configuration
          css_class = @rouge_config['css_class'] || 'highlight'
          line_numbers = @rouge_config['line_numbers'] || false
          wrap = @rouge_config.fetch('wrap', true)
          
          begin
            # Get the lexer for the language
            lexer = Rouge::Lexer.find_fancy(lang, code) || Rouge::Lexers::PlainText.new
            
            # Tokenize the code
            tokens = lexer.lex(code)
            
            # Choose formatter based on configuration
            if line_numbers
              formatter = Rouge::Formatters::HTMLTable.new(
                Rouge::Formatters::HTML.new,
                css_class: css_class,
                gutter_class: @rouge_config['gutter_class'] || 'gutter',
                code_class: @rouge_config['code_class'] || 'code'
              )
            else
              formatter = Rouge::Formatters::HTML.new
            end
            
            # Format the tokens
            highlighted = formatter.format(tokens)
            
            # Wrap in div with highlight class if wrap is enabled
            if wrap && !line_numbers
              %(<div class="#{css_class}"><pre><code class="language-#{lang}">#{highlighted}</code></pre></div>)
            elsif line_numbers
              # HTMLTable formatter already wraps, just add the outer highlight class
              %(<div class="#{css_class}">#{highlighted}</div>)
            else
              highlighted
            end
          rescue => e
            Jekyll.logger.warn "Commonmarker:", "Rouge highlighting failed for language '#{lang}': #{e.message}"
            # Fallback to plain code block
            %(<div class="#{css_class}"><pre><code class="language-#{lang}">#{CGI.escapeHTML(code)}</code></pre></div>)
          end
        end

        def symbolize_keys(hash)
          hash.transform_keys(&:to_sym).transform_values do |value|
            if value.is_a?(Hash)
              symbolize_keys(value)
            else
              value
            end
          end
        end
      end
    end
  end
end
