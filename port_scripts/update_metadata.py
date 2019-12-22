from ase.db import connect

db = connect('tp01.db') # connect to ASE DB
db.metadata = {         # Update metadata
'title': 'Topological Phonon Database',
'key_descriptions': {
    'mat_id': ('Material ID', 'Unique material ID', ''),
    'z': ('Z', 'Z', ''),
    'spg': ('Space Group', 'Space Group', ''),
    'spgnum': ('Space Group #', 'Space Group Number', ''),
    'proto': ('Prototype', 'Prototype', ''),
    },
'default_columns': ['mat_id', 'formula', 'z', 'spg', 'spgnum', 'proto']}