import sqlite3, os, datetime
from collections import OrderedDict
from tabulate import tabulate
import pandas as pd
import sys
import time
from tqdm import tqdm

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

def set_figs(f,formula,fig_band,fig_dos,mid):
    fig_band=fig_band[3:]
    fig_dos=fig_dos[3:]
    label = 'bd'+'-'+mid
    f.write('''
\\begin{figure}[htbp]
\\centering

    \\subfigure[band]
    {
    \\begin{minipage}{8cm}
    \\centering
    \\includegraphics[scale=0.5]{%s}
    \\end{minipage}
    }
    \\subfigure[dos]
    {
    \\begin{minipage}{8cm}
    \\centering
    \\includegraphics[scale=0.5]{%s}
    \\end{minipage}
    }
\\caption{The phonon band and dos of %s}
\\label{%s}
\\end{figure}\n'''%(fig_band,fig_dos,formula,label)
)
    

def set_Weyl_table(f, cur, captions, mid):
    cur.execute("""SELECT * FROM Weyl_points WHERE Material_id = ?""", (mid,))
    pts = cur.fetchall()
    if len(pts)>0:
        pt_dict = OrderedDict()
        pt_dict = {
               'x': [],
               'y': [],
               'z': [],
               'Mode': [],
               'Freq': [],
               'Chern':[],
               'Deg': [],
               'Type': [],
               'Ratio': [],
              }
        for pt in pts:
            (_, x, y, z, mode1, mode2, freq1, freq2, dos, dos_min, c1, c2, multi, deg, w_type, path, ratio, weyl) = pt
            if weyl >0:
                pt_dict['x'].append(round(x,3))
                pt_dict['y'].append(round(y,3))
                pt_dict['z'].append(round(z,3))
                pt_dict['Mode'].append(mode2)
                pt_dict['Freq'].append(round(freq1,3))
                pt_dict['Chern'].append(int(c1))
                pt_dict['Deg'].append(deg)
                pt_dict['Type'].append(w_type)
                pt_dict['Ratio'].append(round(ratio,2))
        df = pd.DataFrame(pt_dict)
        raw_tex = df.to_latex()
        captions='Weyl points along high symmetry lines of '+ captions
        raw_tex=c2latex(raw_tex,captions,mid+'-wp')
        f.write(raw_tex)

def set_nls(f,cur,captions,mid):
    cur.execute("""SELECT * FROM Nodal_lines WHERE Material_id = ?""", (mid,))
    paths = cur.fetchall()
    if len(paths) > 0:
        nl_dict = OrderedDict()
        nl_dict = {
                'label1': [],
                'label2': [],
                'mode' : [],
                'start' : [],
                'end' : [],
                }
        for path in paths:
            (_,label1,label2,x1,y1,z1,x2,y2,z2,mode,start,end) = path
            label1 = label1 + ' ({:5.3f} {:6.3f} {:6.3f})'.format(x1, y1, z1)
            label2 = label2 + ' ({:5.3f} {:6.3f} {:6.3f})'.format(x2, y2, z2)
            nl_dict['label1'].append(label1)
            nl_dict['label2'].append(label2)
            nl_dict['mode'].append(mode+1)
            nl_dict['start'].append(round(start,2))
            nl_dict['end'].append(round(end,2))
        df = pd.DataFrame(nl_dict)
        raw_tex = df.to_latex()
        captions="Nodal line details of "+captions
        raw_tex=c2latex(raw_tex,captions,mid+'-ndl')
        f.write(raw_tex)

def set_nodal_ring_table(f, cur, captions, mid):
    cur.execute("""SELECT * FROM Nodal_ring_points WHERE Material_id = ?""", (mid,))
    pts = cur.fetchall()
    if len(pts)>0:
        pt_dict = OrderedDict()
        pt_dict = {
               'x': [],
               'y': [],
               'z': [],
               'Mode': [],
               'Freq': [],
               'Berry':[],
               'Deg': [],
               'Ratio': [],
              }
        for pt in pts:
                (_, x, y, z, mode1, mode2, freq1, freq2, dos, dos_min, c1, c2, multi, deg, w_type, path, ratio) = pt
                pt_dict['x'].append(round(x,3))
                pt_dict['y'].append(round(y,3))
                pt_dict['z'].append(round(z,3))
                pt_dict['Mode'].append(mode2)
                pt_dict['Freq'].append(round(freq1,3))
                pt_dict['Berry'].append(int(c2))
                pt_dict['Deg'].append(deg)
                pt_dict['Ratio'].append(round(ratio,2))
        df = pd.DataFrame(pt_dict)
        raw_tex = df.to_latex()
        captions='Nodal ring pints along high symmetry path of '+ captions
        raw_tex=c2latex(raw_tex,captions,mid+'-ndr')
        f.write(raw_tex)

########################################
tex_dir = 'Tex/'
if not os.path.exists(tex_dir):
    os.makedirs(tex_dir)

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
i=0
for row in tqdm(rows):
    (mid,spg,number,formula,prototype,fig_band,fig_dos,\
    poscar, incar, potcar, kpoints, supercell)=row
    tex_path=tex_dir+mid+'.tex'
    name=mid+'-'+formula
    with open(tex_path,'w') as f:
        set_figs(f,name,fig_band,fig_dos,mid)
        set_Weyl_table(f,cur,name,mid)
        set_nls(f,cur,name,mid)
        set_nodal_ring_table(f,cur,name,mid)
#    sys.stdout.write('> ')
#    sys.stdout.flush()
#    i=i+1
#    print(i)
