# fmt: off
import io

from ase.build import bulk
from ase.collections import g2
from ase.io import iread, write


def test_traj_bytesio():

    images = [bulk('Si') + bulk('Fe')] + list(g2)

    buf = io.BytesIO()
    write(buf, images, format='traj')
    txt = buf.getvalue()

    buf = io.BytesIO()
    buf.write(txt)
    buf.seek(0)

    images2 = list(iread(buf, format='traj'))

    for atoms1, atoms2 in zip(images, images2):
        assert atoms1 == atoms2
