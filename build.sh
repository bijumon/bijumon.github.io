#!/bin/sh
set -eu

mkdir -p _site

find . -type f \( -name '*.md' -o -name '*.markdown' \) \
    -not -path './_site/*' \
    -exec sh -c '
        set -eu

        for file do
            case "$file" in
                *.markdown)
                    output="_site/${file#./}"
                    output="${output%.markdown}.html"
                    ;;
                *.md)
                    output="_site/${file#./}"
                    output="${output%.md}.html"
                    ;;
            esac

            mkdir -p "$(dirname "$output")"

            pandoc "$file" \
                --standalone \
                --to=html5 \
                --output="$output"
        done
    ' sh {} +
