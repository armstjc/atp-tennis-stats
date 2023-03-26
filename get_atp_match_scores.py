from datetime import datetime
import time
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

def get_atp_singles_match_scores(year:int,save=False):
    matches_df = pd.DataFrame()
    row_df = pd.DataFrame()
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    
    print(f'\nGetting the ATP singles match scores for the {year} season.')

    sched_df = pd.read_csv(f'atp/tournament_schedules/annual/csv/{year}_atp_schedule.csv')
    sched_df = sched_df.dropna(subset=['tourney_url_suffix'])
    sched_urls_arr = sched_df['tourney_url_suffix'].to_list()
    tourney_ids_arr = sched_df['tourney_year_id'].to_list()
    tourney_order_arr = sched_df['tourney_order'].to_list()
    tourney_name_arr = sched_df['tourney_name'].to_list()
    tourney_slug_arr = sched_df['tourney_slug'].to_list()
    try:
        tourney_fin_commit_arr = sched_df['tourney_fin_commit'].to_list()
    except:
        tourney_fin_commit_arr = np.zeros(200)

    tourney_date_arr = sched_df['tourney_date'].to_list()

    for i in tqdm(range(0,len(sched_urls_arr))):
        print(f'\nOn tournament {i+1} of {len(sched_urls_arr)+1} for {year}.')
        tourney_year_id = tourney_ids_arr[i]
        tourney_order = tourney_order_arr[i]
        tourney_name = tourney_name_arr[i]
        tourney_slug = tourney_slug_arr[i]
        sched_url = sched_urls_arr[i]
        tourney_fin_commit = tourney_fin_commit_arr[i]

        url = f"https://www.atptour.com{sched_url}?matchType=singles"
        #print(url)
        print(f'\n{tourney_name}')
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text,features='lxml')
        
        time.sleep(0.5)

        try:
            scores_table = soup.find('table',{'class':'day-table'})
        except:
            print('Couldn\'t locate a scores table.')
            continue
        
        if scores_table == None:
            continue
        else:
            matches = scores_table.find_all('tbody')
            match_titles = scores_table.find_all('thead')

            try:
                tourney_dates = str(soup.find('span',{'class':'tourney-dates'}).text).replace('\r','').replace('\n','').replace(' ','')
                first_tourney_date,last_tourney_date = tourney_dates.split('-')
                first_tourney_date_year, first_tourney_date_month, first_tourney_date_day = first_tourney_date.split('.')
                last_tourney_date_year, last_tourney_date_month, last_tourney_date_day = last_tourney_date.split('.')
            
            except:
                first_tourney_date = tourney_date_arr[i]
                last_tourney_date = first_tourney_date
                first_tourney_date_year, first_tourney_date_month, first_tourney_date_day = first_tourney_date.split('/')
                last_tourney_date_year, last_tourney_date_month, last_tourney_date_day = last_tourney_date.split('/')

            round_order = 0
            for j in tqdm(range(0,len(matches))):
                round_order += 1
                match_order = 0

                for k in matches[j].find_all('tr'):
                    match_order += 1
                    match_content = k.find_all('td')

                    row_df = pd.DataFrame({
                            'tourney_year_id':tourney_year_id,
                            'tourney_order':tourney_order,
                            'tourney_name':tourney_name,
                            'tourney_slug':tourney_slug,
                            'tourney_url_suffix':sched_url,
                            'first_tourney_date':first_tourney_date,
                            'first_tourney_date_year':first_tourney_date_year,
                            'first_tourney_date_month':first_tourney_date_month,
                            'first_tourney_date_day':first_tourney_date_day,
                            'last_tourney_date':last_tourney_date,
                            'last_tourney_date_year':last_tourney_date_year,
                            'last_tourney_date_month':last_tourney_date_month,
                            'last_tourney_date_day':last_tourney_date_day,
                            'tourney_fin_commit':tourney_fin_commit,
                            'tourney_year':year
                        },
                        index=[0]
                    )

                    row_df['tourney_round_name'] = match_titles[j].find('th').text
                    row_df['round_order'] = round_order
                    row_df['match_order'] = match_order
                    
                    try:
                        row_df['winner_seed'] = str(match_content[0].find('span').text).replace('\r','').replace('\n','').replace(' ','')
                    except:
                        row_df['winner_seed'] = None

                    try:
                        row_df['winner_nationality'] = match_content[1].find('img').get('alt')
                    except:
                        row_df['winner_nationality'] = None

                    row_df['winner_name'] = str(match_content[2].text).replace('\r','').replace('\n','').replace('  ','')

                    try:
                        row_df['winner_player_id'] = str(match_content[2].find('a').get('href')).split('/')[3]
                    except:
                        row_df['winner_player_id'] = None
                    
                    try:
                        winner_slug = str(match_content[2].find('a').get('href')).split('/')[4]
                        row_df['winner_slug'] = winner_slug
                        #del winner_slug
                    except:
                        winner_slug = ''
                        row_df['winner_slug'] = winner_slug

                    try:
                        row_df['loser_seed'] = str(match_content[4].find('span').text).replace('\r','').replace('\n','').replace(' ','')
                    except:
                        row_df['loser_seed'] = None

                    try:
                        row_df['loser_nationality'] = match_content[5].find('img').get('alt')
                    except:
                        row_df['loser_nationality'] = None
                    
                    row_df['loser_name'] = str(match_content[6].text).replace('\r','').replace('\n','').replace('  ','')
                    
                    try:
                        row_df['loser_player_id'] = str(match_content[6].find('a').get('href')).split('/')[3]
                    except:
                        row_df['loser_player_id'] = None

                    
                    try:
                        loser_slug = str(match_content[6].find('a').get('href')).split('/')[4]
                        row_df['loser_slug'] = loser_slug
                        
                    except:
                        loser_slug = ''
                        row_df['loser_slug'] = loser_slug

                    match_score = str(match_content[7].text).replace('\r','').replace('\n','').replace('    ','')
                    row_df['match_score_tiebreaks'] = match_score
                    row_df['winner_sets_won'] = 0
                    row_df['loser_sets_won'] = 0
                    row_df['winner_games_won'] = 0
                    row_df['loser_games_won'] = 0
                    row_df['winner_tiebreaks_won'] = 0
                    row_df['loser_tiebreaks_won'] = 0
                    row_df['match_id'] = f'{tourney_year_id}-{winner_slug}-{loser_slug}'
                    del winner_slug, loser_slug
                    try:
                        row_df['match_stats_url_suffix'] = match_content[7].find('a').get('href')
                    except:
                        row_df['match_stats_url_suffix'] = None

                    match_games = match_score.split(' ')

                    for x in match_games:
                        try:
                            if x == '(RET)':
                                w_score = 0
                                l_score = 0
                            else:
                                w_score = int(x[0])
                                l_score = int(x[1])
                        except:
                            #print(f'\nNo score can be extracted from {x}.')
                            continue

                        if w_score > l_score:
                            row_df['winner_sets_won'] = row_df['winner_sets_won'] + 1
                        elif x == '(RET)':
                            row_df['winner_sets_won'] = row_df['winner_sets_won'] + 1
                        else:
                            row_df['loser_sets_won'] = row_df['loser_sets_won'] + 1
                        
                        row_df['winner_games_won'] = row_df['winner_games_won'] + w_score
                        row_df['loser_games_won'] = row_df['loser_games_won'] + l_score

                        if len(x) > 2 and (w_score > l_score):
                            row_df['winner_tiebreaks_won'] = row_df['winner_tiebreaks_won'] + 1
                        if len(x) > 2 and (w_score < l_score):
                            row_df['loser_tiebreaks_won'] = row_df['loser_tiebreaks_won'] + 1

                        del w_score, l_score

                    matches_df = pd.concat([matches_df,row_df],ignore_index=True)

    if save == True:
        matches_df.to_csv(f'atp/match_scores/singles/csv/{year}_atp_match_scores.csv',index=False)
        matches_df.to_parquet(f'atp/match_scores/singles/parquet/{year}_atp_match_scores.parquet',index=False)

    return matches_df



if __name__ == "__main__":
    now = datetime.now().year
    for i in range(1994,2019+1):
        get_atp_singles_match_scores(i,True)