import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


# Bar funcions------------------------------------------------------------------

# Faceted bar with hline (specific score plots)
def cust_bar_hline(df_data: pd.DataFrame,
                   x_data: str, y_data: str, facet_data_col: str, selector: str, selector_filter: str,
                   hline_values: str = None, hline_annot_iter: list = None, hline_annot: str = '', show_hline :bool = False,
                   y_title: str = None, customdata_cols: list=None, hovertemplate: str = None,
                   category_order: list = None,
                   title: str=None, barcornerradius: str = '0%', theme: str = 'plotly_white',
                   w: int = 900, h: int = 400) -> go.Figure:
    """
    Function
    -
    Creates a figure with interactive bar plots and horizontal lines. Recommended for
    data that has agregated numerical values.

    Parameters
    -
    - **df_data**: *pd.DataFrame*, main data to plot
    - **x_data**: *str*, category values on x axis for barplots
    - **y_data**: *str*, numerical values on y axis for barplots
    - **facet_data_col**: *str*, column with categorical data to facet plots
    - **selector**: *str*, filter value, can be set directly, recommended for value selector objects
    - **hline_values**: *str = None*, column with values for horizontal line position
    - **hline_annot_iter**: *list = None*, list or array to iterate for hline annotation
    - **hline_annot**: *str = ''*, additional annotation
    - **show_hline** : *bool = False*, if True, adds horizontal lines on bar subplots
    - **y_title**: *str = None*, single y axis title for all subplots
    - **customdata_cols**: *list = None*, list of columns that will be used in hovertemplate
    - **hovertemplate**: *str = None*, text displayed on hover info and label, using html text format
    - **category_order**: *list = None*, sort bar plot figures
    - **title**: *str= None*, figure title
    - **barcornerradius**: *str = '0%'*, set bar round corners
    - **theme**: *str = 'plotly_white'*, set plotly template to mix with default template
    - **w**: *int = 900*, set figure width 
    - **h**: *int = 400*, set figure height
    """

    # Iterative variables
    subplot_cols = list(df_data[facet_data_col].unique())

    template_color = pio.templates[pio.templates.default]['layout']['colorway']
    color_theme = template_color[:len(subplot_cols)]

    # Subplot figure
    bar_h_fig = make_subplots(cols = len(subplot_cols),
                            shared_xaxes = True,
                            shared_yaxes=True,
                            #y_title = y_title,
                            column_titles= subplot_cols,
                            print_grid=False,
                            specs = [[{"secondary_y" : True} for t in range(len(subplot_cols))]])
    # legend group
    bar_legendgroup = [True]
    bar_legendgroup.extend([False for e in range(len(subplot_cols[1:]))])

    # bar
    for i in range(len(subplot_cols)):
        bar_h_fig.add_trace(
            go.Bar(
                x = df_data[df_data[selector]==selector_filter][df_data[facet_data_col]==subplot_cols[i]][x_data],
                y = df_data[df_data[selector]==selector_filter][df_data[facet_data_col]==subplot_cols[i]][y_data].values,
                name = subplot_cols[i],
                marker_color = color_theme[i], marker_line_width = 0,
                legendgroup = subplot_cols[i]+' bar',
                customdata = df_data[df_data[selector]==selector_filter][df_data[facet_data_col]==subplot_cols[i]][customdata_cols],
                hovertemplate = hovertemplate
            ),row = 1, col = i+1, secondary_y = False)
    # hline
    if show_hline == True:
        for i in range(len(subplot_cols)):
            bar_h_fig.add_hline(y = df_data[df_data[selector]==selector_filter][df_data[facet_data_col]==subplot_cols[i]][hline_values].unique()[0],
                            line_color = color_theme[i],
                            line_width = 1,
                            annotation_text = f"{hline_annot_iter[i]}{hline_annot}",
                            annotation_position = 'bottom left',
                            exclude_empty_subplots=False, secondary_y=True)

    # axes styling and category order
    #----- x axes
    bar_h_fig.update_xaxes(
        categoryorder = 'array',
        categoryarray = category_order,
        matches = 'x',
        showticklabels= False,
        showspikes = False,
        showgrid = False)
    #----- y axes (matches param fixes hline_annot weird positioning too)
    bar_h_fig.update_yaxes(showgrid = False, showticklabels = False, matches = 'y')
    bar_h_fig.update_yaxes(showticklabels = True, secondary_y = True)
    #---------- if y_title doesn`t work from Figure in app output, use this line
    bar_h_fig.update_yaxes(title=y_title, secondary_y=False)

    # layout styling
    if title!= None:
        bar_h_fig.update_layout(title=title)
    else:
        bar_h_fig.update_layout(margin_t= 50)
    
    bar_h_fig.update_layout(
            barmode = 'group',
            legend = dict(font_size = 14,
                        tracegroupgap = 0, y = -.2,
                        yanchor = 'bottom', xanchor = 'left',
                        orientation = 'h'),
            barcornerradius = barcornerradius,
            template = f'{theme}+{pio.templates.default}',
            width = w, height = h)

    return bar_h_fig

# grouped metrics bar plot


#------------------------------------------------------------------------------

# Barpolar funcion-------------------------------------------------------------

def cust_barpolar(df_data: pd.DataFrame, r: str, theta: str, group_data:str, color_order: list|tuple, sortby: str|list,
                  title: str = None, customdata = None, hovertemplate = None, add_name:str = '',
                  h: int = 400, w: int = 400, hole: float = .0, theme: str = 'plotly_white',
                  ascending: bool = True, sorted: bool = True) -> go.Figure:
    """
    Function
    -
    Creates a custom barpolar from plotly.graphic_objects.Barpolar
    
    Parameters
    - df_data: pd.DataFrame, main data for plot
    - r: str, column containing numerical values
    - theta: str, column containing radial bar labels
    - group_data: str, column containing data categories
    - color_order: list|tuple, set color order, recommended to standarize with other plots in a dashboard
    - sortby: str|list column(s) used to sort values. Even if sorted=False, it must be specified
    - title: str = None, plot title
    - customdata = None, specify additional data to be shown in hover
    - hovertemplate = None, specify hover template with custom data
    - add_name:str = None, plot name for plotly make_subplots
    - h: int = 400, plot hight
    - w: int = 400 plot width
    - hole: float = .0, hole size, value between 0 and 1
    - theme: str = 'plotly_white', theme used, with be mixed with default theme
    - ascending: bool = True, sorting order (False for descending order)
    - sorted: bool = True, if False, data will be in original order and other sorting params won`t
        take effect
    """
    # copy to keep integrity
    df=df_data.copy()
    # sort values before building the figure (if ascending=True)
    df.sort_values(sortby, ascending=ascending, inplace=sorted)

    #----- color theme from default template
    template_color = pio.templates[pio.templates.default]['layout']['colorway']
    color_theme = tuple(template_color[:len(color_order)])
    group_color = {order:color for order,color in zip(color_order, color_theme)}

    group = tuple(group_color.keys())

    # barpolar figure
    fig_s_barpolar = go.Figure()
    for i in range(len(group)):
        r_values = list(df[df[group_data] == group[i]][r])
        t_values = list(df[df[group_data] == group[i]][theta])
        fig_s_barpolar.add_traces(go.Barpolar(
            name = f"{add_name}{group[i]}",
            r = r_values,
            theta = t_values,
            marker_color = group_color[group[i]],
            marker_line_color = group_color[group[i]],
            customdata = df[df[group_data] == group[i]][customdata],
            hovertemplate = hovertemplate))
        
    fig_s_barpolar.update_polars(
        patch = dict(
            hole = hole,
            radialaxis = dict(
                showticklabels=False,
                visible = False),
            angularaxis= dict(
                showticklabels=False,
                visible = False,
                categoryorder = 'array',
                categoryarray = color_order)),
        bargap = 0)
    #----- figure layout
    if title != None:
        fig_s_barpolar.update_layout(title=title)
    else:
        fig_s_barpolar.update_layout(title=' ', margin_t = 50)

    fig_s_barpolar.update_layout(
        legend = dict(
            font_size = 14,
            orientation = 'h',
            y = 1.1,
            x = 0, bgcolor = 'rgba(255,255,255,0.2)'),
        hoverlabel = dict(
            bordercolor = 'rgba(0,0,0,0)',
            font_size = 12
            ),
        template = f'{theme}+{pio.templates.default}',
        margin = dict(b = 0, l=0, r=0),
        height = h, width = w
    )
    
    return fig_s_barpolar

#------------------------------------------------------------------------------

# Sunburst function-------------------------------------------------------------

# 1 - structure data path
def polar_data_path(data: pd.DataFrame, lv_base:str, lv_mid:str, lv_out:str, empty_leaf: str=None) -> list[pd.DataFrame, list[int]]:

    """
    Function
    -
    Data processing for polar charts, icicle and treemaps. Returns formated data according to given path columns,
    ideal to create subplot traces with plotly graph_objects and plotly make_subplots.

    Parameters
    -
    - data: DataFrame that has no None or null values, must be raw or disaggregated data
    - lv_base: column of strings with base (root) labels
    - lv_mid: column of strings with middle ring (branch) labels
    - lv_out: column of strings with outter ring (leafs) labels
    - empty_leaf: if some values don't reach the last detail level (or outmost ring), can set a str value
        that is not meant to be shown, leaving an empty space in the chart. This won't define ids, parents or
        labels for those values, keeping the same length for all output lists. Please note it allows for a
        single value (None by default).

    Returns
    -
    A pd.DataFrame with ids, labels, parents and values columns, and a list of integers with each level length,
    starting from leaf to root.
    """

    # prep params-----------------------------------------------------------
    path = [lv_base, lv_mid, lv_out]
    levels = len(path)
    aux_id, aux_parent, aux_label, aux_value = [],[],[],[]

    # grouped df based on value counts, bypass bias from "score" and categorical columns
    df_gb = data.copy().value_counts(subset=path).reset_index()\
    .sort_values(path, ascending=True, ignore_index=True)

    df_gb.columns = [lv_base, lv_mid, lv_out, 'count']
    #-----------------------------------------------------------------------

    # Leaf / Outer Level----------------------------------------------------
    # for full ring
    if empty_leaf == None:
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
        len_lv2 = len(aux_id)
            
    # for fragmented ring
    else:
        aux_df = df_gb[df_gb[path[-1]] != empty_leaf]
            
        # insert values to aux_value, excluding where the ring won't be filled
        aux_value = aux_df['count'].to_list()
            
        lv_iter = [tuple(aux_df[p]) for p in path]
        *lv, last = lv_iter
                
        for lv0,lv1,lv2 in zip(*lv, last):
            aux_id.append(f"{lv0}/{lv1}/{lv2}")
            aux_parent.append(f"{lv0}/{lv1}")
            aux_label.append(lv2)
        
        len_lv2 = len(aux_id)
    #-----------------------------------------------------------------------

    # Branch / Middle Level-------------------------------------------------
    levels -= 1
    path = path[:levels]
            
    df_gb = df_gb.groupby(path).sum('count').reset_index()
    df_gb.sort_values(by=path[levels::-1], ascending=True, ignore_index=True, inplace=True)
            
    lv_iter = [tuple(df_gb[p]) for p in path]
    *lv, last = lv_iter
            
    # build level
    aux_value.extend(df_gb['count'].to_list())
            
    for lv0,lv1 in zip(*lv, last):
        aux_id.append(f"{lv0}/{lv1}")
        aux_parent.append(f"{lv0}")
        aux_label.append(lv1)
        
    len_lv1 = len(aux_id)
    #-----------------------------------------------------------------------

    # Root / Base Level-----------------------------------------------------
    levels -= 1
    path = path[:levels]
            
    df_gb = df_gb.groupby(path).sum('count').reset_index()
    df_gb.sort_values(by=path[levels::-1], ascending=True, ignore_index=True, inplace=True)
            
    # build level
    aux_value.extend(df_gb['count'].to_list())
    lv_iter = df_gb[path].values.flatten().tolist()
            
    for lv0 in lv_iter:
        aux_id.append(lv0)
        aux_parent.append("")
        aux_label.append(lv0)
        
    len_lv0 = len(aux_id)
    #-----------------------------------------------------------------------

    return pd.DataFrame({'ids':aux_id, 'parents':aux_parent, 'labels':aux_label, 'values':aux_value}), [len_lv2, len_lv1-len_lv2, len_lv0-len_lv1 ]
    #-----------------------------------------------------------------------

# 2 - Structure hover template

# 2.1 - hovertemplate info data groups
def customdata_levels(data : pd.DataFrame, col_orders : list[str], mode : str = 'simple',
                      categorical_cols : str | list[str] = None):
    """
    Function
    -
    Adapts input data for hovertemplate customdata and formating in plotly tree-type figures

    Parameters
    -
    - data: dataframe with additional data not present in figure main data
    - col_orders: list of all columns, sorted as needed. If mode is set to 'group', the last
        column will be used to create a sum column
    - mode: can be 'simple' or 'group' (default: 'simple'). In simple mode, a sort_values will
        be applied, in 'group' mode, a groupby will be applied instead, with a resulting sum column
    - categorical_cols: columns to rectify it's dtype from categorical to object. Recommended
        when the category orders affects and creates discrepancies.
    """
    if categorical_cols != None:
        data.reset_index(inplace=True)
        aux_data = data[categorical_cols].to_numpy()
        data[categorical_cols] = pd.DataFrame(aux_data, dtype='object')

    match mode:
        case 'simple':
            c_data = data.sort_values(by= col_orders, ignore_index=True)
        case 'group':
            c_data = data[col_orders].groupby(col_orders[:-1]).sum(col_orders[-1]).reset_index()

    return c_data

# 2.2- hovertemplate structure to add in customdata patameter
def polar_customdata(data : list[pd.DataFrame], customdata_l : list[str],
                     customdata_b : list[str], customdata_r : list[str],
                     n_rows : list[int], col_orders : list[list]) -> list[str]:
    """
    Function
    -
    Creates a list with custom template hover data for each level rendered in a tree or polar
    plotly plot with base, one branch and leafs (3 level depth). This function can be
    modified according to each plotly tree-like or polar-like structure.

    Parameters
    -
    - data: list with 3 data origins related to data path used in a tree/polar figure
    - customdata_l: columns used, in order, to be displayed in hover for leaf level
    - customdata_b: columns used, in order, to be displayed in hover for branch level
    - customdata_r: columns used, in order, to be displayed in hover for root level
    - n_rows: level n_rows from data path, from leaf to root
    - col_orders: list of columns used to sort each data level, must be the same order
        as in data path levels
    """

    # check lenghts (avoid error)
    data_leaf = customdata_levels(data = data[0], col_orders = col_orders[0],
                                categorical_cols= 'medal')
    data_branch = customdata_levels(data = data[1], col_orders = col_orders[1], mode = 'group')
    data_root = customdata_levels(data = data[2], col_orders = col_orders[2], mode = 'group')

    if len(data_leaf) != n_rows[0]:
        return "Leaf data has not the same length as leaf data info"
    if len(data_branch) != n_rows[1]:
        return "Branch data has not the same length as branch data info"
    if len(data_root) != n_rows[2]:
        return "Root data has not the same length as root data info"

    # leaf customdata-----------------------------------------------------------------
    hover_leaf = [f"<b>{data_leaf[customdata_l[0]].at[i].capitalize()} medal</b><br>"+
                f"<i>Medal count</i>: {data_leaf[customdata_l[1]].at[i]}<br>"+
                f"<i>Medal relative count</i>: {data_leaf[customdata_l[2]].at[i]}%<br>"+
                f"<br><b>Medal Score Methods</b><br>"+
                f"<i>Accumulative</i>: {data_leaf[customdata_l[3]].at[i]}<br>"+
                f"<i>Performance</i>: {data_leaf[customdata_l[4]].at[i]:.2f}<br>"+
                "<extra></extra>" for i in range(n_rows[0])]

    # branch customdata---------------------------------------------------------------
    hover_branch = [f"<b>{data_branch[customdata_b[0]].at[i].capitalize()}</b><br>"+
                    f"<i>Active team`s players</i>: {data_branch[customdata_b[1]].at[i]}<br>"+
                    f"<i>Team participation</i>: {data_branch[customdata_b[2]].at[i]}%<br>"+
                    f"<br><b>Team Score Methods</b><br>"+
                    f"<i>Accumulative</i>: {data_branch[customdata_b[3]].at[i]}<br>"+
                    f"<i>Performance</i>: {data_branch[customdata_b[4]].at[i]:.2f}<br>"+
                    "<extra></extra>" for i in range(n_rows[1])]

    # root customdata-----------------------------------------------------------------
    hover_root = [f"<b>Event {data_root[customdata_r[0]].at[i].capitalize()}</b><br>"+
                    f"<i>Player count</i>: {data_root[customdata_r[1]].at[i]}<br>"+
                    "<extra></extra>" for i in range(n_rows[2])]


    customdata_l = hover_leaf+hover_branch+hover_root

    return customdata_l

#...
