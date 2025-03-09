# Reddit to Telegram Poster

Этот скрипт автоматически собирает популярные посты из Reddit, переводит их на русский язык и публикует на платформе [Telegra.ph](https://telegra.ph). Затем ссылки на созданные посты отправляются в Telegram-канал. Скрипт также сохраняет информацию о публикациях в базу данных MySQL, чтобы избежать дублирования.

---

## Основные функции

1. **Сбор данных с Reddit**:
   - Получает топовые посты из выбранного сабреддита за неделю.
   - Собирает 10 самых популярных комментариев к каждому посту.

2. **Перевод текста**:
   - Автоматически переводит заголовок, текст поста и комментарии с английского на русский язык с помощью Google Translate API.

3. **Публикация на Telegra.ph**:
   - Создает статью на платформе Telegra.ph с переведенным текстом и комментариями.
   - Форматирует контент для удобного чтения (заголовки, параграфы, цитаты).

4. **Отправка ссылок в Telegram**:
   - Отправляет ссылки на созданные статьи в Telegram-канал через Telegram Bot API.

5. **База данных**:
   - Сохраняет уникальные идентификаторы постов в базу данных MySQL, чтобы избежать повторной публикации.

---

## Установка и настройка

### 1. Установка зависимостей
Убедитесь, что у вас установлен Python 3.8 или выше. Установите необходимые библиотеки:

```bash
pip install -r requirements.txt
```

Файл ```requirements.txt``` должен содержать следующие зависимости:
```
praw
requests
sqlalchemy
pymysql
googletrans==4.0.0-rc1
python-dotenv
```
## 2. Настройка переменных окружения
Создайте файл ```.env``` в корневой директории проекта и добавьте следующие переменные:
```
# Reddit API credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=your_user_agent_here

# Telegram Bot credentials
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_name

# Telegra.ph credentials
TELEGRAPH_ACCESS_TOKEN=your_telegraph_access_token_here
TELEGRAPH_AUTHOR_NAME=YourAuthorName

# Database credentials
DATABASE_URL=mysql+pymysql://login:password@ip/name_bd
```

## 3. Создание таблицы в базе данных
Скрипт автоматически создает таблицу ```posted_reddit``` при первом запуске. Если вы хотите создать её вручную, выполните следующий SQL-запрос:
```
CREATE TABLE IF NOT EXISTS posted_reddit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
## Использование
### 1. Запуск скрипта :
Запустите скрипт с помощью команды:
```python script_name.py```
Скрипт выполнит следующие шаги:
* Соберет топовые посты из Reddit.
* Переведет текст на русский язык.
* Создаст статью на Telegra.ph.
* Отправит ссылку на статью в Telegram-канал.
### 2. Автоматизация :
Для автоматической публикации постов настройте выполнение скрипта по расписанию с помощью ```cron``` (Linux/macOS) или ```Task Scheduler ```(Windows).

## Пример работы
### Исходный пост на Reddit:
- Заголовок : "Just submitted my resignation"
- Текст : "Mid-40s. Single. ~$2.25MM nw..."
- Комментарии :
	- "Great decision!"
	- "I support you!"
### Результат на Telegra.ph:
#### Я только что подал заявление об уходе

Мне за 40. Холост. ~2.25 млн долларов...

##### Комментарии:

> user1: Отличное решение!

> user2: Я поддерживаю тебя.
>
### При получении нового поста - отправляется в телеграм канал
![image](https://github.com/user-attachments/assets/f8f11bdb-9ed6-41eb-92ae-bf647adba80e)
### По ссылке открывается сам пост и комментарии к нему
![image](https://github.com/user-attachments/assets/9ac20c13-fb6a-431d-bea0-2f32aa4a19f7)


# Автор
Telegram @djuli1337
[КЛИК](https://t.me/djuli1337)

# Дополнительная информация

- [Reddit API Documentation](https://www.reddit.com/dev/api)
- [Telegra.ph API Documentation](https://telegra.ph/api)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Google Translate API Documentation](https://cloud.google.com/translate/docs)
