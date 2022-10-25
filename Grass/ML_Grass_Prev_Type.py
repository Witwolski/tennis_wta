import datetime
from random import seed
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
from elotable_grass import GetElo
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

username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database)
devengine = create_engine(devconnection_uri)

def ML_Prev(Surface,Date):
    dataset=pd.read_sql_query("Select [Player 1],[Elo Favourite],[Estimated Odds grass] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference grass], [Elo Difference Hard],RankDiff FROM Bets_yesterday_grass where Surface  like '{}'\
        and [Estimated Odds] >1 and date not  like '202252x%'  --and [Actual Odds] > 1.85 and [Actual Odds] > [Estimated Odds]\
            and [Actual Odds] > [Estimated Odds {}]".format(Surface,Surface),con=devengine)

    prediction=pd.read_sql_query("Select distinct [Player 1],[Elo Favourite],[Estimated Odds grass] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference grass], [Elo Difference Hard],RankDiff FROM Bets_yesterday_grass where Surface  like '{}'\
        and [Estimated Odds] >1 and date  like '{}%'  --and [Actual Odds] > 1.85 and [Actual Odds] > [Estimated Odds]\
            and [Actual Odds] > [Estimated Odds {}]".format(Surface,Date,Surface),con=devengine)
    prediction1=pd.read_sql_query("Select distinct [Player 1],[Elo Favourite],[Estimated Odds grass] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference grass], [Elo Difference Hard],RankDiff FROM Bets_yesterday_grass where Surface  like '{}'\
         and [Estimated Odds] >1 and date  like '{}%' --and [Actual Odds] > 1.85 and [Actual Odds] > [Estimated Odds]\
             and [Actual Odds] > [Estimated Odds {}]".format(Surface,Date,Surface),con=devengine)
    dataset=dataset.dropna()
    prediction=prediction.dropna()
    prediction1=prediction1.dropna()

    dataset["Player 1"]=dataset.apply(lambda x: "EloFav" if x["Player 1"]==x["Elo Favourite"] else "EloDog",axis=1)
    #dataset["Elo Difference"]=dataset.apply(lambda x: abs(x["Elo_Player1"]-x["Elo_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["Elo_Player2"]-x["Elo_Player1"]) ,axis=1)
    #dataset["Elo Difference grass"]=dataset.apply(lambda x: abs(x["cElo_Player1"]-x["cElo_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["cElo_Player2"]-x["cElo_Player1"]) ,axis=1)
    #dataset["Elo Difference Hard"]=dataset.apply(lambda x: abs(x["hElo_Player1"]-x["hElo_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["hElo_Player2"]-x["hElo_Player1"]) ,axis=1)
    #dataset["RankDiff"]=dataset.apply(lambda x: (x["Rank_Player1"]-x["Rank_Player2"]) if x["Player 1"]==x["Elo Favourite"] else (x["Rank_Player2"]-x["Rank_Player1"]) ,axis=1)

    if len(prediction1) ==0:
        return None

    dataset["Winner"]=dataset["Player 1"]
    dataset["Elo Favourite"]="EloFav"
    dataset["OddsDifference"]=abs(dataset["Odds"]-dataset["EstOdds"])
    dataset["OddsDifferenceClay"]=abs(dataset["Odds"]-dataset["EstOddsClay"])

    prediction["Player 1"]=dataset.apply(lambda x: "EloFav" if x["Player 1"]==x["Elo Favourite"] else "EloDog",axis=1)
    prediction["Elo Favourite"]="EloFav"
    prediction["OddsDifference"]=abs(prediction["Odds"]-prediction["EstOdds"])
    prediction["OddsDifferenceClay"]=abs(prediction["Odds"]-prediction["EstOddsClay"])

    prediction["Elo Difference"]=pd.to_numeric(prediction["Elo Difference"])
    prediction["Elo Difference grass"]=pd.to_numeric(prediction["Elo Difference grass"])
    prediction["Elo Difference Hard"]=pd.to_numeric(prediction["Elo Difference Hard"])
    prediction["Elo Difference"]=abs(prediction["Elo Difference"])
    prediction["Elo Difference grass"]=abs(prediction["Elo Difference grass"])
    prediction["Elo Difference Hard"]=abs(prediction["Elo Difference Hard"])
    #prediction["RankDiff"]=abs(prediction["RankDiff"])
    '''
    dataset=dataset[dataset["Odds"].ge(1.9)]
    prediction=prediction[prediction["Odds"].ge(1.9)]
    prediction1=prediction1[prediction1["Odds"].ge(1.9)]
    '''
    #print(dataset["RankDiff"])
    #dataset=dataset.drop(columns=['EstOddsClay','EstOdds',\
    #    'Player 1','Elo_Player1','Elo_Player2','cElo_Player1','cElo_Player2','gElo_Player1','gElo_Player2','hElo_Player1','hElo_Player2','Rank_Player1','Rank_Player2'])
    #dataset=dataset.drop(columns=['Elo Difference','Elo Difference grass','Elo Difference Hard','RankDiff'])
    #dataset=dataset.drop(columns=['Elo Difference','Elo Difference grass','Elo Difference Hard'])
    prediction=prediction.drop(columns=['Player 1','EstOddsClay','EstOdds'])
    #prediction=prediction.drop(columns=['Elo Difference','Elo Difference grass','Elo Difference Hard'])
    #prediction=prediction.drop(columns=['Elo Difference grass','Elo Difference Hard'])

    #final_result= pd.get_dummies(dataset, prefix=['Elo Favourite'], columns=['Elo Favourite'])
    #prediction_final=pd.get_dummies(prediction, prefix=['Elo Favourite'], columns=['Elo Favourite'])
    if Surface == 'grass':
        final_result=dataset[["Winner","Elo Difference grass","Elo Difference"]]
        prediction_final=prediction[["Elo Difference grass","Elo Difference"]]
    if Surface == 'grass':
        final_result=dataset[["Winner","Elo Difference"]]
        prediction_final=prediction[["Elo Difference"]]
    #final_result=final_result.drop(columns=['Surface_Hard'])

    X=final_result.drop(['Winner'],axis=1)
    y=final_result['Winner']
    X_train, X_test, y_train, y_test=train_test_split(X,y)
    
    model=LogisticRegression(max_iter=100000000000000)
    model2=SVC()
    model2.fit(X_train,y_train)
    model.fit(X_train,y_train)
    train_score=model.score(X_train,y_train)
    train_score2=model2.score(X_train,y_train)
    test_score2=model2.score(X_test,y_test)
    test_score=model.score(X_test,y_test)
    '''
    print("Training accuracy: ",train_score)
    print("Training accuracy2: ",train_score2)
    print("Testing accuracy: ",test_score)
    print("Testing accuracy2: ",test_score2)
    '''
    if test_score2 > 0 and test_score2 > 0:
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
        df=df[df["Odds"].ge(1.85)]
        #df=df[(df["Odds"].gt(1.11)&df["Odds"].le(1.2))|df["Odds"].ge(1.85)]
        #df=df[df["Odds"].le(1.9)]
        #print(df)
        df=df[df["Prediction"]=="EloFav"]
        countbets=len(df)
        Stake=100
        df["Profit"]=df.apply(lambda x: -Stake if x["Elo Favourite"]!=x["Player1"] else (x["Odds"]*Stake)-Stake,axis=1)
        df.loc['Profit']= df.sum(axis=0)
        #dates=prediction=pd.read_sql_query("Select distinct Date FROM Bets_yesterday where date  like '%'",con=devengine)
        #print(df[["Prediction","Elo Favourite","Odds","Profit"]].to_string(index=False))
        #print(df)
        print("{}   ${} Profit in {} bets".format(Surface,df["Profit"].iloc[-1],countbets))
        df.to_excel("YD.xlsx")
        return df["Profit"].iloc[-1]
    #df.to_excel("YD.xlsx")
for x in range(1,100):
    Date='2022'
    #profit1=ML_Prev('Hard',Date)
    profit2=ML_Prev('grass',Date)
    #print(profit1+profit2)