FROM ruby:slim

# ✅ Install ONLY what native Ruby gems actually need (no graphics stack)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    nodejs \
    npm \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ✅ Update RubyGems and install Jekyll properly
RUN gem update --system && \
    gem install bundler jekyll
