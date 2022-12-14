import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db,db, Book

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app,resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    
    @app.errorhandler(404)
    def not_found(error):
        print(error)
        return jsonify({
            "success" : False,
            "error" : 404,
            "message" : "content Not found"
        })

    @app.route('/books', methods=['GET'])
    def get_all_books():
        title_ask = request.args.get("title") 
        if title_ask is None :
            page = request.args.get('page',1,int)
            limit = BOOKS_PER_SHELF
            offset = (page - 1) * limit if page > 0 else abort(404)
            books = [book.format() for book in Book.query.offset(offset).limit(limit).all()]
            if len(books) < 1 :
                abort(404)

            return jsonify({
                "success" : True,
                "totalBooks": Book.query.count(),
                "books": books,
                "page": page
            })
        else:
            title = request.args.get("title")
            s = f"%{title}%"
            result = [book.format() for book in Book.query.filter(Book.title.ilike(s)).order_by(db.desc(Book.id)).all()]
            if len(result)<1:
                return jsonify({
                    "success" : False,
                    "message" : "Could not found any matching result"
                }),404

            return jsonify({
                "success" : True,
                "results" : len(result),
                "books" : result
            })

    @app.route('/books/<int:book_id>',methods=['PATCH'])
    def update_book_rating(book_id):
        try:
            data = request.json
            rating=data['rating']
            book = Book.query.get(book_id)
            book.rating = rating
            db.session.add(book)
            db.session.commit()
            return jsonify({
                "success" : True,
            })
        except Exception as e:
            print(e)
            return jsonify({
                "success" : False,
                "message" : "Your request did not provided requested datas"
            }),200
    
    @app.route('/books/<int:book_id>',methods=['DELETE'])
    def delete_book(book_id):
        try:
            book = Book.query.get(book_id)
            db.session.delete(book)
            db.session.commit()
            return jsonify({
                "success" : True,
            })
        except:
            return jsonify({
                "success" : False,
                "message" : "Your request did not succeed"
            }),400

    @app.route('/books', methods=['POST'])
    def add_new_book():
        datas = request.json
        try:
            book = Book(
                author = datas["author"],
                title = datas["title"],
                rating = datas["rating"],
            )
            db.session.add(book)
            db.session.commit()
            return jsonify({
                "success" : True,
                "created" : book.id,
                "books" : [book.format() for book in Book.query.all()],
                "total_books" : Book.query.count(),
            })
        except Exception as e:
            print(e)
            return jsonify({
                "success" : False,
                "message" : "Your request did not succeed"
            }),400
    

    # DONE: @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

    # DONE : @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh

    # DONE: @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'

    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.

    return app
