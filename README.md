Проект FoodGram Recipe
Это блог для обмена рецептами разными поварами и любителями готовки.
На сайте люди могут зарегистрироваться и быть полноценной частью проекта. 
Пользователи смогут подписываться на друг друга, обмениваться рецептами, добавлять 
рецепты в избранное, а также добавлять любимые рецепты в список покупок.

Технологии  и инструменты, использованные в разработке этого проекта:
Python
Django Rest Framework
Docker
Nginx
Postgres
GitHub
DockerHub
Postman


Клонировать репозиторий и перейти в папку backend:
1. git clone https://github.com/Asif-KHAN-1-1998/foodgram-project-react.git
2. cd backend/foodgram
Создать и активировать виртуальное окружение:
3. python -m venv venv
4. source venv/Scripts/activate
Установить зависимости из файла requirements.txt:
5. pip install -r requirements.txt
Выполнить миграции:
6. python manage.py makemigrations
7. python manage.py migrate
Загрузить ингридиенты из csv-файла:
8. docker exec backend python manage.py import_csv
Загрузить тэги из csv-файла:
9. docker exec backend python manage.py importtag_csv

Авторизация 
email = admin@mail.ru
password= admin