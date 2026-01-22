#!/bin/bash
# 
# LEGO-xtal: AI-Assisted Rapid Crystal Structure Generation Towards a Target Local Environment
# 
# Authors: Osman Goni Ridwan, Sylvain Pitié, Monish Soundar Raj, Dong Dai, Gilles Frapper, 
#          Hongfei Xue, Qiang Zhu
# 
# Reference:
# @article{ridwan2025ai,
#   title={AI-Assisted Rapid Crystal Structure Generation Towards a Target Local Environment},
#   author={Ridwan, Osman Goni and Piti{\'e}, Sylvain and Raj, Monish Soundar and Dai, Dong and Frapper, Gilles and Xue, Hongfei and Zhu, Qiang},
#   journal={arXiv preprint arXiv:2506.08224},
#   year={2025}
# }
#
# Contact: oridwan@charlotte.edu, qzhu8@charlotte.edu
# Research Group: Materials Modelling and Informatics (MMI) / Zhu's Group
# PI: Qiang Zhu (Interim Director of BATT CAVE, Associate Professor)
#     Mechanical Engineering and Engineering Science
#     https://qzhu2017.github.io
#

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

# 2. Determine port (CLI arg > $PORT > default 5000)
if [ -n "$1" ]; then
    PORT="$1"
elif [ -z "$PORT" ]; then
    PORT=5000
fi
export PORT

# 3. Run the Flask app directly so we can set the port
echo "Starting ASE web server on port $PORT..."
export PYTHONPATH="$PWD/ase_root${PYTHONPATH:+:$PYTHONPATH}"
python3 - <<'PY'
import os
from ase.db.app import DBApp
from ase.db import connect

db_path = 'lego-sp2.db'
port = int(os.environ.get('PORT', '5000'))

app = DBApp()
app.add_project('default', connect(db_path))
app.flask.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
PY
