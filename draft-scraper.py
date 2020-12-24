'''
Credit: Savvas Tjortjoglou
http://savvastjortjoglou.com/nfl-draft.html#Additional-Resources
https://github.com/savvastj/nfl_draft.git
'''

import pandas as pd 
from urllib.request import urlopen
from bs4 import BeautifulSoup

url_2010 = "http://www.pro-football-reference.com/years/2010/draft.htm"

# get the html
html = urlopen(url_2010)

# create the BeautifulSoup object
soup = BeautifulSoup(html, "lxml")

# Extract the necessary values for the column headers from the table
# and store them as a list
column_headers = [th.getText() for th in 
                  soup.findAll('tr', limit=2)[1].findAll('th')]

# Add the two additional column headers for the player links
column_headers.extend(["Player_NFL_Link", "Player_NCAA_Link"])

# The data is found within the table rows of the element with id=draft
# We want the elements from the 3rd row and on
table_rows = soup.select("#drafts tr")[2:]

def extract_player_data(table_rows):
    """
    Extract and return the the desired information from the td elements within
    the table rows.
    """
    # create the empty list to store the player data
    player_data = []
    
    for row in table_rows:  # for each row do the following

        # Get the text for each table data (td) element in the row
        # Some player names end with ' HOF', if they do, get the text excluding
        # those last 4 characters,
        # otherwise get all the text data from the table data
        player_list = [td.get_text() for td in row.find_all("th")]
        player_list.extend([td.get_text() for td in row.find_all("td")])

        # there are some empty table rows, which are the repeated 
        # column headers in the table
        # we skip over those rows and and continue the for loop
        if not player_list:
            continue

        # Extracting the player links
        # Instead of a list we create a dictionary, this way we can easily
        # match the player name with their pfr url
        # For all "a" elements in the row, get the text
        # NOTE: Same " HOF" text issue as the player_list above
        links_dict = {(link.get_text()[:-4]   # exclude the last 4 characters
                       if link.get_text().endswith(" HOF")  # if they are " HOF"
                       # else get all text, set thet as the dictionary key 
                       # and set the url as the value
                       else link.get_text()) : link["href"] 
                       for link in row.find_all("a", href=True)}

        # The data we want from the dictionary can be extracted using the
        # player's name, which returns us their pfr url, and "College Stats"
        # which returns us their college stats page
    
        # add the link associated to the player's pro-football-reference page, 
        # or en empty string if there is no link
        player_list.append(links_dict.get(player_list[3], ""))

        # add the link for the player's college stats or an empty string
        # if ther is no link
        player_list.append(links_dict.get("College Stats", ""))

        # Now append the data to list of data
        player_data.append(player_list)
        
    return player_data

####

# Create an empty list that will contain all the dataframes
# (one dataframe for each draft)
draft_dfs_list = []

# a list to store any errors that may come up while scraping
errors_list = []

# The url template that we pass in the draft year inro
url_template = "http://www.pro-football-reference.com/years/{year}/draft.htm"

def scrape_years(start=2000, end=2016):
    years = range(start, end)
    # for each year from 2010-2016
    for year in years: 
        
        # Use try/except block to catch and inspect any urls that cause an error
        try:
            # get the draft url
            url = url_template.format(year=year)

            # get the html
            html = urlopen(url)

            # create the BeautifulSoup object
            soup = BeautifulSoup(html, "lxml") 

            # get the column headers
            column_headers = [th.getText() for th in 
                            soup.findAll('tr', limit=2)[1].findAll('th')]
            column_headers.extend(["Player_NFL_Link", "Player_NCAA_Link"])

            # select the data from the table using the '#drafts tr' CSS selector
            table_rows = soup.select("#drafts tr")[2:] 

            # extract the player data from the table rows
            player_data = extract_player_data(table_rows)

            # create the dataframe for the current years draft
            year_df = pd.DataFrame(player_data, columns=column_headers)

            # if it is a draft from before 1994 then add a Tkl column at the 
            # 24th position
            if year < 1994:
                year_df.insert(24, "Tkl", "")

            # add the year of the draft to the dataframe
            year_df.insert(0, "Draft_Yr", year)

            # append the current dataframe to the list of dataframes
            draft_dfs_list.append(year_df)
        
        except Exception as e:
            # Store the url and the error it causes in a list
            error =[url, e] 
            # then append it to the list of errors
            errors_list.append(error)
    
    print(f'Errors During Scraping: {len(errors_list)}')
    draft_df = pd.concat(draft_dfs_list, ignore_index=True)
    return draft_df

draft_df = scrape_years(start=2000, end=2016)

# filter out positions other than Quarterback
def select_qbs():
    df_qbs = draft_df[draft_df['Pos'] == 'QB']
    df_qbs = df_qbs.reset_index(drop=True)
    return df_qbs

df_qbs = select_qbs()

# select only relevant rows
rows = ['Draft_Yr', 'Rnd', 'Pick', 'Tm', 'Player', 'Pos', 'Age', 'To', 'St', 'G', 'College/Univ', 'Player_NFL_Link', 'Player_NCAA_Link']
df_qbs = df_qbs[rows]

# save the data as a csv in the data folder 
def save(filename): 
    try:
        df_qbs.to_csv(f'data/{filename}.csv')
    except:
        print("Error saving as a CSV")

    print("Scraper Complete")

save(filename = 'draft_qbs_2000-2015')