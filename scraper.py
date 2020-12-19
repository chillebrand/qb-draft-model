# credit Reddit u/jpf5046

import pandas as pd

url_template = "http://www.pro-football-reference.com/years/{year}/draft.htm"

data = []

for year in range(2005, 2019):
    df_list = pd.read_html(url_template.replace("{year}",str(year)), skiprows = 0)[0]
    data.append(df_list)
data = pd.concat(data)

# removing first row of multiheader
data.columns = data.columns.droplevel(0)

# remove all multiple headers
data = data[data.Player != 'Player']

# export to csv
data.to_csv('draft.csv')