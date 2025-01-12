import numpy as np
import pandas as pd

import plotly.graph_objects as go
#from plotly.subplots import make_subplots
import plotly.io as pio
from plotly.validators.scatter.marker import SymbolValidator

from sklearn.preprocessing import Normalizer
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans

import streamlit as st

import warnings
warnings.simplefilter("ignore", UserWarning)


# Preprocess

def preprocess(base : pd.DataFrame) -> list:
    df_clust_data = base[['event_date', 'player_id', 'team', 'score', 'medal']].copy()
    df_clust_data['player_participation'] = df_clust_data['medal'].replace({'gold':1, 'silver':1, 'bronze':1, 'not played':0})
    df_clust_data = df_clust_data.groupby(['event_date', 'player_id', 'team']).sum(['score', 'played']).reset_index()

    df_clust_data['player_participation'] = df_clust_data['player_participation'].apply(lambda x: x/len(base['event_game'].unique()))
    df_clust_data = pd.concat([df_clust_data, pd.get_dummies(df_clust_data['team'])], axis=1)

    X = df_clust_data[['score', 'player_participation']].to_numpy()
    #X = df_clust_data[['score', 'player_participation'] + list(df_clust_data['team'].unique())].to_numpy()

    return X, df_clust_data

# Best params selector for unsupervised kmeans

def kmeans_silhouette_score_eval(X : np.array) -> list:
    """
    Function
    -
    Cluster labels, ideal number of clusters, average silhouete score and label samples,
    based on sklearn metrics

    Parameters
    -
    - X: numpy array with data to cluster with KMeans
    """

    # evaluate silhouette best score and n_clusters
    clusters, label_l, sample_l, c_centers, avg_sil_score, inertias = [], [], [], [], [], []

    for n_clusters in range(2, len(X)):
        kmeans = KMeans(n_clusters = n_clusters)
        labels = kmeans.fit_predict(X)
        samples = silhouette_samples(X, labels)
        sil_score = silhouette_score(X, labels)
        centroid_innertia = kmeans.inertia_
        centroids = kmeans.cluster_centers_

        clusters.append(n_clusters)
        label_l.append(labels) # list of labels (list)
        sample_l.append(samples) # list of samples (list)
        c_centers.append(centroids) # list of centroids (list)
        avg_sil_score.append(sil_score)
        inertias.append(centroid_innertia) # list of inertias (list)

    # sort together to get best score with clusters
    eval = pd.DataFrame({'n_clusters' : clusters,
                'silhouette_score' : avg_sil_score}
                ). sort_values('silhouette_score', ascending=False, ignore_index=True)

    avg_sil_score_eval = eval.at[0,'silhouette_score']
    clusters_eval = eval.at[0,'n_clusters']

    # build dict with all data
    kmean_outputs : dict = {
        'clusters'  : clusters,
        'labels'    : label_l,
        'samples'   : sample_l,
        'centroids' : c_centers,
        'silhouette': avg_sil_score,
        'inertias'  : inertias
    }

    return avg_sil_score_eval, clusters_eval, kmean_outputs
#----------------------------------------------------------------------------------

# Preprocess and usupervised clustering model application 
@st.cache_data(ttl='1h')
def base_dataset():
    # load disaggregated data
    base = pd.read_csv("sources/df_teams_disagg.csv")

    # preprocess and best params based on silhouette
    X, df_clust_data = preprocess(base = base)
    sil_eval, clust_eval, output = kmeans_silhouette_score_eval(X)

    return X, df_clust_data, sil_eval, clust_eval, output

#----------------------------------------------------------------------------------

# Results and Metrics Visualizations

# kmeans contour data
def contour_data(X, depth : list, v_margin : float|int = .35, h_margin : float|int = .35, mesh_size: float= .1) -> list[list]:
    """
    Function
    -
    Configures range values to build plotly contour traces from KMeans input X for x and y
    axes and scores or resulting cluster labels for z (depth).

    Parameters
    -
    - X: training features applied in KMeans. Is recommended to have as first and second features
        the considered most important to plot
    - depth: KMeans output, generaly will be the labels or samples output
    - margin: (default .35) reescale the plot for use as add_traces
    - mesh_size: (default .1) detail in contour gradient defined from xrange. yrange and zrange are
        defined from xrange shape.
    
    Output
    -
    Three arrays containing x, y and z values for plotly contour trace
    """
    # score feature as x, participation feature as y 
    x_min, x_max = X[:,0].min() - h_margin, X[:,0].max() + h_margin
    y_min, y_max = X[:,1].min() - v_margin, X[:,1].max() + v_margin
    z_min, z_max = depth.min(), depth.max()

    xrange = np.arange(x_min, x_max, mesh_size)

    y_mesh_size = (y_max-y_min)/xrange.shape[0]
    yrange = np.arange(y_min, y_max, y_mesh_size)

    z_mesh_size = ((z_max-z_min)/xrange.shape[0])
    zrange = np.arange(z_min, z_max, z_mesh_size)

    return xrange, yrange, zrange

# contour trace for make_subplots
def score_contour_trace(name: str, opacity: float, xrange: list[float], yrange: list[float],
                        zrange: list[float]) -> go.Contour:
    """
    Function
    -
    Generates a plotly contour trace to add with add_traces or bluid subplots. Ideal for
    visualizing KMeans clustering results.

    Parameters
    -
    - name: trace name
    - opacity: trace opacity, between 0 and 1
    - x: array or list of float values with the first (or main first) feature
    - y: array or list of float values with the second (or main second) feature, must have
        the same length as the first feature
    - z: array or list of float values with KMeans output, wich can be scores or labels
        range, and must have the same length as the first and second features
    """

    colorscale = pio.templates[pio.templates.default]['layout']['colorscale']['sequential']

    contour_trace = go.Contour(
            x = xrange, y = yrange, z = zrange,
            showscale=False, opacity=opacity, hoverinfo='skip',
            name=name, colorscale = colorscale, contours_coloring = 'lines', line_width = 5)

    return contour_trace

# kmean scatter figure
def kmean_scatter(data : pd.DataFrame, category : list, sub_category : list, x : str, y : str, sub_cat_col : str, legendgroup: str,  size : str, sizescale : float,
                  customdata : str, legend_title :str):
    """
    Function
    -
    Creates a scatter figure, iterating through kmeans results and base data

    Parameters
    -
    - data: main data, must have a labels_desc column related with category entry values
    - category: list main categorical group unique values, must be values contained in 'labels_desc' column
    - sub_category: list with unique values, must be related with sub_cat_col entry
    - x: column for x axis values
    - y: column for y axis values
    - sub_cat_col: column used to group iterarions and to filter sub category data
    - legendgroup: groups traces' legends
    - size: column with float values to give size to markers
    - sizescale: marker size scalar
    - customdata: column used to display in hoverdata
    - legend_title: descriptive name of overal legend
    """
    color = list(pio.templates[pio.templates.default]['layout']['colorway'])
    symbols = list(SymbolValidator().values[2::12])

    while len(category) > len(color) or len(sub_category) > len(color):
        color.extend(color)
    
    while len(category) > len(symbols) or len(sub_category) > len(symbols):
        symbols.extend(symbols)

    scatter_fig = go.Figure()

    for sc_i in range(len(sub_category)):
        for c_i in range(len(category)):
            data_filtered = data[data['labels_desc']== category[c_i]][data[sub_cat_col]== sub_category[sc_i]]
            scatter_fig.add_trace(go.Scatter(
                x = data_filtered[x],
                y = data_filtered[y],
                name = f"{category[c_i]} - {sub_category[sc_i]}",
                legendgroup = f"{c_i}{legendgroup}",
                mode = 'markers',
                marker_color = color[sc_i],
                marker_opacity = .5,
                marker_line_width = 1.5,
                marker_line_color = color[c_i],
                marker_size = data_filtered[size]*sizescale,
                marker_sizemode = 'diameter',
                marker_symbol = symbols[sc_i],
                customdata = data_filtered[customdata],
                hovertemplate = f"<i>{customdata}: </i>" + "%{customdata}<br>" +
                                f"<b>{x}</b> "+"%{x} points<br>" +
                                f"<b>{y}</b> "+"%{y:2.2%}" +
                                "<extra></extra>"
            ))

    scatter_fig.update_layout(legend_title = legend_title,
                              legend = dict(orientation = 'v',
                                            yanchor = 'top', yref='paper', y=0.9,
                                            xanchor = 'right', xref='container', x=0.9,
                                            #groupclick ="toggleitem"
                                            ),
                              width = 1800, height = 600, margin = dict(t=0,b=30,l=0,r=0))

    return scatter_fig

# Elbow plot
def elbow_method_plot(n_clusters : list[int], inertias : list[float], umbral : int, t : int = 50,b : int = 30,l : int = 0,r : int = 0, show_title: bool = False, theme = 'plotly_white'):

    color = list(pio.templates[pio.templates.default]['layout']['colorway'])

    n_clusters_a, n_clusters_b = n_clusters[:umbral-1], n_clusters[umbral-1:]
    inertias_a, inertias_b = inertias[:umbral-1], inertias[umbral-1:]

    elb_fig = go.Figure()
    elb_fig.add_trace(go.Scatter(
        x = n_clusters_a,
        y = inertias_a,
        mode = "lines+markers",
        marker_size = 10,
        marker_sizemode = 'diameter',
        marker_color = color[-1],
        marker_symbol = 'star',
        line_color = color[-1],
        line_width = 1,
        showlegend= False,
        hovertemplate= "<extra>%{x} clusters</extra>%{y}"
    ))
    elb_fig.add_trace(go.Scatter(
        x = n_clusters_b,
        y = inertias_b,
        mode = "lines",
        line_color = color[0],
        line_width = .5,
        showlegend= False,
        hovertemplate= "<extra>%{x} clusters</extra>%{y}"
    ))

    elb_fig.add_vline(x= umbral,
                    annotation_text = f"Clusters <br>based on silhouette: {umbral}",
                    annotation_align = 'left',
                    annotation_position = 'top right', opacity = .5)

    elb_fig.update_yaxes(showticklabels = True, showgrid = False)
    elb_fig.update_yaxes(showticklabels = False, showgrid = False)

    if show_title == True:
        title = f"Elbow Method"
    else:
        title = " "
    elb_fig.update_xaxes(showticklabels = True, showgrid=False)
    elb_fig.update_yaxes(showticklabels=False, showgrid=False, showspikes=False)
    elb_fig.update_layout(hovermode = 'x',
                        template = f'{theme}+{pio.templates.default}',
                        margin = dict(t=t,b=b,l=l,r=r),
                        width = 900, height = 300,
                        title= title)
    return elb_fig

# silhouette interactive figure
def silhouette_figure(data : pd.DataFrame, score : float, clusters : int, t : int = 50,b : int = 30,l : int = 0,r : int = 0, show_title: bool = False, theme = 'plotly_white'):
    """
    Function
    -
    Shows silhouette analysis of a kmeans clustering result.

    Parameters
    -
    - data: dataframe containing preprocessed and kmeans processed data in columns named ['labels, 'samples'], ideally from scikit-learn predict and silhouette samples
    - score: best average silhouette score obtained
    - clusters: number of clusters that gave as result the best average silhouette score
    - t, b, l, r: plot margins (50, 30, 0, 0 by default)
    - theme: plotly theme to combine with default custom theme
    """
    
    sil_fig = go.Figure()
    y_lower = 0

    for i in range(len(data['labels'].unique())):
        cluster_size_i = data\
            [data['labels']==data['labels'].unique()[i]]\
            ['samples'].to_numpy().shape[0]
        
        y_upper = y_lower + cluster_size_i

        sil_fig.add_trace(go.Scatter(
            x = data[data['labels']==data['labels'].unique()[i]]\
                .sort_values('samples')['samples'],
            y = np.arange(y_lower, y_upper),
            mode = 'lines',
            line_width=.5,
            fill = 'tozerox',
            showlegend=False,
            hovertemplate = f"<extra>cluster {i}</extra>"+"%{y}"
        ))

        y_lower = y_upper

    sil_fig.add_vline(x= score,
                    annotation_text = f"Avg. <br>silhouette score:<br> {score:.4f}",
                    annotation_align = 'right',
                    annotation_position = 'top left')

    if show_title == True:
        title = f"Silhouette analysis with {clusters} clusters"
    else:
        title = " "
    sil_fig.update_xaxes(showticklabels = True, showgrid=False)
    sil_fig.update_yaxes(showticklabels=False, showgrid=False, showspikes=False)
    sil_fig.update_layout(hovermode = 'x',
                        template = f'{theme}+{pio.templates.default}',
                        margin = dict(t=t,b=b,l=l,r=r),
                        width = 900, height = 300,
                        title= title)

    return sil_fig

# cluster composition barplot
def cluster_composition(data : pd.DataFrame, cluster_col : str, group_col : str, color_order : list = None,
                        t : int = 50,b : int = 30,l : int = 0,r : int = 0,
                        show_title: bool = False, theme = 'plotly_white'):
    """
    Function
    -
    Shows the composition of all clusters from kmeans output.
    """

    color = list(pio.templates[pio.templates.default]['layout']['colorway'])
    group_col_t = data[group_col].unique()
    cluster_col_t = data[cluster_col].sort_values(ascending=True).unique()
    
    # color groups
    if color_order == None:
        color_map = {k:v for k,v in zip(group_col_t, color)}
    else:
        color_map = {k:v for k,v in zip(color_order, color)}

    while len(color) < len(cluster_col_t): # prevent indexing error
        color.extend(color)
    
    comp_bar = go.Figure()

    for a in range(len(group_col_t)):
        for b in range(len(cluster_col_t)):
            aux_filter_data = data[data[cluster_col] == cluster_col_t[b]][data[group_col] == group_col_t[a]]

            comp_bar.add_trace(go.Bar(
                x = [cluster_col_t[b]],#aux_filter_data[cluster_col],
                y = [len(aux_filter_data[group_col])],
                #name = group_col_t[a]+'-'+cluster_col_t[b],
                marker_color = color_map[group_col_t[a]],
                marker_line_color = color[b], marker_line_width = 3,
                showlegend= False,
                customdata= [group_col_t[a]],
                hovertemplate= "<extra></extra>Cluster: %{x}<br>Team: %{customdata}<br>N players: %{y}"
            ))

    comp_bar.update_xaxes(showticklabels = True, showgrid=False)
    comp_bar.update_yaxes(showticklabels = False, showgrid=False)

    if show_title == True:
        title = f"Clusters composition"
    else:
        title = " "
    
    comp_bar.update_layout(barmode='stack',
                           template = f'{theme}+{pio.templates.default}',
                           margin = dict(t=t,b=b,l=l,r=r),
                           width = 900, height = 300,
                           title= title)

    return comp_bar