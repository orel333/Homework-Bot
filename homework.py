import logging
import os
import sys
import time
from typing import Dict, List

from dotenv import load_dotenv
import telegram
import telegram.ext
import requests
from requests.exceptions import ConnectionError

import exceptions as exc

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s - строка %(lineno)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)

logger.addHandler(handler)
handler.setFormatter(formatter)


def get_bot():
    """Создаёт бота.
    Для обращения к нему из любой части кода.
    """
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        logger.debug('Бот успешно инициализирован')
        return bot
    except Exception as error:
        logger.error(
            f'Бота не удалось запустить по причине {error}'
        )


def send_message(bot, message):
    """Отправка сообщения ботом."""
    try:
        logger.debug(f'Попытка обращения к чату ={TELEGRAM_CHAT_ID}=')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except Exception as error:
        logger.error(f'Не удалось отправить сообщение "{message}"'
                     f'по причине ошибки "{error}"', exc_info=True)
    else:
        logger.info(
            f'В Telegram успешно отправлено сообщение "{message}"'
        )


def get_api_answer(current_timestamp):
    """Получение ответа API в формате python."""
    bad_format = False
    cts_type = type(current_timestamp)
    if (cts_type is not int) and (cts_type is not float):
        logger.warning(
            ('Тип current_timestamp не соответствует '
             f'ожидаемому: {cts_type}')
        )
        bad_format = True
    if len(str(int(current_timestamp))) != 10:
        logger.warning(
            ('В переменную current_timestamp передано '
             f'некорректное число: {current_timestamp}')
        )
        bad_format = True
    if bad_format is True:
        timestamp = int(time.time())
    else:
        timestamp = current_timestamp
    # timestamp = 0
    params = {'from_date': timestamp}
    logger.debug(params)
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        resp_json = response.json()
        if response.status_code == 200:
            return resp_json
        SERVER_FAULT_KEYS = ['error', 'code']
        premessage = ''
        fault_keys = False
        for key in SERVER_FAULT_KEYS:
            if key in resp_json:
                fault_keys = True
                error_descr = resp_json.get(key)
                premessage = ('Признак отказа сервера.'
                              f'Ошибка: "{error_descr}"\n')
                # на случай, если и code, и error будет в ответе
                premessage += premessage
        if not fault_keys:
            premessage = f'Недоступен URL "{ENDPOINT}". '
        message = (
            premessage,
            f'Статус ответа API: {response.status_code}'
            f'Запрос: {response.request.__dict__}')
        logger.error(message)
        send_message(get_bot(), message)
        raise ConnectionError('Ответ от эндпойнта отличается от 200')
    except Exception as error:
        message = (
            f'Недоступен URL "{ENDPOINT}" '
            f'по причине: {error}'
        )
        logger.error(message)
        send_message(get_bot(), message)
        raise ConnectionError('Обращение к эндпойнту выдаёт ошибку')


def check_response(response):
    """Проверка корректности ответа API."""
    keys = ['current_date', 'homeworks']

    if not isinstance(response, Dict):
        message = (f'Ответ от API представляет собой {type(response)}, '
                   'а не словарь.')
        logger.error(message)
        send_message(get_bot(), message)
        raise TypeError(
            'Некорректный тип ответа API'
        )
    if keys[0] not in response.keys() or keys[1] not in response:
        no_keys_list = []
        for item in keys:
            if item not in response.keys():
                no_keys_list.append(item)
        message = (f'Отсутствует ожидаемый ключ API: '
                   f'{",".join(no_keys_list)}')
        logger.error(message)
        send_message(get_bot(), message)
        raise exc.ImproperAPIAnswerException(
            'Некорректные ключи в ответе API'
        )
    if not isinstance(response.get('homeworks'), List):
        message = (
            'Перечень домашних работ представляет '
            f'собой {type(response)}, а не список.'
        )
        logger.error(message)
        send_message(get_bot(), message)
        raise TypeError(
            'Некорректный тип перечня домашних работ'
        )
    return response.get('homeworks')


def parse_status(homework):
    """Определяет статус последней работы.
    Готовит сообщение с информацией о нём.
    """
    logger.info('Запущена функция "parse_status"')
    keys = ['homework_name', 'status']
    for key in keys:
        if key not in homework.keys():
            message = f'В ответе API не обнаружен ключ "{key}"'
            logger.error(message)
            send_message(get_bot(), message)
            raise KeyError('Не обнаружены необходимые ключи в ответе API')

    homework_status = homework['status']
    logger.debug(f'Получен статус домашней работы: {homework_status}')
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except Exception as error:
        message = f'Недокументированный статус домашней работы({error})'
        logger.error(message)
        send_message(get_bot(), message)
        raise exc.ImproperAPIAnswerException(
            'Недокументированный статус домашней работы'
        )
    else:
        homework_name = homework['homework_name']
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка полноты набора необходимых данных.
    Для авторизации и доступа к чату.
    """
    TOKENS_DICT = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    if None in TOKENS_DICT.values():
        no_tokens_list = []
        for key in TOKENS_DICT.keys():
            if TOKENS_DICT[key] is None:
                no_tokens_list.append(key)
        count = len([value for value in TOKENS_DICT.values() if value is None])
        message = f'Нет переменных окружения: {",".join(no_tokens_list)}'
        if TOKENS_DICT['PRACTICUM_TOKEN'] is None and count == 1:
            logger.critical(message)
            send_message(get_bot(), message)
            return False
        logger.critical(message)
        return False
    logger.debug('Все переменные окружения доступны')
    return True


def main():
    """Основная логика работы бота."""
    tokens_exist = check_tokens()
    logger.debug(f'check_tokens вернула {tokens_exist}')
    if tokens_exist:

        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())

        while True:
            response = get_api_answer(current_timestamp)
            logger.debug(f'get_api_answer вернула "{response}"')
            try:
                homeworks = check_response(response)
                if homeworks is False:
                    raise exc.ImproperAPIAnswerException(
                        'Получен некорректный ответ API'
                    )
                if len(homeworks) != 0:
                    new_status = parse_status(homeworks[0])
                    logger.debug(f'parse_status выдала "{new_status}"')
                    send_message(
                        bot,
                        new_status
                    )
                else:
                    logger.debug('Новый статус не обнаружен')

                current_timestamp = response.get('current_date')
                time.sleep(RETRY_TIME)

            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message)
                send_message(get_bot(), message)

                time.sleep(RETRY_TIME)
            else:
                continue
    else:
        logger.critical('Переданы не все обязательные переменные окружения')
        raise exc.TokensAreNotGivenException(
            'Ошибка передачи обязательных переменных окружения'
        )


if __name__ == '__main__':
    main()
