# 🎮 Викторина

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Приложение для викторин с вопросами.

## ✨ Особенности

- 📚 Загрузка вопросов из Open Trivia DB API
- ⏱️ Таймер на каждый вопрос
- 📊 Подсчет очков с учетом сложности

## 🛠 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/git@github.com:AlexZhelPy/TriviaGame.git
```
2. Установите зависимости:

```bash
pip install -r requirements.txt
```
3. Запустите приложение:

```bash
python app.py
```
Приложение будет доступно по адресу: http://localhost:5000

## 📝 Используемые технологии
- Python 3.8+

- Flask (веб-фреймворк)

- requests (работа с API)

- Bootstrap 5 (интерфейс)

## ⚙️ Настройка
Вы можете настроить параметры викторины в файле app.py:

```python
# Основные настройки
DEFAULT_QUESTIONS = 10  # Количество вопросов по умолчанию
TIME_LIMIT = 30         # Время на ответ в секундах
```

## 📜 Лицензия
Этот проект распространяется под лицензией MIT.
