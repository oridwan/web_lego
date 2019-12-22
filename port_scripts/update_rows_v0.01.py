from ase.db import connect

with connect('tp01.db') as db:
    for row in db.select():
        db.update(row.id, data={'parents': [7, 34, 14], 'stuff': [[1,2],[3,4]]})
        #db.update(row.id, spgnum=0) # WORKS!