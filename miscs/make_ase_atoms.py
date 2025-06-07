import sqlite3, os, datetime
from ase.io import read
###############################################################
con = sqlite3.connect('test.db') 
cur = con.cursor()
sql = """SELECT Material_ID, Poscar FROM Materials"""
cur.execute(sql)
rows = cur.fetchall()
for row in rows[:1]:
    (mid, poscar) = row
    print(poscar)
    filename = '1.vasp'
    with open(filename, 'w') as f:
        f.write(poscar)
    ase_atoms = read(filename, format='vasp')
    print(ase_atoms)
cur.close()
