from django.core.management.base import BaseCommand
from reports.models import Cabinet, Campaign


class Command(BaseCommand):
    help = "Наполняет базу тестовыми данными"

    def handle(self, *args, **options):
        cab1 = Cabinet.objects.create(ext_id=35549234, ext_name='Кабинет Васи')
        cab2 = Cabinet.objects.create(ext_id=84567483, ext_name='Газпром_медиа')
        Campaign.objects.create(ext_id=34875849, ext_name='Кампания на малоимущих', cabinet=cab1)
        Campaign.objects.create(ext_id=34464434, ext_name='Лидген', cabinet=cab1)
        Campaign.objects.create(ext_id=348768945, ext_name='Кампания на стариков. ЙА КРЕВЕДКО', cabinet=cab2)
        Campaign.objects.create(ext_id=685679, ext_name='Флексишь?', cabinet=cab2)
        Campaign.objects.create(ext_id=834758943, ext_name='кротовуха', cabinet=cab2)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added test data')
        )
