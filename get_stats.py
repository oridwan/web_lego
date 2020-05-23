from ase.db import connect

db = connect('tp01.db')
spgs = []
protos = []

rows = db.select()
stats = {'matertials': 0,
         'space_group': 0,
         'prototypes': 0,
         'clean_materials': 0,
         'nodal_ring_pts': 0,
         'nodal_lines': 0,
         'Weyl_pts' : 0,
         'Multi_Weyl_pts': 0,
         }

for row in rows:
    print(row.formula)
    stats['matertials'] += 1
    if row.spgnum not in spgs:
        spgs.append(row.spgnum)
        stats['space_group'] += 1
    if row.proto not in protos:
        protos.append(row.proto)
        stats['prototypes'] += 1
    stats['nodal_lines'] += row.lines
    stats['nodal_ring_pts'] += row.ring_pts
    stats['Weyl_pts'] += row.weyl_pts
    stats['Multi_Weyl_pts'] += row.multi_deg_weyl_pts
    if row.clean:
        stats['clean_materials'] += 1

for key in stats.keys():
    print("{:20s}   {:8d}".format(key, stats[key]))
