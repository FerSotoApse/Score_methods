import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# color maps and categorical orders in plotly interactive plots


# Bar/Scatter subplots by event and teams

def score_figure(df_data, score_type, legend=True, scale=1, scatter_opacity=1, width = 900, height = 400, theme_colors=theme_colors):

    """
    Creates an interactive figure with subplots for each event and team. Can work for a single event
    or many, as for a single team or many.

    Parameters
    df: DataFrame containing all data features developed
    score_type: set 'accumulative' or 'performance'. If 'accumulative', will plot traditional scoring,
                if 'performance', will plot proposed scoring method based on medal relative frequency,
                ignoring team size.
    scale: set scale for scatter bubbles when score_type is 'accumulative' (1 by default). If score_type
                is set to 'performance', scatter bubbles scale multiplier is 0.1
    scatter_opacity: set a float from 0 to 1, changes scatter bubbles opacity (1 by default)
    """

    # set categorical medal before anything and sort values to have correct color per medal
    df = df_data.copy()
    df['medal'] = pd.Categorical(df['medal'], ordered=True, categories=['bronze', 'silver', 'gold'])
    df.sort_values(by=['team','medal'], ascending=[False,True], inplace=True)
    
    # score_type selector
    if score_type == 'accumulative':
        score_columns = ['medal_frequence', 'acc_w_score', 'acc_w_score_total']
    elif score_type == 'performance':
        score_columns = ['medal_relative', 'performance_score', 'performance_score_total']
    #---------------------------------------- build figure
    # team list
    team_names = [i for i in df['team'].unique()]
    # event list
    events = [i for i in df['event_game'].unique()]
    # subplots config
    score_fig = make_subplots(rows= len(events), cols= len(team_names),
                            shared_xaxes = True,
                            shared_yaxes=True,
                            column_titles= team_names,
                            print_grid=False,
                            specs = [[{"secondary_y" : True} for t in range(len(team_names))] for e in range(len(events))])
    
    #---------------------------------------- legend config
    sp_legendgroup = [legend]
    sp_legendgroup.extend([False for e in range(len(events[1:]))])

    #---------------------------------------- marker size parameter
    # sub-function: create an aux list of lists to flexibilize the code (indirect function)
    
    def marker_size(df, score_type, score_columns, scale):
    
        """
        Returns a list of lists to give marker size according to total scores. Use solely in score_figure function
        """
        
        l_aux = []
        l_subaux = []
        # first list groups total scores per event, all scores are in the same list
        for e in range(len(events)):
            l_subaux.extend([(df[df['event_game']== events[e]][score_columns[2]]).to_list()])
            if len(events)<2:
                if e == len(events):
                    break
            elif len(events)>=2:
                if e == len(events) -1:
                    break
            l_aux.append(l_subaux)
    
        # empty list of lists for 2nd for
        l_score_size = [[] for e in range(len(events))]
        
        # iterates through the auxiliar list to group scores by team, by event
        # the result is list[event idx][team idx]
        for e in range(len(events)):
            # first and last indexes
            first = 0
            last = 3
        
            if score_type == 'accumulative':
                l_score_size[e] = []
            # mask for each team score
            for t in range(len(team_names)):
                l_score_size[e].extend([l_aux[0][e][first:last]])
                first = first + 3
                last  = last + 3
        
        for e in range(len(events)):
            if score_type == 'accumulative':
                l_score_size[e] = [[s/scale for s in sl] for sl in l_score_size[e]]
            if score_type == 'performance':
                l_score_size[e] = [[s/10 for s in sl] for sl in l_score_size[e]]

        # clean memory
        del l_aux, l_subaux, first, last
        
        return l_score_size 
    #----------------------- marker size
    l_marker_size = marker_size(df = df, score_type = score_type, score_columns = score_columns, scale = scale)
    
    #---------------------------------------- build graphs
    for e in range(len(events)):
        for i in range(len(team_names)):
    #----------------------- traces: bar accumulative score values per medal: FIX FILL COLOR!!!
            score_fig.add_trace(
                go.Bar(
                    x = df[df['event_game']== events[e]][df['team']==team_names[i]]['medal'], #.map(lambda x : x.capitalize()),
                    y = df[df['event_game']== events[e]][df['team']==team_names[i]][score_columns[0]].values,
                    name = '<b>'+team_names[i]+' medals</b>',
                    #marker_color = [medal_colors[2], medal_colors[1],medal_colors[0], medal_colors[3]],
                    marker_color = [cm_medal[l] for l in df[df['event_game']== events[e]][df['team']==team_names[i]]['medal']],
                    #marker_line_color = [cm_team[l] for l in df[df['team']==team_names[i]]['team']],
                    marker_line_width = 2,
                    opacity = 0.8,
                    text = df[df['event_game']== events[e]][df['team']==team_names[i]][score_columns[0]].values,
                    textposition = 'inside',
                    textangle = 0,
                    textfont_color = 'black',
                    legendgroup = team_names[i]+' bar',
                    showlegend = sp_legendgroup[e],
                    customdata = df[df['event_game']== events[e]][df['team']==team_names[i]][['medal_frequence','medal', score_columns[1]]],
                    hovertemplate = '<br><i>Total medals</i>: %{customdata[0]} %{customdata[1]}<br>'+
                                    '<i>Medal score</i>: %{customdata[2]} points',
                ), row = e+1, col = i+1, secondary_y = False)

    #----------------------- traces: scatter accumulative total score values
            score_fig.add_trace(
                go.Scatter(
                    x = df[df['event_game']== events[e]][df['team']==team_names[i]]['medal'],#.map(lambda x : x.capitalize()),
                    y = df[df['event_game']== events[e]][df['team']==team_names[0]][score_columns[1]],
                    name = '<b>'+team_names[i]+ ' metrics</b>',
                    mode = 'markers',
                    marker_size = l_marker_size[e][i],
                    marker_color = [cm_team[l] for l in df[df['team']==team_names[i]]['team']],
                    #marker_line_color = [cm_medal[l] for l in df[df['event_game']== events[e]][df['team']==team_names[i]]['medal']],
                    marker_line_width = 2,
                    opacity = scatter_opacity,
                    legendgroup = team_names[i]+' scatter', # 'Scatter scores'
                    showlegend = sp_legendgroup[e], # change to scatter
                    customdata = df[df['event_game']== events[e]][df['team']==team_names[i]][['medal_relative','player_ratio', 'total_players', score_columns[2]]],
                    hovertemplate = '<br><i>Medal distribution</i>: %{customdata[0]}%<br>'+
                                    '<i>Participation</i>: %{customdata[1]}%<br>'+
                                    '<i>Team players</i>: %{customdata[2]}<br>'+
                                    '<br><b>Team Score</b>: %{customdata[3]}'
                ), row = e+1, col = i+1, secondary_y = True)
    #---------------------------------------- fix category orders for 0 values
    score_fig.update_xaxes(
        categoryorder = 'array',
        categoryarray = ['gold', 'silver', 'bronze'],
        showticklabels= False,
        showspikes = False)
    #---------------------------------------- applies secondary y axis for subplots
    score_fig.update_yaxes(
        side = 'right',
        secondary_y = True)
    #---------------------------------------- config: title, legend, hover, template, fig dimensions
    score_fig.update_layout(
        title = f"Event {score_type.capitalize()} scores, by teams, date {df['event_date'].unique()[0]}",
        barmode = 'group',
        legend_font_size = 8,
        legend_tracegroupgap = 0,
        hovermode = 'x unified',
        hoverlabel_align = 'right',
        barcornerradius = "50%",
        template = 'plotly_white',
        width = width, height = height)

    #----------------------- clean memory

    del df, score_type, score_columns, sp_legendgroup, l_marker_size
    
    #----------------------- 'show' line (return for Streamlit)
    return score_fig



# Custom Sunburst data

def polar_data(df, path, empty_leaf=None):

    """
    Data processing for polar charts, icicle and treemaps. Returns lists of ids, labels, parents and values,
    and a list with each level length for chart customization. The lengths are ordered by base element count
    (lv0), middle element count (lv1) and label (outter) count (lv2), useful for colormapping and hovertemplate
    customization.

    **Parameters**
    df: DataFrame that has no None or null values.
    path: list of column order for the subsequent chart. Start from base, inner or larger group to outmost,
        detailed data.
    empty_leaf: if some values don't reach the last detail level (or outmost ring), can set a str value
        that is not meant to be shown, leaving an empty space in the chart. This won't define ids, parents or
        labels for those values, keeping the same length for all output lists. Please note it allows for a
        single value (None by default).
    """
    # prep params
    levels = len(path)
    
    #----- build etiquettes
    # aux lists
    aux_id, aux_parent, aux_label, aux_value = [],[],[],[]
    
    # grouped df based on value counts, bypass bias from "score" and categorical columns
    df_gb = df.copy().value_counts(subset=path).reset_index()\
            .sort_values(path, ascending=True, ignore_index=True)
    
        # for full ring
    if empty_leaf == None:
        # insert values to aux_value
        aux_value = df_gb['count'].to_list()
        
        # for zip pack
        lv_iter = [tuple(df_gb[p]) for p in path]
        *lv, last = lv_iter
            
        # fill lists with level etiquettes
        for lv0,lv1,lv2 in zip(*lv, last):
            aux_id.append(f"{lv0}/{lv1}/{lv2}")
            aux_parent.append(f"{lv0}/{lv1}")
            aux_label.append(lv2)
    
        # for chart customization purposes
        len_lv2 = len(df_gb)
        
    # for fragmented ring
    else:
        aux_df = df_gb[df_gb[path[-1]] != empty_leaf]
        
    # insert values to aux_value, excluding where the ring won't be filled
        aux_value = aux_df['count'].to_list()
        
        # for zip pack
        lv_iter = [tuple(aux_df[p]) for p in path]
        *lv, last = lv_iter
            
        for lv0,lv1,lv2 in zip(*lv, last):
            aux_id.append(f"{lv0}/{lv1}/{lv2}")
            aux_parent.append(f"{lv0}/{lv1}")
            aux_label.append(lv2)
    
        len_lv2 = len(aux_df)
    
    #----- middle ring: repeats the process, sustracting the outer label
    levels -= 1
    path = path[:levels]
        
    # groupby and sort values
    df_gb = df_gb.groupby(path).sum('count').reset_index()
    df_gb.sort_values(by=path[levels::-1], ascending=True, ignore_index=True, inplace=True)
        
    # update zip
    lv_iter = [tuple(df_gb[p]) for p in path]
    *lv, last = lv_iter
        
    # build level
    aux_value.extend(df_gb['count'].to_list())
        
    for lv0,lv1 in zip(*lv, last):
        aux_id.append(f"{lv0}/{lv1}")
        aux_parent.append(f"{lv0}")
        aux_label.append(lv1)
    
    len_lv1 = len(df_gb)
    
    #----- inner circle: base labels
    levels -= 1
    path = path[:levels]
        
    # groupby and sort values
    df_gb = df_gb.groupby(path).sum('count').reset_index()
    df_gb.sort_values(by=path[levels::-1], ascending=True, ignore_index=True, inplace=True)
        
    # build level
    aux_value.extend(df_gb['count'].to_list())
    lv_iter = df_gb[path].values.flatten().tolist()
        
    for lv0 in lv_iter:
        aux_id.append(lv0)
        aux_parent.append("")
        aux_label.append(lv0)
    
    len_lv0 = len(df_gb)

    # clean memory
    del levels, df_gb, lv_iter, aux_df
    
    return aux_id, aux_label, aux_parent, aux_value, [len_lv0, len_lv1, len_lv2]

#----- sunburst function

#...

#-----


# bar polar for individual scores

def players_score_figure(df_data, sorted=True, ascending=True,hole=0.50, h=400, w=900, theme_colors=theme_colors):

    """
    Creates figure with barpolar subplots to represent individual players scores in each event in a given date.

    **Parameters**
    df_data: dataframe containing desagregate players, teams (factions, color, etc.), scores and score description
    (medal, cups, etc.)
    sorted: sorts players by scores (default: True).
    ascending: way player scores are sorted, only takes effect if sorted is set to True (default: True).
    hole: set empty center from 0 to 1 (default: 0.5)
    h: figure height (default: 400)
    w: figure width (defautl: 900)
    theme_colors: set colors in HEX code (default: color_theme palette in app, max. 5 colors)
    """

    # copy to keep integrity
    df=df_data.copy()
    # sort values before building the figure (if ascending=True)
    df.sort_values(['team', 'score'], ascending=ascending, inplace=sorted)

    # team list
    team_names = [i for i in df['team'].unique()]
    # event list
    events = [i for i in df['event_game'].unique()]
    # other config: color theme
    color_map = dict(zip(team_names, theme_colors[:len(team_names)]))
    
    #---------------------------------------- create Figure
    fig_polar = make_subplots(
        rows = 1, cols = len(events),
        column_titles = [f"Event: {e}" for e in events],
        specs = [[{'type':'polar'}]*len(df['event_game'].unique())]
    )
    #----------------------- config unified legend
    sp_legendgroup = [True]
    sp_legendgroup.extend([False for e in range(len(events[1:]))])
    sp_legendgroup
    
    #----------------------- traces: bar polar by event and team
    for e in range(len(events)):
        for t in range(len(team_names)):
            fig_polar.add_trace(go.Barpolar(
                name = "Team "+ team_names[t],
                r = list(df[df['event_game']==events[e]][df['team']==team_names[t]]['score']),
                theta = list(df[df['event_game']==events[e]][df['team']==team_names[t]]['player_id']),
                marker_color = theme_colors[t],
                legendgroup = team_names[t],
                showlegend = sp_legendgroup[e],
                customdata = df[df['event_game']==events[e]][df['team']==team_names[t]][['event_date', 'medal']],
                hovertemplate = "<extra><b style='color:black;'>" "Team "+ team_names[t] +"</b></extra>"
                                "<b>Player %{theta}</b><br>"+
                                "<br><i>Date</i>: %{customdata[0]}<br>"+
                                "<i>Medal</i>: %{customdata[1]}<br>"+
                                "<i>Score</i>: %{r} points"
                ),row=1, col=e+1)

    #----------------------- bar polar config
    fig_polar.update_polars(
        patch = dict(hole = hole,
                     radialaxis = dict(showticklabels=False,
                                       visible = False),
                     angularaxis= dict(showticklabels=False,
                                       visible = False,
                                       categoryorder = 'array',
                                       categoryarray = team_names)))

    #----------------------- figure layout
    fig_polar.update_layout(
        legend = dict(font_size = 10,
                      orientation = 'h',
                      yanchor = 'bottom'
                     ),
        hoverlabel = dict(bordercolor = 'white',
                          font_size = 8,
                          font_color = 'black',
                         ),
        template = 'plotly_white',
        height = h, width = w,
        margin = dict(t=70, l=50, r=50, b=70),
        title = f"Players participation during {', '.join(events[:-1])} and {events[-1]} events"
    )
    
    return fig_polar