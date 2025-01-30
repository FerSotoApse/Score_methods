# Score Methods Study #

[Streamlit app link](https://scoremethods.streamlit.app/)

# Resume

Common scoring systems used in games consider a simple accumulation of points gained by the user, and tend to gain complexity
depending on what is being measured. This methods work well when are applied on single players or on team games with a defined,
unmutable size, but not in a situation were the size is defined by user preferences, were teams or categories will be naturally
unbalanced. Here is proposed an alternative scoring method based on the performance of each group, which can be
applied on large, naturally irregular groups, tested on a event escenario with multiple activities.

# Data description

All initial synthetic data is randomly generated, and based on the user point of view interface:

- player_id: user unique identification
- event_date: date of the event, in YYYY-MM-DD format
- event_game: activity within the overall event, can be multiple activities happening at the same time
- team: team, group or category where the user belongs.
- score: user score in an activity. 0 is given if not participated in the activity, 1 to 3 if the user participated
- medal: medal won by the user in an activity. 0 is 'not played', 1 is 'bronze', 2 is 'silver', 3 is 'gold'

# Method

# Sources

- [Sky: Children of the Light Fandom, "Tournament of Triumph"](https://sky-children-of-the-light.fandom.com/wiki/Tournament_of_Triumph)
- [Godai Sky: "¿Cuál es el reino más popular de Sky: Children of the Light?"](https://youtu.be/06E3c04gVlA)
- "Sky: Children of the Light", official That Game Company (TGC) Discord server, news channel.

# Libraries

## Data generation and manipulation
- Pandas
- Numpy
- Random
- Datetime

## Machine Learning Model
- Scikit-learn for KMeans unsupervised model and metrics

## Data visualization
- Plotly graph_objects
- Plotly Express
