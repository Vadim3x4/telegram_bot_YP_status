import os
import requests
import telegram
import time
import logging
from dotenv import load_dotenv


logging.basicConfig(filename='home_work.log', filemode='w', 
                    format='%(name)s - %(levelname)s - %(message)s')

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_API = os.getenv('URL_API')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework.get('status') == 'approved':
        verdict = ('Ревьюеру всё понравилось, можно '
                   'приступать к следующему уроку.')
    else:
        logging.error('Неверный данные API')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            URL_API, headers=headers, params=params)
        if homework_statuses.json().get('homeworks') is None:
            logging.error("Неверные данные API")
            print(homework_statuses.json())
        return homework_statuses.json()
    except (requests.exceptions.RequestException, ValueError):
        logging.exception("Неверный ответ сервера")


def send_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                                        new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get(
                                        'current_date')
            time.sleep(300)

        except Exception as e:
            logging.exception(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
