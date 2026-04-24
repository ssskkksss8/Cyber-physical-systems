# Лабораторная работа 2: NLP

Проект представляет собой proof-of-concept сервис для распознавания SMS-спама с помощью локальной LLM через **Ollama**.

Внутри Docker-контейнера запускаются:

- **Ollama**
- модель **qwen2.5:0.5b**
- **FastAPI**-сервис с HTTP-эндпоинтом для классификации сообщений

Снаружи контейнера запускается Python-скрипт `main.py`, который отправляет тестовые запросы в сервис и формирует отчёты в форматах **CSV**, **Markdown** и **JSON**.

---

## Используемый стек

- Docker
- Docker Compose
- Ollama
- Qwen2.5:0.5b
- FastAPI
- Python
- requests

---

## Архитектура проекта

```text
ollama-lab/
│
├── app/
│   └── main.py              # FastAPI-приложение внутри контейнера
│
├── reports/                 # выходные файлы с результатами
│   ├── report.md
│   ├── report.csv
│   └── log.json
│
├── main.py                  # внешний клиентский скрипт
├── Dockerfile               # сборка контейнера
├── docker-compose.yml       # конфигурация контейнера и проброс портов
├── requirements.txt         # зависимости внешнего Python-скрипта
├── start.sh                 # запуск Ollama и FastAPI внутри контейнера
└── README.md
```

## Как запустить проект
1. Перейти в корень проекта
   cd ollama-lab
2. Собрать и запустить контейнер
   docker compose up --build -d

После запуска контейнера будут доступны:

```
Ollama API: http://localhost:11434
FastAPI API: http://localhost:8000
Swagger UI: http://localhost:8000/docs
```

## Проверка работы Ollama

Проверка списка загруженных моделей:

curl http://localhost:11434/api/tags

В ответе должна присутствовать модель:

```text
qwen2.5:0.5b
Проверка работы FastAPI
Пример запроса через PowerShell
$body = '{"message":"Congratulations! You have won a free vacation. Call now to claim your prize!"}'
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/classify" -ContentType "application/json" -Body $body
Пример ответа
{
"message": "Congratulations! You have won a free vacation. Call now to claim your prize!",
"verdict": 1,
"reasoning": "The message is clearly promoting a free vacation, which is a common type of spam.",
"raw_response": "{...}",
"model": "qwen2.5:0.5b"
}
```
## Где:

verdict = 1 — spam
verdict = 0 — non-spam
Установка зависимостей для внешнего скрипта

На хост-машине должен быть установлен Python.

## Установка зависимостей:

python -m pip install -r requirements.txt
Запуск внешнего скрипта

Из корня проекта выполнить:

python main.py

## После выполнения будут сгенерированы файлы:

reports/report.md — таблица результатов инференса

reports/report.csv — структурированный отчёт

reports/log.json — полный лог запросов и ответов

