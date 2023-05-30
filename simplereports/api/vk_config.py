GENERAL_URL = 'https://ads.vk.com/api/v2/'
TOKEN = 'eKppLLD7bq3R58MvrO7knzmW9FAA50WErNre2RyPapDSnI5Ecbw1LHVfhb212ie9ZRKZnbngzo4SnOQ9JCMnIS8A5OfkjuXdiubkXjfW8JfdzFLbciGYJaKVIDjVk9D18FcTD7kUbFNzAgXYidtHlCK9uP8OI1Rutxs9k2tTL3JLlbigavm38IKxZ43w6dcJDyRm2d6WvoonPajnmVFwhd6GZiOl'
REQUEST_HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
}


# инфо о пользователе
GETUSER = 'user.json'

# Список кампаний
GETPLANS = 'statistics/ad_plans/summary.json'

# метрики
METRICS_VK = (
    'shows',
    'cpm',
    'clicks',
    'ctr',
    'cpc',
    'goals',
    'cr',
    'cpa',
    'spent',
)
