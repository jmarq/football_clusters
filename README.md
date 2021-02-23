# K-Means clustering of NFL player stats

A few years ago I wrote some code to download player stats from the wonderful pro-football-reference.com, and run the data through a basic un-supervised clustering algorithm, to see which player rows were deemed "similar".

Here is that code in all its unpolished glory.

Main requirements are `requests` and `beautifulsoup4` for downloading/parsing stats page, and `numpy` and `scikit-learn` for data cleaning and clustering.

Written for `python3`

once dependencies are installed (perhaps use a virtualenv and pip install from requirements.txt):

## Downloading stats
- `python football_reference.py` to download/parse stats from 2020 season (given that PFR hasn't changed their html formatting), resulting in a json file.
- Be respectful with your automated downloads. Don't hammer the site! Give credit if using their data.

## Using the clustering script
- `python cluster_players.py` to print out the resulting cluster information.
- You can pass `python cluster_players.py -p POSITION` aka `-p QB`, `-p RB` to only cluster certain positions.
- You can pass `python cluster_players.py -n NUM_CLUSTERS` aka `-n 10` to generate a specified number of clusters
- Certain stats are ignored by the clustering algorithm by default. You can pass the column name to `python cluster_players.py -i COL_NAME` to include the column when clustering. For example, `python cluster_players.py -i age`
