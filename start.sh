#!/bin/bash
set -e  # Exit immediately on error

# 1. Extract jsmol.zip if it hasn't been already
#if [ ! -d "jsmol" ]; then
#    echo "Unzipping jsmol..."
#    unzip jmol-*/jsmol.zip -d jsmol
#fi

# 2. Create symbolic link for jsmol in correct location (if not already linked)
#TARGET_LINK="ase_root/ase/db/static/jsmol"
#if [ ! -L "$TARGET_LINK" ]; then
#    echo "Linking jsmol to $TARGET_LINK"
#    mkdir -p "$(dirname "$TARGET_LINK")"
#    ln -s "$PWD/jsmol" "$TARGET_LINK"
#fi
ln -s $PWD/jsmol /opt/render/project/src/ase_root/ase/db/static/jsmol
# 3. Start the ASE web server
echo "Starting ASE web server..."
ase db lego-sp2.db -w
