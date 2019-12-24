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
html_dir = 'htmls/'
if not os.path.exists(html_dir):
    os.makedirs(html_dir)

Materials_dict = {
     'Material_ID': [],
     'Formula': [],
     'Z': [],
     'Space_group': [],
     'Spg#': [],
     'Prototype': [],
     'Nodal Line':[],
     'Nodal Ring Point':[],
     'Weyl Point':[],
     'Link': [],
    }

con = sqlite3.connect('test.db') 
cur = con.cursor()
sql = """SELECT Material_id,
      Space_group,
      International_number,
      Formula,
      Z,
      Prototype
      FROM Materials"""

cur.execute(sql)
rows = cur.fetchall()
tables = ['Materials', 'Nodal_lines', 'Nodal_ring_points', 'Nodal_ring_points2', 'Weyl_points', 'Clean_materials']
data = [0]*len(tables)
for i, table in enumerate(tables):
    cur.execute("SELECT * from {:}".format(table))
    data[i] = len(cur.fetchall())

for row in rows:
    (mid, spg, number, formula, Z, prototype) = row
    Materials_dict['Material_ID'].append(mid)
    Materials_dict['Formula'].append(formula)
    Materials_dict['Space_group'].append(spg)
    Materials_dict['Spg#'].append(number)
    Materials_dict['Prototype'].append(prototype)
    Materials_dict['Z'].append(Z)
    link = '<a href=htmls/materials/' + mid + '.html>detail </a>' 
    Materials_dict['Link'].append(link)
    stat = [0]*4
    for i, table in enumerate(tables[1:-1]):
        cur.execute("SELECT * from {:} WHERE Material_id = '{:}'".format(table, mid))
        stat[i] = len(cur.fetchall())
    Materials_dict['Nodal Line'].append(stat[0])
    Materials_dict['Nodal Ring Point'].append(stat[1]+stat[2])
    Materials_dict['Weyl Point'].append(stat[3])

cur.close()

html_path = 'index.html'
with open(html_path, 'w') as f:
    set_head(f, 'Topological Phonon Database')
    set_style(f)

    f.write('<div class="section" id="materials">\n')
    f.write('<h2>Summary</h2>\n')
    f.write('<table>\n<thead>\n')
    for i, table in enumerate(tables):
        f.write('<tr>\n')
        if i == len(tables)-1:
            table = '<a href=htmls/clean.html>'+table+'</a>'
        f.write('<th>Number of {:}:</th>\n'.format(table))
        f.write('<th>{:}</th>\n'.format(data[i]))
        f.write('</tr>\n')
    f.write('</thead>\n</table>\n')

    f.write('<h2>All Materials</h2>\n')
    df = pd.DataFrame(Materials_dict)
    df = df.sort_values(['Z', 'Spg#', 'Prototype'], ascending=[True, False, False])
    df.to_csv('summary.csv')
    raw_html = df.to_html(index=False, justify='center', col_space=20, escape=False)
    f.write(raw_html)
    set_stamps(f)
    f.write("</html>\n")

