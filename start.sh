#!/bin/bash
set -e  # Exit immediately on error

# 1. Ensure jsmol assets exist (Render sometimes starts without them)
TARGET_LINK="ase_root/ase/db/static/jsmol"
mkdir -p "$(dirname "$TARGET_LINK")"

# If a bundled jsmol folder is present, prefer it
if [ -d "jsmol" ]; then
    if [ ! -e "$TARGET_LINK" ] && [ ! -L "$TARGET_LINK" ]; then
        echo "Linking bundled jsmol to $TARGET_LINK"
        ln -s "$PWD/jsmol" "$TARGET_LINK"
    elif [ -L "$TARGET_LINK" ]; then
        echo "Updating existing jsmol link..."
        rm -f "$TARGET_LINK"
        ln -s "$PWD/jsmol" "$TARGET_LINK"
    fi
else
    # Fallback: unzip from bundled Jmol archive if available
    if ls jmol-*/jsmol.zip >/dev/null 2>&1; then
        echo "Unzipping jsmol from bundled archive..."
        unzip jmol-*/jsmol.zip -d jsmol
        ln -s "$PWD/jsmol" "$TARGET_LINK"
    else
        echo "jsmol assets missing. Attempting to download latest minimal JSmol..."
        mkdir -p jsmol
        curl -L "https://sourceforge.net/projects/jmol/files/latest/download" -o /tmp/jmol-latest.tar.gz
        tar -xzf /tmp/jmol-latest.tar.gz -C /tmp && find /tmp -maxdepth 3 -name "jsmol.zip" -type f -print -quit | xargs -I {} cp {} /tmp/jsmol.zip 2>/dev/null || true
        if [ -f /tmp/jsmol.zip ]; then
            unzip /tmp/jsmol.zip -d jsmol
            ln -s "$PWD/jsmol" "$TARGET_LINK"
        else
            echo "WARNING: JSmol download failed; structure viewer will be unavailable." >&2
        fi
    fi
fi

# 2. Start the ASE web server
echo "Starting ASE web server..."
ase db lego-sp2.db -w
