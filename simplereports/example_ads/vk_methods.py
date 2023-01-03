import requests
import time
from .models import Cabinet, Campaign, Case, DateStat

VERSION = 5.131
#FIXME! брать из соответствующей модели
ACCOUNT_ID = 1604063875

TOKEN = 'vk1.a.5cuK_J3FZE66Bvio3RuvfqGzBm00HAZu_vzFRU3L64SNpbyuJVroifvbVItBivpaHeFJbxkWCcUHDisY2myAJbUHKEq0gZa4_GmSNXN-hhFW_bAUZjJferRcCZbpE_lxG2T8eEzBfGOjP-opqVOF24G7NFfNNbGHuOsoyJcXCnNgVX5pBcfqR9_kaMT8HIvFwzOIoOC6FHZ5Do5NPUUH0g'

# PARAMS = {
#         'access_token': TOKEN,
#         'v': VERSION,
#         'account_id': ACCOUNT_ID,
#         'client_id': ACCOUNT_ID
#     }

camps = {
    'URL': 'https://api.vk.com/method/ads.getCampaigns',
}

stats = {
    'URL': 'https://api.vk.com/method/ads.getStatistics'
}


