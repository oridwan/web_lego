# fmt: off
import numpy as np
from scipy.optimize import fmin_bfgs

from ase.build import bulk
from ase.calculators.emt import EMT
from ase.io import Trajectory, read


class NDPoly:
    def __init__(self, ndims=1, order=3):
        """Multivariate polynomium.

        ndims: int
            Number of dimensions.
        order: int
            Order of polynomium."""

        if ndims == 0:
            exponents = [()]
        else:
            exponents = []
            for i in range(order + 1):
                E = NDPoly(ndims - 1, order - i).exponents
                exponents += [(i,) + tuple(e) for e in E]
        self.exponents = np.array(exponents)
        self.c = None

    def __call__(self, *x):
        """Evaluate polynomial at x."""
        return np.dot(self.c, (x**self.exponents).prod(1))

    def fit(self, x, y):
        """Fit polynomium at points in x to values in y."""
        A = (x**self.exponents[:, np.newaxis]).prod(2)
        self.c = np.linalg.solve(np.inner(A, A), np.dot(A, y))


def polyfit(x, y, order=3):
    """Fit polynomium at points in x to values in y.

    With D dimensions and N points, x must have shape (N, D) and y
    must have length N."""

    p = NDPoly(len(x[0]), order)
    p.fit(x, y)
    return p


def test_hcp(testdir):
    a0 = 3.52 / np.sqrt(2)
    c0 = np.sqrt(8 / 3.0) * a0
    print(f'{a0:.4f} {c0 / a0:.3f}')
    for _ in range(3):
        with Trajectory('Ni.traj', 'w') as traj:
            eps = 0.01
            for a in a0 * np.linspace(1 - eps, 1 + eps, 4):
                for c in c0 * np.linspace(1 - eps, 1 + eps, 4):
                    ni = bulk('Ni', 'hcp', a=a, covera=c / a)
                    ni.calc = EMT()
                    ni.get_potential_energy()
                    traj.write(ni)

        configs = read('Ni.traj', index=':')
        energies = [config.get_potential_energy() for config in configs]
        ac = [(config.cell[0, 0], config.cell[2, 2]) for config in configs]
        p = polyfit(ac, energies, 2)
        a0, c0 = fmin_bfgs(p, (a0, c0))
        print(f'{a0:.4f} {c0 / a0:.3f}')
    assert abs(a0 - 2.466) < 0.001
    assert abs(c0 / a0 - 1.632) < 0.005
