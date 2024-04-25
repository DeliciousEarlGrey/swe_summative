# Import packages
import requests
import json
import os
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

uri_22 = 'https://api.football-data.org/v4/competitions/PL/matches?season=2022'
headers = { 'X-Auth-Token': '14072c3198154792bff0420b28e91968' }

response_22 = requests.get(uri_22, headers=headers)

# Load JSON data
data_22 = response_22.json()['matches']

# Create a DataFrame
df_s22 = pd.DataFrame(data_22)

uri_23 = 'https://api.football-data.org/v4/competitions/PL/matches?season=2023'

response_23 = requests.get(uri_23, headers=headers)

# Load JSON data
data_23 = response_23.json()['matches']

# Create a DataFrame
df_s23 = pd.DataFrame(data_23)


def preprocess_dataframe(input_df):
    df = input_df.copy()  # Create a copy of the input DataFrame

    # Extracting information from nested dictionaries
    df['seasonid'] = df['season'].apply(lambda x: x['id'])
    df['homeTeamid'] = df['homeTeam'].apply(lambda x: x['id'])
    df['homeTeamName'] = df['homeTeam'].apply(lambda x: x['shortName'])
    df['awayTeamid'] = df['awayTeam'].apply(lambda x: x['id'])
    df['awayTeamName'] = df['awayTeam'].apply(lambda x: x['shortName'])
    df['matchWinner'] = df['score'].apply(lambda x: x['winner'])
    df['homeGoals'] = df['score'].apply(lambda x: x['fullTime']['home'])
    df['awayGoals'] = df['score'].apply(lambda x: x['fullTime']['away'])
    df['refID'] = df['referees'].apply(lambda x: x[0]['id'] if len(x) > 0 else None)
    df['refName'] = df['referees'].apply(lambda x: x[0]['name'] if len(x) > 0 else None)

    columns_to_drop = ["area", "competition", "stage", "group", "lastUpdated", "odds", "season", "homeTeam", "awayTeam", "score", "referees"]
    df = df.drop(columns=columns_to_drop, axis=1)

    return df

preprocessed_df_s23 = preprocess_dataframe(df_s23)
preprocessed_df_s22 = preprocess_dataframe(df_s22)



def calculate_cumulative_points(df):
    home_cumulative_points = {}
    away_cumulative_points = {}

    for index, row in df.iterrows():
        home_team = row['homeTeamid']
        away_team = row['awayTeamid']
        match_winner = row['matchWinner']
        matchday = row['matchday']

        if home_team not in home_cumulative_points:
            home_cumulative_points[home_team] = 0

        if away_team not in away_cumulative_points:
            away_cumulative_points[away_team] = 0

        # Check if the match result is a draw
        if match_winner == 'DRAW':
            home_cumulative_points[home_team] += 1
            away_cumulative_points[away_team] += 1

        # Check if the home team won and update cumulative points
        elif match_winner == 'HOME_TEAM':
            home_cumulative_points[home_team] += 3

        # Check if the away team won and update cumulative points
        elif match_winner == 'AWAY_TEAM':
            away_cumulative_points[away_team] += 3

        # Update the DataFrame with the cumulative points except for the current matchday
        df.at[index, 'homePoints'] = home_cumulative_points[home_team] - (3 if match_winner == 'HOME_TEAM' else 0) - (1 if match_winner == 'DRAW' else 0)
        df.at[index, 'awayPoints'] = away_cumulative_points[away_team] - (3 if match_winner == 'AWAY_TEAM' else 0) - (1 if match_winner == 'DRAW' else 0)

    # Convert 'awayPoints' column to integer type
    df['awayPoints'] = df['awayPoints'].astype(int)

    return df


def calculate_cumulative_goals(df):
    home_cumulative_goals = {}
    away_cumulative_goals = {}

    for index, row in df.iterrows():
        home_team = row['homeTeamid']
        away_team = row['awayTeamid']
        home_goals = row['homeGoals']
        away_goals = row['awayGoals']
        match_winner = row['matchWinner']
        matchday = row['matchday']

        if home_team not in home_cumulative_goals:
            home_cumulative_goals[home_team] = 0

        if away_team not in away_cumulative_goals:
            away_cumulative_goals[away_team] = 0

        # Check if home_goals is a valid numeric value (not NaN)
        if pd.notna(home_goals):
            home_cumulative_goals[home_team] += home_goals

        # Check if away_goals is a valid numeric value (not NaN)
        if pd.notna(away_goals):
            away_cumulative_goals[away_team] += away_goals

        # Update the DataFrame with cumulative goals excluding the current matchday
        df.at[index, 'homeTeamHomeGoals'] = home_cumulative_goals[home_team]
        df.at[index, 'awayTeamAwayGoals'] = away_cumulative_goals[away_team]

    return df


def calculate_form(df):
    df['homeTeamForm'] = 0
    df['awayTeamForm'] = 0

    for index, match in df.iterrows():
        home_team_id = match['homeTeamid']
        away_team_id = match['awayTeamid']
        matchday = match['matchday']

        # Calculate home team's form
        home_form_points = 0
        for i in range(index - 1, -1, -1):
            if matchday - df.at[i, 'matchday'] > 3:
                break

            if df.at[i, 'homeTeamid'] == home_team_id:
                if df.at[i, 'matchWinner'] == 'HOME_TEAM':
                    home_form_points += 3
                elif df.at[i, 'matchWinner'] == 'DRAW':
                    home_form_points += 1
            elif df.at[i, 'awayTeamid'] == home_team_id:
                if df.at[i, 'matchWinner'] == 'AWAY_TEAM':
                    home_form_points += 3

        # Calculate away team's form
        away_form_points = 0
        for i in range(index - 1, -1, -1):
            if matchday - df.at[i, 'matchday'] > 3:
                break

            if df.at[i, 'awayTeamid'] == away_team_id:
                if df.at[i, 'matchWinner'] == 'AWAY_TEAM':
                    away_form_points += 3
                elif df.at[i, 'matchWinner'] == 'DRAW':
                    away_form_points += 1
            elif df.at[i, 'homeTeamid'] == away_team_id:
                if df.at[i, 'matchWinner'] == 'HOME_TEAM':
                    away_form_points += 3

        df.at[index, 'homeTeamForm'] = home_form_points
        df.at[index, 'awayTeamForm'] = away_form_points

    return df


def calculate_total_goals(df):
    team_cumulative_goals = {}  # Dictionary to store cumulative goals for each team

    for index, row in df.iterrows():
        home_team = row['homeTeamid']
        away_team = row['awayTeamid']
        home_goals = row['homeGoals']
        away_goals = row['awayGoals']

        # Update cumulative goals for home team (if homeGoals is not NaN)
        if not np.isnan(home_goals):
            if home_team not in team_cumulative_goals:
                team_cumulative_goals[home_team] = 0
            team_cumulative_goals[home_team] += home_goals

        # Update cumulative goals for away team (if awayGoals is not NaN)
        if not np.isnan(away_goals):
            if away_team not in team_cumulative_goals:
                team_cumulative_goals[away_team] = 0
            team_cumulative_goals[away_team] += away_goals

        # Update the DataFrame with cumulative goals
        df.at[index, 'homeTeamTotalGoals'] = team_cumulative_goals.get(home_team, 0)
        df.at[index, 'awayTeamTotalGoals'] = team_cumulative_goals.get(away_team, 0)

    return df


def calculate_total_points(df):
    team_cumulative_points = {}  # Dictionary to store cumulative points for each team

    for index, row in df.iterrows():
        home_team = row['homeTeamid']
        away_team = row['awayTeamid']
        match_winner = row['matchWinner']

        # Calculate points based on match result
        if match_winner == 'HOME_TEAM':
            home_points = 3
            away_points = 0
        elif match_winner == 'AWAY_TEAM':
            home_points = 0
            away_points = 3
        elif match_winner == 'DRAW':
            home_points = 1
            away_points = 1
        else:
            home_points = 0
            away_points = 0

        # Update cumulative points for home and away teams
        if home_team not in team_cumulative_points:
            team_cumulative_points[home_team] = 0
        team_cumulative_points[home_team] += home_points

        if away_team not in team_cumulative_points:
            team_cumulative_points[away_team] = 0
        team_cumulative_points[away_team] += away_points

        # Update the DataFrame with cumulative points
        df.at[index, 'homeTeamTotalPoints'] = team_cumulative_points.get(home_team, 0)
        df.at[index, 'awayTeamTotalPoints'] = team_cumulative_points.get(away_team, 0)

    return df


# Add Features to dataframes
points_s22 = calculate_cumulative_points(preprocessed_df_s22)
goals_s22 = calculate_cumulative_goals(points_s22)
form_s22 = calculate_form(goals_s22)
totalgoals_s22 = calculate_total_goals(form_s22)
totalpoints_s22 = calculate_total_points(totalgoals_s22)

points_s23 = calculate_cumulative_points(preprocessed_df_s23)
goals_s23 = calculate_cumulative_goals(points_s23)
form_s23 = calculate_form(goals_s23)
totalgoals_s23 = calculate_total_goals(form_s23)
totalpoints_s23 = calculate_total_points(totalgoals_s23)

# Add Target Column
totalpoints_s22['homeWinDraw'] = totalpoints_s22['matchWinner'].apply(lambda x: 1 if x in ['HOME_TEAM', 'DRAW'] else 0)
totalpoints_s23['homeWinDraw'] = totalpoints_s23['matchWinner'].apply(lambda x: 1 if x in ['HOME_TEAM', 'DRAW'] else 0)
totalpoints_s22['awayWinDraw'] = totalpoints_s22['matchWinner'].apply(lambda x: 1 if x in ['AWAY_TEAM', 'DRAW'] else 0)
totalpoints_s23['awayWinDraw'] = totalpoints_s23['matchWinner'].apply(lambda x: 1 if x in ['AWAY_TEAM', 'DRAW'] else 0)

# Add previous season data (manually atm)
previous_season = {
    'teamName': ['Man City', 'Liverpool', 'Chelsea', 'Tottenham', 'Arsenal', 'Man Utd', 'West Ham', 'Leicester', 'Brighton', 'Wolves', 'Ncastle', 'C Palace', 'Brentford', 'Ast Villa', 'Southampton', 'Everton', 'Leeds',
                 'Man City', 'Arsenal', 'Man Utd', 'Ncastle', 'Lpool', 'Brighton', 'A Villa', 'Tottenham', 'Brentford', 'Fulham', 'C Palace', 'Chelsea', 'Wolves', 'W Ham', 'Bournemouth', 'Nott Forest', 'Everton'],
    'teamid': [65, 64, 61, 73, 57, 66, 563, 338, 397, 76, 67, 354, 402, 58, 340, 62, 341,
               65, 57, 66, 67, 64, 397, 58, 73, 402, 63, 354, 61, 76, 563, 1044, 351, 62],
    'seasonid': [1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1490, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564, 1564],
    'previousSeasonPoints': [93, 92, 74, 71, 69, 58, 56, 52, 51, 51, 49,48, 46, 45, 40, 39, 38, 89, 84, 75, 71, 67, 62, 61, 60, 59, 52, 45, 44, 41, 40, 39, 38, 36]
}
previous_season_df = pd.DataFrame(previous_season)

def merge_previous_season(goals_points_df, previous_season_df):
    # Merge based on seasonid and homeTeamid
    merged_home = goals_points_df.merge(previous_season_df, left_on=['seasonid', 'homeTeamid'], right_on=['seasonid', 'teamid'], how='left')
    merged_home.rename(columns={'previousSeasonPoints': 'homeTeamPreviousSeason'}, inplace=True)
    merged_home.drop(columns=['teamid', 'teamName'], inplace=True)

    # Merge based on seasonid and awayTeamid
    merged_final = merged_home.merge(previous_season_df, left_on=['seasonid', 'awayTeamid'], right_on=['seasonid', 'teamid'], how='left')
    merged_final.rename(columns={'previousSeasonPoints': 'awayTeamPreviousSeason'}, inplace=True)
    merged_final.drop(columns=['teamid', 'teamName'], inplace=True)

    # Replace NaN values with the lowest existing value in each column
    lowest_home_value = merged_final['homeTeamPreviousSeason'].min()
    merged_final['homeTeamPreviousSeason'].fillna(lowest_home_value, inplace=True)

    lowest_away_value = merged_final['awayTeamPreviousSeason'].min()
    merged_final['awayTeamPreviousSeason'].fillna(lowest_away_value, inplace=True)

    return merged_final

result_df_s22 = merge_previous_season(totalpoints_s22, previous_season_df)
result_df_s23 = merge_previous_season(totalpoints_s23, previous_season_df)

# Concatenate the DataFrames vertically
combined_df = pd.concat([result_df_s22, result_df_s23], ignore_index=True)

features = ['homeTeamid', 'awayTeamid', 'homePoints', 'homeTeamHomeGoals', 'awayTeamAwayGoals', 'awayTeamForm',
            'homeTeamTotalGoals', 'awayTeamTotalGoals', 'homeTeamTotalPoints', 'awayTeamTotalPoints', 'homeTeamPreviousSeason', 'awayTeamPreviousSeason']
target = 'homeWinDraw'
target2 = 'awayWinDraw'

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['awayTeamForm', 'homeTeamPreviousSeason', 'awayTeamPreviousSeason', 'homePoints', 'homeTeamHomeGoals', 'awayTeamAwayGoals',
                                   'homeTeamTotalGoals',	'awayTeamTotalGoals',	'homeTeamTotalPoints',	'awayTeamTotalPoints']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['homeTeamid', 'awayTeamid'])
    ])

print("Current working directory:", os.getcwd())
print("Templates directory:", os.path.join(os.getcwd(), 'templates'))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict')
def predict():
    matchweek = int(request.args.get('matchweek'))

    # Separating Training and Predicting Data
    training_data = combined_df[(combined_df['seasonid'] == 1490) | (combined_df['matchday'] < matchweek)]
    predicting_data = combined_df[(combined_df['seasonid'] == 1564) & (combined_df['matchday'] == matchweek)]

    # Separate features and target variable from training_data
    X_train = training_data[features]
    y_train = training_data[target]
    y2_train = training_data[target2]

    X_train_preprocessed = preprocessor.fit_transform(X_train)



    # Initialize and train your chosen model (e.g., Logistic Regression)
    model = LogisticRegression()
    model.fit(X_train_preprocessed, y_train)

    model2 = LogisticRegression()
    model2.fit(X_train_preprocessed, y2_train)


    # Separate features from predicting_data
    X_predict = predicting_data[features]
    X_predict_preprocessed = preprocessor.transform(X_predict)

    # Make predictions on predicting_data and add to predictions df
    predictions = model.predict(X_predict_preprocessed)
    predictions2 = model2.predict(X_predict_preprocessed)

    outcome_df = predicting_data[features]
    outcome_df['homeTeamName'] = predicting_data['homeTeamName']
    outcome_df['awayTeamName'] = predicting_data['awayTeamName']
    outcome_df['home win/draw predictions'] = predictions
    outcome_df['away win/draw predictions'] = predictions2
    

    #Get confidence of the prediction
    proba_scores = model.predict_proba(X_predict_preprocessed)
    proba_scores2 = model2.predict_proba(X_predict_preprocessed)
    print("Probability scores shape:", proba_scores.shape)
    print("Probability scores:", proba_scores)
    print("Probability scores 2 shape:", proba_scores2.shape)
    print("Probability scores 2:", proba_scores2)


    positive_class_confidences = proba_scores[:, 1]
    positive_class_confidences2 = proba_scores2[:, 1]

    print("Positive class confidences:", positive_class_confidences)
    print("Positive class confidences 2:", positive_class_confidences2)

    outcome_df['home_confidence'] = (positive_class_confidences*100).round(2)
    outcome_df['away_confidence'] = (positive_class_confidences2*100).round(2)
    
    print("home confidence: ", outcome_df['home_confidence'])
    print("away confidence: ", outcome_df['away_confidence'])
    

    return jsonify(outcome_df.to_dict(orient='records'))



if __name__ == '__main__':
    app.run(debug=True)