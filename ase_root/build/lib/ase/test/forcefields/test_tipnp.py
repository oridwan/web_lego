# fmt: off
from math import cos, pi, sin

from ase import Atoms
from ase.calculators.fd import calculate_numerical_forces
from ase.calculators.tip3p import TIP3P, angleHOH, rOH
from ase.calculators.tip4p import TIP4P


def test_tipnp():
    """Test TIP3P forces."""

    r = rOH
    a = angleHOH * pi / 180

    dimer = Atoms('H2OH2O',
                  [(r * cos(a), 0, r * sin(a)),
                   (r, 0, 0),
                   (0, 0, 0),
                   (r * cos(a / 2), r * sin(a / 2), 0),
                   (r * cos(a / 2), -r * sin(a / 2), 0),
                   (0, 0, 0)])
    dimer = dimer[[2, 0, 1, 5, 3, 4]]
    dimer.positions[3:, 0] += 2.8

    for TIPnP in [TIP3P, TIP4P]:
        # put O-O distance in the cutoff range
        dimer.calc = TIPnP(rc=4.0, width=2.0)
        F = dimer.get_forces()
        print(F)
        dF = calculate_numerical_forces(dimer) - F
        print(dF)
        assert abs(dF).max() < 2e-6
