# frozen_string_literal: true
source "https://rubygems.org"

# -------------------------------------------------------------
# Jekyll setup
# -------------------------------------------------------------
gem "jekyll", "~> 4.4.1"

# Core Jekyll plugins
group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
end

# Markdown engine
gem "commonmarker", "~> 2.4.1"
gem "rouge"

# -------------------------------------------------------------
# Platform-specific dependencies
# -------------------------------------------------------------
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", platforms: [:mingw, :x64_mingw, :mswin]
gem "http_parser.rb", platforms: [:jruby]

# -------------------------------------------------------------
# Optional utilities (if your build or plugins require them)
# -------------------------------------------------------------
gem "logger"
gem "csv"
gem "ostruct"
gem "base64"
