### Telegram-бот для проверки статуса домашнего задания Яндекс.Практикум

#### Технологии:
- Python 3.7.0
- python-telegram-bot 13.7

#### Запуск проекта
- Установите и активируйте виртуальное окружение.
- Установите зависимости из файла `requirements.txt`.
```
pip install -r requirements.txt
``` 
- Если Вы не зарегистрированы в TELEGRAM, [зарегистрируйтесь](https://messengers.guru/telegram/kak-zaregistrirovatsya-telegrame)
- Создайте в TELEGRAM бота и получите токен для доступа к его API-интерфейсу:
  - Наберите в TELEGRAM в поиске "BotFather".
  - Выберите бота с точно таким же названием.
  - Наберите и отправьте команду `/start` либо нажмите кнопку `START` внизу экрана, если никогда до этого не пользовались данным сервисом.
  - Наберите и отправьте команду `/newbot`.
  - Ответьте на вопрос BotFather о том, как бот будет называться.
  - Ответьте на вопрос BotFather о том, какой у бота будет username; если такое имя уже есть, придумайте другое.
  - Скопируйте токен для доступа к API-интерфейсу бота.
  - Перейдите по ссылке после слов "You will find it at" - Вы откроете (для себя :) ) своего бота.
  - Нажмите кнопку `START` внизу. 
- Получите ID своего чата в TELEGRAM:
  - Наберите в TELEGRAM в поиске 'userinfobot'.
  - Выберите бота с точно таким же названием.
  - Наберите и отправьте команду `/start` либо нажмите кнопку `START` внизу экрана, если никогда до этого не пользовались данным сервисом.
  - Наберите и отправьте команду `/me`.
  - Запишите номер после "Id:" в ответе бота.
- Получите токен Вашего аккаунта в Яндекс: [здесь](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a).
- - Создайте в папке проекта файл `.env`.
- Запишите в файл `.env` информацию вида[^1]:
```
   PRACTICUM_TOKEN=токен Вашего аккаунта в Яндекс
   TELEGRAM_TOKEN=токен, полученный для Вашего TELEGRAM-бота
   TELEGRAM_CHAT_ID=ID Вашего чата
```
- Сохраните файл `.env`.
- Запустите выполнение программы.
- Откройте созданного Вами бота.

[^1]: Все токены и ID вставляются сразу после "=" без пробелов и кавычек
