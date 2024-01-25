import csv
import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Tag

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        static_path = settings.SCV_DATA[0]
        csv_file_path = os.path.join(static_path, "data", "tag.csv")
        with open(csv_file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            counter = 0
            for name, color, slug in csv_reader:
                obj, created = Tag.objects.get_or_create(
                    name=name, color=color, slug=slug
                )
                if created:
                    counter += 1
                print(f"Добавлено {counter} ингредиентов"
                      "из файла {csv_file_path}")
