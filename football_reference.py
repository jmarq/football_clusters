from bs4 import BeautifulSoup as Soup
import requests
import json
import datetime

outfilename = "football_reference_2020.json"

# http GET request, grab the stats page
page = requests.get("https://www.pro-football-reference.com/years/2020/fantasy.htm").text

# construct html parser
soup = Soup(page,"html.parser")

# .find is pretty much like a CSS selector. Having inspected the page, I know I want the first table element.
table = soup.find("table")

# there are some rows I'm not interested in. How to filter these out? find the COLUMNS i'm interested in, and get the parent.
player_cells = table.select("td[data-stat=player]")
player_rows = list(map(lambda d: d.parent, player_cells))
del player_cells
print(len(player_rows))


# turn a table row into a hash of stat names/values
def tr_to_dict(row):
    stat_cells = row.select("td[data-stat]");
    player_dict = {}
    # go through each column and create its entry in the hash
    for cell in stat_cells:
        stat = cell.get("data-stat")
        stat_value = cell.text
        if(stat not in ['team', 'player', 'fantasy_pos']):
            # some basic data cleaning: if there's no value, let's just call it zero, instead of crashing our program with nulls
            if not stat_value:
                stat_value = 0
            stat_value = float(stat_value)
        player_dict[stat] = stat_value
    return player_dict

player_dicts = list(map(tr_to_dict, player_rows))
output_object = {
  "created": datetime.datetime.now().strftime("%m/%d/%Y %T%p"),
  "players": player_dicts
}
players_json = json.dumps(output_object)
# write the resulting json array to our speficied data file
outfile = open(outfilename,'w')
outfile.write(players_json)
outfile.close()
# profit
