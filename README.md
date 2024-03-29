# Проект «Продуктовый помощник»
![](https://img.shields.io/badge/Foodgram-black?style=for-the-badge&logo={LOGO}&logoColor=white)

![example workflow](https://github.com/VladBorisof/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# IP
```
158.160.27.179
```

Foodgram - продуктовый помощник, позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в «Избранное» и «Список покупок». Доступно скачивание сводного списка продуктов в формате txt, необходимых для приготовления одного или нескольких выбранных блюд. Для приложения настроен Continuous Integration (CI) и Continuous Deployment (CD).

# Описание проекта:
## Главная страница
На странице - cписок первых шести рецептов, отсортированных по дате публикации (от новых к старым). Остальные рецепты доступны на следующих страницах: внизу страницы есть пагинация.

## Страница рецепта
На странице - полное описание рецепта. Для авторизованных пользователей - возможность добавить рецепт в избранное и в список покупок, возможность подписаться на автора рецепта.

## Страница пользователя
На странице - имя пользователя, все рецепты, опубликованные пользователем и возможность подписаться на пользователя.

## Подписка на авторов
Подписка на публикации доступна только авторизованному пользователю. Страница подписок доступна только владельцу.

## Сценарий поведения пользователя:

1. Пользователь переходит на страницу другого пользователя или на страницу рецепта и подписывается на публикации автора кликом по кнопке «Подписаться на автора».
2. Пользователь переходит на страницу «Мои подписки» и просматривает список рецептов, опубликованных теми авторами, на которых он подписался. Сортировка записей - по дате публикации (от новых к старым).
3. При необходимости пользователь может отказаться от подписки на автора: переходит на страницу автора или на страницу его рецепта и нажимает «Отписаться от автора».

## Список избранного
Список избранного может просматривать только его владелец. Сценарий поведения пользователя:

1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в избранное».
2. Переходит на страницу «Список избранного» и просматривает персональный список избранных рецептов. При необходимости пользователь может удалить рецепт из избранного.

## Список покупок
Список покупок может просматривать только его владелец. Сценарий поведения пользователя:

1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в покупки».
2. Пользователь переходит на страницу Список покупок, там доступны все добавленные в список рецепты. Пользователь нажимает кнопку «Скачать список» и получает файл с суммированным перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке покупок».
3. При необходимости пользователь может удалить рецепт из списка покупок.

Список покупок скачивается в формате txt. При скачивании списка покупок ингредиенты в результирующем списке не дублируются; если в двух рецептах есть сахар (в одном рецепте - 5 г, в другом - 10 г), то в списке будет один пункт: Сахар - 15 г. В результате список покупок выглядит так:

- Фарш (баранина и говядина) - 600 г
- Сыр плавленый - 200 г
- Лук репчатый - 50 г

## Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам. При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. Такой же принцип соблюдается при фильтрации списка избранного.


# Подготовка удалённого сервера
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
