import streamlit as st
import requests

import numpy as np
import pandas as pd
import time, datetime
from random import randint, shuffle

pd.options.mode.copy_on_write = True

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import modules.my_themes

pio.templates.default = 'aer_bg_alpha0_tstmp'

from modules.app_sim_sidebar import side_bar_params, metrics_bulk
from modules.pipeline import *
from modules.graph_funct import *
from modules.data_metrics_funct import *
from modules.kmeans_funct import *


# Streamlit app

st.set_page_config(page_title = 'Score methods',
                   page_icon = None,
                   layout = 'wide',
                   initial_sidebar_state = "expanded",
                   menu_items={'Report a bug': 'mailto:fefy.sotoapse@outlook.com',
                               'About' : '''App developed by Fernanda Soto (2024). All
                                         simulated or input data will last for a short time
                                         and will reset when a new session starts.'''})

# Main page intro
if __name__ == "__main__":
    st.title("Scoring methods study")
#    st.text("resume en pocas palabras el estudio")
    st.divider()

######### end intro

##### Sidebar: user inputs and random generated data

    # for pipeline
    df_first_team = pd.DataFrame()
    df_teams = [pd.DataFrame()]
    bool_list = []
    df_teams_disagg = pd.DataFrame()
    df_teams_agg = pd.DataFrame()

    # sidebar sim data outputs
    simulated_data, n_player_base = side_bar_params()

######### end sidebar

##### Pipeline: takes aggregated data to calculate metrics

    if type(simulated_data) == dict:
        #----- sim data, separated
        df_first_team   = simulated_data['teams_raw'][0]
        df_teams        = simulated_data['teams_raw'][1]
        bool_list       = simulated_data['bool_list']
        df_teams_disagg = simulated_data['all_teams_disagg']
        df_teams_agg    = simulated_data['all_teams_agg']

        #----- transformed agg data with pipeline
        df_teams_agg_metrics = pipeline(df_agg_data         = df_teams_agg,
                                        df_disagg_data      = df_teams_disagg,
                                        df_first_team_data  = df_first_team,
                                        df_teams_l_data     = df_teams,
                                        b_l                 = bool_list)
    
        # save cache data
        df_first_team.to_csv('sources/df_first_team.csv', index=False)
        df_teams_disagg.to_csv('sources/df_teams_disagg.csv', index=False)
        df_teams_agg.to_csv('sources/df_teams_agg.csv', index=False)
        df_teams_agg_metrics.to_csv('sources/df_teams_agg_metrics.csv', index=False)

######### end pipeline

######### EDA and ML tabs        
        tab_data, tab_ml = st.tabs(['Sim data EDA', 'User segmentation'])

##### General Stats: segmented control selector and  st metrics

        with tab_data:

    ####### Polar overview
            # sunburst data params
            sb_data, lengths = polar_data_path(df_teams_disagg, 'event_game', 'team', 'medal', empty_leaf='not played')

            customdata_list = polar_customdata(
                data         = [df_teams_agg_metrics[df_teams_agg_metrics['medal']!='not played'],
                                df_teams_agg_metrics[df_teams_agg_metrics['medal']!='not played'],
                                df_teams_agg_metrics],
                customdata_l = ['medal', 'medal_abs_frequence', 'medal_rel_frequence', 'acc_w_score', 'perform_score', 'team'],
                customdata_b = ['team', 'medal_abs_frequence', 'team_participation_ratio', 'acc_w_score_total', 'perform_score_total', 'event_game'],
                customdata_r = ['event_game','medal_abs_frequence'],
                n_rows       = lengths,
                col_orders   = [['event_game', 'team', 'medal'],
                                ['team', 'event_game', 'team_participation_ratio','acc_w_score_total', 'perform_score_total', 'medal_abs_frequence'],
                                ['event_game','medal_abs_frequence']])

            *polardata_col, = st.columns(2)
            # sunburst: overview
            sunburst_general = go.Figure(go.Sunburst(
                ids          = sb_data['ids'],
                labels       = sb_data['labels'],
                parents      = sb_data['parents'],
                values       = sb_data['values'],
                branchvalues = 'total',
                customdata   = customdata_list,
                hovertemplate = "%{customdata}" ))

            sunburst_general.update_layout(
                width = 900, height = 400, margin = dict(t=0, b=0, l=0, r=0))

            polardata_col[0].plotly_chart(sunburst_general)
            #---------------------------------------

            # barpolar plot and selector
            barpolar_cont = polardata_col[1].container(border=False, height= 300)
            # the selector will appear under the barpolar
            bp_select = polardata_col[1].select_slider('Barplot events',
                                                       list(df_teams_disagg['event_game'].unique()),
                                                       label_visibility= 'collapsed')
            # the container is on the slider, so the plot will appear on the slider
            barpolar_players = cust_barpolar(df_data = df_teams_disagg[df_teams_disagg['event_game']==bp_select],
                          r             = 'score',
                          theta         = 'player_id',
                          group_data    = 'team',
                          color_order   = tuple(df_teams_disagg['team'].unique()),
                          sortby        = ['team', 'score'],
                          title         = None,
                          customdata    = ['event_date', 'medal'],
                          hovertemplate = "<extra></extra>"+
                                          "<b>Player ID</b> %{theta}<br>"+
                                          "<i>Date</i> %{customdata[0]}<br>"+
                                          "<i>Position</i> %{customdata[1]} medal<br>"
                                          "<b>Score</b> %{r}",
                          add_name = '', h = 300, w = 900, hole = .25)

            barpolar_cont.plotly_chart(barpolar_players)

    ######## End polar overview

    ############ Metrics
            # all selector metrics
            metrics_describe = df_teams_agg_metrics.describe()

            # specific selector metrics
            metrics_acc_win     = event_winners(df_agg_data= df_teams_agg_metrics, score_method='accumulative')
            metrics_perf_win    = event_winners(df_agg_data= df_teams_agg_metrics, score_method='performance')
            metrics_part_sort   = df_teams_agg_metrics.sort_values(by=['team_participation_ratio'], ascending=False)
            aux_metrics_part    = metrics_part_sort[['team','team_participation_ratio']]\
                                    .groupby(['team']).mean('team_participation_ratio')\
                                    .reset_index().sort_values('team_participation_ratio',ascending=False)

            # selector
            metric_options = [':material/stat_0:','Accumulative Score', 'Performance Score', 'Event participation', 'Team participation']                
            metric_select = st.segmented_control(label= 'General metrics',
                                                 options= metric_options,
                                                 default= metric_options[0],
                                                 label_visibility= 'collapsed')

            *metric_col, = st.columns(4, gap = 'small', vertical_alignment='center')

            match metric_select:
            # Particular Highlights (only selected in selectbox)
                case 'Accumulative Score':
                    m_selectbox = metric_col[0].selectbox('Events',
                                                        list(df_teams_disagg['event_game'].unique()),
                                                        label_visibility = 'collapsed')
                    metrics_bulk(columns        = metric_col,
                                labels          = ['Highest score: ', 'Lowest score: ', 'Average event score'],
                                data            = metrics_acc_win,
                                col_filter      = 'event_game', select_filter = m_selectbox,
                                col_value       = 'acc_w_score_total', col_delta_value = 'acc_w_score_total',
                                delta_compare   = metrics_describe.at['mean', 'acc_w_score_total'],
                                label_annot     = 'team', delta_annot = ' (avg score)')
                    
                    c_d, c_x, c_y, c_color = df_teams_agg_metrics[['team', 'acc_w_score_total', 'event_game']].drop_duplicates(ignore_index=True),\
                                            'team', 'acc_w_score_total', 'event_game'

                case 'Performance Score':
                    m_selectbox = metric_col[0].selectbox('Events',
                                                        list(df_teams_disagg['event_game'].unique()),
                                                        label_visibility = 'collapsed')
                    metrics_bulk(columns        = metric_col,
                                labels          = ['Highest score: ', 'Lowest score: ', 'Average event score'],
                                data            = metrics_perf_win,
                                col_filter      = 'event_game', select_filter = m_selectbox,
                                col_value       = 'perform_score_total', col_delta_value = 'perform_score_total',
                                delta_compare   = metrics_describe.at['mean', 'perform_score_total'],
                                label_annot     = 'team', delta_annot = ' (avg score)')

                    c_d, c_x, c_y, c_color = df_teams_agg_metrics[['team', 'perform_score_total', 'event_game']].drop_duplicates(ignore_index=True),\
                                             'team', 'perform_score_total', 'event_game'

                case 'Event participation':
                    m_selectbox = metric_col[0].selectbox('Teams',
                                                          list(df_teams_disagg['team'].unique()),
                                                          label_visibility = 'collapsed')
                    metrics_bulk(columns        = metric_col,
                                labels          = ["Team`s fav event", "Least fav event", "Team avg. participation"],
                                data            = metrics_part_sort,
                                col_filter      = 'team', select_filter = m_selectbox,
                                col_value       = 'event_game', col_delta_value = 'team_participation_ratio',
                                delta_compare   = metrics_describe.at['mean', 'team_participation_ratio'],
                                delta_annot     = ['%', '%', '% (avg. part.)'], value_annot = '%')

                    c_d, c_x, c_y, c_color = df_teams_agg_metrics[['event_game', 'team_participation_ratio', 'team']].drop_duplicates(ignore_index=True),\
                                             'event_game', 'team_participation_ratio', 'team'

                case 'Team participation':
                    m_selectbox = metric_col[0].selectbox('Events',
                                                          list(df_teams_disagg['event_game'].unique()),
                                                          label_visibility = 'collapsed')
                    metrics_bulk(columns        = metric_col,
                                labels          = ['Most active team', 'Least active team', 'Event avg. participation'],
                                data            = metrics_part_sort,
                                col_filter      = 'event_game', select_filter = m_selectbox,
                                col_value       = 'team', col_delta_value = 'team_participation_ratio',
                                delta_compare   = metrics_describe.at['mean', 'team_participation_ratio'],
                                delta_annot     = ['% (event avg)', '% (event avg)', '% (avg. part.)'],
                                value_annot     = '%')

                    c_d, c_x, c_y, c_color = df_teams_agg_metrics[['team', 'team_participation_ratio', 'event_game']].drop_duplicates(ignore_index=True),\
                                             'team', 'team_participation_ratio', 'event_game'

            # Overall highlights (selected or not from selecbox)
                case _:
                    # best acc total
                    aux_sort = df_teams_agg_metrics.sort_values(by=['acc_w_score_total'], ascending=False)
                    metric_col[0].metric(f"Best Acc: {aux_sort['team'].values[0]} ({aux_sort['event_game'].values[0]})",
                                         aux_sort['acc_w_score_total'].values[0],
                                         round(aux_sort['acc_w_score_total'].values[0] - metrics_describe.at['mean', 'acc_w_score_total'], 2))
                    # best perf total
                    aux_sort = df_teams_agg_metrics.sort_values(by=['perform_score_total'], ascending=False)
                    metric_col[1].metric(f"Best perf: {aux_sort['team'].values[0]} ({aux_sort['event_game'].values[0]})",
                                         round(aux_sort['perform_score_total'].values[0], 2),
                                         round(aux_sort['perform_score_total'].values[0] - metrics_describe.at['mean', 'perform_score_total'], 2))
                    # fav event based on team participation ratio
                    metric_col[2].metric(f"Favourite event",
                                         metrics_part_sort['event_game'].values[0],
                                         f"""{round(metrics_part_sort['team_participation_ratio'].values[0] - metrics_describe.at['mean', 'team_participation_ratio'], 2)}%
                                             ({metrics_part_sort['team'].values[0]})""")
                    # most active team based on mean team participation ratio
                    metric_col[3].metric(f"Most active team",
                                         aux_metrics_part['team'].values[0],
                                         f"""{round(aux_metrics_part['team_participation_ratio'].values[0] - metrics_describe.at['mean', 'team_participation_ratio'],2)}%""")

                    aux_data = df_teams_agg_metrics[['team','event_game', 'acc_w_score_total', 'perform_score_total', 'team_participation_ratio']].copy()
                    aux_data.drop_duplicates(inplace = True, ignore_index=True)
                    

            # visualize according to selected option (NECESITA ACTUALIZAR)

            if metric_select == ':material/stat_0:':
                st.plotly_chart(bar_highlights(data = aux_data,
                                               x                = 'team',
                                               y                = ['acc_w_score_total', 'perform_score_total', 'team_participation_ratio'],
                                               subplot_titles   = ['Accumulated Score', 'Performance Score', 'Teams Participacion'],
                                               col_group        = 'event_game',
                                               legend_group     = aux_data['event_game'].unique()))
            else:
                st.plotly_chart(px.bar(c_d,
                                       x       = c_x,
                                       y       = c_y,
                                       color   = c_color,
                                       barmode = 'group',
                                       height  = 300)\
                                       .update_layout(legend_orientation='h', legend_y = 0, legend_x = 0))

    ############ End metrics

    ######## Score Methods barplots
            *select_col, = st.columns([2,1])
            score_select = select_col[0].segmented_control(label            = 'Medals per event',
                                                           options          = ['Accumulative medal scores', 'Performance medal scores'],
                                                           default          = 'Accumulative medal scores',
                                                           label_visibility = 'collapsed')
            score_event = select_col[1].selectbox('Score per Events',
                                                  list(df_teams_disagg['event_game'].unique()),
                                                  label_visibility = 'collapsed')
            #----- bar plots
            *plot_col, = st.columns(len(df_teams_disagg['team'].unique()))
            match score_select:
                case 'Performance medal scores':
                    for i in range(len(plot_col)):
                        y_data          = "perform_score"
                        y_title         = 'Scores by Performance Method'
                        hline_values    = 'perform_score_total'
                case _:
                    for i in range(len(plot_col)):
                        y_data          = "acc_w_score"
                        y_title         = 'Scores by Accumulative Method'
                        hline_values    = 'acc_w_score_total'

            test_bar=cust_bar_hline(df_data     = df_teams_agg_metrics[df_teams_agg_metrics['medal']!='not played'],
                            x_data              = 'medal',
                            y_data              = y_data,
                            facet_data_col      = 'team',
                            selector            = 'event_game',
                            selector_filter     = score_event, 
                            y_title             = y_title,
                            show_hline          = True,
                            hline_values        = hline_values,
                            hline_annot_iter    = df_teams_agg_metrics[df_teams_agg_metrics['medal']!='not played']['team'].unique(),
                            hline_annot         = f' total score',
                            category_order      = ['bronze', 'silver', 'gold'],
                            barcornerradius     = "0%", w = 1800, h = 400,
                            customdata_cols     = ['medal_rel_frequence','medal','team_participation_ratio', 'acc_w_score'],
                            hovertemplate       = '''<br><i>Proportion %{customdata[0]} medals</i>: %{customdata[1]}
                                                     <br>Team event participation %{customdata[2]}%
                                                     <br><i>Medal score</i>: %{customdata[3]} points<extra></extra>''')

            st.plotly_chart(test_bar)

    ########### End barplots

######## ML: unsupervised clustering model - KMeans
        with tab_ml:
        ##### page composition
            # 1st: scatter-contour
            clust_cont = st.container(border=False, height=600)
            # 2nd: metrics-n_cluster, cluster composition, silhouette, elbow columns
            silmet_col, comp_col, sil_col, elbow_col = st.columns(4, gap='small', vertical_alignment='top')

        ##### Execution order
            X, df_clust_data, sil_eval, clust_eval, output = base_dataset()

            # params and best score metrics (up to max stable param defined by best silhouette)
            with silmet_col:
                # n clusters selector for custom clustering and score
                t_clusters = st.slider('Choose number of clusters', 2, clust_eval, value = clust_eval)
                select_idx = t_clusters-2

                st.write(f"Avg. Silhouette Score = {(output['silhouette'][select_idx]):6f}")
                st.write(f"Centroids` Inertia = {(output['inertias'][select_idx]):6f}")
                # best score
                st.divider()
                st.markdown("**Kmeans unsupervised evaluation**")
                st.write(f"Best Avg. Silhouette Score = {sil_eval:.6f}")
                st.write(f"Centroids` Inertia = {(output['inertias'][clust_eval-2]):.6f}")
                st.write(f"Number of clusters = {clust_eval}")
                
                # appends outputs to cluster data df for visualizations
                df_clust_data[['samples', 'labels']] = pd.DataFrame({
                    'samples'   : output['samples'][select_idx],
                    'labels'    : output['labels'][select_idx]})
                df_clust_data['labels_desc'] = pd.Series([f'cluster {l}'for l in df_clust_data['labels']])

#            # only preview ##########################
#            aux_cont = st.container(border =True, height=400)
#            aux_cont.dataframe(df_clust_data)
#            aux_cont.write(output)
#            #########################################

            with comp_col:
                st.plotly_chart(cluster_composition(
                    data=df_clust_data,
                    cluster_col='labels_desc',
                    group_col='team',
                    color_order = list(df_teams_disagg['team'].unique()),
                    show_title = True))

        ##### Build clustering visualization
            # cluster scatter-contour figure
            with clust_cont:
                #st.dataframe(df_clust_data[['player_id','samples']])
                if len(set(df_clust_data['samples'])) == 1:# or len(set(t_samples)) == 1:
                    st.write("""
                             <h2>Looks like the model results are too <i>(im)perfect</i>!</h2>
                             <p>This can happen when all clusters are almost or perfectly overlaped (inertia = 0) or the silhouette scores 1.
                             The nature of this data can give unexpected results, you can still try with other numbers of clusters.</p>
                             <p>Look at the Elbow Method plot down below! It has some usefull clues of how many clusters may work better with the model.
                             It's recommended to choose a number of clusters that are easy to understand in the plots.</p>
                             """)
                    st.plotly_chart(elbow_method_plot(n_clusters = [i for i in range(2, output['clusters'][-1])],
                                                    inertias = output['inertias'],
                                                    umbral = clust_eval,
                                                    show_title=True))
                else:
                    *ranges, = contour_data(X, depth = df_clust_data['samples'], mesh_size = .5)
                    clust_fig = kmean_scatter(data = df_clust_data,
                        category        = df_clust_data['labels_desc'].sort_values().unique(),
                        sub_category    = df_teams_disagg['team'].unique(),
                        x               = 'score',
                        y               = 'player_participation',
                        sub_cat_col     = 'team',
                        legendgroup     = 'cluster',
                        size            = 'player_participation',
                        sizescale       =  25,
                        customdata      = 'player_id',
                        legend_title    = "Clusters, teams")

                    clust_fig.add_trace(score_contour_trace('clust_scores', .5,
                        xrange = ranges[0],
                        yrange = ranges[1],
                        zrange = ranges[2]))

                    clust_fig.update_xaxes(showgrid=False, showticklabels=False)
                    clust_fig.update_yaxes(showgrid=False, showticklabels=False)
                    clust_fig.update_layout(showlegend = True, legend_orientation = 'h')

                    st.plotly_chart(clust_fig)

            with sil_col:
                st.plotly_chart(silhouette_figure(data = df_clust_data,
                                                  score = output['silhouette'][select_idx],
                                                  clusters = t_clusters,
                                                  show_title=True))

            with elbow_col:
                if len(set(df_clust_data['samples'])) != 1:
                    st.plotly_chart(elbow_method_plot(n_clusters = [i for i in range(2, output['clusters'][-1])],
                                                    inertias = output['inertias'],
                                                    umbral = clust_eval,
                                                    show_title=True))
                

############ End clustering model
    
    else:
        *intro_cols, = st.columns([1,2])
        with intro_cols[0]:
            st.html("""
                    <h2>Instructions</h2>
                    <h3>Sim Data</h3>
                    <p>In the sidebar, select the parameters:<br>
                    1- Select a date<br>
                    2- Choose all the simultaneous events you want to visualize<br>
                    3- Select up to 4 'teams'<br>
                    4- Define total of users and 'teams' sizes<br>
                    5- Click on 'Ready to go!' buttom<br>
                    6- Start exploring all interactive plots!</p>
                    <h3>Segmentation tab</h3>
                    <p>In the Segmentation tab you can additionally define how many clusters will be given from <b>KMeans usupervised clustering</b>.
                    If the amout of clusters aren't easy to interpret, you can always check the <b>Elbow Method plot</b> in the bottom right corner,
                    then use the <b>cluster slide selector</b> to redefine how many clusters you need to understand better the user segments.</p>
                    <p>In this model, the user segmentation is based on each <b>user total absolute score</b> and <b>mean relative participation</b>.
                    The main <i>clustering scatter plot</i> shows how users are segmented individually, the <i>cluster bar plot</i> shows the composition
                    of each cluster, and the <i>silhouette plot</i> shows the 'quality' of each cluster.</p>
                    """)
        with intro_cols[1]:
            st.html("""
                    <h2>About this project</h2><br>
                    <p>...</p>
                    """)

else:
    pass