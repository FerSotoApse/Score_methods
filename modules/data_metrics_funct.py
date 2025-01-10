import numpy as np
import pandas as pd

# sorted teams for metrics show
def event_winners(df_agg_data: pd.DataFrame, score_method: str) -> pd.DataFrame:
    """
    Function
    -
    Shows the winners sorted by total score > medal score > team participation ratio.

    Parameters
    -
    - df_agg_data: data containing all aggregated data after pipeline
    - score_method: choose a score method, can be 'accumulative' or 'performance'
      (default: 'accumulative')
    """
    # condition from score_method input
    if score_method == 'accumulative':
        score_cols = ['acc_w_score_total', 'acc_w_score']
    if score_method == 'performance':
        score_cols = ['perform_score_total', 'perform_score']

    # for iteration and indexing
    events_aux = list(df_agg_data['event_game'].unique())
    n_teams = len(df_agg_data['team'].unique())

    observed_winners = df_agg_data[df_agg_data['event_game']==events_aux[0]].copy()\
        .sort_values(by = [score_cols[0], score_cols[1], 'team_participation_ratio'],
                     ascending = False, ignore_index=True)\
                     [['event_game','team','medal',score_cols[0], score_cols[1], 'team_participation_ratio']]
    
    # mask with unique sorted teams (first ocurrence of each team)
    winners = observed_winners[observed_winners.duplicated('team')==False]

    # if there are more than a single event, concatenate results
    if len(events_aux) > 1:
        for e in range(1, len(events_aux)):
            observed_winners = df_agg_data[df_agg_data['event_game']==events_aux[e]].copy()\
                                    .sort_values(by = [score_cols[0], score_cols[1], 'team_participation_ratio'],
                                                 ascending = False, ignore_index=True)\
                                   [['event_game','team', 'medal',score_cols[0], score_cols[1],'team_participation_ratio']]
    
            winners = pd.concat([winners, observed_winners[observed_winners.duplicated('team')==False]])
    
    # clear memory
    del n_teams, events_aux, observed_winners

    return winners