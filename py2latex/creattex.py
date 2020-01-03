import sqlite3, os, datetime
from collections import OrderedDict
from tabulate import tabulate
import pandas as pd
import time
from tqdm import tqdm
def set_style(f):
    f.write('\documentclass[amsmath,amssymb]{revtex4}\n')
    f.write('\\usepackage[ansinew] {inputenc}\n')
    f.write('\\usepackage{graphicx}\n')
    f.write('''\\usepackage{pst-all}
\\usepackage{color}
\\usepackage{dcolumn}
\\usepackage{amsmath}
\\usepackage{amsthm}
\\usepackage{bm}
\\usepackage{layout}
\\usepackage{float}
\\usepackage{txfonts}
\\usepackage{amsfonts}
\\usepackage{amssymb}%
\\setcounter{MaxMatrixCols}{30}
\\usepackage[ansinew]{inputenc}
\\usepackage{array}
\\usepackage{multirow,bigdelim}
\\usepackage{enumitem}
\\usepackage{epstopdf}
\\usepackage{CJK}
\\usepackage{longtable}
\\usepackage[english]{babel}
\\usepackage{amstext}
\\usepackage{latexsym}
\\usepackage{microtype}
\\usepackage{dcolumn}
\\usepackage{soul}
\\usepackage{booktabs}
\\usepackage{tabu}
\\usepackage{subfigure}
\\usepackage{lscape}\n\n''')

con = sqlite3.connect('test.db')
cur = con.cursor()
sql = """SELECT Material_id,
      Space_group,
      International_number,
      Formula,
      Prototype,
      Fig_band,
      Fig_dos,
      Poscar,
      Incar,
      Potcar,
      Kpoints,
      Supercell
      FROM Materials"""
cur.execute(sql)
rows = cur.fetchall()
with open('db.tex','w') as f:
    set_style(f)
    f.write('\\begin{document}\n')
    f.write('\\section{All topological phonon candidates}\n')
    f.write('\\input{Tex/%s}\n'%('all-materials'))
    f.write('\\newpage')
    f.write('\\section{clean topological phonon candidates}\n')
    f.write('\\input{Tex/clean}\n')
    f.write('\\newpage')
    f.write('\\section{Details of all topological phonon materials}\n')
    for row in rows:
         (mid,spg,number,formula,prototype,fig_band,fig_dos,\
         poscar, incar, potcar, kpoints, supercell)=row
         f.write('\\input{Tex/%s}\n'%(mid))
    f.write('\\end{document}\n')
