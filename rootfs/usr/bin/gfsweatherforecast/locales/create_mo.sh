#!/bin/bash

# Recursively find all .po files and compile them to .mo files
find . -type f -name "*.po" | while read -r pofile; do
    mofile="${pofile%.po}.mo"
    echo "Compiling $pofile -> $mofile"
    msgfmt -o "$mofile" "$pofile"
done