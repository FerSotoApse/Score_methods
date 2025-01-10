import numpy as np
import pandas as pd
import time, datetime
from random import randint, shuffle

# 1- Score data random generation 

#----- individual player
def player_score(player_id = randint(10000, 99999), date = datetime.date.today().isoformat(), events=['A','B']):
    """
    Creates a DataFrame with a single random player and scores for each event (game)

    **Parameters**
    player_id: player unique identifier
    date: date in YYYY-MM-DD (today by default)
    """
    player = pd.DataFrame(
        {
            'player_id'  : [f"{player_id}" for i in range(len(events))],
            'event_date' : [date for i in range(len(events))],
            'event_game' : events,
            'score'      : [randint(0,3) for i in range(len(events))]
        }
    )

    return player

#----- team
def team_players(player_id= [randint(10000,99999)], date = datetime.date.today().isoformat(), events=['A','B']):

    """
    Creates a team score data with a given list of players with random scores for each event.
    """
    
    # creates a dataframe with the first player on list (player_id)
    team = player_score(player_id[0], date, events)
    
    # if more players on list, it will concatenate this new players (from team_player[1])
    if len(player_id) > 1:
        for player in range(1, len(player_id)):
            team = pd.concat([team, # main dataframe
                              player_score(player_id[player], date, events)
                             ])
    # row reindex
    team.reset_index(drop = True, inplace = True)
    
    return team

#----- team with scores
def team_scores(player_id = [randint(10000,99999)], date = datetime.date.today().isoformat(), events=['A','B']):
    """
    Creates a team score data with a given list of players with random scores
    for each event, and asigns score description.
    """

    team = team_players(player_id, date, events)

    medal = []

    for s in team['score'].values:
        if s == 1:
            medal.append('bronze')
        elif s == 2:
            medal.append('silver')
        elif s == 3:
            medal.append('gold')
        else:
            medal.append('not played')

    team['medal'] = pd.Series(medal)
    
    return team

#def data_simulation(date, events_input, team_names_input, n_player_base, input_a, team_b, team_c, team_d):
    #----- random player ids
    player_ids = [i for i in range(10000,100000)]
    shuffle(player_ids)
    #----- define player lists
    team_a_players = player_ids[:input_a]
    team_b_players = player_ids[input_a:(input_a+team_b)]
    team_c_players = player_ids[(input_a+team_b):(input_a+team_b+team_c)]
    team_d_players = player_ids[(input_a+team_b+team_c):(input_a+team_b+team_c+team_d)]

    #----- build DataFrame
    df_team_b, df_team_c, df_team_d = None, None, None
    #---------- team A
    df_team_a = team_scores(player_id = team_a_players, date = date, events = events_input)
    df_team_a['team'] = pd.Series([team_names_input[0] for i in range(len(df_team_a))])
    # for accumulative sum method demonstration
    df_eventplayers = df_team_a.copy()

    # builds a total_players list for df (team a by default)
    total_players = [input_a for i in range(3)]
    # packs teams dfs for stats functions
    df_teams_list = [df_team_a]

    bool_list = []

    #---------- team B 
    if len(team_b_players) > 0:
        df_team_b = team_scores(player_id = team_b_players, date = date, events = events_input)
        df_team_b['team'] = pd.Series([team_names_input[1] for i in range(len(df_team_b))])
        df_eventplayers = pd.concat([df_eventplayers, df_team_b]).reset_index(drop=True)
        
        # appends team b players and team list
        total_players.extend([team_b for i in range(3)])
        df_teams_list.append(df_team_b)
        bool_list.append(True)
    else:
        bool_list.append(False)
        
    #---------- team C
    if len(team_c_players) > 0:
        df_team_c = team_scores(player_id = team_c_players, date = date, events = events_input)
        df_team_c['team'] = pd.Series([team_names_input[2] for i in range(len(df_team_c))])
        df_eventplayers = pd.concat([df_eventplayers, df_team_c]).reset_index(drop=True)

        # appends team c players
        total_players.extend([team_c for i in range(3)])
        df_teams_list.append(df_team_c)
        bool_list.append(True)
    else:
        bool_list.append(False)

    #---------- team D
    if len(team_d_players) > 0:
        df_team_d = team_scores(player_id = team_d_players, date = date, events = events_input)
        df_team_d['team'] = pd.Series([team_names_input[3] for i in range(len(df_team_d))])
        df_eventplayers = pd.concat([df_eventplayers, df_team_d]).reset_index(drop=True)

        # appends team d players
        total_players.extend([team_d for i in range(3)])
        df_teams_list.append(df_team_d)
        bool_list.append(True)
    else:
        bool_list.append(False)

    df_eventteams_scores = df_eventplayers.groupby(['event_date', 'event_game', 'team', 'medal']).sum('score').reset_index()

    return df_eventteams_scores, df_eventplayers, bool_list, total_players, df_teams_list, df_team_a, df_team_b, df_team_c, df_team_d

######### copied!!!

# 2- Data metrics

# a- player participation ratios
#----- ratio of players competing in a single or multiple events
def competitor_r(total_players, n_players):
    """
    Proportion of players who have participated in an event. Outputs float, can be multiplied by 100.
    total_players: player base
    n_plyers: players who did/didn't participate.
    """
    competitors_ratio = (total_players - n_players) / total_players

    return competitors_ratio

def general_participation(df_base, df_teams, n_team_players, checkbox):

    """
    General competitor ratios, or player ratios, by event and by team

    **Output**
    List of general events player participation (competitors ratios) and list of general teams participation
    (competitors ratios). Can access to individual values with indexing. Values can be multiplied by 100 for
    relative format.
    
    **Parameters**
    df_base: dataframe with main data
    df_teams: list of df with each team data
    n_player_base: all player users
    checkbox: list of checkboxes bool values
    """
    
    # from df_base
    events = list(df_base['event_game'].unique())
    base_players = len(df_base['player_id'].unique())
    first_df_team, *df_team = df_teams
    
    
    #-------------- general ratio
    event_comp_ratio = []
    
    for event in events:
        event_comp = len(df_base[df_base['score']==0][df_base['event_game']==event])
        event_comp_ratio.append(competitor_r(base_players, event_comp))
    
    #-------------- team ratios
    #--------------------- team A by default, the rest defined by checkboxes
    team_comp_ratio = [competitor_r(len(n_team_players[0]), len(first_df_team[first_df_team['score']==0]))]
    
        #--------------------- ADD: if not autogenerated dataframe (simulation), don't use checkboxes
    for cb, players, team in zip(checkbox, n_team_players[1:], df_team):
        if cb == True:
            team_cr = competitor_r(len(players), len(team[team['score']==0]))
            team_comp_ratio.append(team_cr)
        else:
            pass
    
    return event_comp_ratio, team_comp_ratio

def team_event_participation(df, n_players):

    """
    DataFrame with all competitor ratios by team per event

    **Parameters**
    df: dataframe of a single team (no general playerbase)
    n_players: number of players in the team
    """
    
    events = list(df['event_game'].unique())
    event_team_cr = [competitor_r(n_players, len(df[df['score']==0][df['event_game']==event])) for event in events]

    # builds ratio data to append to main team dataframe
    df_event_team_cr = pd.DataFrame({
        'player_ratio' : event_team_cr,
        'event_game'   : events,
        'team'         : [df.at[0,'team'] for i in range(len(events))]
    })
    
    return df_event_team_cr

# b- medal relative frequencies
#----- medal proportion, by team
def medal_r(team_players, n_gold, n_silver, n_bronze):
    """
    Proportion of medals won.
    Team_players: int
    medals (n_gold, n_silver, n_bronze): int
    """
    goldm = n_gold / team_players
    silvm = n_silver / team_players
    bronm = n_bronze / team_players

    return goldm, silvm, bronm

#----- medal proportion, by team and event
def event_medal_r(df_team, event):
    """
    Proportion of medals won, counting from a DataFrame an filtering by event
    """
    competitors = int((len(df_team))-len(df_team[df_team['score']==0][df_team['event_game']==event]))
    n_gold = len(df_team[df_team['score']==3][df_team['event_game']==event])
    n_silv = len(df_team[df_team['score']==2][df_team['event_game']==event])
    n_bron = len(df_team[df_team['score']==1][df_team['event_game']==event])

    gold, silver, bronze = medal_r(competitors, n_gold, n_silv, n_bron)
    
    return gold, silver, bronze

#----------- Direct use in Streamlit
#----- build auxiliar medal df to concatenate with main df 
def team_event_medals(df_team, main_df):
    """
    Builds df of medal relative frequence by team and event.
    
    Parameters
    df: team dataframe (not general)
    """
    # builds auxiliar df with medal relative count (from team A by default)
    medals = ['gold', 'silver', 'bronze']
    events = list(main_df['event_game'].unique())
    aux_data = list(event_medal_r(df_team, events[0])[:])

    # creates a list of events based on medal colors (winning positions)
    aux_events = [events[0] for e in range(len(medals))]
    
    aux_medals = medals.copy()
    #for i in range(len(events)):
        
    for i in range(1,len(events)):
        aux_events.extend([events[i] for e in range(len(medals))])
        aux_data.extend(list(event_medal_r(df_team, events[i])[:]))
        aux_medals.extend(medals)
    

    df_aux = pd.DataFrame({
        'event_game'     : aux_events,
        'team'           : [df_team['team'].unique()[0] for i in range(len(aux_events))],
        'medal'          : aux_medals,
        'medal_relative' : aux_data})

    del aux_data, aux_events, aux_medals
    
    return df_aux

# c- Winners
def event_winners(df,score_type = 'accumulative'):

    """
    Shows the winners sorted by total score > medal score > competitor ratio (or player ratio).

    **Parameters**
    score_type: choose 'performance' or 'accumulative' ('accumulative' by default)
    df: main DataFrame
    """

    if score_type == 'accumulative':
        score_cols = ['acc_w_score_total', 'acc_w_score']
    if score_type == 'performance':
        score_cols = ['performance_score_total', 'performance_score']

    # for iteration and indexing
    events = list(df['event_game'].unique())
    n_teams = len(df['team'].unique())

    # sort values to pick the best scores #[df['medal']!='bronze']
    observed_winners = df[df['event_game']==events[0]].copy()\
                        .sort_values(by = [score_cols[0], score_cols[1], 'player_ratio'],
                                     ascending = [False, False, False], ignore_index=True)\
                       [['event_game','team','medal',score_cols[0], score_cols[1],'player_ratio']]

    # mask with unique sorted teams (first ocurrence of each team)
    winners = observed_winners[observed_winners.duplicated('team')==False]

    # if there are more than a single event, concatenate results
    if len(events)>1:
        for e in range(1,len(events)):
            observed_winners = df[df['event_game']==events[e]].copy()\
                                    .sort_values(by = [score_cols[0], score_cols[1], 'player_ratio'],
                                                 ascending = False, ignore_index=True)\
                                   [['event_game','team', 'medal',score_cols[0], score_cols[1],'player_ratio']]
    
            winners = pd.concat([winners, observed_winners[observed_winners.duplicated('team')==False]])
    
    # clear memory
    del n_teams, observed_winners

    return winners

# 3 - Other data transformations
# Custom Sunburst data

def polar_data(df_disagg, df_agg, path, empty_leaf=None):

    """
    Data processing for polar charts, icicle and treemaps. Returns lists of ids, labels, parents and values,
    and customized hover template.

    **Parameters**
    df_disagg: DataFrame that has no None or null values, and has not been grouped data (almost raw from
        simulated generation)
    df_agg : DataFrame with transformed data from the pipeline
    path: list of column order for the subsequent chart. Start from base, inner or larger group to outmost,
        detailed data.
    empty_leaf: if some values don't reach the last detail level (or outmost ring), can set a str value
        that is not meant to be shown, leaving an empty space in the chart. This won't define ids, parents or
        labels for those values, keeping the same length for all output lists. Please note it allows for a
        single value (None by default).
    """

    # prep params
    levels = len(path)


    # 1 - Build etiquettes -----------------------------------------------

    # aux lists
    aux_id, aux_parent, aux_label, aux_value = [],[],[],[]

    # grouped df based on value counts, bypass bias from "score" and categorical columns
    df_gb = df_disagg.copy().value_counts(subset=path).reset_index()\
    .sort_values(path, ascending=True, ignore_index=True)

    ## CORRECCION 1
    df_gb.columns = ['event_game', 'team_played', 'medal', 'count']

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
        len_lv2 = len(aux_id)
            
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
        
        len_lv2 = len(aux_id)

    ## CORRECCION 2 EN len_lv1
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
        
    len_lv1 = len(aux_id)

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
        
    len_lv0 = len(aux_id)

    # 2 - Build Hovertemplate --------------------------------------------------

    # 2.a - Hover data
    # outer ring hover data
    custdata_lv2 = df_agg.copy().sort_values(by=['medal', 'team', 'event_game'], ignore_index=True)

    # mid ring hover data
    custdata_lv1 = df_agg[['event_game', 'team','acc_w_score_total', 'performance_score_total',
                                        'medal_frequence', 'player_ratio']]\
                                        .groupby(['event_game', 'team','player_ratio','acc_w_score_total',
                                                'performance_score_total'])\
                                        .sum(['medal_frequence'])\
                                        .reset_index()

    if df_disagg['team_played'].isin(['Not played']).sum() != 0:
        custdata_lv1 = pd.merge(right = custdata_lv1,
                                left = pd.DataFrame({'team' : aux_label[len_lv2 : len_lv1],
                                            'medal_frequence' : aux_value[len_lv2 : len_lv1]}),
                                on = ['team', 'medal_frequence'], how = 'outer'
                                ).sort_values(by=['team', 'event_game'], ignore_index=True).round(2).fillna('--')

    # base hover data
    custdata_lv0 = df_agg[['event_game','medal_frequence']].groupby(['event_game'])\
                                        .sum('medal_frequence').reset_index()
    
    # 2.b - Hover template
    
    hover_lv2 = [f"<b>{custdata_lv2['medal'].at[i].capitalize()} medal</b><br>"+
                f"<i>Medal count</i>: {custdata_lv2['medal_frequence'].at[i]}<br>"+
                f"<i>Medal rel. frequence</i>: {custdata_lv2['medal_relative'].at[i]}%<br>"+
                f"<br><b>Medal Score Methods</b><br>"+
                f"<i>Accumulative</i>: {custdata_lv2['acc_w_score'].at[i]}<br>"+
                f"<i>Performance</i>: {custdata_lv2['performance_score'].at[i]}<br>"+
                f"<extra><b>Team<br>{custdata_lv2['team'].at[i]}<br>medals</b></extra>" for i in range(len_lv2)]

    hover_lv1 = [f"<b>{custdata_lv1['team'].at[i].capitalize()}</b><br>"+
                f"<i>Player count</i>: {custdata_lv1['medal_frequence'].at[i]}<br>"+
                f"<i>Team participation</i>: {custdata_lv1['player_ratio'].at[i]}%<br>"+
                f"<br><b>Team Score Methods</b><br>"+
                f"<i>Accumulative</i>: {custdata_lv1['acc_w_score_total'].at[i]}<br>"+
                f"<i>Performance</i>: {custdata_lv1['performance_score_total'].at[i]}<br>"+
                f"<extra><b>In event<br>{aux_parent[len_lv2 : len_lv1][i]}</b></extra>" for i in range(len_lv1 - len_lv2)]
    hover_lv0 = [f"<b>Event {custdata_lv0['event_game'].at[i].capitalize()}</b><br>"+
                f"<i>Player count</i>: {custdata_lv0['medal_frequence'].at[i]}<br>"+
                f"<i>Event participation</i>: func_placeholder %" for i in range(len_lv0 - len_lv1)]

    # func_placeholder: round(event_compr[i]*100,2)

    lv_hovertemplate = hover_lv2 + hover_lv1 + hover_lv0

    # clear catche
    del df_gb, lv_iter, len_lv0, len_lv1, len_lv2, levels, custdata_lv0, custdata_lv1, custdata_lv2, hover_lv0, hover_lv1, hover_lv2

    return aux_id, aux_label, aux_parent, aux_value, lv_hovertemplate