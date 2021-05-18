from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from database_manager import get_chat, language, cursor, connect
from constants import SELECTING_QUANTITY, REQUESTING_PHONE, REQUESTING_ADDRESS, REQUESTING_COMMENTS, \
    CONFIRMING_ORDER, MAIN_PAGE
from typing import Union, List
from callbacks.mainpage import back_to_main
from text import buttons, texts
import datetime
from configurations import DELIVERY_PRICE, UNIT_PRICE, ORDERS_CHANNEL_ID
import requests


def build_menu(
        b: List[KeyboardButton],
        n_cols: int,
        header_buttons: Union[KeyboardButton, List[KeyboardButton]] = None,
        footer_buttons: Union[KeyboardButton, List[KeyboardButton]] = None
) -> List[List[KeyboardButton]]:
    menu = [b[i:i + n_cols] for i in range(0, len(b), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons if isinstance(header_buttons, list) else [header_buttons])
    if footer_buttons:
        menu.append(footer_buttons if isinstance(footer_buttons, list) else [footer_buttons])
    return menu


def preview(update, context: CallbackContext):
    context.bot.send_photo(chat_id=get_chat(update),
                           photo='AgACAgIAAxkBAAMxYKN2sDqj6YNOus2_'
                                 'uQQT1EBIAAGjAAJksTEbAAHAGUkpn3z1K'
                                 'cYAAZIibAABny4AAwEAAwIAA3gAAwNBBAABHwQ',
                           caption=texts['description'][language(update)],
                           parse_mode='HTML')
    quantity(update, context)
    return SELECTING_QUANTITY


def quantity(update, context: CallbackContext):
    button_list = [KeyboardButton(str(s)) for s in range(1, 10)]

    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['choose_quantity'][language(update)],
                             reply_markup=ReplyKeyboardMarkup(
                                 build_menu(button_list,
                                            n_cols=3,
                                            footer_buttons=KeyboardButton(
                                                buttons['back'][language(update)])
                                            )
                                 , resize_keyboard=True),
                             parse_mode='HTML')


def get_quantity(update, context: CallbackContext):
    q = update.message.text
    current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        if int(q) < 20:
            if int(q) >= 5:
                cursor.execute("""INSERT INTO orders(timestamp, customer_id, quantity, 
                unit_price, delivery_cost) VALUES ('{}', '{}', '{}', '{}', '{}')"""
                               .format(time, get_chat(update), q, UNIT_PRICE, 0))
                context.chat_data.update({
                    'order_id': cursor.execute("SELECT last_insert_rowid() FROM orders").fetchone()[0]
                })
                connect.commit()
            else:
                cursor.execute("""INSERT INTO orders(timestamp, customer_id, quantity, 
                unit_price, delivery_cost) VALUES ('{}', '{}', '{}', '{}', '{}')"""
                               .format(time, get_chat(update), q, UNIT_PRICE, DELIVERY_PRICE))
                context.chat_data.update({
                    'order_id': cursor.execute("SELECT last_insert_rowid() FROM orders").fetchone()[0]
                })
                connect.commit()

            request_phone(update, context)
            return REQUESTING_PHONE
        else:
            context.bot.send_message(chat_id=get_chat(update),
                                     text=texts['too_much'][language(update)])
    except ValueError:
        context.bot.send_message(chat_id=get_chat(update),
                                 text=texts['not_quantity'][language(update)])


def request_phone(update, context):
    button = [
        [KeyboardButton(buttons['send_phone_button'][language(update)], request_contact=True)],
        [KeyboardButton(buttons['back'][language(update)])]
    ]

    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['send_number'][language(update)],
                             reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True),
                             parse_mode='HTML')
    return REQUESTING_PHONE


def check_phone(update, context):
    message = update.effective_message

    if message.contact:
        if message.contact.phone_number[:3] == '998' or message.contact.phone_number[1:4] == '998':
            phone = message.contact.phone_number

            cursor.execute("UPDATE orders SET phone_number = '{}' WHERE order_id = '{}'"
                           .format(phone, context.chat_data['order_id']))
            connect.commit()
            cursor.execute("UPDATE users SET phone_number = '{}' WHERE telegram_id = '{}'"
                           .format(phone, get_chat(update)))
            connect.commit()
            request_address(update, context)
            return REQUESTING_ADDRESS
        else:
            update.effective_message.reply_text(texts['country_error'][language(update)])
    else:
        phone = message.text[1:]
        if phone[:3] == '998' and len(phone) == 12 and int(phone):  # chat not found
            context.bot.send_message(chat_id=get_chat(update),
                                     text=texts['good_number'][language(update)])
            request_address(update, context)
            return REQUESTING_ADDRESS
        else:
            update.effective_message.reply_text(texts['format_error'][language(update)])  # language


def request_address(update, context: CallbackContext):
    button = [
        [KeyboardButton(text=buttons['send_location'][language(update)], request_location=True)],
        [KeyboardButton(buttons['back'][language(update)])]
    ]

    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['send_address'][language(update)],
                             reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True))
    return REQUESTING_ADDRESS


def get_address_from_coords(coords):
    PARAMS = {
        "apikey": 'c6e76d4f-0205-49f5-b75b-91067f1acd42',
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }
    r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
    json_data = r.json()
    address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
        "GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
    return address_str


def address(update, context):
    location = update.message.location
    current_position = (location.longitude, location.latitude)

    coords = f"{current_position[0]},{current_position[1]}"

    address_str = get_address_from_coords(coords)

    cursor.execute("UPDATE orders SET location = '{}' WHERE order_id = '{}'"
                   .format(address_str, context.chat_data['order_id']))
    connect.commit()

    request_comments(update, context)
    return REQUESTING_COMMENTS


def request_comments(update, context):
    button = [
        [KeyboardButton(buttons['skip'][language(update)])],
        [KeyboardButton(buttons['back'][language(update)])]
    ]

    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['any_comments?'][language(update)],
                             reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True))


def get_comments(update, context):
    txt = update.effective_message.text

    cursor.execute("UPDATE orders SET comments = '{}' WHERE order_id = '{}'"
                   .format(txt, context.chat_data['order_id']))
    connect.commit()

    checkout(update, context)
    return CONFIRMING_ORDER


def format_price(number):
    raw_list = list(str(number))
    raw_list.insert(-3, ' ')
    formatted = "".join(i for i in raw_list)
    return formatted


def checkout(update, context):
    order_id = context.chat_data['order_id']
    q = cursor.execute("SELECT quantity FROM orders WHERE order_id = '{}'".format(order_id)).fetchone()[0]
    comment = cursor.execute("SELECT comments FROM orders WHERE order_id = '{}'".format(order_id)).fetchone()[0]
    deliver_to = cursor.execute("SELECT location FROM orders WHERE order_id = '{}'".format(order_id)).fetchone()[0]
    user = cursor.execute("SELECT name, phone_number FROM users WHERE telegram_id = '{}'"
                          .format(get_chat(update))).fetchmany()[0]

    if q >= 5:
        total = q * UNIT_PRICE
        cursor.execute("UPDATE orders SET total = '{}' WHERE order_id = '{}'"
                       .format(total, order_id))
        connect.commit()
    else:
        total = q * UNIT_PRICE + DELIVERY_PRICE
        cursor.execute("UPDATE orders SET total = '{}' WHERE order_id = '{}'"
                       .format(total, order_id))
        connect.commit()

    markup = [
        [KeyboardButton(buttons['confirm'][language(update)])],
        [KeyboardButton(buttons['cancel'][language(update)])]
    ]

    txt = texts['checkout'][language(update)]

    context.bot.send_message(chat_id=get_chat(update),
                             text=txt.format(
                                 user[0],
                                 user[1] if user[1][0] == '+' else '+' + user[1],
                                 deliver_to,
                                 texts['no_comments'][language(update)] if comment is None else comment,
                                 q,
                                 format_price(UNIT_PRICE),
                                 format_price(q * UNIT_PRICE) + ' ' + texts['currency'][language(update)],
                                 format_price(total - q * UNIT_PRICE),
                                 texts['currency'][language(update)],
                                 format_price(total),
                                 texts['currency'][language(update)]),
                             reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True),
                             parse_mode='HTML')
    return CONFIRMING_ORDER


def cancel_order(update, context):
    cursor.execute("UPDATE orders SET comments ='CANCELED' WHERE order_id = '{}'".format(context.chat_data['order_id']))
    connect.commit()

    update.effective_message.reply_text(texts['canceled'][language(update)])

    back_to_main(update, context)
    return MAIN_PAGE


def confirm_order(update, context):
    new_order = texts['new_order_for_admin']
    order_id = context.chat_data['order_id']
    timestamp = cursor.execute("SELECT timestamp FROM orders WHERE order_id = '{}'".format(order_id)).fetchone()[0]
    q = cursor.execute("SELECT quantity FROM orders WHERE order_id = '{}'".format(order_id)).fetchone()[0]
    comment = cursor.execute("SELECT comments FROM orders WHERE order_id = '{}'".format(order_id)).fetchone()[0]
    deliver_to = cursor.execute("SELECT location FROM orders WHERE order_id = '{}'".format(order_id)).fetchone()[0]
    user = cursor.execute("SELECT name, phone_number, username, language FROM users WHERE telegram_id = '{}'"
                          .format(get_chat(update))).fetchmany()[0]
    delivery_cost = cursor.execute("SELECT delivery_cost FROM orders WHERE order_id = '{}'"
                                   .format(order_id)).fetchone()[0]

    context.bot.send_message(chat_id=ORDERS_CHANNEL_ID,
                             text=new_order
                             .format(
                                 timestamp,
                                 user[0],
                                 user[1] if user[1][0] == '+' else '+' + user[1],
                                 'тут пусто 🙃' if user[2] is None else user[2],
                                 user[3],
                                 q, format_price(UNIT_PRICE), format_price(q * UNIT_PRICE),
                                 format_price(int(delivery_cost)),
                                 deliver_to,
                                 'без коммента' if comment is None else comment,
                                 format_price(q * UNIT_PRICE + int(delivery_cost))
                             ),
                             parse_mode='HTML')

    context.bot.send_message(chat_id=get_chat(update),
                             text=texts['order_accepted'][language(update)])

    back_to_main(update, context)
    return MAIN_PAGE
