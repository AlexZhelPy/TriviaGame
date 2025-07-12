import random
from datetime import datetime
from typing import Dict, Optional
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
from dotenv import load_dotenv
from urllib.parse import unquote


load_dotenv()

app = Flask(__name__)

# Конфигурация
TRIVIA_API_URL = "https://opentdb.com/api.php"
DEFAULT_QUESTIONS = 10
TIME_LIMIT = 30  # секунд на вопрос
CATEGORIES = {
    9: "Общие знания",
    10: "Книги",
    11: "Фильмы",
    12: "Музыка",
    13: "Мюзиклы и театры",
    14: "Телевидение",
    15: "Видеоигры",
    17: "Наука и природа",
    18: "Компьютеры",
    19: "Математика",
    20: "Мифология",
    21: "Спорт",
    22: "География",
    23: "История",
    24: "Политика",
    25: "Искусство",
    26: "Знаменитости",
    27: "Животные",
    28: "Транспорт"
}

class TriviaGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.start_time = None
        self.total_questions = DEFAULT_QUESTIONS
        self.category = None
        self.difficulty = None

    def fetch_questions(self, amount: int, category: Optional[int], difficulty: Optional[str]) -> bool:
        params = {
            'amount': amount,
            'type': 'multiple',
            'encode': 'url3986'
        }
        if category: params['category'] = category
        if difficulty: params['difficulty'] = difficulty

        try:
            response = requests.get(TRIVIA_API_URL, params=params)
            data = response.json()
            if data['response_code'] == 0:
                self.questions = data['results']
                self.total_questions = len(self.questions)
                self.start_time = datetime.now()
                return True
        except requests.RequestException:
            pass
        return False

    def get_current_question(self) -> Optional[Dict]:
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            answers = q['incorrect_answers'] + [q['correct_answer']]
            random.shuffle(answers)
            return {
                'text': q['question'],
                'answers': answers,
                'correct': q['correct_answer']
            }
        return None

    def check_answer(self, answer: str) -> bool:
        if not answer or self.current_index >= len(self.questions):
            return False

        is_correct = answer == self.questions[self.current_index]['correct_answer']
        if is_correct:
            self.score += self.get_question_points()
        return is_correct

    def next_question(self):
        self.current_index += 1
        self.start_time = datetime.now()

    def get_question_points(self) -> int:
        difficulty = self.questions[self.current_index].get('difficulty', 'medium')
        return {'easy': 1, 'medium': 2, 'hard': 3}.get(difficulty, 1)

    def get_time_left(self) -> int:
        if not self.start_time:
            return TIME_LIMIT
        elapsed = (datetime.now() - self.start_time).seconds
        return max(0, TIME_LIMIT - elapsed)

    def is_complete(self) -> bool:
        return self.current_index >= len(self.questions)

    def get_progress(self) -> Dict:
        return {
            'current': self.current_index + 1,
            'total': self.total_questions,
            'score': self.score
        }


@app.template_filter('urldecode')
def urldecode_filter(s):
    return unquote(s)


# Вспомогательные функции
def init_game():
    if 'game' not in session:
        session['game'] = {}
    return TriviaGame()


def save_game(game: TriviaGame):
    session['game'] = {
        'questions': game.questions,
        'current_index': game.current_index,
        'score': game.score,
        'total': game.total_questions,
        'category': game.category,
        'difficulty': game.difficulty,
        'start_time': game.start_time.isoformat() if game.start_time else None
    }
    session.modified = True


def load_game() -> TriviaGame:
    game = TriviaGame()
    if 'game' in session:
        game_data = session['game']
        game.questions = game_data.get('questions', [])
        game.current_index = game_data.get('current_index', 0)
        game.score = game_data.get('score', 0)
        game.total_questions = game_data.get('total', DEFAULT_QUESTIONS)
        game.category = game_data.get('category')
        game.difficulty = game_data.get('difficulty')
        if 'start_time' in game_data and game_data['start_time']:
            game.start_time = datetime.fromisoformat(game_data['start_time'])
    return game


# Маршруты
@app.route('/')
def home():
    return render_template('home.html', categories=CATEGORIES)


@app.route('/start', methods=['POST'])
def start():
    try:
        game = init_game()
        game.reset_game()

        category = int(request.form['category']) if request.form.get('category') else None
        difficulty = request.form.get('difficulty')
        questions = int(request.form.get('questions', DEFAULT_QUESTIONS))

        if game.fetch_questions(questions, category, difficulty):
            save_game(game)
            return redirect(url_for('play'))
    except (ValueError, KeyError):
        pass
    return redirect(url_for('home'))


@app.route('/play')
def play():
    game = load_game()
    if game.is_complete():
        return redirect(url_for('result'))

    question = game.get_current_question()
    if not question:
        return redirect(url_for('home'))

    return render_template(
        'play.html',
        question=question,
        progress=game.get_progress(),
        time_left=game.get_time_left()
    )


@app.route('/answer', methods=['POST'])
def answer():
    game = load_game()
    answer = request.form.get('answer')

    result = {
        'correct': game.check_answer(answer),
        'progress': game.get_progress(),
        'complete': False
    }

    if not game.is_complete():
        game.next_question()
        save_game(game)
    else:
        result['complete'] = True

    return jsonify(result)


@app.route('/result')
def result():
    game = load_game()
    if not game.is_complete():
        return redirect(url_for('play'))

    return render_template(
        'result.html',
        score=game.score,
        total=game.total_questions,
        category=CATEGORIES.get(game.category, "Все категории"),
        difficulty=game.difficulty.capitalize() if game.difficulty else "Любая"
    )


if __name__ == '__main__':
    app.run(debug=True)
