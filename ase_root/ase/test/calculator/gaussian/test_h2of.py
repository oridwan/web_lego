# fmt: off
from ase import Atoms
from ase.calculators.gaussian import Gaussian

basis = """H     0
S   3   1.00
     13.0107010              0.19682158E-01
      1.9622572              0.13796524
      0.44453796             0.47831935
S   1   1.00
      0.12194962             1.0000000
P   1   1.00
      0.8000000              1.0000000
****
O     0
S   5   1.00
   2266.1767785             -0.53431809926E-02
    340.87010191            -0.39890039230E-01
     77.363135167           -0.17853911985
     21.479644940           -0.46427684959
      6.6589433124          -0.44309745172
S   1   1.00
      0.80975975668          1.0000000
S   1   1.00
      0.25530772234          1.0000000
P   3   1.00
     17.721504317            0.43394573193E-01
      3.8635505440           0.23094120765
      1.0480920883           0.51375311064
P   1   1.00
      0.27641544411          1.0000000
D   1   1.00
      1.2000000              1.0000000
****
F     0
S   5   1.00
   2894.8325990             -0.53408255515E-02
    435.41939120            -0.39904258866E-01
     98.843328866           -0.17912768038
     27.485198001           -0.46758090825
      8.5405498171          -0.44653131020
S   1   1.00
      1.0654578038           1.0000000
S   1   1.00
      0.33247346748          1.0000000
P   3   1.00
     22.696633924           -0.45212874436E-01
      4.9872339257          -0.23754317067
      1.3491613954          -0.51287353587
P   1   1.00
      0.34829881977          1.0000000
D   1   1.00
      1.4000000              1.0000000
****
"""


def test_h2of(gaussian_factory):
    with open('def2-svp.gbs', 'w') as bfile:
        bfile.write(basis)

    atoms = Atoms('OH2F', positions=[(-1.853788, -0.071113, 0.000000),
                                     (-1.892204, 0.888768, 0.000000),
                                     (-0.888854, -0.232973, 0.000000),
                                     (1.765870, 0.148285, 0.000000)])

    label = 'h2of-anion'
    calc = Gaussian(
        charge=-1.0,
        basis='gen',
        method='B3LYP',
        basisfile='@def2-svp.gbs/N',
        label=label,
        ioplist=['6/80=1', '6/35=4000000'],
        density='current',
        addsec=['%s.wfx' % label]
    )
    # FIXME: the "addsec" argument above is correctly incorporated into the
    # input file, but it doesn't appear to do anything to the calculation.
    # What is it for? What is it suppsoed to do?

    atoms.calc = calc
    atoms.get_potential_energy()
