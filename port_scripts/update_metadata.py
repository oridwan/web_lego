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
    'lines': ('Nodal lines', 'Nodal lines', ''),
    'ring_pts': ('Nodal ring points', 'Nodal ring points', ''),
    'weyl_pts': ('Weyl points', 'Weyl points', ''),
    'multi_deg_weyl_pts': ('Multi_deg Weyl points', 'Multi_deg Weyl points', ''),
    },
'default_columns': ['mat_id', 'formula', 'z', 'spg', 'spgnum', 'proto',\
                    'lines', 'ring_pts', 'weyl_pts', 'multi_deg_weyl_pts']}
