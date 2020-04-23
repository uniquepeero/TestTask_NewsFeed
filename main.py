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

    comments_info = {}
    for comment in comments['comments']:
        if comment['newsId'] not in comments_info:
            comments_info[comment['newsId']] = {
                'commentsCount': 1,
                'lastComment': comment['publishedAt']
            }
        else:
            comments_info[comment['newsId']]['commentsCount'] += 1
            if comment['publishedAt'] > comments_info[comment['newsId']]['lastComment']:
                comments_info[comment['newsId']]['lastComment'] = comment['publishedAt']

    good_news = []
    for news_item in news['news']:
        if datetime.now().isoformat() > news_item['publishedAt'] and not news_item['isDeleted']:
            news_id = news_item['id']
            try:
                news_item['commentsCount'] = comments_info[news_id]['commentsCount']
                news_item['lastComment'] = comments_info[news_id]['lastComment']
            except KeyError:
                news_item['commentsCount'] = 0
                news_item['lastComment'] = None

            good_news.append(news_item)

    return jsonify({"news": good_news, 'totalResults': len(good_news)})


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

            news_item['comments'] = [comment for comment in comments['comments'] if comment['newsId'] == news_id]
            news_item['comments'].sort(key=lambda comment: comment['publishedAt'], reverse=True)

            return news_item

    abort(404)
