import plotly.graph_objects as go
import plotly.io as pio
import datetime


# template: alpha 0, custom annot (sim data + timestamp), custom colorscales/colorway
timestamp = datetime.datetime.now(tz = datetime.timezone.utc)
utc_timestamp = timestamp.replace(tzinfo = datetime.timezone.utc).timestamp()

pio.templates['aer_bg_alpha0_tstmp'] = go.layout.Template(
    layout_annotations = [dict(
        name = 'timestamp',
        text = f'Simulated Data · {timestamp.strftime("%Y-%B-%d, %H:%M:%S %Z %z")}<br>Timestamp:{utc_timestamp}',
        textangle = 0,
        opacity = 0.3,
        font = dict(color = 'gray', size = 12),
        xref = 'paper',
        yref = 'paper',
        x = 0.5,
        y = 0.01,
        showarrow = False)],
    layout_geo_bgcolor = 'rgba(0,0,0,0)',
    layout_polar_bgcolor = 'rgba(0,0,0,0)',
    layout_ternary_bgcolor = 'rgba(0,0,0,0)',
    layout_paper_bgcolor = 'rgba(0,0,0,0)',
    layout_plot_bgcolor = 'rgba(0,0,0,0)',
    layout_colorway = ['#84a6f5', '#ff78b2', '#ecfa91', '#c485dd', '#ffa8e7',
                       '#616cd6', '#ff7383', '#3dc8ff', '#0064c2', '#fa8c91'],
    layout_colorscale_diverging = [[0, '#F29ABD'],
                                   [0.1, '#F2AAB8'],
                                   [0.2, '#F1BBB3'],
                                   [0.3, '#F1CBAF'],
                                   [0.4, '#F0DCAA'],
                                   [0.5, '#F0ECA5'],
                                   [0.6, '#CAD3A7'],
                                   [0.7, '#A4B9AA'],
                                   [0.8, '#7DA0AC'],
                                   [0.9, '#5786AF'],
                                   [1, '#316DB1']],
    layout_colorscale_sequential = [[0.0, '#EEC5DD'],
                                    [0.1111111111111111, '#DBBCD8'],
                                    [0.2222222222222222, '#C8B3D4'],
                                    [0.3333333333333333, '#B5ABD0'],
                                    [0.4444444444444444, '#A2A2CB'],
                                    [0.5555555555555556, '#9099C7'],
                                    [0.6666666666666666, '#7D90C3'],
                                    [0.7777777777777778, '#6A87BE'],
                                    [0.8888888888888888, '#577FBA'],
                                    [0.9999999999999999, '#4476B5'],
                                    [1.0, '#316DB1']],
    layout_colorscale_sequentialminus =  [[0.0, '#EEC5DD'],
                                    [0.1111111111111111, '#DBBCD8'],
                                    [0.2222222222222222, '#C8B3D4'],
                                    [0.3333333333333333, '#B5ABD0'],
                                    [0.4444444444444444, '#A2A2CB'],
                                    [0.5555555555555556, '#9099C7'],
                                    [0.6666666666666666, '#7D90C3'],
                                    [0.7777777777777778, '#6A87BE'],
                                    [0.8888888888888888, '#577FBA'],
                                    [0.9999999999999999, '#4476B5'],
                                    [1.0, '#316DB1']])
