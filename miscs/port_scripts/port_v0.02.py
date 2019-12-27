import sqlite3, os
from ase.io import read
from ase.db import connect
from topo_phonon.topo_phonon import topo_phon, loader
from plotly_band import plot_all
import numpy as np

tables = ['Materials', 'Nodal_lines', 'Nodal_ring_points', 'Nodal_ring_points2', 'Weyl_points', 'Clean_materials']
num_materials = 10
filename = 'temp_atom.vasp'

con = sqlite3.connect('../web-page/test.db') # connect to old DB
cur = con.cursor()
sql = """SELECT Material_id,
      Space_group,
      International_number,
      Z,
      Prototype,
      Dir_name, 
      Poscar,
      Potcar,
      Kpoints,
      Supercell
      FROM Materials"""
cur.execute(sql)
mat_rows = cur.fetchall()
stats = [] # for topological statistics
ase_atoms = []
htmls = []
calculations = []

for row in mat_rows[:num_materials]:
    (mid, spg,  number, _, _, dir_name, poscar, potcar, kpt, supercell) = row
    phonon = loader(dir_name).phonon
    my_test = topo_phon(phonon)
    title = mid + ': ' + spg + '(' + str(number) + ')'
    calculation = {'POSCAR': poscar, 'POTCAR': potcar, 'Kpoints': kpt, 'Supercell': supercell}
    calculations.append(calculation)
    with open(filename, 'w') as f:
        f.write(poscar)
    ase_atoms.append(read(filename, format='vasp'))
    os.remove(filename)
    stat = [0] * 5
    pts = []
    nls = []

    for i, table in enumerate(tables[1:-1]):
        cur.execute("SELECT * from {:} WHERE Material_id = '{:}'".format(table, mid)) 
        rows = cur.fetchall()
        stat[i] = len(rows)
        for row in rows:
            if table == 'Nodal_lines':
                (_, label1, label2, _, _, _, _, _, _, mode, ratio1, ratio2) = row
                path_id = my_test.get_path_id([label1, label2])
                dicts = {'path_id': path_id, 'Start_ratio': ratio1, 'End_ratio': ratio2, 'mode': mode}
                nls.append(dicts)
            else:
                if table in ['Weyl_points', 'Nodal_ring_points']:
                    (_, x, y, z, mode1, mode2, freq1, freq2, _, _, _, _, _, deg, _, _, _) = row
                    if deg <= 2:
                        type = 0
                    elif deg > 2:
                        type = 1
                        stat[-1] += 1
                        stat[-2] -= 1
                else:
                    (_, x, y, z, mode1, mode2, freq1, freq2, _, _, _, _, _, deg, _, _) = row
                    type = 2
                at_path, qpoint1, path_ids, ratios = my_test.check_q_at_paths([x,y,z])
                dicts = {'path_id': path_ids, 'ratio': ratios, \
                         'frequency1': freq1, 'frequency2': freq2, 'type': type}
                pts.append(dicts) 
    stats.append(stat)
    print(title, len(nls), len(pts))
    htmls.append(plot_all(my_test, pts, nls, title))
cur.close()

with connect('tp01.db') as db:
    for i in range(num_materials):             # Port atoms from old DB
        kvp = { # Define key-value pairs
            "mat_id": mat_rows[i][0],
            "spg": mat_rows[i][1],
            "spgnum": mat_rows[i][2],
            "z": mat_rows[i][3],
            "proto": mat_rows[i][4],
            "lines": stats[i][0],
            "ring_pts": stats[i][1] + stats[i][2],
            "weyl_pts": stats[i][3],
            "multi_deg_weyl_pts": stats[i][4],
            }
        data = {'Dir_name': mat_rows[i][5], 
                'plotly_HTML': htmls[i], 
                'calculation': calculations[i]}
        db.write(ase_atoms[i], key_value_pairs=kvp, data=data) # write to new ASE DB
