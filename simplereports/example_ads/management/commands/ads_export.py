from django.core.management.base import BaseCommand

from webb.ads_export import export, get_campaigns, agregate_datestat, test

class Command(BaseCommand):
    help = "Запрос"

    def handle(self, *args, **options):
        # get_campaigns()
        # agregate_datestat()
        # export()
        test()

        # self.stdout.write(self.style.SUCCESS(f'Кабинет ответил {data}'))
