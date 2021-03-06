# credit Reddit u/jpf5046

import pandas as pd

url_template = "http://www.pro-football-reference.com/years/{year}/draft.htm"

data = []
years = range(2010, 2016)

for year in years:
    df_list = pd.read_html(url_template.replace("{year}",str(year)), skiprows = 0)[0]
    data.append(df_list)
data = pd.concat(data)

# removing first row of multiheader
data.columns = data.columns.droplevel(0)

# remove all multiple headers
data = data[data.Player != 'Player']

# export to csv
filename = 'drafted_qbs_2010-2015'
data.to_csv(f'data/{filename}.csv')
print('Scraper successful')