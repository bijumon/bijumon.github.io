# frozen_string_literal: true

require 'commonmarker'

module Jekyll
  module Converters
    class Markdown
      class Commonmarker
        def initialize(config)
          @config = config
          Jekyll.logger.debug "Commonmarker:", "Initializing converter"
          
          # Get commonmarker configuration from _config.yml
          commonmarker_config = config.fetch('commonmarker', {})
          
          # Build options hash with parse, render, and extension options
          @options = build_options(commonmarker_config)
          
          # Build plugins hash (e.g., syntax highlighter)
          @plugins = build_plugins(commonmarker_config)
          
          Jekyll.logger.debug "Commonmarker:", "Options: #{@options.inspect}"
          Jekyll.logger.debug "Commonmarker:", "Plugins: #{@plugins.inspect}"
        end

        def convert(content)
          ::Commonmarker.to_html(content, options: @options, plugins: @plugins)
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

        def build_plugins(config)
          plugins = {}
          
          if config['plugins']
            if config['plugins']['syntax_highlighter']
              syntax_config = config['plugins']['syntax_highlighter']
              
              # Handle nil case (disable plugin)
              if syntax_config.nil?
                plugins[:syntax_highlighter] = nil
              # Handle boolean false (disable plugin)
              elsif syntax_config == false
                plugins[:syntax_highlighter] = nil
              # Handle configuration hash
              elsif syntax_config.is_a?(Hash)
                plugins[:syntax_highlighter] = symbolize_keys(syntax_config)
              # Handle boolean true (use defaults)
              elsif syntax_config == true
                plugins[:syntax_highlighter] = {}
              end
            end
          end
          
          plugins
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
