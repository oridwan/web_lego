import sqlite3, os, datetime
from creattex import set_style
from collections import OrderedDict
from tabulate import tabulate
import pandas as pd
import sys
import time
from tqdm import tqdm
from plotly_band import plot_all, get_path_table, get_pt_tables

def c2latex(a,caption,label):
#    caption='caption{'+caption+'}\\\\\n\\label{'+label+'}'
    caption="caption{%s}\\\\\n\\label{%s}\\\\\n\\toprule"%(caption,label)
    a=a.replace('toprule',caption)
    a=a.replace('\\bottomrule\n','')
    a=a.replace('tabular','longtable')
    a=a.replace('midrule','midrule\n\\endhead\n\\bottomrule\n\\endfoot')
    a=a.replace('\\$\\textbackslash mathrm','$\\mathrm')
    a=a.replace('\\_','_')
    a=a.replace('\\$','$')
    a=a.replace('\\{','{')
    a=a.replace('\\}','}')
    a=a.replace('lllrrr','p{3em}<{\\centering}p{10.15em}<{\\centering}p{10.15em}<{\\centering}p{3em}<{\\centering}p{5em}<{\\centering}p{5em}<{\\centering}')
    a='{\n\\tiny\n'+a+'}'
    a=a+'\n'
    a=a.replace('$\\textbackslash Gamma$','$\\mathrm{\\Gamma}$')
    return a

def set_figs(row, f):
    label = 'bd'+'-'+row.mat_id
    fig_name = 'imgs/' + row.mat_id + '.pdf'
    formula = row.formula

    fig = plot_all(row['data']['plotly_data']['frequencies'],
                   row['data']['plotly_data']['distances'],
                   row['data']['plotly_data']['path_connections'],
                   row['data']['plotly_data']['labels'],
                   row['data']['plotly_data']['freq_pts'],
                   row['data']['plotly_data']['dos'],
                   row['data']['plotly_data']['pts'],
                   row['data']['plotly_data']['lines'],
                   row['data']['plotly_data']['title'],
                   )
    fig.write_image(fig_name)
    f.write('''
\\begin{figure}[htbp]
    \\includegraphics[width=0.85\\textwidth]{%s}
\\caption{The phonon band and DOS of %s}
\\label{%s}
\\end{figure}\n'''%(fig_name,formula,label)
)
    

def set_pt_table(row, f, captions, mid):
    data = get_pt_tables(row['data']['plotly_data']['pts'])
    keys = ['Coordinates', 'Frequency', 'Mode 1', 'Mode 2', 'Multi.', 'Deg.', 'Path', 'Ratio']  
    for id, name in enumerate(['Weyl Points', 'Multi_Deg Weyl Points', 'Nodal Ring Points']):
        if data[id] is not None:
            pt_dict = OrderedDict()
            pt_dict = {
                   'Coordinates': [],
                   'Frequency': [],
                   'Mode 1':[],
                   'Mode 2':[],
                   'Multi.':[],
                   'Deg.': [],
                   'Path': [],
                   'Ratio': [],
                   }
            for cols in data[id]:
                for id1, col in enumerate(cols):
                    pt_dict[keys[id1]].append(col)
            df = pd.DataFrame(pt_dict)
            raw_tex = df.to_latex()
            captions= name + ' along high symmetry lines of '+ captions
            raw_tex=c2latex(raw_tex,captions,mid+'-wp')
            f.write(raw_tex)

def set_path_table(row, f, captions, mid):
    data = get_path_table(row['data']['plotly_data']['paths'], 
                          row['data']['plotly_data']['_labels'])
    keys = ['Start', 'End']
    pt_dict = OrderedDict()
    pt_dict = {
           'Start': [],
           'End': [],
           }
    for cols in data:
        for id1, col in enumerate(cols):
            col=col.replace('&#915;','$\Gamma$')
            col=col.replace('<sub>','_')
            col=col.replace('</sub>','')
            pt_dict[keys[id1]].append(col)
    df = pd.DataFrame(pt_dict)
    raw_tex = df.to_latex()
    captions='High symmetry lines of '+ captions
    raw_tex=c2latex(raw_tex,captions,mid+'-wp')
    f.write(raw_tex)


########################################
from ase.db import connect
tex_dir = 'Tex/'
if not os.path.exists(tex_dir):
    os.makedirs(tex_dir)

print('Creating tex file for each materials')
with connect('../tp01.db') as db:
    rows = db.select(z=2)
    for row in tqdm(rows):
        tex_path=tex_dir+row.mat_id+'.tex'
        name=row.mat_id+'-'+row.formula
        with open(tex_path,'w') as f:
            set_figs(row, f)
            set_pt_table(row, f, name, row.mat_id)
            set_path_table(row, f, name, row.mat_id)
    sys.stdout.write('> ')
    sys.stdout.flush()
    
print('Creating main tex file')
with connect('../tp01.db') as db:
    rows = db.select(z=2)

    with open('db.tex','w') as f:
        set_style(f)
        f.write('\\begin{document}\n')
        f.write('\\input{title_abs}\n')
        f.write('\\tableofcontents\n')
        f.write('\\newpage\n')
        f.write('\\section{All topological phonon candidates}\n')
        f.write('\\input{Tex/%s}\n'%('all-materials'))
        f.write('\\newpage\n')
        f.write('\\section{clean topological phonon candidates}\n')
        f.write('\\input{Tex/clean}\n')
        f.write('\\newpage\n')
        f.write('\\section{high degenerate Weyl points}\n')
        f.write('\\input{Tex/hdwps}\n')
    
        f.write('\\section{Details of all topological phonon materials}\n')
        count = 0
        for row in rows:
            count += 1
            f.write('\\input{Tex/%s}\n'%(row.mat_id))
            print(count, row.mat_id)
        f.write('\\end{document}\n')
