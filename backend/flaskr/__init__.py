import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get("page", 1 , type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    questions = [question.format() for question in selection]
    current_books = questions[start:end]
    return current_books

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})    
    
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content_Type,Authorisation,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS")
        return response
    
    @app.route("/categories")
    def get_categories():
        categories_data = Category.query.all()
        data = {}
        for category in categories_data:
            data.update({
                category.id: category.type
            })
            
        if len(data) == 0:
            abort(404)
            
        return jsonify({
            "success": True,
            "categories": data,
            "totalCategories": len(data)
        })
        
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
​
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    
    @app.route("/questions")
    def get_questions():
        selection = Question.query.order_by(
                        Question.id
                    ).all()
        current_questions = paginate_questions(request, selection)
        
        categories_data = Category.query.all()
        categories = {}
        for category in categories_data:
            categories.update({
                category.id: category.type
            })
            
        if len(current_questions) == 0:
            abort(404)
            
        return jsonify({
            "success": True,
            "questions": current_questions,
            "categories": categories,
            "totalQuestions": len(Question.query.all())
        })
        
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
​
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                            Question.id == question_id
                        ).one_or_none()
            
            if question is None:
                abort(404)
                
                
            question.delete()
            
            return jsonify({
                "success": True,
                "deletedQuestion": question_id,
                "message": "succesfully deleted"
            })
            
        except BaseException:
            abort(422)
            
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
​
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
​
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    
    @app.route("/questions", methods=["POST"])
    def create_or_search_question():
        body = request.get_json()
        
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get('searchTerm', None)
        
        
        try:
            if search:
                selection = Question.query.order_by(
                                Question.id
                            ).filter(
                                Question.question.ilike('%{}%'.format(search))
                            )
                current_searched_question = paginate_questions(request, selection)
                
                return jsonify({
                    "success": True,
                    "questions": current_searched_question,
                    "totalQuestions": len(selection.all())
                })
                
                
            else:
                question = Question(
                    question=new_question, 
                    answer=new_answer, 
                    category=new_category,
                    difficulty=new_difficulty
                    )
                question.insert()
                
                
                selection = Question.query.order_by(
                                Question.id
                            ).all()
                current_questions = paginate_questions(request, selection)
                
                return jsonify({
                    'success': True,
                    'created_questions': question.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all())
                    })
                
                
        except BaseException:
            abort(422)
            
            
    @app.route("/categories/<int:category_id>/questions")
    def get_question_by_category(category_id):
        questions_query = Question.query.order_by(
                            Question.id
                          ).filter(
                            Question.category==category_id
                          ).all()
        category_questions = [question.format() for question in questions_query]
        category = Category.query.get(category_id)
        
        
        if len(category_questions) == 0:
            abort(404)
        
        return jsonify({
            "success": True,
            "questions": category_questions,
            "currentCategory": category.type,
            "totalQuestions": len(category_questions)
        })
        
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
​
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_quizzes():
        try:
            body = request.get_json()
            previous_questions = body.get("previous_questions", None)
            quiz_category = body.get("quiz_category", None)
            category_id = quiz_category["id"]
            
            if category_id:
                 # get questions based on category
                quizz_questions = Question.query.filter(
                                        Question.category == category_id
                                    ).all()
                
                
            else:
                 # get all the questions
                quizz_questions = Question.query.all()
                
            next_questions = [
                                question.format()
                                for question in quizz_questions
                            ]
            
            random_question = random.choice(next_questions)
            
            while random_question['id'] in previous_questions:
                if len(previous_questions) == len(next_questions):
                    random_question = None
                    break
                
            random_question = random.choice(next_questions)
                
            return jsonify(
                {
                    "success": True,
                    "question": random_question,
                }
            )
              
        except BaseException:
            abort(404)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
        
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
        
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
        "success": False, 
        "error": 500,
        "message": "internal server error"
        }), 500
        
    return app










