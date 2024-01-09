import csv
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

from posts.models import Tag

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        static_path = settings.STATICFILES_DIRS[0]
        csv_file_path = os.path.join(static_path, 'data', 'tag.csv')

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                count_created = 0

                for name, color, slug in csv_reader:
                    obj, created = Tag.objects.get_or_create(
                        name=name,
                        color=color,
                        slug=slug
                    )

                    if created:
                        count_created += 1

                logger.info(f'Добавлено {count_created} тэгов'
                            ' из файла {csv_file_path}')
                print(f'Добавлено {count_created} тэгов'
                    ' из файла {csv_file_path}')
        except FileNotFoundError as e:
            logger.error(str(e))
