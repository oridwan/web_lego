#!/bin/bash
set -e

tar -xf Jmol-*-binary.tar.gz
unzip jmol-*/jsmol.zip
ln -s $PWD/jsmol /opt/render/project/src/ase_root/ase/db/static/jsmol
ase db tp01.db -w
