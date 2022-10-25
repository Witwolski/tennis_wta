import datetime
from sqlite3 import connect
import requests
from bs4 import BeautifulSoup
import argparse
import datetime
from tabulate import tabulate
import pandas as pd
from Tennis import *
import openpyxl
import xlsxwriter
from elotable import GetElo
from cmath import nan
from typing import Type
import pandas as pd
import os
import csv
from pandas.core.arrays.integer import safe_cast
import sqlalchemy as sa
from sqlalchemy import create_engine
import pymssql
import time
from pathlib import Path
import msvcrt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
#import xgboost as xgb
from collections import Counter

username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database)
devengine = create_engine(devconnection_uri)


def ML(LowOdds,HighOdds,Surface):
    global counting
    dataset=pd.read_sql_query("Select [Player 1],[Elo Favourite],[Estimated Odds Clay] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference Clay], [Elo Difference Hard],RankDiff FROM Bets_yesterday \
        where  date like '%' and [Actual Odds] >= {} and [Actual Odds] <= {} and [Actual Odds] > [Estimated Odds]  and Surface  like '{}'".format(LowOdds,HighOdds,Surface),con=devengine)

    prediction=pd.read_sql_query("Select [Player 1],[Elo Favourite],[Estimated Odds Clay] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference Clay], [Elo Difference Hard],RankDiff FROM Bets_today \
        where   [Actual Odds] >= {} and   [Actual Odds] <= {} and [Actual Odds] > [Estimated Odds] and Surface  like '{}'".format(LowOdds,HighOdds,Surface),con=devengine)
    prediction1=pd.read_sql_query("Select [Player 1],[Elo Favourite],[Estimated Odds Clay] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference Clay], [Elo Difference Hard],RankDiff FROM Bets_today \
        where [Actual Odds] >= {} and [Actual Odds] <= {} and [Actual Odds] > [Estimated Odds]  and Surface like '{}'".format(LowOdds,HighOdds,Surface),con=devengine)
    dataset=dataset.dropna()
    prediction=prediction.dropna()
    prediction1=prediction1.dropna()
    #print(prediction1)

    dataset["Player 1"]=dataset.apply(lambda x: "EloFav" if x["Player 1"]==x["Elo Favourite"] else "EloDog",axis=1)
    #dataset["Elo Difference"]=dataset.apply(lambda x: abs(x["Elo_Player1"]-x["Elo_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["Elo_Player2"]-x["Elo_Player1"]) ,axis=1)
    #dataset["Elo Difference Clay"]=dataset.apply(lambda x: abs(x["cElo_Player1"]-x["cElo_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["cElo_Player2"]-x["cElo_Player1"]) ,axis=1)
    #dataset["Elo Difference Hard"]=dataset.apply(lambda x: abs(x["hElo_Player1"]-x["hElo_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["hElo_Player2"]-x["hElo_Player1"]) ,axis=1)
    #dataset["RankDiff"]=dataset.apply(lambda x: abs(x["Rank_Player1"]-x["Rank_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["Rank_Player2"]-x["Rank_Player1"]) ,axis=1)

    #for col in dataset.columns:
    #    print(col)

    dataset["Winner"]=dataset["Player 1"]
    dataset["Elo Favourite"]="EloFav"
    dataset["OddsDifference"]=abs(dataset["Odds"]-dataset["EstOdds"])
    dataset["OddsDifferenceClay"]=abs(dataset["Odds"]-dataset["EstOddsClay"])

    prediction["Player 1"]=dataset.apply(lambda x: "EloFav" if x["Player 1"]==x["Elo Favourite"] else "EloDog",axis=1)
    prediction["Elo Favourite"]="EloFav"
    prediction["OddsDifference"]=abs(prediction["Odds"]-prediction["EstOdds"])
    prediction["OddsDifferenceClay"]=abs(prediction["Odds"]-prediction["EstOddsClay"])

    prediction["Elo Difference"]=pd.to_numeric(prediction["Elo Difference"])
    prediction["Elo Difference Clay"]=pd.to_numeric(prediction["Elo Difference Clay"])
    prediction["Elo Difference Hard"]=pd.to_numeric(prediction["Elo Difference Hard"])
    prediction["Elo Difference"]=abs(prediction["Elo Difference"])
    prediction["Elo Difference Clay"]=abs(prediction["Elo Difference Clay"])
    prediction["Elo Difference Hard"]=abs(prediction["Elo Difference Hard"])
    prediction["RankDiff"]=abs(prediction["RankDiff"])

    #print(prediction)
    #print(dataset["RankDiff"])
    #dataset=dataset.drop(columns=['EstOddsClay','EstOdds','Odds',\
    #    'Player 1','Elo_Player1','Elo_Player2','cElo_Player1','cElo_Player2','gElo_Player1','gElo_Player2','hElo_Player1','hElo_Player2','Rank_Player1','Rank_Player2'])
    #dataset=dataset.drop(columns=['Elo Difference','Elo Difference Clay','Elo Difference Hard','RankDiff'])
    #dataset=dataset.drop(columns=['Elo Difference','Elo Difference Clay','Elo Difference Hard'])
    prediction=prediction.drop(columns=['Player 1','EstOddsClay','EstOdds','Odds'])
    #prediction=prediction.drop(columns=['Elo Difference','Elo Difference Clay','Elo Difference Hard'])
    #prediction=prediction.drop(columns=['Elo Difference Clay','Elo Difference Hard'])

    final_result= pd.get_dummies(dataset, prefix=['Elo Favourite'], columns=['Elo Favourite'])
    prediction_final=pd.get_dummies(prediction, prefix=['Elo Favourite'], columns=['Elo Favourite'])

    if Surface == 'Clay':
        final_result=dataset[["Winner","Elo Difference Clay","Elo Difference"]]
        prediction_final=prediction[["Elo Difference Clay","Elo Difference"]]
    if Surface == 'Hard':
        final_result=dataset[["Winner","Elo Difference Hard","Elo Difference"]]
        prediction_final=prediction[["Elo Difference Hard","Elo Difference"]]

    X=final_result.drop(['Winner'],axis=1)
    y=final_result['Winner']
    X_train, X_test, y_train, y_test=train_test_split(X,y,test_size=25)
    model=LogisticRegression(max_iter=100000000)
    model2=SVC()
    check1=len(np.unique(X_train))
    check2=len(np.unique(y_train))
    if check1 <2 or check2 < 2:
        return 0,''
    model2.fit(X_train,y_train)
    model.fit(X_train,y_train)
    train_score=model.score(X_train,y_train)
    train_score2=model2.score(X_train,y_train)
    test_score2=model2.score(X_test,y_test)
    test_score=model.score(X_test,y_test)

    #print('')
    #print('#########################')  
    #print(" Training accuracy: {:.0%}".format(train_score))
    #print(" Testing accuracy:  {:.0%}".format(test_score))
    #print('#########################')
    if len(prediction1) ==0:
        return 0,''    
    pred=model.predict(prediction_final)
    pred2=model2.predict(prediction_final)
    cols=["Prediction","Elo Favourite","Player1","Odds"]
    df=pd.DataFrame(columns=cols)
    List=[]
    for index,tuples in prediction1.iterrows():
        if index<len(prediction1):

            values=[pred2[index],prediction1["Elo Favourite"][index],prediction1["Player 1"][index],prediction1["Odds"][index]]
            zipped = zip(cols, values)
            a_dictionary = dict(zipped)
        # print(a_dictionary)
            List.append(a_dictionary)
            #print(pred[index],",",prediction1["Elo Favourite"][index],",",prediction1["Player 1"][index],",",prediction1["Odds"][index]) 
    df=df.append(List,True)
    #df=df[df["Odds"].ge(1.85)|df["Odds"].le(1.2)]
    #df=df[(df["Odds"].gt(1.11)&df["Odds"].le(1.2))|df["Odds"].ge(1.85)]
    df=df[df["Prediction"]=="EloFav"]
    players=[]
    if train_score2>0.7 and test_score2>0.7:
        #print('')
        #print('              {}'.format(Surface))
        #print('************************************')
        #print(df[["Prediction","Elo Favourite","Odds"]].to_string(index=False))
        #df.to_excel("today.xlsx")
        #print('************************************')
        #print('')
        for player in df['Elo Favourite']:
            #print(player)
            players.append(player)
        counting=counting+1
        return 1,players 
    else:
        return 0,''   

counting=0
players1=[]
for x in range(1,1000):
    pl=ML(1.5,1.6,'Clay')[1]
    players1.append(pl)
flat_list = [item for sublist in players1 for item in sublist]
print(Counter(flat_list),counting)

counting=0
players1=[]
for x in range(1,1000):
    p1=ML(1.5,1.6,'Hard')[1]
    players1.append(p1)
flat_list = [item for sublist in players1 for item in sublist]
print(Counter(flat_list),counting)

counting=0
players1=[]
for x in range(1,1000):
    p1=ML(1.15,1.3,'Clay')[1]
    players1.append(p1)
flat_list = [item for sublist in players1 for item in sublist]
print(Counter(flat_list),counting)

counting=0
players1=[]
for x in range(1,1000):
    p1=ML(1.15,1.3,'Hard')[1]
    players1.append(p1)
flat_list = [item for sublist in players1 for item in sublist]
print(Counter(flat_list),counting)