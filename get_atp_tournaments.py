from datetime import datetime
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests
from tqdm import tqdm

def get_atp_schedule(year:int,save=False):
    sched_df = pd.DataFrame()
    row_df = pd.DataFrame()
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    url = f"https://www.atptour.com/en/scores/results-archive?year={year}"

    print(f'\nGetting the ATP tournaments for the {year} season.')

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text,features='lxml')
    sched_tbl = soup.find('table',{'class':'results-archive-table mega-table'})
    sched_tbl = sched_tbl.find_all('tr',{'class':'tourney-result'})
    tourney_order = 0
    for i in tqdm(sched_tbl):
        tourney_order +=1
        cells = i.find_all('td')
        row_df = pd.DataFrame({'tourney_year':year},index=[0])
        row_df['tourney_order'] = tourney_order
        try:
            row_df['tourney_type_id'] = str(cells[1].find('img').get('src')).split('/')[-1].replace('.png','').replace('.svg','').replace('categorystamps_','')
        except:
            row_df['tourney_type_id'] = None
        #row_df['tourney_type'] = row_df['tourney_type_id']
        row_df['tourney_name'] = str(cells[2].find('a').text).replace('\r','').replace('\n','').replace('  ','')
        tourney_id = int(str(cells[2].find('a').get('href')).split('/')[4])
        row_df['tourney_id'] =tourney_id
        row_df['tourney_slug'] = str(cells[2].find('a').get('href')).split('/')[3]
        row_df['tourney_year_id'] = f"{year}-{tourney_id}"
        # row_df['tourney_url_suffix'] = cells[2].find('a').get('href')
        row_df['tourney_location'] = str(cells[2].find('span',{'class':'tourney-location'}).text).replace('\r','').replace('\n','').replace('  ','')
        row_df['tourney_date'] = str(cells[2].find('span',{'class':'tourney-dates'}).text).replace('\r','').replace('\n','').replace(' ','').replace('.','/')
        row_df['tourney_month'] = int(str(cells[2].find('span',{'class':'tourney-dates'}).text).split('.')[1])
        row_df['tourney_day'] = int(str(cells[2].find('span',{'class':'tourney-dates'}).text).split('.')[2])
        
        draws = cells[3].find_all('a')
        
        for j in draws:
            temp_url = j.get('href')
            if temp_url == None or temp_url == '':
                pass
            elif 'singles' in temp_url:
                row_df['tourney_singles_draw'] = int(j.find('span',{'class':'item-value'}).text)
            elif 'doubles' in temp_url:
                row_df['tourney_doubles_draw'] = int(j.find('span',{'class':'item-value'}).text)
            else:
                raise SyntaxError(f'Unhandled tournament draw!\nURL:{temp_url}')
            
            del temp_url
        
        conditions = cells[4].find('div').text
        
        if 'Outdoor' in conditions:
            row_df['tourney_conditions'] = 'Outdoor'
        elif 'Indoor' in conditions:
            row_df['tourney_conditions'] = 'Indoor'
        else:
            raise SyntaxError(f'Unhandled tournament conditions!\nUnhandled cell in question:{conditions}')

        del conditions

        row_df['tourney_surface'] = str(cells[4].find('span',{'class':'item-value'}).text).replace('\r','').replace('\n','').replace('  ','')
        
        tourney_fin_commit_raw = str(cells[5].text).replace('\r','').replace('\n','').replace('  ','')
        row_df['tourney_fin_commit_raw'] = tourney_fin_commit_raw

        if tourney_fin_commit_raw == None or tourney_fin_commit_raw == '':
            pass
        elif 'A$' in tourney_fin_commit_raw:
            row_df['currency'] = 'AUD'
            row_df['tourney_fin_commit'] = int(tourney_fin_commit_raw.replace(',','').replace('A$',''))
        elif '$' in tourney_fin_commit_raw:
            row_df['currency'] = 'USD'
            row_df['tourney_fin_commit'] = int(tourney_fin_commit_raw.replace(',','').replace('$',''))
        elif '€' in tourney_fin_commit_raw:
            row_df['currency'] = 'EUR'
            row_df['tourney_fin_commit'] = int(tourney_fin_commit_raw.replace(',','').replace('€',''))
        elif '£' in tourney_fin_commit_raw:
            row_df['currency'] = 'GBR'
            row_df['tourney_fin_commit'] = int(tourney_fin_commit_raw.replace(',','').replace('£',''))

        else:
            raise SyntaxError(f'Unhandled tournament financial committment!\nCell in question:{tourney_fin_commit_raw}')
        try:
            row_df['tourney_url_suffix'] = cells[7].find('a').get('href')
        except:
            row_df['tourney_url_suffix'] = None

        for j in cells[6].find_all('div',{'class':'tourney-detail-winner'}):
            winners = j.find_all('a')
            
            if j.text == None or j.text == '':
                pass
            elif 'SGL' in j.text:
                row_df['singles_winner_name'] = str(winners[0].text).replace('\r','').replace('\n','').replace('\t','').replace('  ','')
                row_df['singles_winner_url'] = winners[0].get('href')
                row_df['singles_winner_player_slug'] = str(winners[0].get('href')).split('/')[3]
                row_df['singles_winner_player_id'] = str(winners[0].get('href')).split('/')[4]
            
            elif 'DBL' in j.text:
                row_df['doubles_winner_1_name'] = str(winners[0].text).replace('\r','').replace('\n','').replace('\t','').replace('  ','')
                row_df['doubles_winner_1_url'] = winners[0].get('href')
                row_df['doubles_winner_1_player_slug'] = str(winners[0].get('href')).split('/')[3]
                row_df['doubles_winner_1_player_id'] = str(winners[0].get('href')).split('/')[4]

                row_df['doubles_winner_2_name'] = str(winners[1].text).replace('\r','').replace('\n','').replace('\t','').replace('  ','')
                row_df['doubles_winner_2_url'] = winners[1].get('href')
                row_df['doubles_winner_2_player_slug'] = str(winners[1].get('href')).split('/')[3]
                row_df['doubles_winner_2_player_id'] = str(winners[1].get('href')).split('/')[4]

            elif 'Team' in j.text:
                row_df['singles_winner_name'] = str(j.find('span').text).replace('\r','').replace('\n','').replace('\t','').replace('  ','')
                row_df['singles_winner_url'] = None
                row_df['singles_winner_player_slug'] = None
                row_df['singles_winner_player_id'] = 'TEAM'

            else:
                raise SyntaxError(f'Unhandled tournament victors!\nCell in question:\n"{tourney_fin_commit_raw}"')

        sched_df = pd.concat([sched_df,row_df],ignore_index=True)

    time.sleep(4)

    if save == True:
        sched_df.to_csv(f'atp/tournament_schedules/annual/csv/{year}_atp_schedule.csv',index=False)
        sched_df.to_parquet(f'atp/tournament_schedules/annual/parquet/{year}_atp_schedule.parquet',index=False)
        #sched_df.to_json(f'atp/tournament_schedules/annual/json/{year}_atp_schedule.json')

    return sched_df

if __name__ == "__main__":
    now = datetime.now().year
    for i in range(now,now+1):
        get_atp_schedule(i,True)