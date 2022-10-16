import os
from unicodedata import category
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS
    CORS(app)

    # after_request decorator to set Access-Control-Allow
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

    # Endpoint to handle GET requests for all available categories.

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        category_dict = {}
        for category in categories:
            category_dict[category.id] = category.type

        if len(category_dict) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": category_dict
            })

    # Endpoint to handle GET requests for paginated questions
    # Returns a list of questions,number of total questions,
    # current category, categories.
    @app.route('/questions')
    def get_questions():
        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)
        try:
            categories = Category.query.all()
            category_dict = {}
            for category in categories:
                category_dict[category.id] = category.type

            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "categories": category_dict
            }
            )
        except BaseException:
            abort(422)
    # Endpoint to DELETE question using a question ID.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                "success": True,
                "deleted": question_id
            })
        except BaseException:
            abort(422)

    # Add questions to the database
    @app.route('/questions', methods=['POST'])
    def add_question():
        # load data from form
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        # if (len(new_question) is None or len(new_answer) is None):
        #     abort(422)
        if (new_question is None) or (new_answer is None):
            abort(422)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty)
            question.insert()
            return jsonify({
                "success": True,
                "created": question.id,
            })
        except BaseException:
            abort(422)

    # Endpoint to get questions based on a search term.
    @app.route('/questions/search', methods=['POST'])
    def search():
        body = request.get_json()
        input = body.get('searchTerm', None)

        if input is None:
            abort(404)

        questions = Question.query.filter(
            Question.question.ilike(
                "%{}%".format(input))).all()
        current_questions = paginate_questions(request, questions)
        if len(questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(questions)
        })

    # Endpoint to get questions based on category.

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_based_on_category(category_id):
        category = Question.query.get(category_id)
        if category:
            abort(404)
        try:
            questions = Question.query.filter(
                Question.category == category_id).all()
            current_questions = paginate_questions(request, questions)
            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(questions),
                "current_category": category_id
            })
        except BaseException:
            abort(400)

    # Endpoint to get questions to play the quiz.
    @app.route('/quizzes', methods=['POST'])
    def play_game():
        # Load data from the frontend QuizView
        body = request.get_json()
        # This is given as a list of question ids that have been asked.
        previous_questions = body.get('previous_questions')
        # This is given as a dictionary of quizCategory with {type,id}
        quiz_category = body.get('quiz_category')
        
        if previous_questions is None or quiz_category is None:
            abort(400) 

        # Obtaining questions for each category
        '''
        src https://stackoverflow.com/questions/20060485/
        sqlalchemy-select-using-reverse-inclusive-not-in-list-of-child-column-values
        '''
        # Id of 0 is given in the frontend as a default which applies for the
        # 'ALL' object

        if quiz_category['id'] == '1':
            questions = Question.query.filter(
                Question.category == 1,
                ~Question.id.in_(previous_questions)).all()
        elif quiz_category['id'] == '2':
            questions = Question.query.filter(
                Question.category == 2,
                ~Question.id.in_(previous_questions)).all()
        elif quiz_category['id'] == '3':
            questions = Question.query.filter(
                Question.category == 3,
                ~Question.id.in_(previous_questions)).all()
        elif quiz_category['id'] == '4':
            questions = Question.query.filter(
                Question.category == 4,
                ~Question.id.in_(previous_questions)).all()
        elif quiz_category['id'] == '5':
            questions = Question.query.filter(
                Question.category == 5,
                ~Question.id.in_(previous_questions)).all()
        elif quiz_category['id'] == '6':
            questions = Question.query.filter(
                Question.category == 6,
                ~Question.id.in_(previous_questions)).all()
        else:
            questions = Question.query.filter(
                ~Question.id.in_(previous_questions)).all()

        while questions:
            current_question = random.choice(questions)
            return jsonify({
                "success": True,
                "question": current_question.format()
            })
        else:
            return jsonify({
                "success": True,
            })

    # Error handlers for all expected errors

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500

    return app
