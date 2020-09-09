import os
import requests
import telegram
import time
import logging
from dotenv import load_dotenv
from custom_except import ConnectionException

logging.basicConfig(filename='app.log', filemode='a',
                    format='%(name)s - %(levelname)s - %(message)s - %(asctime)s')



load_dotenv()
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_API = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework.get('status') == 'approved':
        verdict = ('Ревьюеру всё понравилось, можно '
                   'приступать к следующему уроку.')
    else:
        logging.error('Возникла ошибка с получением данных')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        logging.error('Возникла ошибка с форматом даты')
        return {}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            URL_API, headers=headers, params=params)
        if homework_statuses.status_code != 200:
            raise ConnectionException()
        return homework_statuses.json()
    except (requests.exceptions.RequestException, CE):
        logging.error('Ошибка соединения, проверьте URL_API и PRACTICUM_TOKEN')
        

def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())


    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                    send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Quit')

