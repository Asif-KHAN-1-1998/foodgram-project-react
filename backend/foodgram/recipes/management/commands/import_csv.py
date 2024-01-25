import csv
import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        static_path = settings.SCV_DATA[0]
        csv_file_path = os.path.join(static_path, "data", "ingredients.csv")
        with open(csv_file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            counter = 0
            for name, measurement_unit in csv_reader:
                obj, created = Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )
                if created:
                    counter += 1
                print(f"Добавлено {counter} ингредиентов"
                      "из файла {csv_file_path}")
