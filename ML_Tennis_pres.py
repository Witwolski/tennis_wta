from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from collections import Counter
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")


def ML(Surface):
    dataset = pd.read_sql_query(
        "Select Winner, Elo_Fav,Elo_Fav_Odds, Elo_Dog_Odds, Elo_Winner, Elo_Loser FROM Elo_AllMatches where  date < '2022-07-01' and WinnerTotal > 50 and LoserTotal > 50 and Elo_Fav_Odds >1.9 ",
        con=devengine,
    )

    date_from = "2022-07-01"
    date_to = "2022-08-11"
    prediction = pd.read_sql_query(
        "Select  Winner,Loser,Elo_Fav, Elo_Fav_Odds ,Elo_Dog_Odds, Elo_Winner, Elo_Loser FROM Elo_AllMatches where  date > '{}' and date < '{}' and WinnerTotal > 50 and LoserTotal > 50 and Elo_Fav_Odds >1.9".format(
            date_from, date_to
        ),
        con=devengine,
    )
    prediction1 = pd.read_sql_query(
        "Select Date,Winner,Loser,Elo_Fav, Elo_Fav_Odds, Elo_Dog_Odds, Elo_Winner, Elo_Loser  FROM Elo_AllMatches where  date > '{}' and date < '{}' and WinnerTotal > 50 and LoserTotal > 50 and Elo_Fav_Odds >1.9".format(
            date_from, date_to
        ),
        con=devengine,
    )

    dataset["Winner"] = dataset.apply(
        lambda x: "EloFav" if x["Winner"] == x["Elo_Fav"] else "EloDog", axis=1
    )
    dataset["Elo_Fav"] = dataset.apply(
        lambda x: x["Elo_Winner"] if x["Winner"] == x["Elo_Fav"] else x["Elo_Loser"],
        axis=1,
    )
    dataset["Elo_Dog"] = dataset.apply(
        lambda x: x["Elo_Loser"] if x["Winner"] == x["Elo_Fav"] else x["Elo_Winner"],
        axis=1,
    )
    dataset["Odds_Difference"] = abs(dataset["Elo_Fav_Odds"] - dataset["Elo_Dog_Odds"])
    dataset["Elo_Difference"] = abs(dataset["Elo_Fav"] - dataset["Elo_Dog"])
    dataset = dataset[["Winner", "Odds_Difference", "Elo_Difference"]]
    my_list = ["EloFav", "EloDog"]
    dataset["Player_1"] = np.random.choice(my_list, len(dataset))
    dataset["Player_2"] = dataset.apply(
        lambda x: "EloDog" if x["Player_1"] == "EloFav" else "EloFav", axis=1
    )

    prediction["Player_1"] = prediction.apply(
        lambda x: "EloFav" if x["Winner"] == x["Elo_Fav"] else "EloDog", axis=1
    )
    prediction["Player_2"] = prediction.apply(
        lambda x: "EloFav" if x["Winner"] != x["Elo_Fav"] else "EloDog", axis=1
    )
    prediction["Odds_Difference"] = abs(
        prediction["Elo_Fav_Odds"] - prediction["Elo_Dog_Odds"]
    )
    prediction["Elo_Fav"] = prediction.apply(
        lambda x: x["Elo_Winner"] if x["Winner"] == x["Elo_Fav"] else x["Elo_Loser"],
        axis=1,
    )
    prediction["Elo_Dog"] = prediction.apply(
        lambda x: x["Elo_Loser"] if x["Winner"] == x["Elo_Fav"] else x["Elo_Winner"],
        axis=1,
    )
    prediction["Elo_Difference"] = abs(prediction["Elo_Fav"] - prediction["Elo_Dog"])
    prediction = prediction[
        ["Player_1", "Player_2", "Odds_Difference", "Elo_Difference"]
    ]

    final_result = pd.get_dummies(
        dataset, prefix=["Player_1", "Player_2"], columns=["Player_1", "Player_2"]
    )
    prediction = pd.get_dummies(
        prediction, prefix=["Player_1", "Player_2"], columns=["Player_1", "Player_2"]
    )

    X = final_result.drop(["Winner"], axis=1)
    y = final_result["Winner"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=25)
    # model = LogisticRegression(max_iter=20000000)
    model2 = SVC(max_iter=20000000)
    model2.fit(X_train, y_train)
    # model.fit(X_train, y_train)
    # train_score = model.score(X_train, y_train)
    train_score2 = model2.score(X_train, y_train)
    test_score2 = model2.score(X_test, y_test)
    # test_score = model.score(X_test, y_test)

    if len(prediction) == 0:
        return 0, ""
    # pred = model.predict(prediction)
    pred2 = model2.predict(prediction)
    cols = [
        "Date",
        "Prediction",
        "Elo_Fav",
        "Elo_Fav_Odds",
        "Winner",
        "Loser",
        # "Training_Accuracy",
        # "Testing_Accuracy",
    ]
    df = pd.DataFrame(columns=cols)
    List = []
    for index, tuples in prediction1.iterrows():
        if index < len(prediction1):

            values = [
                prediction1["Date"][index],
                pred2[index],
                prediction1["Elo_Fav"][index],
                prediction1["Elo_Fav_Odds"][index],
                prediction1["Winner"][index],
                prediction1["Loser"][index],
                #  "{:.0%}".format(train_score2),
                #  "{:.0%}".format(test_score2),
            ]
            zipped = zip(cols, values)
            a_dictionary = dict(zipped)
            List.append(a_dictionary)
    temp = pd.DataFrame(List)
    df = pd.concat([df, temp])
    df = df[df["Prediction"] == "EloFav"]
    players = []
    if train_score2 > 0.5 and test_score2 > 0.5:
        for _, i in df.iterrows():
            players.append(i)
        return 1, players
    else:
        return 0, ""


players1 = []
for x in range(1, 100):
    pl = ML("Hard")[1]
    players1.append(pl)
flat_list = [item for sublist in players1 for item in sublist]
x = pd.DataFrame(flat_list)
x = x.groupby(x.columns.tolist()).size().reset_index().rename(columns={0: "records"})
# x = x[x["records"].ge(10)]
x["win_loss"] = x.apply(
    lambda x: "Win" if x["Elo_Fav"] == x["Winner"] else "Loss", axis=1
)
wins = len(x[x["win_loss"] == "Win"])
losses = len(x[x["win_loss"] == "Loss"])
print(wins / (wins + losses))
print(len(x))
x.to_csv("Predictions_Past.csv", index=False)
