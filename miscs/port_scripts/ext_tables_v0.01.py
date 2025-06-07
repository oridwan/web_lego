from ase.db import connect

num_features = 5
feature_dict = dict(('feature' + str(i), i) for i in range(num_features))

with connect('tp01.db') as db:
    for row in db.select():
        db.update(row.id, external_tables={'extratable': feature_dict})

db = connect('tp01.db')
for row in db.select():
    print(row['extratable'])