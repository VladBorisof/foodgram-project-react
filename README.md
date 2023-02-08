# Foodgram

# IP
```
51.250.26.167
```


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
