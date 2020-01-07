import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_path_table(paths, labels):
    table = []
    for p, l in zip(paths, labels):
        col1 = html_label(l[0]) + ' ({:6.3f}, {:6.3f}, {:6.3f})'.format(p[0][0], p[0][1], p[0][2])
        col2 = html_label(l[1]) + ' ({:6.3f}, {:6.3f}, {:6.3f})'.format(p[1][0], p[1][1], p[1][2])
        table.append([col1, col2])
    return table

def get_pt_tables(pts):
    tables = [None]*3
    for w_dict in pts:
        path_id = w_dict['path_id'][0] + 1
        ratio = '{:6.3f}'.format(w_dict['ratio'][0])
        freq = '{:6.3f}'.format(w_dict['frequency1'])
        x, y, z, mode1, mode2 = w_dict['X'], w_dict['Y'], w_dict['Z'], w_dict['mode1'], w_dict['mode2']
        multi = w_dict['multiplicity']
        deg = w_dict['degeneracy']
        coordinate = ' ({:6.3f}, {:6.3f}, {:6.3f})'.format(x, y, z)
        type = w_dict['type']
        if tables[type] is None:
            tables[type] = []
        tables[type].append([coordinate, freq, mode1+1, mode2+1, multi, deg, path_id, ratio])

    return tables

def html_label(label):
    if label.find('Gamma')>0:
        label = '&#915;'
    elif label.find('mathrm')>0:
        label = label.replace('$\\mathrm{','')
        label = label.replace('}$','')
        if label.find('_')>0:
            label = label[:-2]+'<sub>'+label[-1]+'</sub>'
    return label


def get_ticks(path_connections, labels, distances):
    lefts = [0]
    rights = []
    for i, c in enumerate(path_connections):
        if not c:
            lefts.append(i + 1)
            rights.append(i)
    seg_indices = [list(range(l, r + 1)) for l, r in zip(lefts, rights)]
    ticks = []
    values = []
    count = 0
    for indices in seg_indices:
        for i in indices:
            value = distances[i][0]
            #label = html_label(labels[count])
            label = labels[count]
            count += 1
            if len(values) > 0:
                if value - values[-1] < 1e-3:
                    ticks[-1] = ticks[-1] + '|' + label
                else:
                    values.append(value)
                    ticks.append(label)    
            else:
                values.append(value)
                ticks.append(label)               
        if count < len(labels):
            values.append(distances[indices[-1]][-1])
            ticks.append(html_label(labels[count]))
            count += 1
    return values, ticks

def plot_all(frequencies, distances, path_connections, labels, \
             freq_pts, dos, pts, lines, title):
    #frequencies = my.phonon.band_structure.frequencies
    #distances   = my.phonon.band_structure.distances
    #path_connections = my.phonon.band_structure.path_connections
    #labels = my.phonon.band_structure.labels
    #freq_pts = my.phonon._total_dos.frequency_points
    #dos = my.phonon._total_dos.dos

    ratio = [0.8, 0.2]
    fig = make_subplots(rows=1, cols=2, 
                        shared_yaxes=True, 
                        horizontal_spacing=0.04,
                        column_widths = ratio,
                        #subplot_titles=("Band dispersion", "DOS")
                        subplot_titles=(title, "DOS")
                       )
    data = []
    for line in range(len(frequencies)):
        for mode in range(frequencies[line].shape[1]):
            trace1 = go.Scatter(
                x = distances[line],
                y = frequencies[line][:,mode],
                showlegend = False,
                line = dict(color='royalblue'),
                mode = 'lines',
                )
            fig.add_trace(trace1, row=1, col=1)
    
    for line in lines:
        path_id = line['path_id']
        ratio1 = line['Start_ratio']
        ratio2 = line['End_ratio']
        mode = line['mode']
        _distances = distances[path_id]
        min_ID = int(round(len(_distances)*ratio1))
        max_ID = int(round(len(_distances)*ratio2))
        freqs = frequencies[path_id][min_ID:max_ID, mode]
        trace1 = go.Scatter(
                x = _distances[min_ID: max_ID],
                y = freqs,
                showlegend = False,
                line = dict(color='firebrick'),
                mode = 'lines',
                #name = 'Nodal Lines',
                )
        fig.add_trace(trace1, row=1, col=1)
    
    # now collect the points
    Name = ['Wely points', 'Multi Weyl points', 'Nodal ring points']
    colors_lib = ['yellow', 'green', 'grey']
    for symbol in [0, 1, 2]:
        xs = []
        ys = []
        for w_dict in pts:
            if w_dict['type'] == symbol:
                path_ids = w_dict['path_id']
                ratios = w_dict['ratio']
                freq1 = w_dict['frequency1']
                freq2 = w_dict['frequency2']
                for path_id, ratio in zip(path_ids, ratios):
                    dist = distances[path_id]
                    q_dist = dist[0] + ratio*(dist[-1]-dist[0])
                    xs.append(q_dist)
                    ys.append(freq1)
                    if abs(freq1-freq2)>1e-2:
                        xs.append(q_dist)
                        ys.append(freq2)

        trace1 = go.Scatter(
                x = xs,
                y = ys,
                mode='markers',
                #showlegend = False,
                name = Name[symbol],
                marker = dict(size=8, symbol=symbol, color=colors_lib[symbol]),
                )
        fig.add_trace(trace1, row=1, col=1)
        #print(len(xs), Name[symbol])
    
    # Now plot DOS
    trace2 = go.Scatter(
        x=dos,
        y=freq_pts,
        xaxis="x2",
        line = dict(color='lightpink'),
        showlegend = False,
    )
    fig.add_trace(trace2, row=1, col=2)
    
    values, ticks = get_ticks(path_connections, labels, distances)
    fig.update_xaxes(
        tickmode='array',
        tickvals = values,
        ticktext = ticks,
        range=[0, max(distances[-1])],
        col = 1,
        row = 1,
        )
    freqs = [ max(x[-1]) for x in frequencies ]
    fig.update_yaxes(range=[0, 1.05*max(freqs)])

    fig.update_layout(height=600, 
                      width=1080, 
                      #title = title,
                      yaxis_title = 'Frequency (THZ)')
    #html = fig.write_html(html_file)
    return fig
