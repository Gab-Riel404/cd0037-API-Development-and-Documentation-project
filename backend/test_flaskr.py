import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.DB_USER = os.getenv('DB_USER', '4rag3')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'time2quill')
        self.DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
        self.DB_NAME = os.getenv('DB_NAME', 'trivia_test')
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    ''' Test for handling GET requests for all categories. '''
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalCategories"])
        self.assertTrue(len(data["categories"]))

    def test_404_requesting_wrong_categories(self):
        res = self.client().get("/categories/1")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    ''' Test for handling GET requests for all questions. '''
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))

    def test_404_sent_requesting_beyound_valid_page(self):
        res = self.client().get("/questions?page=1500")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    
    ''' Test for handling DELETE request for a particular question using the id. '''
    def test_delete_question(self):
        question = Question.query.first().format()
        res = self.client().delete("/questions/" + str(question["id"]))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_422_if_question_id_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    ''' Test for handling search request for related questions. '''
    def test_question_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "country"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))

    def test_404_question_search_without_results(self):
        res = self.client().post("/questions", json={"searchTerm": "johnyflips"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["totalQuestions"], 0)
        self.assertEqual(len(data["questions"]), 0)


    ''' Test for handling CREATE/INSERT request for a new question. '''
    def test_create_new_question(self):
        new_question = {
            "question": "Who has the most ballon d'or ?",
            "answer": "Lionel Messi",
            "difficulty": 3,
            "category": 6
            }
        res = self.client().post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_cannot_create_new_question(self):
        res = self.client().post(".questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    ''' Test for handling GET request for questions based on category. '''
    def test_get_questions_for_category(self):
        curr_category = Category.query.get('1')
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["currentCategory"], curr_category.type)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])

    def test_404_get_questions_from_wrong_category(self):
        res = self.client().get("/categories/1000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    ''' Test for handling POST request to get questions and play the quiz. '''
    def test_get_quizz_questions(self):
        res = self.client().post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": {
                    "id": 1,
                    "type": "Science"
                    }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_404_no_or_bad_input(self):
        res = self.client().post("/quizzes")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()