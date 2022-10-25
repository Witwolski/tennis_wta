import functools, json
from requests_html import AsyncHTMLSession, HTMLSession
import pandas as pd
from sqlalchemy import create_engine

devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")


async def async_get(url):
    replace_url = url.replace("overview", "player-stats")
    r = await Pool.get(replace_url, headers={"user-agent": ""})
    name = r.html.find(".player-profile-hero-name", first=True).text.replace("\n", " ")
    for row in r.html.find(".mega-table")[:-1]:
        service_games = row.find("td")[17].text
    for row in r.html.find(".mega-table"):
        return_games = row.find("td")[11].text
    return {
        "Name": name,
        **{
            "Service Games Won": service_games.replace("%", ""),
            "Return Games Won": return_games.replace("%", ""),
        },
    }


url = "https://www.atptour.com/en/rankings/singles?rankRange=0-900&rankDate=2022-07-18"

r = HTMLSession().get(url, headers={"user-agent": ""})
url_list = []
for tag in r.html.find(".player-cell-wrapper"):
    if len(tag.absolute_links) > 1:
        temp = list(tag.absolute_links)
        if "topcourt" in temp[0]:
            url_list.append(temp[1])
        else:
            url_list.append(temp[0])

    else:
        poo = list(tag.absolute_links)
        url_list.append(poo[0])

Pool = AsyncHTMLSession()

results = Pool.run(*(functools.partial(async_get, tag) for tag in url_list))
serve_return_stats = pd.read_json(json.dumps(results, indent=2))
todays_matches = pd.read_sql_query(
    "Select Player_1, Player_2, Player_1_Odds, Player_2_Odds from TodaysMatches",
    con=devengine,
)
combine = pd.merge(
    todays_matches, serve_return_stats, how="left", left_on="Player_1", right_on="Name"
)
combine2 = pd.merge(
    combine, serve_return_stats, how="left", left_on="Player_2", right_on="Name"
)
combine2[["Service Games Won_x", "Service Games Won_y"]] = combine2[
    ["Service Games Won_x", "Service Games Won_y"]
].astype(float)
filter_serve = combine2[
    (
        ((combine2["Service Games Won_x"]).ge(75))
        & ((combine2["Service Games Won_y"]).ge(1))
    )
    | (
        ((combine2["Service Games Won_y"]).ge(75))
        & ((combine2["Service Games Won_x"]).ge(1))
    )
]
filter_serve.to_excel("servers_today.xlsx", index=False)
