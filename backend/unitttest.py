import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Book


class BookTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'student', 'student', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_book = {
            'title': 'Anansi Boys',
            'author': 'Neil Gaiman',
            'rating': 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            book = Book(
                title=self.new_book["title"],
                author=self.new_book["author"],
                rating=self.new_book["rating"]
            )
            self.db.session.add(book)
            self.db.session.commit()
            self.db.create_all()

    def tearDown(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'student', 'student', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.session.commit()
            try:
                num_rows_deleted = self.db.session.query(Book).delete()
                self.db.session.commit()
            except:
                self.db.session.rollback()

    def test_paginated_data(self):
        res = self.client().get('/books')
        data = json.loads(res.data)
        self.assertEqual(200, res.status_code)
    
    def test_search_book_should_appear_in_result(self):
        res = self.client().get(f'/books?title={self.new_book["title"]}')
        data = json.loads(res.data)
        self.assertEqual(200, res.status_code)
        self.assertGreaterEqual(1,data["results"])
        self.assertEqual(self.new_book["title"], data["books"][0]["title"])

            
    def test_search_book_should_be_case_insensitive(self):
        res = self.client().get(f'/books?title={self.new_book["title"].lower()}')
        data = json.loads(res.data)
        self.assertEqual(200, res.status_code)
        self.assertGreaterEqual(1,data["results"])
        self.assertEqual(self.new_book["title"], data["books"][0]["title"])

    

# @TODO: Write at least two tests for each endpoint - one each for success and error behavior.
#        You can feel free to write additional tests for nuanced functionality,
#        Such as adding a book without a rating, etc.
#        Since there are four routes currently, you should have at least eight tests.
# Optional: Update the book information in setUp to make the test database your own!


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
