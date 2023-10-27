""" from simplereports.settings import TOKEN """

GENERAL_URL = "https://ads.vk.com/api/v2/"
""" REQUEST_HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
} """


# инфо о пользователе
GETUSER = "user.json"

# Список кампаний
ADPLANS = "ad_plans.json"
GETPLANS = "statistics/ad_plans/summary.json"
GETPLANSDAY = "statistics/ad_plans/day.json"


# метрики
METRICS_VK = (
    "shows",
    "cpm",
    "clicks",
    "ctr",
    "cpc",
    "goals",
    "cr",
    "cpa",
    "spent",
)
