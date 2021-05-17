from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

import text
from database_manager import get_chat, language, cursor, connect
from constants import SELECTING_QUANTITY, REQUESTING_PHONE, REQUESTING_ADDRESS, REQUESTING_COMMENTS, \
    CONFIRMING_ORDER
from typing import Union, List
from callbacks.mainpage import back_to_main
from text import buttons, texts
import datetime
from configurations import DELIVERY_PRICE, UNIT_PRICE
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
                           photo='AgACAgIAAxkBAAMKYKIdCbYXhUlpdlHadmv2BplSoUkAAtayMRuvn'
                                 'BhJg-Szr5vYGO091o2iLgADAQADAgADbQADiGoCAAEfBA'
                           ,
                           caption=text.captions['money'][language(update)])
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


def checkout(update, context):
    order_id = context.chat_data['order_id']
    q = cursor.execute("SELECT quantity FROM orders WHERE order_id = '{}'".format(order_id)).fetchone()[0]
    price = cursor.execute("SELECT unit_price FROM orders WHERE order_id = '{}'".format(order_id)).fetchone()[0]
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
                             text=f'{txt}quantity-{q} price-{price} delivery-{DELIVERY_PRICE} total-{total}',
                             reply_markup=ReplyKeyboardMarkup(markup, resize_keyboard=True))
    return CONFIRMING_ORDER


def cancel_order(update, context):
    cursor.execute("UPDATE orders SET comments ='CANCELED' WHERE last_insert_rowid()")
    connect.commit()

    back_to_main(update, context)
