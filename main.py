
from datetime import datetime
import threading
from strategy import TradingBot
from trader import get_symbol_specs, close_position
import settings as cfg
from logger import setup_logging
import os
import telebot
from telebot import types
from requests.exceptions import ReadTimeout, ConnectionError
import time

from trader import get_balance, get_position_pnl


chat_id = os.getenv("TELEGRAM_CHAT_ID")
traiding_start = False
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("Start_bot")
btn2 = types.KeyboardButton('Stop_&_Close')
btn3 = types.KeyboardButton('Balance')
btn4 = types.KeyboardButton('PnL')
btn5 = types.KeyboardButton('Stop_&_Save')
markup.add(btn1, btn2, btn5, btn3, btn4)

@bot.message_handler(commands=['start'])
def start(message):
    global chat_id, markup
    bot.send_message(chat_id, "Выберите действие", reply_markup=markup)


def start_traiding():
    global traiding_start
    traiding_start = True


def stop_traiding(traiding_bot):
    global traiding_start
    traiding_start = False
    traiding_bot.close_on_stop = True


def stop_traiding_save(traiding_bot):
    global traiding_start
    traiding_start = False
    traiding_bot.close_on_stop = False


def print_balance():
    global chat_id
    try:
        balance = get_balance()
        bot.send_message(chat_id, f"Текущий баланс: {balance:.2f} USDT")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка получения баланса: {str(e)}")


def print_pnl():
    global chat_id
    try:
        pnl = get_position_pnl(cfg.SYMBOL)
        bot.send_message(chat_id, f"PnL: {pnl}")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка получения PnL: {str(e)}")


def main():
    logger = setup_logging()
    logger.info("Запуск торгового бота...")

    # Загрузить спецификацию символа: tickSize, minQty и т.п.
    get_symbol_specs(cfg.SYMBOL)

    # Создаём и запускаем стратегию
    traiding_bot = TradingBot(tg_bot=bot, chat_id=chat_id, markup=markup, logger=logger)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        global chat_id, markup
        if message.text == "Start_bot":
            bot.send_message(chat_id, f"{datetime.now().strftime('%H:%M:%S %d-%m-%Y')} [BOT ACTIVE] Awaiting signals...", reply_markup=markup)
            start_traiding()
        elif message.text == "Stop_&_Close":
            stop_traiding(traiding_bot)
            bot.send_message(chat_id, message.text, reply_markup=markup)
        elif message.text == "Stop_&_Save":
            stop_traiding_save(traiding_bot)
            bot.send_message(chat_id, message.text, reply_markup=markup)
        elif message.text == "Balance":
            print_balance()
        elif message.text == "PnL":
            print_pnl()

    # Запуск Telegram бота в отдельном потоке
    telegram_thread = threading.Thread(target=bot.infinity_polling, args=(), kwargs={'timeout': 60, 'long_polling_timeout': 60}, daemon=True)
    telegram_thread.start()

    while True:
        try:
            traiding_bot.run(traiding_start)  # Основной цикл робота
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем. Позиции закрыты")
            try:
                close_position(cfg.SYMBOL)
            except Exception as e:
                logger.error(f"Ошибка закрытия позиции: {e}")
            break
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(10) # Пауза перед повторной попыткой
            continue

if __name__ == "__main__":
    main()
