import unittest
from datetime import datetime, timedelta

import main
from main import get_list, get_item


source_news = {
    "news": [
        {
            "id": 1,
            "author": "John Doe",
            "image": "https://placekitten.com/822/520",
            "teaser": "John Does teaser",
            "content": "John Does content",
            "publishedAt": (datetime.now() - timedelta(days=1)).replace(microsecond=0).isoformat(),
            "isDeleted": True
        },
        {
            "id": 2,
            "author": "John Smith",
            "image": "https://placekitten.com/822/521",
            "teaser": "Teaser of John Smith",
            "content": "Content of John Smith",
            "publishedAt": (datetime.now() - timedelta(days=3)).replace(microsecond=0).isoformat(),
            "isDeleted": False
        },
        {
            "id": 3,
            "author": "Melisa Doe",
            "image": "https://placekitten.com/822/522",
            "teaser": "Melisa Does teaser",
            "content": "Melisa Does content",
            "publishedAt": (datetime.now() + timedelta(days=5)).replace(microsecond=0).isoformat(),
            "isDeleted": False
        },
        {
            "id": 4,
            "author": "Albert Einstein",
            "image": "https://placekitten.com/822/523",
            "teaser": "Einsteins teaser",
            "content": "Einsteins content",
            "publishedAt": (datetime.now() + timedelta(days=1)).replace(microsecond=0).isoformat(),
            "isDeleted": True
        },
        {
            "id": 5,
            "author": "Axel Coon",
            "image": "https://placekitten.com/822/524",
            "teaser": "Teaser of Axel Coon",
            "content": "Сontent of Axel Coon",
            "publishedAt": (datetime.now() - timedelta(days=5)).replace(microsecond=0).isoformat(),
            "isDeleted": False
        }
    ],
    "totalResults": 5
}

source_comments = {
    "comments": [
        {
            "newsId": 2,
            "user": "kendriclamar@gmail.com",
            "comment": "Lamar comment",
            "publishedAt": (datetime.now() - timedelta(days=2)).replace(microsecond=0).isoformat()
        },
        {
            "newsId": 2,
            "user": "harrepotter@gmail.com",
            "comment": "Potter comment",
            "publishedAt": (datetime.now() - timedelta(days=1)).replace(microsecond=0).isoformat()
        },
        {
            "newsId": 5,
            "user": "kendriclamar@gmail.com",
            "comment": "Lamar comment",
            "publishedAt": (datetime.now() - timedelta(days=4)).replace(microsecond=0).isoformat()
        },
        {
            "newsId": 5,
            "user": "harrepotter@gmail.com",
            "comment": "Potter comment",
            "publishedAt": (datetime.now() - timedelta(days=2)).replace(microsecond=0).isoformat()
        },
        {
            "newsId": 5,
            "user": "service@gmail.com",
            "comment": "Service comment",
            "publishedAt": (datetime.now() - timedelta(days=1)).replace(microsecond=0).isoformat()
        }
    ],
    "totalResults": 2417
}


class TestSome(unittest.TestCase):
    def setUp(self):
        def returner(data):
            return data

        def loader():
            return source_news.copy(), source_comments.copy()

        def abort(code):
            raise Exception(code)
        main.loader = loader
        main.jsonify = returner
        main.abort = abort

    def test_list(self):
        news_list = get_list()

        self.assertEqual(news_list["totalResults"], 2)
        self.assertEqual(news_list["totalResults"], len(news_list["news"]))
        self.assertEqual(news_list["news"][0]["id"], 2)
        self.assertEqual(news_list["news"][0]["commentsCount"], 2)
        self.assertEqual(
            datetime.strptime(news_list["news"][0]["publishedAt"], "%Y-%m-%dT%H:%M:%S"),
            (datetime.strptime(news_list["news"][0]["lastComment"], "%Y-%m-%dT%H:%M:%S") - timedelta(days=2))
        )
        self.assertEqual(news_list["news"][1]["id"], 5)
        self.assertEqual(news_list["news"][1]["commentsCount"], 3)
        self.assertEqual(
            datetime.strptime(news_list["news"][1]["publishedAt"], "%Y-%m-%dT%H:%M:%S"),
            (datetime.strptime(news_list["news"][1]["lastComment"], "%Y-%m-%dT%H:%M:%S") - timedelta(days=4))
        )

    def test_item(self):
        news_item = get_item(5)
        self.assertEqual(news_item["author"], "Axel Coon")
        self.assertEqual(news_item["comments"][0]["newsId"], 5)
        self.assertEqual(
            datetime.strptime(news_item["publishedAt"], "%Y-%m-%dT%H:%M:%S"),
            (datetime.strptime(news_item["comments"][0]["publishedAt"], "%Y-%m-%dT%H:%M:%S") - timedelta(days=4))
        )
        self.assertEqual(news_item["comments"][1]["newsId"], 5)
        self.assertEqual(
            datetime.strptime(news_item["publishedAt"], "%Y-%m-%dT%H:%M:%S"),
            (datetime.strptime(news_item["comments"][1]["publishedAt"], "%Y-%m-%dT%H:%M:%S") - timedelta(days=3))
        )
        self.assertEqual(news_item["comments"][2]["newsId"], 5)
        self.assertEqual(
            datetime.strptime(news_item["publishedAt"], "%Y-%m-%dT%H:%M:%S"),
            (datetime.strptime(news_item["comments"][2]["publishedAt"], "%Y-%m-%dT%H:%M:%S") - timedelta(days=1))
        )

    def test_not_found(self):
        with self.assertRaises(Exception) as context:
            get_item(1)
            self.assertTrue(404 in context.exception)

        with self.assertRaises(Exception) as context:
            get_item(3)
            self.assertTrue(404 in context.exception)

        with self.assertRaises(Exception) as context:
            get_item(4)
            self.assertTrue(404 in context.exception)

        with self.assertRaises(Exception) as context:
            get_item(11)
            self.assertTrue(404 in context.exception)
