import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
            label = labels[count]
            count += 1
            if label.find('Gamma')>0:
                label = '&#915;'
            elif label.find('mathrm')>0:
                label = label.replace('$\\mathrm{','')
                label = label.replace('}','')
                if label.find('_')>0:
                    label = label+'<sub>'+label[-1]+'</sub>'
            if len(values) > 0:
                if value - values[-1] < 1e-3:
                    ticks[-1] = ticks[-1][:-1]
                    if ticks[-1][-1] == '}':
                        ticks[-1] = ticks[-1][:-1]
                        label = label.replace('$\\mathrm{','')
                    ticks[-1] = ticks[-1] + '|' + label
                else:
                    values.append(value)
                    ticks.append(label)    
            else:
                values.append(value)
                ticks.append(label)               
        if count < len(labels):
            values.append(distances[indices[-1]][-1])
            ticks.append(labels[count])
            count += 1
    return values, ticks

my_test.phonon.auto_band_structure()
frequencies = my_test.phonon.band_structure.frequencies
distances = my_test.phonon.band_structure.distances
path_connections = my_test.phonon.band_structure.path_connections
labels = my_test.phonon.band_structure.labels
freq_pts = my_test.phonon._total_dos.frequency_points
dos = my_test.phonon._total_dos.dos
ratio = [0.8, 0.2]
fig = make_subplots(rows=1, cols=2, 
                    shared_yaxes=True, 
                    horizontal_spacing=0.04,
                    column_widths = ratio,
                    subplot_titles=("Band dispersion", "DOS")
                   )

data = []
for line in range(len(frequencies)):
    for mode in range(frequencies[line].shape[1]):
        trace1 = go.Scatter(
            x = distances[line],
            y = frequencies[line][:,mode],
            showlegend = False,
            line = dict(color='royalblue'),
            )
        fig.add_trace(trace1, row=1, col=1)
        
trace1 = go.Scatter(
            x = [0, 0.1, 0.2],
            y = [3.4, 3.2, 2.5],
            mode='markers',
            showlegend = False,
            )
fig.add_trace(trace1, row=1, col=1)
        
        
trace2 = go.Scatter(
    x=dos,
    y=freq_pts,
    xaxis="x2",
    line = dict(color='firebrick'),
    showlegend = False,
)
fig.add_trace(trace2, row=1, col=2)

values, ticks = get_ticks(path_connections, labels, distances)
fig.update_xaxes(
    tickmode='array',
    tickvals = values,
    ticktext = ticks,
    col = 1,
    row = 1,
    )

fig.update_layout(height=600, 
                  width=1000, 
                  title = 'AAA',
                  yaxis_title = 'Frequency (THZ)')
fig.show()
