import requests
from datetime import date
from django.shortcuts import get_object_or_404
from oauth2client import service_account
import gspread
from .models import Cabinet, Campaign, Case, DateStat
import time

from .vk_methods import ACCOUNT_ID, TOKEN, VERSION, camps, stats

def get_campaigns():
    params = {
        'access_token': TOKEN,
        'v': VERSION,
        'account_id': ACCOUNT_ID,
        'clien_id': ACCOUNT_ID
    }
    response = requests.get(
        camps.get('URL'),
        params=params
    )
    data = response.json()
    objs = (
        Campaign(
            id=campaign.get('id'),
            name=campaign.get('name'),
            status=campaign.get('status')
        ) for campaign in data.get('response')
    )
    Campaign.objects.all().delete()
    Campaign.objects.bulk_create(objs)

def agregate_datestat():
    today = date.today()
    all_campaigns = Campaign.objects.all().values('id')
    campaigns = []
    for campaign in all_campaigns:
        campaigns.append(campaign.get('id'))
    campaigns_str = ''
    for campaign in campaigns:
        campaigns_str += str(campaign) + ','
    params = {
        'access_token': TOKEN,
        'v': VERSION,
        'account_id': ACCOUNT_ID,
        'client_id': ACCOUNT_ID,
        'ids_type': 'campaign',
        'ids': campaigns_str[:len(campaigns_str)-1],
        'period': 'day',
        'date_from': '2022-01-01',
        'date_to': '2022-12-21'
        # 'date_from': f'{today.year}-01-{today.day-1}',
        #FIXME!Надо сделать нормально, смена года это может поломать
        # 'date_to': f'{today.year}-{today.month}-{today.day-1}'
    }
    response = requests.get(
        stats.get('URL'),
        params=params
    )
    data = response.json()
    resp = data['response']
    if resp:
        for campaign in resp:
            if campaign.get('stats') is None:
                continue
            for stat in campaign.get('stats'):
                pass
                current_day, status = DateStat.objects.get_or_create(
                    date=date(
                        int(stat.get('day').split('-')[0]),
                        int(stat.get('day').split('-')[1]),
                        int(stat.get('day').split('-')[2])
                    )
                )
                if stat.get('spent'):
                    spent_to_add = float(stat.get('spent'))
                    spent_existing = current_day.spent
                    if spent_existing:
                        current_day.spent = str(float(spent_existing) + spent_to_add)
                    else:
                        current_day.spent = str(spent_to_add)
                if stat.get('impressions'):
                    current_day.impressions += stat.get('impressions')
                if stat.get('clicks'):
                    current_day.clicks += stat.get('clicks')
                if stat.get('reach'):
                    current_day.reach += stat.get('reach')
                if stat.get('uniq_views_count'):
                    current_day.unique_views += stat.get('uniq_views_count')
                current_day.save()


HEADER = ['дата', 'spent', 'impressions', 'clicks']


def export():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = service_account.ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('data').sheet1

    if sheet.cell(1, 1).value != HEADER[0]:
        for i in range(len(HEADER)):
            sheet.update_cell(1, i+1, HEADER[i])

    row_to_start = len(sheet.col_values(1)) + 1
    for obj in DateStat.objects.all():
        sheet.update_cell(row_to_start, 1, str(obj.date))
        sheet.update_cell(row_to_start, 2, str(obj.spent))
        sheet.update_cell(row_to_start, 3, str(obj.impressions))
        sheet.update_cell(row_to_start, 4, str(obj.clicks))
        row_to_start += 1
        time.sleep(60)

def test():
    pass
    # scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # creds = service_account.ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    # client = gspread.authorize(creds)
    # sh = client.open('data')
    # new_sheet = sh.add_worksheet(title='sheet2', rows=100, cols=20)
    # sheet = sh.worksheet('sheet2')
    # sheet.update_cell(1, 1, 'тестовые данные на второй вкладке')
    # print(sheet.cell(1, 2).value)
    # print(sheet.acell('A1').value)
    # cell = sheet.find("Картошка")
    # print("Найдено в ячейке R%sC%s" % (cell.row, cell.col))
    # value = cell.value
    # row_number = cell.row
    # column_number = cell.col




if __name__ == '__main__':
    export()



# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#     creds = service_account.ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
#     client = gspread.authorize(creds)
#     sheet = client.open('data').sheet1
#     count_of_rows = len(df)
#     count_of_columns = len(df.columns)
#     for i in range(count_of_columns):
#         sheet.update_cell(1, i + 1, list(df.columns)[i])
#     for i in range(1, count_of_rows + 1):
#         for j in range(count_of_columns):
#             sheet.update_cell(i + 1, j + 1, str(df.iloc[i, j]))
#             time.sleep(1)