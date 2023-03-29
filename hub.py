import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import numpy as np
import re
import dataframe_image as dfi

import tweepy 
from twitter_secrets import twitter_secrets as ts
from shot_map_mvp import plot

consumer_key = ts.CONSUMER_KEY
consumer_secret = ts.CONSUMER_SECRET
access_token = ts.ACCESS_TOKEN
access_secret = ts.ACCESS_SECRET

#authenticating to access the twitter API
auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_secret)
api=tweepy.API(auth)

# shotMap('https://understat.com/match/18221')

class Hub:
    def __init__(self, match_id):
        self.match_id = match_id
        
        self.url = f'https://understat.com/match/{match_id}'
        self.request = requests.get(self.url)
        self.soup = BeautifulSoup(self.request.content,'lxml')
        self.scripts = self.soup.find_all('script')

        self.title, self.score, self.date = scrape_title(self.soup)
        self.home_name, self.away_name = scrape_teams(self.title)

        self.home_player_stats, self.away_player_stats = scrape_player_data(self.scripts)
        self.home_player_image = style_player_data(self.home_player_stats, self.home_name)
        self.away_player_image = style_player_data(self.away_player_stats, self.away_name)

        self.home_shotmap_data, self.away_shotmap_data = scrape_shotmap_data(self.scripts)
        self.home_shotmap_image, self.home_goals, self.home_total_shots, self.home_xGcum, self.home_xG_per_shot = plot(self.home_shotmap_data, self.home_name)
        self.away_shotmap_image, self.away_goals, self.away_total_shots, self.away_xGcum, self.away_xG_per_shot = plot(self.away_shotmap_data, self.away_name) 

def scrape_title(soup):
    title = str(soup.find('title'))
    for excess in ['<title>', ' | xG | Understat.com</']:
        title = title.strip(excess)
        split_title = title.split(' (')

        score = split_title[0]
        date = '(' + split_title[1]

    return title, score, date

def scrape_teams(title):
    end = title.index(' (')
    score = title[:end]
    teams = re.split('\s\d+\s-\s\d+\s',score)
    home = teams[0]
    away = teams[1]

    return home, away


def format_player_data(data):
    data = data.T
    player_data = data[['player', 'position', 'time', 'goals', 'assists', 'key_passes', 'xG', 'xA']]

    return player_data

def scrape_player_data(scripts):
    strings = scripts[2].string
    ind_start = strings.index("('")+2 
    ind_end = strings.index("')") 
    json_data = strings[ind_start:ind_end] 
    json_data = json_data.encode('utf8').decode('unicode_escape')
    data = json.loads(json_data)

    home_players = format_player_data(pd.DataFrame(data['h']))
    away_players = format_player_data(pd.DataFrame(data['a']))

    return home_players, away_players

def format_numeric(val):
    if isinstance(val, (int, float)):
        return '{:.2f}'.format(val)
    else:
        return val

def style_player_data(data, team_name):
    stats = data[['player', 'position', 'time', 'goals', 'assists', 'key_passes', 'xG', 'xA']]
    stats.columns = stats.columns.str.title()
    stats.rename(columns={'Key_Passes' : 'Key Passes'}, inplace=True)
    stats.rename(columns={'Xg' : 'xG'}, inplace=True)
    stats.rename(columns={'Xa' : 'xA'}, inplace=True)

    stats['xG'] = pd.to_numeric(stats['xG'])
    stats['xA'] = pd.to_numeric(stats['xA'])

    stats['xG'] = stats['xG'].round(2)
    stats['xA'] = stats['xA'].round(2)


    subset = pd.IndexSlice[:, pd.Index([col for col in stats.columns if stats[col].dtype in [np.float64, np.int64]])]

    table = stats.style.format(subset=subset, formatter={col:format_numeric for col in subset[1]}).set_table_styles(
                [
                    {'selector': 'th',
                    'props': [('background', '#34b1eb'),
                    ('font-family', 'verdana')]},

                    {'selector': 'td',
                    'props': [('font-family', 'verdana')]},

                    {'selector': 'tr:nth-of-type(odd)',
                    'props': [('background', '#DCDCDC')]},

                    {'selector': 'tr:nth-of-type(even)',
                    'props': [('background', 'white')]},
                    ]
                    ).hide_index()

    image_name = f'{team_name}.png'
    dfi.export(table, image_name)

    return image_name

def scrape_shotmap_data(scripts):
    strings = scripts[1].string
    ind_start = strings.index("('")+2 
    ind_end = strings.index("')") 
    json_data = strings[ind_start:ind_end] 
    json_data = json_data.encode('utf8').decode('unicode_escape')
    data = json.loads(json_data)

    home = pd.DataFrame(data['h'])
    away = pd.DataFrame(data['a'])

    return home, away

                
for i in range(18010, 18011):
    id = str(i)
    g = Hub(id)
    
    orig = f'{g.home_name} ({g.home_xGcum}) {g.home_goals}-{g.away_goals} ({g.away_xGcum}) {g.away_name}\n{g.date}\n(Statistics by stat_alert | @tom_cannonnn)\nTHREAD'
    r1 = f'{g.home_name} Shot Map: \nGoals: {g.home_goals} \nShots: {g.home_total_shots} \nxG: {g.home_xGcum} \nxG per Shot: {g.home_xG_per_shot}'
    r2 = f'{g.away_name} Shot Map: \nGoals: {g.away_goals} \nShots: {g.away_total_shots} \nxG: {g.away_xGcum} \nxG per Shot: {g.away_xG_per_shot}'
    r3 = f'{g.home_name} Player Stats:'
    r4 = f'{g.away_name} Player Stats:'

    ret1 = api.media_upload(g.home_shotmap_image)
    ret2 = api.media_upload(g.away_shotmap_image)
    ret3 = api.media_upload(g.home_player_image)
    ret4 = api.media_upload(g.away_player_image)

    original_tweet = api.update_status(status=orig)

    reply1_tweet = api.update_status(media_ids=[ret1.media_id_string], 
                    status = r1,
                    in_reply_to_status_id=original_tweet.id,
                    auto_populate_reply_metadata=True)

    reply2_tweet = api.update_status(media_ids=[ret2.media_id_string], 
                    status = r2,
                    in_reply_to_status_id=reply1_tweet.id,
                    auto_populate_reply_metadata=True)

    reply3_tweet = api.update_status(media_ids=[ret3.media_id_string], 
                    status = r3,
                    in_reply_to_status_id=reply2_tweet.id,
                    auto_populate_reply_metadata=True)

    reply4_tweet = api.update_status(media_ids=[ret4.media_id_string], 
                    status = r4,
                    in_reply_to_status_id=reply3_tweet.id,
                    auto_populate_reply_metadata=True)