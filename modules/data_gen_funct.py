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

def general_participation(df, n_player_base = n_player_base,
                          cb_b = cb_b, cb_c = cb_c, cb_d = cb_d):
    
    """
    General competitor ratios, or player ratios, by event and by team. Works only with Streamlit checkboxes.

    **Output**
    List of general events player participation (competitors ratios) and list of general teams participation
    (competitors ratios). Can access to individual values with indexing. Values can be multiplied by 100 for
    relative format.
    
    **Parameters**
    df: dataframe with main data
    n_player_base: all player users
    *kwards: other data related to teams and checkboxes
    """
    
    events = list(df['event_game'].unique())
    event_compr = []

    # users, teams and event participation ratios (we use desagregated dfs)
    #-------------- general ratio
    for event in events:
        event_comp = len(df[df['score']==0][df['event_game']==event])
        event_compr.append(competitor_r(n_player_base, event_comp))
        # can apply round(event_compr*100,2) for value in %
    
    #-------------- team ratios
    #--------------------- team A by default, the rest defined by checkboxes
    team_cr = [competitor_r(len(team_a_players), len(df_team_a[df_team_a['score']==0]))]
    
    if cb_b == True:
        team_b_cr = competitor_r(len(team_b_players), len(df_team_b[df_team_b['score']==0]))
        team_cr.append(team_b_cr)
    if cb_c == True:
        team_c_cr = competitor_r(len(team_c_players), len(df_team_c[df_team_c['score']==0]))
        team_cr.append(team_c_cr)
    if cb_d == True:
        team_d_cr = competitor_r(len(team_d_players), len(df_team_d[df_team_d['score']==0]))
        team_cr.append(team_d_cr)

    return event_compr, team_cr

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
def event_medal_r(team_players_df, event):
    """
    Proportion of medals won, counting from a DataFrame an filtering by event
    """
    competitors = int((len(team_players_df)/len(events_input))-len(team_players_df[team_players_df['score']==0][team_players_df['event_game']==event]))
    n_gold = len(team_players_df[team_players_df['score']==3][team_players_df['event_game']==event])
    n_silv = len(team_players_df[team_players_df['score']==2][team_players_df['event_game']==event])
    n_bron = len(team_players_df[team_players_df['score']==1][team_players_df['event_game']==event])

    gold, silver, bronze = medal_r(competitors, n_gold, n_silv, n_bron)
    
    return gold, silver, bronze

#----------- Direct use in Streamlit
#----- build auxiliar medal df to concatenate with main df 
def team_event_medals(df_team, main_df = df_eventteams_scores):
    """
    Builds df of medal relative frequence by team and event.
    
    Parameters
    df: team dataframe (not general)
    """
    # builds auxiliar df with medal relative count (from team A by default)
    
    events = list(main_df['event_game'].unique())
    aux_data = list(event_medal_r(df_team, events[0])[:])

    # creates a list of events based on medal colors (winning positions)
    aux_events = [events[0] for e in range(len(main_df['medal'].unique()))]
    medals = ['gold', 'silver', 'bronze']
    aux_medals = ['gold', 'silver', 'bronze']
    #for i in range(len(events)):
        
    for i in range(1,len(events)):
        aux_events.extend([events[i] for e in range(len(main_df['medal'].unique()))])
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
def event_winners(score_type = 'accumulative', df = df_eventteams_scores):

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