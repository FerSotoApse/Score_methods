import streamlit as st

import numpy as np
import pandas as pd
import datetime
from random import randint, shuffle


# 1 - Data simulation functions
# player lists
def players_ids_list(n_players) -> list[list[int]]:

    """
    Create a list of lists containing each team's players.
    """
    # random player ids, shuffled
    player_ids = [i for i in range(10000,100000)]
    shuffle(player_ids)

    n_first = 0
    n_last = n_players[0]
        
    # first team
    player_list = player_ids[n_first : n_last]
    all_players_list = [player_list]

    # other teams if n_players recieved more than 1 user input
    if len(n_players) > 1:
        for n in n_players[1:]:
            n_first = n_last
            n_last += n

            player_list = player_ids[n_first : n_last]
            all_players_list.extend([player_list])

    return all_players_list

# create individual player
def player_score(player_id = randint(10000, 99999), date = datetime.date.today().isoformat(),
                 events=['A','B']) -> type[pd.DataFrame]:
    """
    Creates a DataFrame with a single random player and scores for each event (game)

    **Parameters**
    -------------
    player_id: player unique identifier
    date: date in YYYY-MM-DD (today by default)
    events: list of str of simultaneous activities
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

# create a team
def team_players(player_id= [randint(10000,99999)], date = datetime.date.today().isoformat(),
                 events=['A','B']) -> type[pd.DataFrame]:

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

# create a team with random scores
def team_scores(player_id = [randint(10000,99999)], date = datetime.date.today().isoformat(),
                events=['A','B']) -> type[pd.DataFrame]:
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

#----------------------------------------------------------------------------------------

# 2 - Sidebar: user inputs
def side_bar_params() -> tuple[dict,int]:
    st.sidebar.header("Simulate some data!")

    date_input = st.sidebar.date_input('Event day', format = "YYYY-MM-DD")
    events_input = st.sidebar.multiselect("Event games", ['Racing', 'Swimming', 'Flying',
                                                          'Skydiving', 'Diving', 'Shooting', 'Tag',
                                                          'Battle Royale', 'Card game'])
    team_names_input = st.sidebar.multiselect("User team preference",
                                                ['Summer', 'Autumn', 'Winter', 'Spring',
                                                'Cats', 'Dogs', 'Birds', 'Fish', 'Humans',
                                                'Elves', 'Orcs', 'Anthropomorph', 'Knights',
                                                'Sorcerers', 'Archers', 'Thieves'])
    #----- total players user input
    n_player_base = st.sidebar.number_input("Set a number of players (between 100 and 10000)", 100, 10000)

    team_a = 1
    team_b, team_c, team_d = 0,0,0

    # sidebar sliders
    #----- team a
    if len(team_names_input)>=1:
        team_a = st.sidebar.slider(f"1st team size (max: {n_player_base})",
                                        1, n_player_base)
    #----- team b
    if team_a < n_player_base and len(team_names_input)>=2:
        team_b = st.sidebar.slider(f"2nd team size (max: {n_player_base-team_a})",
                                    0, n_player_base-team_a)
            
    #----- team c
        if n_player_base-team_a-team_b >= 1 and team_b != 0 and len(team_names_input)>=3:
            team_c = st.sidebar.slider(f"3nd team size (max: {n_player_base-team_a-team_b})",
                                        0, n_player_base-team_a-team_b)
                
    #----- team d
            if n_player_base-team_a-team_b-team_c >= 1 and team_c!=0 and len(team_names_input)>=4:
                team_d = st.sidebar.slider(f"4th team size (max: {n_player_base-team_a-team_b-team_c})",
                                            0, n_player_base-team_a-team_b-team_c)

    # clear cache
    if st.sidebar.button(":material/restart_alt: Ready to go!"):
        st.cache_data.clear()
    
    # Iterable data from inputs for simulation

    input_n_players = [team_a, team_b, team_c, team_d]
    first_team, *teams = players_ids_list(input_n_players)
          
        
    # 3 - Simulation pipeline
    @st.cache_data(ttl= '1h')
    def data_sim() -> dict:
        """
        Simulated data from user defined parameters. Returns a dict with all needed variables for
        the pipeline (individual teams raw data, bool list for iteration, full df with teams raw data
        and aggregated teams data)
        """
        if len(team_names_input)>=1 and len(events_input)>=1:
            df_first_team = team_scores(player_id = first_team,
                                        date = date_input,
                                        events=events_input)
            df_first_team['team'] = pd.Series([team_names_input[0] for i in range(len(df_first_team))])

            *df_teams, = [pd.DataFrame() for i in range(3)]
            bool_list = []

            for l_idx in range(len(teams)):
                if len(teams[l_idx]) > 1:
                    df_teams[l_idx] = team_scores(player_id = teams[l_idx],
                                                date = date_input,
                                                events=events_input)
                    df_teams[l_idx]['team'] = pd.Series([team_names_input[1:][l_idx] for i in range(len(df_teams[l_idx]))])
                    bool_list.append(True)
                else:
                    bool_list.append(False)

            # concatenate all teams
            df_teams_disagg = df_first_team.copy()
            for i in range(len(bool_list)):
                if bool_list[i] == True:
                    df_teams_disagg = pd.concat([df_teams_disagg, df_teams[i]]).reset_index(drop=True)
                        
            # teams aggregated data
            df_teams_agg = df_teams_disagg.groupby(['event_date', 'event_game', 'team', 'medal']).sum('score').reset_index()

            # full output
            data_sim_output = {
                'teams_raw' : [df_first_team, df_teams],
                'bool_list' : bool_list,
                'all_teams_disagg' :df_teams_disagg,
                'all_teams_agg' : df_teams_agg
                }

            del df_first_team, df_teams, bool_list, df_teams_disagg, df_teams_agg
                        
            return data_sim_output
        else:
            pass
            
    
    simulated_data = data_sim()

    return simulated_data, n_player_base

#####

# 3 - Metrics functions


def metrics_bulk(columns: list,
                     labels: list[str],
                     data: pd.DataFrame,
                     col_filter: str,
                     select_filter: str,
                     col_value: str,
                     col_delta_value: str,
                     delta_compare: int | float,
                     label_annot: str = 'off',
                     delta_annot: str | list = 'off',
                     value_annot: str = '') -> None:
    """
    *Procedure*
    -
    Streamlit metrics and filter selector, organized in columns.

    *Parameters*
    -
    - columns: list, input streamlit columns, must be a list with 4 columns, where 3 are picked
    - labels: list[str], all 3 metric labels
    - label_annot: str, *default: off*, if a list is given, customize label
    - data: pd.DataFrame, main data to show in metrics
    - col_filter: str, data column filtering for selected output
    - select_filter: str, selector value comparison for filtering
    - col_value: str, column for main metric outputs
    - col_delta_value: str, column for main data delta
    - delta_compare: int | float, general value to define increase or decrease, can be used a
        dataframe.describe() value in form of df.describe().at[metric, col_delta_value]
    - delta_annot: str | list, *default: off* adds additional annotation in delta line, if
        its str, will be added in last metric only, if a list (of 3 values), will customize with
        an iteration instead
    """
    # data filter and data value for delta
    data_filtered = data[data[col_filter]==select_filter]
    aux_delta = np.mean(data_filtered[col_delta_value].values)

    # additional dynamic annotation for label and delta
    if label_annot == 'off':
        add_label_annot = ['' for i in range(3)]
    else:
        add_label_annot = data_filtered[label_annot].values
    
    if delta_annot == 'off':
        add_delta_annot = ['' for i in range(3)]
    if delta_annot != 'off' and type(delta_annot) == str:
        add_delta_annot = ['','',delta_annot]
    if type(delta_annot) == list:
        add_delta_annot = delta_annot

    # highlights
    #----- numerical value
    if type(data_filtered[col_value].values[0]) != str and type(data_filtered[col_value].values[-1]) != str:
        columns[1].metric(f"{labels[0]}{add_label_annot[0]}",
                            round(data_filtered[col_value].values[0], 2),
                            f"{round(data_filtered[col_delta_value].values[0] - aux_delta,2)}{add_delta_annot[0]}")
        columns[2].metric(f"{labels[1]}{add_label_annot[-1]}",
                            round(data_filtered[col_value].values[-1], 2),
                            f"{round(data_filtered[col_delta_value].values[-1] - aux_delta,2)}{add_delta_annot[1]}")
        columns[3].metric(f"{labels[2]}",
                            f"{round(aux_delta,2)}{value_annot}",
                            f"{round(aux_delta - delta_compare,2 )}{add_delta_annot[2]}")
        
    else:
        columns[1].metric(f"{labels[0]}{add_label_annot[0]}",
                            data_filtered[col_value].values[0],
                            f"{round(data_filtered[col_delta_value].values[0] - aux_delta,2)}{add_delta_annot[0]}")
        columns[2].metric(f"{labels[1]}{add_label_annot[-1]}",
                            data_filtered[col_value].values[-1],
                            f"{round(data_filtered[col_delta_value].values[-1] - aux_delta,2)}{add_delta_annot[1]}")
        columns[3].metric(f"{labels[2]}",
                            f"{round(aux_delta,2)}{value_annot}",
                            f"{round(aux_delta - delta_compare,2 )}{add_delta_annot[2]}")
