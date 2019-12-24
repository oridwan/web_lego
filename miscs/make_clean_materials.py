import sqlite3, os, datetime
from collections import OrderedDict
from tabulate import tabulate
import pandas as pd

def set_style(f):
    f.write('<link rel="stylesheet" type="text/css" href="../style.css" />\n')

def set_head(f, name):
    f.write("<html>\n")
    f.write("<head>\n")
    f.write("<title>"+name+"</title>\n")
    f.write("</head>\n")

def set_stamps(f):
    currentDT = str(datetime.datetime.now()).split()[0]
    f.write('<br><br>Created by <a href=http://www.physics.unlv.edu/~qzhu/index.html>Qiang Zhu</a>')
    f.write('<br>Last updated: ' + currentDT + '\n')

###############################################################
Materials_dict = {
     'Material_ID': [],
     'Formula': [],
     'Z': [],
     'Space_group': [],
     'Spg#': [],
     'Prototype': [],
     'dEdq': [],
     #'Nodal Line':[],
     #'Nodal Ring Point':[],
     #'Weyl Point':[],
     'Link': [],
    }

con = sqlite3.connect('test.db') 
cur = con.cursor()
sql = """SELECT * FROM Clean_materials"""
cur.execute(sql)
rows = cur.fetchall()
for row in rows:
    (mid, dEdq) = row
    if dEdq > 1:
        dEdq = '{:6.2f}'.format(dEdq)
        sql2 = "SELECT Material_id, Space_group, International_number, Formula, Z, Prototype\
              FROM Materials WHERE Material_id = '{:}'".format(mid)
        cur.execute(sql2)
        line = cur.fetchall()
        (mid, spg, number, formula, Z, prototype) = line[0]
        Materials_dict['dEdq'].append(dEdq)
        Materials_dict['Material_ID'].append(mid)
        Materials_dict['Formula'].append(formula)
        Materials_dict['Space_group'].append(spg)
        Materials_dict['Spg#'].append(number)
        Materials_dict['Prototype'].append(prototype)
        Materials_dict['Z'].append(Z)
        link = '<a href=materials/' + mid + '.html>detail</a>' 
        Materials_dict['Link'].append(link)
cur.close()

html_path = 'htmls/clean.html'
with open(html_path, 'w') as f:
    set_head(f, 'Clean Materials')
    set_style(f)
    f.write('<h2>Clean Materials</h2>\n')
    df = pd.DataFrame(Materials_dict)
    print(len(df))
    df = df.sort_values(['Z', 'Spg#', 'Prototype'], ascending=[True, False, False])
    raw_html = df.to_html(index=False, justify='center', col_space=20, escape=False)
    f.write(raw_html)
    set_stamps(f)
    f.write("</html>\n")

