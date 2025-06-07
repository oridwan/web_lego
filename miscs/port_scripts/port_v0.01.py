import sqlite3, os
from ase.io import read
from ase.db import connect

con = sqlite3.connect('test.db') # connect to old DB
cur = con.cursor()
sql = """SELECT Material_id,
      Space_group,
      International_number,
      Z,
      Prototype,
      Poscar
      FROM Materials"""
cur.execute(sql)
rows = cur.fetchall()

with connect('tp01.db') as db:
    for row in rows[:10]:             # Port atoms from old DB
        (mid, _, _, _, _, poscar) = row
        filename = 'temp_atom.vasp'
        with open(filename, 'w') as f:
            f.write(poscar)
        ase_atoms = read(filename, format='vasp')
        kvp = { # Define key-value pairs
            "mat_id": row[0],
            "spg": row[1],
            "spgnum": row[2],
            "z": row[3],
            "proto": row[4]}
        db.write(ase_atoms, key_value_pairs=kvp) # write to new ASE DB
    cur.close()