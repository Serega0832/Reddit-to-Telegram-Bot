import os
from dotenv import load_dotenv
import praw
import requests
from sqlalchemy import create_engine, text
from googletrans import Translator


# Загрузка переменных из .env
load_dotenv()


# Настройка Reddit API
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)


# Подключение к базе данных через SQLAlchemy
def get_db_engine():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("В файле .env не задана переменная DATABASE_URL.")
    return create_engine(database_url)


# Функция для создания таблицы, если она не существует
def create_table_if_not_exists():
    engine = get_db_engine()
    with engine.connect() as connection:
        query = """
        CREATE TABLE IF NOT EXISTS posted_reddit (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id VARCHAR(255) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        connection.execute(text(query))
        connection.commit()
        print("Таблица 'posted_reddit' успешно создана или уже существует.")


# Функция для перевода текста с английского на русский
def translate_text(text):
    translator = Translator()
    try:
        translated = translator.translate(text, src="en", dest="ru")
        return translated.text
    except Exception as e:
        print(f"Ошибка при переводе текста: {e}")
        return text  # Возвращаем оригинальный текст, если перевод не удался


# Функция для получения заголовков, текста и комментариев постов с Reddit
def get_reddit_posts_with_comments():
    subreddit = reddit.subreddit("Fire")  # Выбираем сабреддит
    top_posts = subreddit.top(time_filter="week", limit=5)  # Топовые посты за неделю
    posts = []

    for post in top_posts:
        # Собираем 10 самых популярных комментариев
        comments = []
        post.comments.replace_more(limit=0)  # Удаляем "MoreComments" объекты

        for comment in sorted(post.comments, key=lambda x: x.score, reverse=True)[:10]:
            comments.append({
                "author": comment.author.name if comment.author else "Неизвестный",
                "body": comment.body
            })

        # Переводим заголовок, текст и комментарии
        translated_title = translate_text(post.title)
        translated_content = translate_text(post.selftext)
        translated_comments = [
            {"author": c["author"], "body": translate_text(c["body"])} for c in comments
        ]

        posts.append({
            "post_id": post.id,
            "title": translated_title,
            "content": translated_content,
            "comments": translated_comments
        })

    print(f"Получено {len(posts)} постов с Reddit.")
    return posts


# Функция для проверки, был ли пост уже опубликован
def is_post_published(post_id):
    engine = get_db_engine()
    with engine.connect() as connection:
        query = text("SELECT EXISTS(SELECT 1 FROM posted_reddit WHERE post_id = :post_id) AS is_posted")
        result = connection.execute(query, {"post_id": post_id}).scalar()
    return bool(result)


# Функция для сохранения post_id в базу данных
def save_post_to_db(post_id):
    engine = get_db_engine()
    with engine.connect() as connection:
        try:
            query = text("INSERT INTO posted_reddit (post_id) VALUES (:post_id)")
            connection.execute(query, {"post_id": post_id})
            connection.commit()
            print(f"Пост с ID {post_id} успешно сохранен в базу данных.")
        except Exception as e:
            print(f"Ошибка при сохранении поста с ID {post_id} в базу данных: {e}")


# Функция для создания поста на Telegra.ph
def create_telegraph_post(title, content, comments):
    try:
        # Получаем access_token из .env
        access_token = os.getenv("TELEGRAPH_ACCESS_TOKEN")
        if not access_token:
            print("Ошибка: TELEGRAPH_ACCESS_TOKEN не задан в файле .env.")
            return None

        # Преобразуем контент в формат array of nodes
        formatted_content = [
            {
                "tag": "h3",  # Заголовок второго уровня
                "children": [title]
            },
            {
                "tag": "p",  # Параграф с текстом
                "children": [content[:65000]]  # Ограничиваем длину текста до 65000 символов
            }
        ]

        # Добавляем комментарии
        if comments:
            formatted_content.append({
                "tag": "h4",
                "children": ["Комментарии:"]
            })
            for comment in comments:
                formatted_content.append({
                    "tag": "blockquote",  # Блок цитаты для комментария
                    "children": [
                        f"{comment['author']}: {comment['body'][:500]}"  # Ограничиваем длину комментария
                    ]
                })

        # Создание поста
        post_data = {
            "access_token": access_token,
            "title": title,
            "content": formatted_content,  # Передаем array of nodes
            "author_name": os.getenv("TELEGRAPH_AUTHOR_NAME")
        }
        response = requests.post("https://api.telegra.ph/createPage", json=post_data)
        print("Ответ от Telegra.ph:", response.json())  # Вывод ответа для отладки

        if "result" not in response.json():
            print("Ошибка при создании поста на Telegra.ph:", response.json())
            return None

        print("Пост успешно создан на Telegra.ph.")
        return response.json()["result"]["url"]

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


# Функция для отправки сообщения в Telegram
def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": channel_id, "text": message}
    response = requests.post(url, json=payload)
    print("Ответ от Telegram:", response.json())  # Вывод ответа для отладки


# Основная логика
if __name__ == "__main__":
    # Создаем таблицу, если она не существует
    create_table_if_not_exists()

    # Получаем заголовки, текст и комментарии постов с Reddit
    reddit_posts = get_reddit_posts_with_comments()
    print("Посты с Reddit получены.")  # Вывод постов для отладки

    # Для каждого поста проверяем, был ли он уже опубликован
    for post in reddit_posts:
        post_id = post["post_id"]
        if is_post_published(post_id):
            print(f"Пост с ID {post_id} уже опубликован. Пропускаем...")
            continue

        # Создаем пост на Telegra.ph
        telegraph_url = create_telegraph_post(post["title"], post["content"], post["comments"])
        if telegraph_url:
            # Отправляем ссылку в Telegram
            send_telegram_message(f"Новый пост: {telegraph_url}")
            # Сохраняем post_id в базу данных
            save_post_to_db(post_id)
