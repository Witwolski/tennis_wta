import datetime
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


def Main(url, current_date, suffix, check):

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0)

    args = parser.parse_args()
    response = requests.get(url)

    # # Analysis with beautifulsoup
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find("table", {"class": "result"})
    table = soup.findAll("table", {"class": "result"})[1]
    if(check == 1):
        table = soup.find("table", {"class": "result"})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    tournament_idx_lst = []
    for i, row in enumerate(rows):
        if '<tr class="head flags">' in str(row):
            t_name = row.find("td", {"class": "t-name"}).text
            tournament_idx_lst.append(i)

    tournament_idx_lst.append(len(rows))

    def getPlayersFullName(playerUrl):
        player_url = 'https://www.tennisexplorer.com' + playerUrl
        player_response = requests.get(player_url)
        player_soup = BeautifulSoup(player_response.content, 'html.parser')
        player_table = player_soup.find("table", {"class": "plDetail"})
        player_table_body = player_table.find('tbody')
        try:
            player_rank = player_table_body.text.split(
                'Current/Highest rank - singles: ')[1].split(".")[0]
            if '-' in player_rank:
                player_rank = "10000"
        except:
            player_rank = "10000"
        try:
            player_hand = player_table_body.text.split(
                'Plays: ')[1].split(".")[0]
        except:
            player_hand = 'right'
        player_name = player_table_body.find_all('h3')
        name = ' '.join(player_name[0].text.split())
        splitname = name.split(' ')
        first_name = splitname[-1]
        last_name = name.replace(' '+first_name, '')
        name = first_name + ' ' + last_name
        name = name.replace('Carlos Alcaraz Garfia','Carlos Alcaraz').replace(
            'Lesya Tsurenko', 'Lesia Tsurenko').replace(
            'Harry Fritz Taylor', 'Taylor Fritz').replace(
                'Manuel Cerundolo Juan', "Juan Manuel Cerundolo").replace(
                    'Martin Etcheverry Tomas', 'Tomas Martin Etcheverry').replace(
                    'John Wolf Jeffrey', 'Jeffrey John Wolf').replace(
            'Victor Cornea Vlad', 'Vlad Victor Cornea').replace(
            'Cristian Jianu Filip', 'Filip Cristian Jianu').replace(
                'Pablo Ficovich Juan', 'Juan Pablo Ficovich').replace(
                    'Felipe Meligeni Rodrigues Alves', 'Felipe Meligeni Alves').replace(
                        'Hsin Tseng Chun', 'Chun Hsin Tseng').replace(
                    'Woo Kwon Soon', 'Soon Woo Kwon').replace(
                        'Moura Monteiro Thiago', 'Thiago Monteiro').replace(
                            'Viktoria Azarenka', 'Victoria Azarenka').replace(
                                'McHugh', 'Mchugh').replace(
                                    'Fco. Vidal Azorin Jose', 'Jose Fco Vidal Azorin').replace(
                                        'Bautista Torres Juan', 'Juan Bautista Torres').replace(
                                'Marco Moroni Gian', 'Gian Marco Moroni').replace(
                                    'Danielle Collins', 'Danielle Rose Collins').replace(
                                        'Pablo Varillas Juan', 'Juan Pablo Varillas').replace(
                                            'Sorana-Mihaela Cirstea', 'Sorana Cirstea').replace(
                                                'Mackenzie McDonald', 'Mackenzie Mcdonald').replace(
            'Irina Begu', 'Irina Camelia Begu').replace(
            'Adina Cristian Jaqueline', 'Jaqueline Adina Cristian').replace(
                'A. Stephens Sloane', 'Sloane Stephens').replace(
                    'Kenny de Schepper', 'Kenny De Schepper').replace(
                    'Matthieu Perchicot', 'Mathieu Perchicot').replace(
                        'Camila Osorio Serrano Maria', 'Camila Osorio').replace(
                            'Maria Bara Irina', 'Irina Maria Bara').replace(
                                'Milan Zekic', 'Miljan Zekic').replace(
                                    'Anna Schmiedlova Karolina', 'Anna Karolina Schmiedlova').replace(
                                        'Annie Fernandez Leylah', 'Leylah Annie Fernandez').replace(
                                            'Xinyu Wang', 'Xin Yu Wang').replace(
                                                'Ignacio Londero Juan','Juan Ignacio Londero'
                                            )
        return name.strip().replace('-', ' ') + '(' + player_rank + ')'

    tournament_dict = {
    }
    for i, item in enumerate(tournament_idx_lst[:-1]):

        tournament_name = rows[item].find("td", class_="t-name").text.strip()
        if 'Futures' not in tournament_name and \
            'ITF' not in tournament_name and \
            'UTR' not in tournament_name and \
            'Pro Series' not in tournament_name and \
                '' in tournament_name:
            print(tournament_name)
            tournament_url = rows[item].find(
                "td", class_="t-name").contents[0].attrs['href']
            tournament_url = 'https://www.tennisexplorer.com' + \
                tournament_url.replace("'", '')
            response = requests.get(tournament_url)

            # # Analysis with beautifulsoup
            soup = BeautifulSoup(response.content, 'html.parser')
            court_type = soup.find("div", {"id": "center"}).text.split('\n')[
                2].split(")")[0].split(",")[-2].strip()
            court_type = court_type.replace(
                "indoors", "Hard").replace('clay', 'Clay').replace('hard', 'Hard')
            if not 'Futures' in tournament_name:
                if not tournament_dict.get(tournament_name):
                    tournament_dict[tournament_name+str(item)] = {}
                    tournament_dict[tournament_name+str(item)][current_date] = []
                for c in range(item+1, tournament_idx_lst[i+1], 2):
                    tournament_dict[tournament_name+str(item)][current_date].append(getPlayersFullName(rows[c].find(
                        "td", class_="t-name").a['href']) + ' vs ' + getPlayersFullName(rows[c+1].find("td", class_="t-name").a['href']) + ":" + court_type)

    for key, value in tournament_dict.items():
        # print(value)
        datefilename = current_date.replace("-", "")

        with xlsxwriter.Workbook(r"C:\Users\chris\OneDrive\Desktop\Tennis\\" + key + datefilename + suffix + ".xlsx") as workbook:
            for i, date in value.items():
                for match in date:
                    match = match.split(':')[0]
                    players = match.split(' vs ')
                    player1 = players[0].split('(')[0]
                    player2 = players[1].split('(')[0]
                    

                    if ValidName(player2) == True and ValidName(player1)==True:
                        Elo_player1, Elo_player2,Fav,elo_diff,Prob,Odds=GetElo(player1,player2)


                        table = [['Sex', 'Tournament', 'Player 1', 'Player 1 Elo', 'Player 2', 'Player 2 Elo','Elo Favourite','Elo Difference','Elo Probability','Estimated Odds'], [
                                suffix.replace('_', ''), key, player1, Elo_player1, player2, Elo_player2,Fav,elo_diff,Prob,Odds]]
                            
                            #tab = tabulate(table, headers='firstrow')

                        worksheetname = player1.split(
                                ' ')[1] + '_' + player2.split(' ')[1]
                        worksheet = workbook.add_worksheet(worksheetname)
                        # Add a format to use wrap the cell text.
                        wrap = workbook.add_format({'text_wrap': True})

                        # Increase the row and cell height so the output is clearer.
                        worksheet.set_column('A:H',100)
                        #worksheet.set_row(0, 20)
                        #worksheet.set_row(1, 100)

                        for row_num, data in enumerate(table):
                            worksheet.write_row(row_num, 0, data, wrap)
        df = pd.concat(pd.read_excel(r"C:\Users\chris\OneDrive\Desktop\Tennis\\" +
                       key + datefilename + suffix + ".xlsx", sheet_name=None), ignore_index=True)
        df.to_excel(r"C:\Users\chris\OneDrive\Desktop\Tennis\\" +
                    key + datefilename + suffix + ".xlsx", index=False)


# # Get the current date
tomorrow = datetime.datetime.now() + datetime.timedelta(hours=-1)
year, month, day = tomorrow.year, tomorrow.month, tomorrow.day
current_date = str(year) + '-' + str(month) + '-' + str(day)
#print('https://www.tennisexplorer.com/matches/?type=atp-single&year={}&month={}&day={}'.format(year, month, day))

Main('https://www.tennisexplorer.com/matches/?type=atp-single&year={}&month={}&day={}'.format(year,
     month, day), current_date, "_Mens", 1)
Main('https://www.tennisexplorer.com/matches/?type=wta-single&year={}&month={}&day={}'.format(year,
     month, day), current_date, "_Womens", 1)

Main('https://www.tennisexplorer.com/matches/?type=atp-single&year={}&month={}&day={}'.format(year,
     month, day), current_date, "_Mens", 0)
Main('https://www.tennisexplorer.com/matches/?type=wta-single&year={}&month={}&day={}'.format(year,
     month, day), current_date, "_Womens", 0)
