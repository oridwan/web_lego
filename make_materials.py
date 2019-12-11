import sqlite3, os, datetime
from collections import OrderedDict
from tabulate import tabulate
import pandas as pd

def set_head(f, name):
    f.write("<html>\n")
    f.write("<head>\n")
    f.write("<title>"+name+"</title>\n")
    f.write("</head>\n")

def set_materials(f, spg, comp, id, prototype):
    currentDT = str(datetime.datetime.now()).split()[0]
    f.write('<div class="section" id="materials">\n')
    f.write('<h2>Materials info</h2>\n')
    f.write('<table>\n<thead>\n')
    f.write('<tr>\n')
    f.write('<th>Date page updated:</th>\n')
    f.write('<th>' + currentDT + '</th>\n')
    f.write('</tr>\n')
    f.write('<tr>\n')
    f.write('<th>Space group type:</th>\n')
    f.write('<th>' + spg + '</th>\n')
    f.write('</tr>\n')
    f.write('<tr>\n')
    f.write('<th>Formula:</th>\n')
    f.write('<th>' + comp + '</th>\n')
    f.write('</tr>\n')
    f.write('<tr>\n')

    f.write('<tr>\n')
    f.write('<th>Prototype:</th>\n')
    #f.write('<th><a href="../' + prototype + '.html">' + prototype +'</a></th>\n')
    f.write('<th>' + prototype + '</th>\n')
    f.write('</tr>\n')

    #f.write('<tr>\n')
    #f.write('<th>Materials Project link:</th>\n')
    #f.write('<th><a href="https://materialsproject.org/materials/' + id + '">' + id +'</a></th>\n')
    #f.write('</tr>\n')

    #f.write('<tr>\n')
    #f.write('<th>Phonon source link:</th>\n')
    #f.write('<th><a href="http://phonondb.mtl.kyoto-u.ac.jp/_downloads/' + id + '-20180417.tar.lzma">link</a></th>\n')
    #f.write('</tr>\n')

    f.write('</thead>\n</table>\n')

def set_style(f):
    f.write('<link rel="stylesheet" type="text/css" href="../../style.css" />\n')

def set_band_dos(f, fig_band, fig_dos):
    f.write('<div class="section" id="phonon-band-structure">\n')
    f.write('<h2>Phonon band structure and DOS</h2>\n')
    f.write('<div class="row">\n')
    f.write('<div class="column">\n')
    f.write('<img src = "' + fig_band + '" alt ="cfg">\n')
    f.write('</div>\n')
    f.write('<div class="column">\n')
    f.write('<img src = "' + fig_dos + '" alt ="cfg">\n')
    f.write('</div>\n')
    f.write('</div>\n')

def set_nodal_ring_table(f, cur, mid):
    cur.execute("""SELECT * FROM Nodal_ring_points WHERE Material_id = ?""", (mid,))
    pts = cur.fetchall()
    if len(pts)>0:
        pt_dict = OrderedDict()
        pt_dict = {
               'x': [],
               'y': [],
               'z': [],
               'Mode#1': [],
               'Mode#2': [],
               'Freq#1': [],
               'Freq#2': [],
               'DOS': [],
               'DOS_min': [],
               'Berryphase #1':[],
               'Berryphase #2':[],
               'Multiplicity':[],
               'Degeneracy': [],
               'Type': [],
               'Path_id': [],
               'Ratio': [],
              }
        for pt in pts:
            (_, x, y, z, mode1, mode2, freq1, freq2, dos, dos_min, c1, c2, multi, deg, w_type, path, ratio) = pt
            pt_dict['x'].append(x)
            pt_dict['y'].append(y)
            pt_dict['z'].append(z)
            pt_dict['Mode#1'].append(mode1+1)
            pt_dict['Mode#2'].append(mode2+1)
            pt_dict['Freq#1'].append(freq1)
            pt_dict['Freq#2'].append(freq2)
            pt_dict['DOS'].append('{:6.2f}'.format(dos))
            pt_dict['DOS_min'].append(dos_min)
            pt_dict['Berryphase #1'].append('{:6.2f}'.format(c1))
            pt_dict['Berryphase #2'].append('{:6.2f}'.format(c2))
            pt_dict['Multiplicity'].append(multi)
            pt_dict['Degeneracy'].append(deg)
            pt_dict['Type'].append(w_type)
            pt_dict['Path_id'].append(path)
            pt_dict['Ratio'].append('{:6.2f}'.format(ratio))

        f.write('<div class="section">\n')
        f.write('<h2>Nodal ring points along high symmetry path</h2>\n')
        f.write('<button type="button" class="collapsible">Open Collapsible</button>\n')
        df = pd.DataFrame(pt_dict)
        raw_html = df.to_html(index=False, justify='right', float_format='{:10,.4f}'.format, col_space=20)
        f.write(raw_html)

def set_nodal_ring2_table(f, cur, mid):
    cur.execute("""SELECT * FROM Nodal_ring_points2 WHERE Material_id = ?""", (mid,))
    pts = cur.fetchall()
    if len(pts)>0:
        pt_dict = OrderedDict()
        pt_dict = {
               'x': [],
               'y': [],
               'z': [],
               'Mode#1': [],
               'Mode#2': [],
               'Freq#1': [],
               'Freq#2': [],
               'DOS': [],
               'DOS_min': [],
               #'Chern Number1':[],
               #'Chern Number2':[],
               #'Berryphase #1':[],
               #'Berryphase #2':[],
               'Multiplicity':[],
               'Degeneracy': [],
               'Type': [],
               'Path_id': [],
               'Ratio': [],
              }
        for pt in pts:
            (_, x, y, z, mode1, mode2, freq1, freq2, dos, dos_min, c1, c2, multi, deg, w_type, path, ratio) = pt
            pt_dict['x'].append(x)
            pt_dict['y'].append(y)
            pt_dict['z'].append(z)
            pt_dict['Mode#1'].append(mode1+1)
            pt_dict['Mode#2'].append(mode2+1)
            pt_dict['Freq#1'].append(freq1)
            pt_dict['Freq#2'].append(freq2)
            pt_dict['DOS'].append('{:6.2f}'.format(dos))
            pt_dict['DOS_min'].append(dos_min)
            #pt_dict['Berryphase #1'].append(c1)
            #pt_dict['Berryphase #2'].append(c2)
            pt_dict['Multiplicity'].append(multi)
            pt_dict['Degeneracy'].append(deg)
            pt_dict['Type'].append(w_type)
            pt_dict['Path_id'].append(path)
            pt_dict['Ratio'].append('{:6.2f}'.format(ratio))

        f.write('<div class="section">\n')
        f.write('<h2>Nodal ring points along high symmetry path</h2>\n')
        f.write('<button type="button" class="collapsible">Open Collapsible</button>\n')
        df = pd.DataFrame(pt_dict)
        raw_html = df.to_html(index=False, justify='right', float_format='{:10,.4f}'.format, col_space=20)
        f.write(raw_html)


def set_Weyl_table(f, cur, mid):
    cur.execute("""SELECT * FROM Weyl_points WHERE Material_id = ?""", (mid,))
    pts = cur.fetchall()
    if len(pts)>0:
        pt_dict = OrderedDict()
        pt_dict = {
               'x': [],
               'y': [],
               'z': [],
               'Mode#1': [],
               'Mode#2': [],
               'Freq#1': [],
               'Freq#2': [],
               'DOS': [],
               'DOS_min': [],
               'Chern Number':[],
               'Multiplicity':[],
               'Degeneracy': [],
               'Type': [],
               'Path_id': [],
               'Ratio': [],
              }
        for pt in pts:
            (_, x, y, z, mode1, mode2, freq1, freq2, dos, dos_min, c1, c2, multi, deg, w_type, path, ratio, weyl) = pt
            if weyl >0:
                pt_dict['x'].append(x)
                pt_dict['y'].append(y)
                pt_dict['z'].append(z)
                pt_dict['Mode#1'].append(mode1+1)
                pt_dict['Mode#2'].append(mode2+1)
                pt_dict['Freq#1'].append(freq1)
                pt_dict['Freq#2'].append(freq2)
                pt_dict['DOS'].append('{:6.2f}'.format(dos))
                pt_dict['DOS_min'].append(dos_min)
                pt_dict['Chern Number'].append('{:6.2f}'.format(abs(c1)))
                pt_dict['Multiplicity'].append(multi)
                pt_dict['Degeneracy'].append(deg)
                pt_dict['Type'].append(w_type)
                pt_dict['Path_id'].append(path)
                pt_dict['Ratio'].append('{:6.2f}'.format(ratio))
        f.write('<div class="section">\n')
        f.write('<h2>Weyl points along high symmetry path</h2>\n')
        f.write('<button type="button" class="collapsible">Open Collapsible</button>\n')
        df = pd.DataFrame(pt_dict)
        raw_html = df.to_html(index=False, justify='right', float_format='{:10,.4f}'.format, col_space=20)
        f.write(raw_html)


def set_nls(f, cur, mid):
    cur.execute("""SELECT * FROM Nodal_lines WHERE Material_id = ?""", (mid,))
    paths = cur.fetchall()
    if len(paths) > 0:
        nl_dict = OrderedDict()
        nl_dict = {
               'Label1': [],
               'Label2': [],
               'Mode': [],
               'Start_ratio': [],
               'End_ratio': [],
              }
        for path in paths:
            (_, label1, label2, x1, y1, z1, x2, y2, z2, mode, start, end) = path
            label1 = decode_letter(label1)
            label2 = decode_letter(label2)
            label1 = label1 + ' ({:5.3f} {:6.3f} {:6.3f})'.format(x1, y1, z1)
            label2 = label2 + ' ({:5.3f} {:6.3f} {:6.3f})'.format(x1, y1, z1)
            nl_dict['Label1'].append(label1)
            nl_dict['Label2'].append(label2)
            nl_dict['Mode'].append(mode+1)
            nl_dict['Start_ratio'].append('{:6.2f}'.format(start))
            nl_dict['End_ratio'].append('{:6.2f}'.format(end))
        df = pd.DataFrame(nl_dict)
        raw_html = df.to_html(index=False, justify='right', escape=False)
        f.write('<div class="section" id="Nodal line details">\n')
        f.write('<h2>Nodal line details</h2>\n')
        f.write('<button type="button" class="collapsible">Open Collapsible</button>\n')
        f.write(raw_html)

def set_calculation(f, poscar, incar, potcar, kpoints, supercell):
    """
    Calculation details
    """
    f.write('<div class="row">\n')

    f.write('<div class="column3">\n')
    f.write('<h3>POSCAR-unitcell</h3>\n')
    for line in poscar:
        f.write('<br>{:s}'.format(line))
    f.write('</div>\n')

    f.write('<div class="column3">\n')
    f.write('<h3>INCAR</h3>\n')
    for line in incar:
        f.write('<br>{:s}'.format(line))
    f.write('</div>\n')

    f.write('<div class="column3">\n')
    f.write('<h3>POTCAR</h3>\n')
    for pot in potcar:
        f.write('<br>{:s}\n'.format(pot))
    f.write('<h3>KPOINTS</h3>\n')
    f.write('<br>{:s} {:s} {:s}\n'.format(kpoints[0], kpoints[1], kpoints[2]))
    f.write('<h3>Supercell in Phonon Calculation</h3>\n')
    f.write('<br>{:s} {:s} {:s}\n'.format(supercell[0], supercell[1], supercell[2]))
    f.write('</div>\n')

    f.write('</div>\n')

def set_stamps(f):
    currentDT = str(datetime.datetime.now()).split()[0]
    f.write('<br><br>Created by <a href=http://www.physics.unlv.edu/~qzhu/index.html>Qiang Zhu</a>')
    f.write('<br>Last updated: ' + currentDT + '\n')
    f.write("""<script>
            var coll = document.getElementsByClassName("collapsible");
            var i;
            
            for (i = 0; i < coll.length; i++) {
              coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.display === "block") {
                  content.style.display = "none";
                } else {
                  content.style.display = "block";
                }
              });
            }
            </script>""")

def decode_list(content):
    return content.split('\n')

def decode_letter(content):
    if content == '$\Gamma$':
        content = '&Gamma;'
    else:
        content = content.replace('$\mathrm{','')
        content = content.replace('}$','')
        if len(content)>1: # C_2
            content = content[0] + '<sub>' + content[2] + '</sub>'
    return content
###############################################################
html_dir = 'htmls/materials/'
if not os.path.exists(html_dir):
    os.makedirs(html_dir)

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

for row in rows:
    (mid, spg, number, formula, prototype, fig_band, fig_dos,\
     poscar, incar, potcar, kpoints, supercell) = row
    if fig_band.find('-2018') == -1:
        fig_band = fig_band.replace('-20180417', '')
        fig_dos = fig_dos.replace('-20180417', '')
        html_path = html_dir + mid + '.html'
        name = mid + '-' + formula
        print(html_path)
        with open(html_path, 'w') as f:
            set_head(f, name)
            set_style(f)
            f.write('<h2><a href="../../index.html">Back to index</a></h2>\n')
            set_materials(f, spg, formula, mid, prototype)
            poscar = decode_list(poscar)
            incar = decode_list(incar)
            potcar = decode_list(potcar)
            kpoints = decode_list(kpoints)
            supercell = decode_list(supercell)
            set_calculation(f, poscar, incar, potcar, kpoints, supercell)
            set_band_dos(f, fig_band, fig_dos)
            set_nls(f, cur, mid)
            set_nodal_ring_table(f, cur, mid)
            set_nodal_ring2_table(f, cur, mid)
            set_Weyl_table(f, cur, mid)
            set_stamps(f)
            f.write("</html>\n")
