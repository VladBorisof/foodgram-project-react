# Foodgram

# IP
 - `51.250.26.167`


## Прогресс
### 05.01.2023
1. Собрать все в контейнерах
   - [x] Что-то не так с базой, может пока что не париться и сделать все на SQLite
     - Запустился с Postgres: добавил в контейнер `environment:- "POSTGRES_HOST_AUTH_METHOD=trust"`
2. Реализовать регистрацию
   - [ ] Модель для юзеров
   - [x] Протестировать суперпользователя

### 09.01.2023
- [x] Дописать модель юзеров
- [ ] Проверить [регистрация пользователя](https://practicum.yandex.ru/learn/backend-developer/courses/61d48df1-d8e7-41a4-9310-e417b15a5cd2/sprints/23186/topics/41804c41-bf40-40ce-8f63-e1ee82eb7559/lessons/c4efa0c1-1908-4115-803c-65128657e346/#:~:text=%D1%84%D0%B8%D0%BB%D1%8C%D1%82%D1%80%D0%B0%D1%86%D0%B8%D0%B8%20%D1%81%D0%BF%D0%B8%D1%81%D0%BA%D0%B0%20%D0%B8%D0%B7%D0%B1%D1%80%D0%B0%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE.-,%D0%A0%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F,-%D0%B8%20%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F)

Разбирался с авторизацией и аутентификацией. Что-то с паролем, почему от пишется 


### 10.01.2023
- [x] Продолжить разбираться с авторизацией. Разобраться с паролем
- [ ] Написать остальные модели

### 11.01.2023
- Вроде разобрался в авторизации - норм
- Пользователя по id
- Остальные модели 

### 12.01.2023
- Доделывал модели
- Нужно теперь писать вьюсеты и серилизаторы!

### 13.01.2023

# ./manage.py makemigrations recipes --empty --name 'add_tag'

`sudo su`
```
docker compose exec web python manage.py migrate
```
```
docker compose exec web python manage.py createsuperuser
```
```
docker compose exec web python manage.py collectstatic --no-input 
```
