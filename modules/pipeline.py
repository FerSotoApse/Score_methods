import numpy as np
import pandas as pd
import time, datetime
from random import randint, shuffle


# Pipeline Functions

def pipeline(df_agg_data: pd.DataFrame, df_disagg_data: pd.DataFrame,
             df_first_team_data: pd.DataFrame, df_teams_l_data = list[pd.DataFrame],
             b_l = list[bool]
             ) -> pd.DataFrame:

    """
    Pipeline Function
    ----------
    Generates all metric columns in the aggregated DataFrame from simulated data.

    Output
    ----------
    A transformed pandas DataFrame with relative and absolute metrics and score methods.
    """

    if len(df_agg_data) > 0 and len(df_disagg_data) > 0:

        # P: absolute medal count procedure
        def abs_medal_count(df_agg_data: pd.DataFrame) -> None:
            """
            *Procedure*
            -
            Adds absolute medal count (absoute frequence) column in df with aggregated data.
            """
            # create an empty list for absolute medal count
            medal_abs_frequence_l = []
            # rename score column
            df_agg_data.columns = ['event_date', 'event_game', 'team', 'medal', 'acc_w_score']

            for i in range(len(df_agg_data)):
                if df_agg_data['medal'].iat[i] == 'gold':
                    medal_abs_frequence_l.append(int(df_agg_data['acc_w_score'].iat[i]/3))
                elif df_agg_data['medal'].iat[i] == 'silver':
                    medal_abs_frequence_l.append(int(df_agg_data['acc_w_score'].iat[i]/2))
                elif df_agg_data['medal'].iat[i] == 'bronze':
                    medal_abs_frequence_l.append(int(df_agg_data['acc_w_score'].iat[i]/1))
                else:
                    medal_abs_frequence_l.append(0)

                # adds a column in df with aggregated data
                df_agg_data['medal_abs_frequence'] = pd.Series(medal_abs_frequence_l)
                

        # P: set categorical type on columns for category order procedure
        def agg_categories(df_agg_data: pd.DataFrame, df_disagg_data: pd.DataFrame) -> None:
            """
            *Procedure*
            -
            Set categorical type on team and medal columns in df with aggregated data.
            """    
            # set categorical type on teams to order by team
            df_agg_data['team'] = pd.Categorical(
                values = [i for i in df_agg_data['team'].values],
                categories = [i for i in df_disagg_data['team'].unique()],
                ordered = True)
            df_agg_data.sort_values(by=['event_game','team', 'medal'], ascending=[True,True, True], ignore_index=True, inplace=True)

            # set categorical type on medal to order by medal
            df_agg_data['medal'] = pd.Categorical(df_agg_data['medal'],
                                                ordered=True,
                                                categories = ['not played','bronze', 'silver', 'gold'])

        #----- data metrics

        #---------- active players count in each team function 
        def players_count(df_first_team_data: pd.DataFrame, df_teams_l_data = list[pd.DataFrame],
                            b_l = list[bool]) -> list:
            """
            *Function*
            -
            Returns a list of active players in each team.
            """
            # first team players (active)
            team_n_players = [len(df_first_team_data['player_id'].unique())]
            # all other team players
            for i in range(len(b_l)):
                if b_l[i] == True:
                    team_n_players.append(len(df_teams_l_data[i]['player_id'].unique()))  # type: ignore

            return team_n_players

        #---------- total active players during the event day function
        def total_players_count(df_first_team_data = df_first_team_data, 
                                df_teams_l_data = df_teams_l_data, 
                                b_l = b_l) -> int: 
            """
            *Function*
            -
            Returns the sum of all values in players_count function.
            """
            t_p_count = players_count(df_first_team_data = df_first_team_data,
                                    df_teams_l_data = df_teams_l_data,
                                    b_l = b_l)

            total_count = 0

            for n in t_p_count:
                total_count += n

            return total_count

        #---------- participation ratio for all purposes function
        def participation_ratio(total_players: int, group_count: int) -> float:
            """
            *Function*
            -
            Simple user ratio. Used for relative comparison.

            *Params*
            -
            total_players: can be: base number of users, total active users, or team users.
            group_count: can be: team users or active users.
            """
            if total_players >= group_count:
                p_r = group_count / total_players

                return round(p_r*100, 2)

        # P: adds teams relative size column from total active players function
        def add_team_rel_size(df_agg_data: pd.DataFrame, df_disagg_data: pd.DataFrame,
                            df_first_team_data: pd.DataFrame,
                            df_teams_l_data: list[pd.DataFrame],
                            b_l: list[bool]) -> pd.DataFrame:
            """
            *Function*
            -
            Adds a column that indicates the relative portion of a team in face to total active players
            """
            # count team players
            team_count_l = players_count(df_first_team_data = df_first_team_data,
                                        df_teams_l_data = df_teams_l_data,
                                        b_l = b_l)
            # team relative size compared to all active players during the day
            team_rel_size_l = [participation_ratio(total_players = total_players_count(),
                                                group_count = team_count_l[n])\
                                    for n in range(len(team_count_l))]
                    
            # aux df with relative size data
            df_aux = pd.DataFrame({
                    'team' : list(df_disagg_data['team'].unique()),
                    'team_relative_size' : team_rel_size_l})
                    
            # merges with df with aggregated data
            df_agg_data = df_agg_data.merge(right=df_aux, on='team', how='inner')

            return df_agg_data

        #---------- participants from each team in a given event function
        def team_event_participation(event: str, filter: str,
                                    df_first_team_data, df_teams_l_data, b_l) -> list[float]:
            """
            *Function*
            -
            List of relative count participation of each team in a given event. The order will be:
            - first team participation ratio (df_first_team)
            - other teams participation ratios, in order, from df_teams (list of dfs)
                
            *Params*
            -
            event: str, name of a common event in each team df
            filter: str, value that represents non participants in given event
            """
            # all active players in each team
            players_count_l = players_count(df_first_team_data = df_first_team_data,
                                            df_teams_l_data = df_teams_l_data,
                                            b_l = b_l)
            # active players that played in an event
            #----- first team filter
            teams_notplayed_count = [len(df_first_team_data[df_first_team_data['event_game']==event][df_first_team_data['medal']!=filter])]
            #------ other teams filter
            for team, b in zip(df_teams_l_data, b_l):
                if b == True:
                    teams_notplayed_count.append(len(team[team['event_game']==event][team['medal']!=filter]))

            # participation relative count from teams and events, not from total players
            teams_participants_ratio = [participation_ratio(t_players, t_particip)
                                        for t_players, t_particip in zip(players_count_l, teams_notplayed_count)]
                
            return teams_participants_ratio

        # P: adds participation ratio column function
        def add_team_event_participation(df_agg_data: pd.DataFrame,
                                        df_disagg_data: pd.DataFrame,
                                        df_first_team_data: pd.DataFrame,
                                        df_teams_l_data: list[pd.DataFrame],
                                        b_l: list[bool]) -> pd.DataFrame:
            """
            *Function*
            -
            Adds team participation ratio column to df with aggregated data
            """
            event_aux = df_disagg_data['event_game'].unique()
            team_aux = df_disagg_data['team'].unique()

            # list of lists with team participation in each event
            team_event_r = [team_event_participation(event_aux[e], 'not played', df_first_team_data, df_teams_l_data, b_l)
                            for e in range(len(event_aux))]

            # lists to create an aux df to add participation ratios to aggregated data
            event_aux_l, team_aux_l, team_event_r_l = [], [], []
            for t in range(len(team_aux)):
                for e in range(len(event_aux)):
                    team_aux_l.append(team_aux[t])
                    event_aux_l.append(event_aux[e])
                    team_event_r_l.append(team_event_r[e][t])

            df_aux = pd.DataFrame({
                'team' : team_aux_l,
                'event_game' : event_aux_l,
                'team_participation_ratio': team_event_r_l})
                
            df_agg_data = df_agg_data.merge(right=df_aux, on=['team', 'event_game'], how='inner')

            return df_agg_data

        # P: add medal relative count from each team player counts procedure
        def add_medal_rel_frequence(df_agg_data: pd.DataFrame,
                                    df_disagg_data: pd.DataFrame,
                                    df_first_team_data: pd.DataFrame,
                                    df_teams_l_data: list[pd.DataFrame],
                                    b_l: list[bool]) -> None:
            """
            *Procedure*
            -
            Adds medal relative count column from each team size (n players) to df with aggregated data
            """
            teams_aux = df_disagg_data['team'].unique()
            team_count = players_count(df_first_team_data = df_first_team_data,
                                    df_teams_l_data = df_teams_l_data, b_l = b_l)
                
            # creates list of medal relative frequences by team
            m_rel_f_l = []
            for count, team in zip(team_count, teams_aux):
                m_rel_f_l.extend(df_agg_data[df_agg_data['team']==team]['medal_abs_frequence'].map(lambda x: round((x/count)*100, 2)))
                
            # appends to aggregated df data
            df_agg_data['medal_rel_frequence'] = pd.Series(m_rel_f_l)

        # P: adds performance score method column procedure
        def team_performance_score(df_agg_data: pd.DataFrame) -> None:
            """
            *Procedure*
            -
            Adds team medals` performance score to df with aggregated data. It`s calculated as:

                performance_score = medal_relative_frequence * medal_weight
                    
            where medal_weight = (acc_w_score/medal_abs_frequence), acc_w_score is accumulated score by
            medal and medal_abs_frequence is each medal count.
            """
            medal_w = (df_agg_data['acc_w_score']/df_agg_data['medal_abs_frequence']).fillna(0)

            df_agg_data['perform_score'] = df_agg_data['medal_rel_frequence']*medal_w

        # P: adds total scores to aggregated data function
        def total_scores(df_agg_data: pd.DataFrame) -> pd.DataFrame:
            """
            *Function*
            -
            Adds columns with sum of accumulative and performance scores.
            """
            # group by to create sum columns and rename before merge
            df_aux = df_agg_data[['event_game', 'team', 'acc_w_score', 'perform_score']]\
                        .groupby(['event_game', 'team']).sum(['acc_w_score', 'perform_score'])\
                        .reset_index()
            df_aux.columns = ['event_game', 'team', 'acc_w_score_total', 'perform_score_total']

            # merge to agg df
            df_agg_data = pd.merge(left = df_agg_data, right= df_aux,
                                   how = 'inner', on = ['event_game', 'team'])
            
            del df_aux
            return df_agg_data

        # Pipeline Excecution (all marked with P)
        abs_medal_count(df_agg_data)
        agg_categories(df_agg_data, df_disagg_data)
        df_agg_data = add_team_rel_size(df_agg_data, df_disagg_data,
                                            df_first_team_data, df_teams_l_data, b_l) 
        df_agg_data = add_team_event_participation(df_agg_data, df_disagg_data,
                                                    df_first_team_data, df_teams_l_data, b_l)
        add_medal_rel_frequence(df_agg_data, df_disagg_data, df_first_team_data, df_teams_l_data, b_l) 
        team_performance_score(df_agg_data)
        df_agg_data = total_scores(df_agg_data)

        return df_agg_data

if __name__ == "__main__":
    pipeline()

else:
    pass
