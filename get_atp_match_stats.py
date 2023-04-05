import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
#from selenium import webdriver
from tqdm import tqdm


def get_atp_basic_singles_match_stats(year:int,save=False):
    matches_df = pd.DataFrame()
    row_df = pd.DataFrame()
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    
    print(f'\nGetting the ATP basic match stats for the {year} season.')

    sched_df = pd.read_csv(f'atp/match_scores/singles/csv/{year}_atp_match_scores.csv')
    sched_df = sched_df.dropna(subset=['match_stats_url_suffix'])
    match_urls_arr = sched_df['match_stats_url_suffix'].to_list()
    tourney_name_arr = sched_df['tourney_name'].to_list()
    match_id_arr = sched_df['match_id'].to_list()
    tourney_order_arr = sched_df['tourney_order'].to_list()

    for i in tqdm(range(0,len(match_urls_arr))):
        print(f'\nOn match {i+1} of {len(match_urls_arr)+1} for {year}.')

        match_url = match_urls_arr[i]
        tourney_name = tourney_name_arr[i]
        match_id = match_id_arr[i]
        tourney_order = tourney_order_arr[i]

        url = f"https://www.atptour.com{match_url}"
        
        has_stats_downloaded = Path(f'atp/match_stats/singles/raw/{match_id}.csv').is_file()

        if has_stats_downloaded == False:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text,features='lxml')
            # driver = webdriver.Chrome()
            # driver.get(url)
            # soup = BeautifulSoup(driver.page_source,features='lxml')

            time.sleep(10)

            row_df = pd.DataFrame(
                {
                    'year':year,
                    'match_id':match_id,
                    'tourney_order':tourney_order,
                    'match_stats_url_suffix':match_url
                },
                index=[0]
            )
            
            match_time = str(soup.find('table',{'class':'scores-table'}).find('td',{'class':'time'}).text).replace('\r','').replace('\n','').replace(' ','')
            match_hr,match_min,match_sec = match_time.split(':')
            row_df['match_time'] = match_time
            row_df['match_duration'] = (60 * int(match_hr)) + int(match_min) 

            del match_time,match_hr,match_min,match_sec

            match_stats_table = soup.find('table',{'class':'match-stats-table'})
            match_stats_table = match_stats_table.find_all('tr',{'class':'match-stats-row percent-on'})

            ###########################################################################################################################################################################################################################################
            ##
            ##  Winner Serve Stats
            ##
            ###########################################################################################################################################################################################################################################
            
            row_df['winner_serve_rating'] =  int(match_stats_table[0].find('td',{'class':'match-stats-number-left'}).text)
            
            row_df['winner_aces'] = int(match_stats_table[1].find('td',{'class':'match-stats-number-left'}).text)
            row_df['winner_double_faults'] = int(match_stats_table[2].find('td',{'class':'match-stats-number-left'}).text)
            row_df['winner_double_faults'] = int(match_stats_table[2].find('td',{'class':'match-stats-number-left'}).text)

            first_serves = str(match_stats_table[3].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            #first_serves = first_serves.replace('(','').replace(')','')
            row_df[['winner_first_serves_in','winner_first_serves_total']] = first_serves.split('/')
            del first_serves

            first_serve_points_won = str(match_stats_table[4].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['winner_first_serve_points_won','winner_first_serve_points_total']] = first_serve_points_won.split('/')
            del first_serve_points_won

            second_serve_points_won  = str(match_stats_table[5].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['winner_second_serve_points_won','winner_second_serve_points_total']] = second_serve_points_won.split('/')
            del second_serve_points_won

            break_points_saved = str(match_stats_table[6].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['winner_break_points_saved','winner_break_points_serve_total']] =  break_points_saved.split('/')
            del break_points_saved

            ###########################################################################################################################################################################################################################################
            ##
            ##  Winner Return Stats
            ##
            ###########################################################################################################################################################################################################################################

            row_df['winner_return_rating'] = int(match_stats_table[8].find('td',{'class':'match-stats-number-left'}).text)

            first_serve_points_won = str(match_stats_table[9].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['winner_first_serve_return_won','winner_first_serve_return_total']] = first_serve_points_won.split('/')
            del first_serve_points_won

            second_serve_points_won  = str(match_stats_table[10].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['winner_second_serve_return_won','winner_second_serve_return_total']] = second_serve_points_won.split('/')
            del second_serve_points_won

            break_points_converted = str(match_stats_table[11].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['winner_break_points_converted','winner_break_points_return_total']] =  break_points_converted.split('/')
            del break_points_converted

            row_df['winner_service_games_played'] = int(match_stats_table[7].find('td',{'class':'match-stats-number-left'}).text)
            row_df['winner_return_games_played'] = int(match_stats_table[12].find('td',{'class':'match-stats-number-left'}).text)

            ###########################################################################################################################################################################################################################################
            ##
            ##  Winner Point Stats
            ##
            ###########################################################################################################################################################################################################################################

            service_points_converted = str(match_stats_table[13].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['winner_serve_points_won',' winner_serve_points_total']] =  service_points_converted.split('/')
            del service_points_converted

            return_points_converted = str(match_stats_table[14].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['winner_return_points_won',' winner_return_points_total']] =  return_points_converted.split('/')
            del return_points_converted

            total_points_converted = str(match_stats_table[15].find('td',{'class':'match-stats-number-left'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['winner_total_points_won','winner_total_points_total']] = total_points_converted.split('/')
            del total_points_converted

            ###########################################################################################################################################################################################################################################
            ##
            ##  loser Serve Stats
            ##
            ###########################################################################################################################################################################################################################################
            
            row_df['loser_serve_rating'] =  int(match_stats_table[0].find('td',{'class':'match-stats-number-right'}).text)
            
            row_df['loser_aces'] = int(match_stats_table[1].find('td',{'class':'match-stats-number-right'}).text)
            row_df['loser_double_faults'] = int(match_stats_table[2].find('td',{'class':'match-stats-number-right'}).text)
            row_df['loser_double_faults'] = int(match_stats_table[2].find('td',{'class':'match-stats-number-right'}).text)

            first_serves = str(match_stats_table[3].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            #first_serves = first_serves.replace('(','').replace(')','')
            row_df[['loser_first_serves_in','loser_first_serves_total']] = first_serves.split('/')
            del first_serves

            first_serve_points_won = str(match_stats_table[4].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['loser_first_serve_points_won','loser_first_serve_points_total']] = first_serve_points_won.split('/')
            del first_serve_points_won

            second_serve_points_won  = str(match_stats_table[5].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['loser_second_serve_points_won','loser_second_serve_points_total']] = second_serve_points_won.split('/')
            del second_serve_points_won

            break_points_saved = str(match_stats_table[6].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['loser_break_points_saved','loser_break_points_serve_total']] =  break_points_saved.split('/')
            del break_points_saved

            ###########################################################################################################################################################################################################################################
            ##
            ##  loser Return Stats
            ##
            ###########################################################################################################################################################################################################################################

            row_df['loser_return_rating'] = int(match_stats_table[8].find('td',{'class':'match-stats-number-right'}).text)

            first_serve_points_won = str(match_stats_table[9].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['loser_first_serve_return_won','loser_first_serve_return_total']] = first_serve_points_won.split('/')
            del first_serve_points_won

            second_serve_points_won  = str(match_stats_table[10].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['loser_second_serve_return_won','loser_second_serve_return_total']] = second_serve_points_won.split('/')
            del second_serve_points_won

            break_points_converted = str(match_stats_table[11].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['loser_break_points_converted','loser_break_points_return_total']] =  break_points_converted.split('/')
            del break_points_converted

            row_df['loser_service_games_played'] = int(match_stats_table[7].find('td',{'class':'match-stats-number-right'}).text)
            row_df['loser_return_games_played'] = int(match_stats_table[12].find('td',{'class':'match-stats-number-right'}).text)

            ###########################################################################################################################################################################################################################################
            ##
            ##  loser Point Stats
            ##
            ###########################################################################################################################################################################################################################################

            service_points_converted = str(match_stats_table[13].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['loser_serve_points_won',' loser_serve_points_total']] =  service_points_converted.split('/')
            del service_points_converted

            return_points_converted = str(match_stats_table[14].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['loser_return_points_won',' loser_return_points_total']] =  return_points_converted.split('/')
            del return_points_converted

            total_points_converted = str(match_stats_table[15].find('td',{'class':'match-stats-number-right'}).find('span',{'class':'stat-breakdown'}).text).replace('\r','').replace('\n','').replace(' ','').replace('(','').replace(')','')
            row_df[['loser_total_points_won','loser_total_points_total']] = total_points_converted.split('/')
            del total_points_converted

            # matches_df = pd.concat([matches_df,row_df],ignore_index=True)

            if save==True:
                row_df.to_csv(f'atp/match_stats/singles/raw/{match_id}.csv',index=False)

    # return matches_df


if __name__ == "__main__":
    try:
        for i in range(1991,2024):
            get_atp_basic_singles_match_stats(i,True)
    except:
        print('Hit a wall when downloading data.')
