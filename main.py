"""
Реализуйте web-приложение, которое состоит из двух страниц: / и /news/{id}.

Для запуска проекта, выберите в PyCharm конфигурацию start.
Для тестов, выберите в PyCharm конфигурацию tests.
Все необходимые файлы находятся в папке с проектом.
"""
from flask import Flask, jsonify, abort
from typing import Tuple
import json
from datetime import datetime

app = Flask(__name__)


def loader() -> Tuple[dict, dict]:
    """
    Функция считывает данные из файлов и преобразует их в dict.
    Функция не должна нарушать изначальную структуру данных.
    Логика фильтрации и сортировки должна быть реализована в функциях 
    get_list и get_item.
    """
    with open('news.json') as news_file:
        news_dict = json.load(news_file)
    with open('comments.json') as comments_file:
        comments_dict = json.load(comments_file)
    return news_dict, comments_dict


@app.route("/")
def get_list():
    """
    На странице / вывести json в котором каждый элемент это:
    - неудаленная новость из списка новостей из файла news.json.
    - для каждой новости указано кол-во комментариев этой новости из файла comments.json
    - для каждой новости указана дата и время последнего (самого свежего) комментария

    В списоке новостей должны отсутствовать новости, дата публикации которых еще не наступила.
    Даты в файле хранятся в формате ISO 8601(%Y-%m-%dT%H:%M:%S) и должны отдаваться в том же формате.

    Формат ответа:
    news: [
        {
            id: <int>,
            author:	<str>,
            publishedAt: <str>,
            image:	<str>,
            teaser: <str>,
            isDeleted: <bool>,
            lastComment: <str>,
            commentsCount: <int>
        }
    ],
    totalResults: <int>
    """
    news, comments = loader()

    good_news = []
    for news_item in news['news']:
        if datetime.now().isoformat() > news_item['publishedAt'] and not news_item['isDeleted']:
            news_id = news_item['id']
            comments_counter = 0
            last_comment = datetime.strptime('2000-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S')

            for comment in comments['comments']:
                if comment['newsId'] == news_id:
                    comments_counter += 1
                    if datetime.strptime(comment['publishedAt'], '%Y-%m-%dT%H:%M:%S') > last_comment:
                        news_item['lastComment'] = comment['publishedAt']

            news_item['commentsCount'] = comments_counter
            good_news.append(news_item)

    output = {"news": good_news, 'totalResults': len(good_news)}

    return jsonify(output)


@app.route("/news/<int:news_id>")
def get_item(news_id):
    """
    На странице /news/{id} вывести json, который должен содержать:
    - новость с указанным в ссылке id
    - список всех комментариев к новости, отсортированных по времени создания от самого свежего к самому старому

    Для следующих случаев нужно отдавать ошибку abort(404):
    - попытка получить новость не из списка
    - попытка получить удаленную новость
    - попытка получить новость с датой публикации из будущего


    Формат ответа:
    id: <int>,
    author:	<str>,
    publishedAt: <str>,
    image:	<str>,
    teaser: <str>,
    content: <str>,
    isDeleted: <bool>,
    comments: [
        user: <str>,
        newsId: <int>,
        comment: <str>,
        publishedAt: <str>
    ]
    """
    news, comments = loader()

    for news_item in news['news']:
        if news_item['id'] == news_id:
            current_time = datetime.now()
            if (news_item['isDeleted'] or
                    datetime.strptime(news_item['publishedAt'], '%Y-%m-%dT%H:%M:%S') > current_time):
                abort(404)

            last_comment = datetime.strptime('2000-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S')

            good_news = news_item
            good_news['comments'] = []
            for comment in comments['comments']:
                if comment['newsId'] == news_id:
                    published_time = datetime.strptime(comment['publishedAt'], '%Y-%m-%dT%H:%M:%S')
                    if published_time > last_comment:
                        good_news['comments'].insert(0, comment)
                        last_comment = published_time
                    else:
                        good_news['comments'].append(comment)

            output = good_news
            return output
    abort(404)

