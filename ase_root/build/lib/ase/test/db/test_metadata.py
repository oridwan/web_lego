# fmt: off
import pytest

from ase import Atoms
from ase.db import connect

# Data for a plot:
plot = {'a': [0, 1, 2],
        'b': [1.2, 1.1, 1.0],
        'abplot': {'title': 'Example',
                   'data': [{'x': 'a',
                             'y': 'b',
                             'label': 'label1',
                             'style': 'o-g'}],
                   'xlabel': 'blah-blah [eV]',
                   'ylabel': 'Answers'}}


@pytest.mark.parametrize('name', ['md.json', 'md.db'])
def test_metadata(name, testdir):
    print(name)
    db = connect(name)
    db.write(Atoms('H'), answer=42, kind='atom', foo=True)
    db.write(Atoms('H2O'), answer=117, kind='molecule', foo=False, data=plot)
    db.metadata = {'test': 'ok'}
    db.metadata = {
        'default_columns': ['formula', 'answer', 'kind'],
        'key_descriptions': {
            'kind': ('Type', 'Type of system', ''),
            'answer': ('Answer', 'Answer to question', 'eV')}}

    db = connect(name)
    md = db.metadata
    assert 'formula' in md['default_columns']
    md['title'] = 'TEST'
    db.metadata = md

    assert connect(name).metadata['title'] == 'TEST'
