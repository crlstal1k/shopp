import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import datetime
from random import choice, randint
from aiogram.dispatcher import FSMContext
from string import ascii_letters, digits
from aiogram.types import message, message_entity, message_id, user
from configparser import ConfigParser
from aiogram.types.callback_query import CallbackQuery

import markups
import state_handler
import user as usr
import stats
import item as itm
import text_templates as tt


conn = sqlite3.connect('data.db')
c = conn.cursor()

conf = ConfigParser()
conf.read('config.ini', encoding='utf8')

storage = MemoryStorage()
bot = Bot(token=conf['main']['token'])
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    conf = ConfigParser()
    conf.read('config.ini', encoding='utf8')
    user = usr.User(message.chat.id)

    markupMain = markups.get_markup_main()
    if user.is_admin():
        markupMain.row(markups.btnAdminPanel)
    if user.is_support():
        markupMain.row(markups.btnSupportMenu)

    if conf["shop_settings"]["enable_sticker"] == "1":
        sti = open('AnimatedSticker.tgs', 'rb')
        await bot.send_sticker(message.chat.id, sti)
        sti.close()
    await bot.send_message(
        chat_id=message.chat.id,
        text=conf["shop_settings"]["shop_greeting"],
        reply_markup=markupMain,
    )


@dp.message_handler()
async def handle_text(message):
    user = usr.User(message.chat.id)
    conf = ConfigParser()
    conf.read('config.ini', encoding='utf8')
    
    if message.text == tt.admin_panel:
        if user.is_admin():
            await bot.send_message(
                chat_id=message.chat.id,
                text=tt.admin_panel,
                reply_markup=markups.get_markup_admin(),
            )
    elif message.text == tt.faq:
        await bot.send_message(
            chat_id=message.chat.id,
            text=tt.get_faq_template(conf["shop_settings"]["shop_name"]),
            reply_markup=markups.get_faq_markup(),
        )
    elif message.text == tt.profile:
        await bot.send_message(
            chat_id=message.chat.id,
            text=tt.get_profile_template(user.get_id(), user.get_orders(), user.get_balance(), user.get_register_date()),
            reply_markup=markups.get_markup_profile(user_id=user.get_id()),
        )
    elif message.text == tt.catalogue: 
        await bot.send_message(
            chat_id=message.chat.id,
            text=tt.catalogue,
            reply_markup=markups.get_markup_catalogue(itm.get_cat_list()),
        )
    else:
        await bot.send_message(message.chat.id, 'Не могу понять команду :(')


@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    call_data = callback_query.data
    
    conf = ConfigParser()
    conf.read('config.ini', encoding='utf8')
    user = usr.User(chat_id)
    
    if call_data.startswith("admin_") and user.is_admin():
        call_data = call_data[6:]
        
        if call_data == "adminPanel":
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=callback_query.message.message_id,
                text=tt.admin_panel,
                reply_markup=markups.get_markup_admin(),
            )

        # Admin tabs
        # Item management
        elif call_data == "itemManagement":
            await bot.edit_message_text(
                text=tt.item_management,
                message_id=callback_query.message.message_id,
                chat_id=chat_id,
                reply_markup=markups.get_markup_itemManagement()
            )
        elif call_data == "addCat":
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=callback_query.message.message_id,
                text="Введите название новой категории или нажмите на кнопку \"Назад\".",
                reply_markup=markups.single_button(markups.btnBackItemManagement),
            )
            await state_handler.addCat.name.set()
            state = Dispatcher.get_current().current_state()
            await state.update_data(state_message=callback_query.message.message_id)
        elif call_data == "editCatChooseCategory":
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=callback_query.message.message_id,
                text="Выберите категорию, которую хотите изменить или нажмите на кнопку \"Назад\".",
                reply_markup=markups.get_markup_editCatChooseCategory(itm.get_cat_list()),
            )
        elif call_data.startswith("editCatDelete"):
            cat = itm.Category(call_data[13:])

            try:
                text = f"Категория {cat.get_name()} была успешно удалена."
                cat.delete()
            except:
                text = f"Произошла ошибка!"
                
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=callback_query.message.message_id,
                text=text,
                reply_markup=markups.single_button(markups.btnBackEditCatChooseCategory),
            )
        elif call_data.startswith("editCatName"):
            pass
        elif call_data.startswith("editCat"):
            cat = itm.Category(call_data[7:])
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=callback_query.message.message_id,
                text=tt.get_category_data(cat),
                reply_markup=markups.get_markup_editCat(cat.get_id()),
            )
        elif call_data == "addItem":
            pass
        elif call_data == "editItem":
            pass

        # User management
        elif call_data == "userManagement":
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=callback_query.message.message_id,
                text=tt.user_management,
                reply_markup=markups.get_markup_userManagement(),
            )

        elif call_data == "seeUserProfile":
            pass

        elif call_data == "notifyEveryone":
            pass

        # Stats
        elif call_data == "shopStats":
            await bot.edit_message_text(
                text=tt.shop_stats,
                chat_id=chat_id,
                message_id=callback_query.message.message_id,
                reply_markup=markups.get_markup_shopStats()
            )

        elif call_data == "registrationStats":
            pass
    
        elif call_data == "orderStats":
            pass

        # Settings
        elif call_data == "shopSettings":
            await bot.edit_message_text(
                text=tt.bot_settings,
                message_id=callback_query.message.message_id,
                chat_id=chat_id,
                reply_markup=markups.get_markup_shopSettings()
            )

        elif call_data == "mainSettings":
            pass

        elif call_data == "statsSettings":
            pass
            

    if call_data != None:
        pass
    elif call_data[:3] == 'cat':
        catMarkup = types.InlineKeyboardMarkup()
        c.execute(f"SELECT * FROM cats WHERE id={callText[3:]}")
        try:
            cat = list(c)[0]
            
            c.execute(f"SELECT * FROM items WHERE cat_id={callText[3:]}")
            items = list(c)
            for item in items:
                amount = get_item_count(item[0])
                text = f'{item[1]} - {amount}шт. - {item[2]}руб.'
                btnCat = types.InlineKeyboardButton(text=text, callback_data=f"item{item[0]}")
                if item[5] == 1:
                    catMarkup.add(btnCat)
            catMarkup.add(markups.get_cat_back())
            await bot.edit_message_text(text=f'➖➖➖➖➖➖➖➖➖\n{cat[1]}\n➖➖➖➖➖➖➖➖➖',
                                        chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=catMarkup)
        except:
            markup = types.InlineKeyboardMarkup()
            markup.add(markups.get_cat_back())
            await bot.edit_message_text(
                text="Категории не существует или произошла ошибка!",
                message_id=callback_query.message.message_id,
                chat_id=chatid,
                reply_markup=markup
            )
    
    
        
    elif callText == "addCat":
        await bot.edit_message_text(
            text="Введите название новой категории или нажмите на кнопку \"Назад\".",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_items()
        )
        await state_handler.addCat.catname.set()
        
    elif callText == "editCats":
        c.execute("SELECT * FROM cats")
        cats = list(c)
        if cats:
            markup = types.InlineKeyboardMarkup()
            for cat in cats:
                markup.add(types.InlineKeyboardButton(text=f"[{cat[0]}] {cat[1]}", callback_data=f"editCat{cat[0]}"))
            markup.add(markups.goBackItems)
            
            await bot.edit_message_text(
                text="Выберите категорию, которую хотите изменить.",
                message_id=callback_query.message.message_id,
                chat_id=chatid,
                reply_markup=markup
            )
        else:
            await bot.edit_message_text(
                text="Вы пока не добавили ни одной категории.",
                message_id=callback_query.message.message_id,
                chat_id=chatid,
                reply_markup=markups.get_items_back()
            )
        
    elif callText[:9] == "deleteCat":
        catid = callText[9:]
        c.execute(f"SELECT * FROM cats WHERE id={catid}")
        cat = list(c)[0]
        c.execute(f"DELETE FROM cats WHERE id={catid}")
        conn.commit()
        await bot.edit_message_text(
            text=f"Категория \"{cat[1]}\" с ID {cat[0]} была удалена!",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_back_cats_edit()
        )
    
    elif callText[:11] == "editNameCat":
        await bot.edit_message_text(
            text="Введите новое название категории или нажмите на кнопку \"Назад\".",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_cats(callText[11:])
        )
        await state_handler.changeCatName.catname.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(catid=callText[11:])
        
    elif callText[:7] == "addItem":
        await bot.edit_message_text(
            text="Введите название нового товара или нажмите на кнопку \"Назад\"",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_additem()
        )
        await state_handler.addItem.itemname.set()
    
    elif callText == "editItems":
        c.execute("SELECT * FROM cats")
        markup = types.InlineKeyboardMarkup()
        for cat in list(c):
            markup.add(types.InlineKeyboardButton(text=f"[{cat[0]}] {cat[1]}", callback_data=f"editItemsCat{cat[0]}"))
        markup.add(markups.goBackItems)
        await bot.edit_message_text(
            text=f"Выберите категорию",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markup
        )

    elif callText[:12] == "editItemsCat":
        c.execute(f"SELECT * FROM cats WHERE id={callText[12:]}")
        cat = list(c)[0]
        c.execute(f"SELECT * FROM items WHERE cat_id={callText[12:]}")
        markup = types.InlineKeyboardMarkup()
        for item in list(c):
            markup.add(types.InlineKeyboardButton(text=item[1], callback_data=f"editItem{item[0]}"))
        markup.add(types.InlineKeyboardButton(text="🔙Назад", callback_data="editItems"))
        await bot.edit_message_text(
            text=f"Выберите товар",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markup
        )

    elif callText[:8] == "editItem":
        c.execute(f"SELECT * FROM items WHERE id={callText[8:]}")
        item = list(c)[0]
        c.execute(f"SELECT * FROM cats WHERE id={item[3]}")
        cat = list(c)[0]
        await bot.edit_message_text(
            text=f"➖➖➖➖➖➖➖➖➖\n{item[1]} - {item[2]}руб.\nКатегория: \"{cat[1]}\"\n➖➖➖➖➖➖➖➖➖\n{item[4]}",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markups.get_edit_item_markup(item)
        )

    elif callText[:11] == "editCatItem":
        markup = types.InlineKeyboardMarkup()
        c.execute("SELECT * FROM cats")
        for cat in list(c):
            markup.add(types.InlineKeyboardButton(text=f"[{cat[0]}] {cat[1]}", callback_data=f"setCatItem{cat[0]}"))
        markup.add(types.InlineKeyboardButton(text="🔙Назад", callback_data="cancelStatesEditItem"))
        c.execute(f"SELECT * FROM items WHERE id={callText[11:]}")
        await bot.edit_message_text(
            text=f"Выберите категорию для {list(c)[0][1]} или нажмите на кнопку \"Назад\"",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markup
        )
        await state_handler.changeItemCat.cat.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(itemid=callText[11:])

    elif callText[:7] == "editCat":
        c.execute(f"SELECT * FROM cats WHERE id={callText[7:]}")
        cat = list(c)[0]
        
        await bot.edit_message_text(
            text=cat[1],
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cat_edit_markup(cat[0])
        )

    elif callText[:12] == "editDescItem":
        c.execute(f"SELECT * FROM items WHERE id={callText[12:]}")
        item = list(c)[0]
        await bot.edit_message_text(
            text=f"Введите новое описание для {item[1]} или нажмите кнопку \"Назад\"",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markups.get_cancel_states_editItem(callText[12:])
        )
        await state_handler.ChangeItemDesc.desc.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(itemid=callText[12:])

    elif callText[:8] == "hideItem":
        c.execute(f"SELECT * FROM items WHERE id={callText[8:]}")
        item = list(c)[0]
        c.execute(f"UPDATE items SET active={1 if item[5] == 0 else 0} WHERE id={callText[8:]}")
        conn.commit()
        c.execute(f"SELECT * FROM items WHERE id={callText[8:]}")
        item = list(c)[0]
        c.execute(f"SELECT * FROM cats WHERE id={item[3]}")
        cat = list(c)[0]
        await bot.edit_message_text(
            text=f"➖➖➖➖➖➖➖➖➖\n{item[1]} - {item[2]}руб.\nКатегория: \"{cat[1]}\"\n➖➖➖➖➖➖➖➖➖\n{item[4]}",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markups.get_edit_item_markup(item)
        )

    elif callText[:17] == "deleteItemConfirm":
        c.execute(f"SELECT * FROM items WHERE id={callText[17:]}")
        item = list(c)
        c.execute(f"DELETE FROM items WHERE id={callText[17:]}")
        conn.commit()

        await bot.edit_message_text(
            text="📦Управление товаром",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_item_management_markup()
        )

    elif callText[:10] == "deleteItem":
        c.execute(F"SELECT * FROM items WHERE id={callText[10:]}")
        item = list(c)[0]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="✅Да", callback_data=f"deleteItemConfirm{callText[10:]}"), types.InlineKeyboardButton(text="❌Нет", callback_data=f"editItem{callText[10:]}"))
        await bot.edit_message_text(
            text=f"Вы уверены, что хотите удалить {item[1]}?",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markup
        )

    elif callText[:12] == "editNameItem":
        c.execute(f"SELECT * FROM items WHERE id={callText[12:]}")
        item = list(c)[0]
        await bot.edit_message_text(
            text=f"Введите новое название для \"{item[1]}\" или нажмите на кнопку \"Назад\"",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markups.get_cancel_states_editItem(item[0])
        )
        await state_handler.ChangeItemName.name.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(itemid=callText[12:])
    
    elif callText[:13] == "editPriceItem":
        c.execute(f"SELECT * FROM items WHERE id={callText[13:]}")
        item = list(c)[0]
        await bot.edit_message_text(
            text=f"Введите новую цену для \"{item[1]}\" или нажмите на кнопку \"Назад\"",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markups.get_cancel_states_editItem(callText[13:])
        )
        await state_handler.ChangeItemPrice.price.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(itemid=callText[13:])
        
    elif callText[:4] == 'item':
        c.execute(f"SELECT * FROM items WHERE id={callText[4:]}")
        for item in c:
            pass
        cat_id = item[3]
        await bot.edit_message_text(
                                    text=f'➖➖➖➖➖➖➖➖➖\n{item[1]} - {item[2]}руб.\n➖➖➖➖➖➖➖➖➖\n{item[4]}',
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=markups.get_item_markup(item[0], cat_id)
                                    )
    elif callText[:7] == 'confirm':
        c.execute(f"SELECT * FROM items WHERE id={callText[7:]}")
        for item in c:
            pass
        await bot.edit_message_text(
            text=f'Вы уверены, что хотите купить {item[1]} за {item[2]}?',
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=markups.get_confirm_buy_markup(callText[7:])
        )
     
    elif callText[:17] == "changeUserBalance":
        await bot.edit_message_text(
            text=f"Введите новый баланс пользователя с ID {callText[17:]} или нажмите на кнопку \"Назад\".",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_user(callText[17:])
        )
        await state_handler.changeUserBalance.bal.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(userid=callText[17:])

    elif callText[:15] == "removeUserAdmin":
        userid = callText[15:]
        if str(userid) != str(chatid):
            profuser = usr.User(userid)
            profuser.set_admin(0)
            text=f"➖➖➖➖➖➖➖➖➖➖\n📝id: {userid}\n📈Кол-во заказов: {len(usr.get_user_orders(userid))}\n💸Баланс: {profuser.get_balance()} руб.\nДата регистрации: {profuser.get_register_date()}\n➖➖➖➖➖➖➖➖➖➖"
            await bot.edit_message_text(
                text=text,
                message_id=callback_query.message.message_id,
                chat_id=chatid,
                reply_markup=markups.get_seeUserProfile_markup(userid)
            )
        
    elif callText[:13] == "makeUserAdmin":
        userid = callText[13:]
        profuser = usr.User(userid)
        profuser.set_admin(1)
        text=f"➖➖➖➖➖➖➖➖➖➖\n📝id: {userid}\n📈Кол-во заказов: {len(usr.get_user_orders(userid))}\n💸Баланс: {profuser.get_balance()} руб.\nДата регистрации: {profuser.get_register_date()}\n➖➖➖➖➖➖➖➖➖➖"
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_seeUserProfile_markup(userid)
        )
    
    elif callText[:18] == "removeUserSupplier":
        userid = callText[18:]
        profuser = usr.User(userid)
        profuser.set_supplier(0)
        text=f"➖➖➖➖➖➖➖➖➖➖\n📝id: {userid}\n📈Кол-во заказов: {len(usr.get_user_orders(userid))}\n💸Баланс: {profuser.get_balance()} руб.\nДата регистрации: {profuser.get_register_date()}\n➖➖➖➖➖➖➖➖➖➖"
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_seeUserProfile_markup(userid)
        )
    
    elif callText[:16] == "makeUserSupplier":
        userid = callText[16:]
        profuser = usr.User(userid)
        profuser.set_supplier(1)
        text=f"➖➖➖➖➖➖➖➖➖➖\n📝id: {userid}\n📈Кол-во заказов: {len(usr.get_user_orders(userid))}\n💸Баланс: {profuser.get_balance()} руб.\nДата регистрации: {profuser.get_register_date()}\n➖➖➖➖➖➖➖➖➖➖"
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_seeUserProfile_markup(userid)
        )
    
    elif callText[:17] == "removeUserSupport":
        userid = callText[17:]
        profuser = usr.User(userid)
        profuser.set_support(0)
        text=f"➖➖➖➖➖➖➖➖➖➖\n📝id: {userid}\n📈Кол-во заказов: {len(usr.get_user_orders(userid))}\n💸Баланс: {profuser.get_balance()} руб.\nДата регистрации: {profuser.get_register_date()}\n➖➖➖➖➖➖➖➖➖➖"
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_seeUserProfile_markup(userid)
        )
    
    elif callText[:15] == "makeUserSupport":
        userid = callText[15:]
        profuser = usr.User(userid)
        profuser.set_support(1)
        text=f"➖➖➖➖➖➖➖➖➖➖\n📝id: {userid}\n📈Кол-во заказов: {len(usr.get_user_orders(userid))}\n💸Баланс: {profuser.get_balance()} руб.\nДата регистрации: {profuser.get_register_date()}\n➖➖➖➖➖➖➖➖➖➖"
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_seeUserProfile_markup(userid)
        )
        
    elif callText[:13] == "seeUserOrders":
        userid = callText[13:]
        markup = types.InlineKeyboardMarkup()
        if not usr.get_user_orders(userid):
            text = f"У пользователя с ID {userid} нет заказов."
        else:
            text = f"Заказы пользователя с ID {userid}."
            for order in usr.get_user_orders(userid):
                try:
                    c.execute(f"SELECT * FROM items WHERE id={order[2]}")
                    itemname = list(c)[0][1]
                except:
                    itemname = "Товар был удалён или произошла ошибка."
                markup.add(types.InlineKeyboardButton(text=f"[{itemname}] - {order[0]}", callback_data=f"seeOrderUser{order[0]}"))
        markup.add(markups.get_back_user_btn(userid))
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markup
        )
        
    elif callText[:12] == "seeOrderUser":
        orderid = callText[12:]
        c.execute(f"SELECT * FROM orders WHERE order_id={orderid}")
        order = list(c)[0]
        c.execute(f"SELECT * FROM items WHERE id={order[2]}")
        item = list(c)[0]
        text = f"➖➖➖➖➖➖➖➖➖\nЗаказ номер {orderid}\n➖➖➖➖➖➖➖➖➖\nТовар: {item[1]}\nЛогин: {order[3].split(':')[0]}\nПароль: {order[3].split(':')[1]}\nДата заказа: {order[4]}"
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_back_user_orders_markup(order[1])
        )
    
    elif callText[:8] == "userBack":
        userid = callText[8:]
        profuser = usr.User(userid)
        profuser.set_support(1)
        text=f"➖➖➖➖➖➖➖➖➖➖\n📝id: {userid}\n📈Кол-во заказов: {len(usr.get_user_orders(userid))}\n💸Баланс: {profuser.get_balance()} руб.\nДата регистрации: {profuser.get_register_date()}\n➖➖➖➖➖➖➖➖➖➖"
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_seeUserProfile_markup(userid)
        )
        
    elif callText[:3] == 'buy':
        itemid = callText[3:]
        c.execute(f"SELECT * FROM items WHERE id={itemid}")
        for item in c:
            pass

        if get_item_count(itemid) > 0:
            if item[2] <= user.get_balance():

                c.execute(f"SELECT * FROM item_stock WHERE item_id={itemid}")
                unused_accounts = list(c)
                account = choice(unused_accounts)
                login = account[2]
                password = account[3]

                usr.set_user_balance(user_id=chatid, price=item[2], remove_value=True)

                if get_item_count(itemid) < 5:
                    for notif in usr.get_notif_list():
                        await bot.send_message(chat_id=notif[0],
                                               text=f'Товара {item[1]} всего {get_item_count(item[0]) - 1}шт. в наличии!')
                c.execute(f"DELETE FROM item_stock WHERE login='{login}' AND password='{password}'")

                unique_fl = True
                while unique_fl:
                    order_id = randint(1000000000, 9999999999)
                    c.execute(f"SELECT * FROM orders WHERE order_id='{order_id}'")
                    if len(list(c)) == 0:
                        unique_fl = False

                logpass = f"{login}:{password}"
                c.execute(f"INSERT INTO orders VALUES({order_id}, {chatid}, {itemid}, '{logpass}', '{str(datetime.datetime.now())[:-7]}')")

                conn.commit()
                text = f'➖➖➖➖➖➖➖➖➖\n' \
                       f'Заказ номер {order_id}\n' \
                       f'➖➖➖➖➖➖➖➖➖\n' \
                       f'Логин: {login}\n' \
                       f'Пароль: {password}\n'
                await bot.delete_message(chat_id=chatid, message_id=callback_query.message.message_id)
                await bot.send_message(
                    chat_id=chatid,
                    text=text
                )
            else:
                await bot.delete_message(chat_id=chatid, message_id=callback_query.message.message_id)
                await bot.send_message(
                    chat_id=chatid,
                    text=f'У вас недостаточно средств :(\nПерейдите в профиль, чтобы пополнить баланс!'
                )
        else:
            await bot.delete_message(chat_id=chatid, message_id=callback_query.message.message_id)
            await bot.send_message(
                chat_id=chatid,
                text=f'Товара {item[1]} нет в наличии'
            )
    elif callText == 'contacts':
        contactsMarkup = types.InlineKeyboardMarkup()
        contactsMarkup.add(markups.get_faq_back())
        text = conf['shop_settings']['shop_contacts'] + '\n\nБот сделан @w1png'
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=contactsMarkup,
        )
        
    elif callText == "notifyAll":
        msg = "Введите сообщение, которое вы хотите отправить всем пользователям, или нажмите на кнопку \"Назад\"."
        await bot.edit_message_text(
            text=msg,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_clients()
        )
        await state_handler.notifyAll.message.set()
                
    elif callText == 'refund':
        refundMarkup = types.InlineKeyboardMarkup()
        refundMarkup.add(markups.get_faq_back())
        text = conf['shop_settings']['refund_policy']
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=refundMarkup,
        )
    elif callText == 'orders':
        orders = usr.get_user_orders(chatid)
        ordersMarkup = types.InlineKeyboardMarkup()
        for order in orders:
            c.execute(f"SELECT * FROM items WHERE id={order[2]}")
            for item in c:
                pass
            btn = types.InlineKeyboardButton(text=f'[{item[1]}] - {order[0]}', callback_data=f'order{order[0]}')
            ordersMarkup.add(btn)
        text = '➖➖➖➖➖➖➖➖➖\nВаши заказы\n➖➖➖➖➖➖➖➖➖'
        ordersMarkup.add(markups.get_profile_back())
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=ordersMarkup
        )
        
    elif callText == "close":
        try:
            await bot.delete_message(
                message_id=callback_query.message.message_id,
                chat_id=chatid
            )
        except:
            await bot.send_message(
                text="Сообщение не может быть удалено!",
                chat_id=chatid
            )

    elif callText == 'backAdmin':
        if user.is_admin():
            await bot.edit_message_text(
                text='🔴Админ панель',
                message_id=callback_query.message.message_id,
                chat_id=chatid,
                reply_markup=markups.get_admin_markup()
            )

    elif callText == 'mainSettings':
        await bot.edit_message_text(
            text='🛠Основные настройки',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_main_settings_markup()
        )

    elif callText == 'qiwiSettings':
        await bot.edit_message_text(
            text='🥝Настройки QIWI кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_qiwi_settings()
        )

    elif callText == "seeUserProfile":
        await bot.edit_message_text(
            text="Введите ID пользователя или нажмите на кнопку \"Назад\"",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_clients()
        )
        await state_handler.seeUserProfile.userid.set()

    elif callText == 'qiwiOn':
        conf.set('payment_settings', 'qiwi_isactive', '1')
        with open('config.ini', 'w') as config:
            conf.write(config)
        await bot.edit_message_text(
            text='🥝Настройки QIWI кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_qiwi_settings()
        )

    elif callText == 'qiwiOff':
        conf.set('payment_settings', 'qiwi_isactive', '0')
        with open('config.ini', 'w') as config:
            conf.write(config)

        await bot.edit_message_text(
            text='🥝Настройки QIWI кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_qiwi_settings()
        )

    elif callText == 'btcSettings':
        await bot.edit_message_text(
            text='💵Настройки BTC кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_btc_settings_markup(),
        )

    elif callText == 'btcOn':
        conf.set('payment_settings', 'btc_isactive', '1')
        with open('config.ini', 'w') as config:
            conf.write(config)
        await bot.edit_message_text(
            text='💵Настройки BTC кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_btc_settings_markup(),
        )

    elif callText == 'btcOff':
        conf.set('payment_settings', 'btc_isactive', '0')
        with open('config.ini', 'w') as config:
            conf.write(config)
        await bot.edit_message_text(
            text='💵Настройки BTC кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_btc_settings_markup(),
        )

    elif callText == 'balance':
        await bot.edit_message_text(
            text='💰Пополнение баланса',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_balance_markup()
        )

    elif callText == "shopStats":
        pass

    elif callText[:10] == "orderStats":
        callText = callback_query.data
        chatid = callback_query.message.chat.id
        charts = stats.OrderCharts()

        if callText == "orderStats":
            await bot.edit_message_text(
                text=f"📦Статистика заказов",
                chat_id=chatid,
                message_id=callback_query.message.message_id,
                reply_markup=markups.get_order_stats_markup()
            )

        elif callText == "orderStatsAllTime":
            try:
                await bot.delete_message(
                    chat_id=chatid,
                    message_id=callback_query.message.message_id
                )
                await bot.send_photo(
                    caption="Заказы за всё время",
                    chat_id=chatid,
                    photo=charts.all_time(),
                    reply_markup=markups.get_order_stats_back()
                )
            except:
                await bot.send_message(
                    chat_id=chatid,
                    text="Произошла ошибка!"
                )

        elif callText == "orderStatsMonthly":
            try:
                await bot.delete_message(
                    chat_id=chatid,
                    message_id=callback_query.message.message_id
                )
                await bot.send_photo(
                    caption="Заказы за последние 30 дней",
                    chat_id=chatid,
                    photo=charts.monthly(),
                    reply_markup=markups.get_order_stats_back()
                )
            except:
                await bot.send_message(
                    chat_id=chatid,
                    text="Произошла ошибка!"
                )
        
        elif callText == "orderStatsWeekly":
            try:
                await bot.delete_message(
                    chat_id=chatid,
                    message_id=callback_query.message.message_id
                )
                await bot.send_photo(
                    caption="Заказы за последние 7 дней",
                    chat_id=chatid,
                    photo=charts.weekly(),
                    reply_markup=markups.get_order_stats_back()
                )
            except:
                await bot.send_message(
                    chat_id=chatid,
                    text="Произошла ошибка!"
                )
        
        elif callText == "orderStatsDaily":
            try:
                await bot.delete_message(
                    chat_id=chatid,
                    message_id=callback_query.message.message_id
                )
                await bot.send_photo(
                    caption="Заказы за сегодня",
                    chat_id=chatid,
                    photo=charts.daily(),
                    reply_markup=markups.get_order_stats_back()
                )
            except:
                await bot.send_message(
                    chat_id=chatid,
                    text="Произошла ошибка!"
                )

        elif callText == "orderStatsBack":
            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_message(
                text=f"📦Статистика заказов",
                chat_id=chatid,
                reply_markup=markups.get_order_stats_markup()
            )
    
    elif callText[:9] == "userStats":
        callText = callback_query.data
        chatid = callback_query.message.chat.id
        charts = stats.RegistrationCharts()
        

        if callText == 'userStats':
            await bot.edit_message_text(
                text='👥Статистика регистраций',
                chat_id=chatid,
                message_id=callback_query.message.message_id,
                reply_markup=markups.get_user_stats_markup()
            )

        elif callText == 'userStatsAllTime':
            try:
                await bot.delete_message(
                    chat_id=chatid,
                    message_id=callback_query.message.message_id
                )
                await bot.send_photo(
                    chat_id=chatid,
                    caption='Регистрации за всё время',
                    photo=charts.all_time(),
                    reply_markup=markups.get_user_stats_back(),
                )
            except:
                await bot.send_message(
                    chat_id=chatid,
                    text="Произошла ошибка!"
                )

        elif callText == 'userStatsMonth':
            try:
                await bot.delete_message(
                    chat_id=chatid,
                    message_id=callback_query.message.message_id
                )
                await bot.send_photo(
                    chat_id=chatid,
                    caption='Регистрации за последние 30 дней',
                    photo=charts.monthly(),
                    reply_markup=markups.get_user_stats_back(),
                )
            except:
                await bot.send_message(
                    chat_id=chatid,
                    text="Произошла ошибка!"
                )

        elif callText == 'userStatsWeek':
            try:
                await bot.delete_message(
                    chat_id=chatid,
                    message_id=callback_query.message.message_id
                )
                await bot.send_photo(
                    chat_id=chatid,
                    caption='Регистрации за последние 7 дней',
                    photo=charts.weekly(),
                    reply_markup=markups.get_user_stats_back(),
                )
            except:
                await bot.send_message(
                    chat_id=chatid,
                    text="Произошла ошибка!"
                )

        elif callText == 'userStatsDay':
            try:
                await bot.delete_message(
                    chat_id=chatid,
                    message_id=callback_query.message.message_id
                )
                await bot.send_photo(
                    chat_id=chatid,
                    caption='Регистрации за сегодня',
                    photo=charts.daily(),
                    reply_markup=markups.get_user_stats_back(),
                )
            except:
                await bot.send_message(
                    chat_id=chatid,
                    text="Произошла ошибка!"
                )

        elif callText == 'userStatsBack':
            try:
                await bot.delete_message(
                    chat_id=chatid,
                    message_id=callback_query.message.message_id
                )
            
                await bot.send_message(
                    text='👥Статистика регистраций',
                    chat_id=chatid,
                    reply_markup=markups.get_user_stats_markup()
                )
            except:
                await bot.send_message(
                    chat_id=chatid,
                    text="Произошла ошибка!"
                )

    elif callText == "statsSettings":
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_photo(
            caption=f"📈Настройки статистики",
            chat_id=chatid,
            photo=stats.get_random_graph(),
            reply_markup=markups.get_stats_settings_markup()
        )

    elif callText == "statsSettingsBack":
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_photo(
            caption=f"📈Настройки статистики",
            chat_id=chatid,
            photo=stats.get_random_graph(),
            reply_markup=markups.get_stats_settings_markup()
        )

    elif callText[:10] == "statsColor":
        if callText == "statsColor":
            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"🌈Цвет графика",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_color_markup()
            )
        
        else:
            match callText[10:]:
                case "Black":
                    color = "000000"
                case "White":
                    color = "ffffff"
                case "Red":
                    color = "cc0000"
                case "Yellow":
                    color = "ffff00"
                case "Purple":
                    color = "a957e3"
                case "Blue":
                    color = "3299ff"
                case "Orange":
                    color = "ffa500"
                case "Green":
                    color = "4ca64c"
                case "Brown":
                    color = "4c3100"
            conf.set("stats_settings", "barcolor", color)
            with open('config.ini', 'w') as config:
                conf.write(config)

            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"🌈Цвет графика",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_color_markup()
            )

    elif callText[:16] == "statsBorderWidth":
        if callText == "statsBorderWidth":
            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"🔲Ширина обводки",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_border_width_markup()
            )
        else:
            match callText[16:]:
                case "Add":
                    conf.set("stats_settings", "linewidth", str(int(conf["stats_settings"]["linewidth"]) + 1))
                case "Reduce":
                    conf.set("stats_settings", "linewidth", str(int(conf["stats_settings"]["linewidth"]) - 1))
            with open('config.ini', 'w') as config:
                conf.write(config)

            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"🔲Ширина обводки",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_border_width_markup()
            )

    elif callText == "defaultBorderWidth":
            conf.set("stats_settings", "linewidth", "1")
            with open('config.ini', 'w') as config:
                conf.write(config)

            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"🔲Ширина обводки",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_border_width_markup()
            )
    
    elif callText[:11] == "defaultFont":
        conf.set("stats_settings", callText[11:], "16")
        with open('config.ini', 'w') as config:
                conf.write(config)
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_photo(
            caption=f"📈Настройки статистики",
            chat_id=chatid,
            photo=stats.get_random_graph(),
            reply_markup=markups.get_stats_settings_markup()
        )

    elif callText[:18] == "statsTitleFontSize":
        if callText == "statsTitleFontSize":
            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"ℹ️Размер названия графика",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_font_markup("titlefontsize", "statsTitleFontSize")
            )
        else:
            match callText[18:]:
                case "Add":
                    conf.set("stats_settings", "titlefontsize", str(int(conf["stats_settings"]["titlefontsize"]) + 2))
                case "Reduce":
                    conf.set("stats_settings", "titlefontsize", str(int(conf["stats_settings"]["titlefontsize"]) - 2))
            with open('config.ini', 'w') as config:
                conf.write(config)

            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"ℹ️Размер названия графика",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_font_markup("titlefontsize", "statsTitleFontSize")
            )

    elif callText[:17] == "statsAxisFontSize":
        if callText == "statsAxisFontSize":
            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"↔️Размер текста для осей",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_font_markup("axisfontsize", "statsAxisFontSize")
            )
        else:
            match callText[17:]:
                case "Add":
                    conf.set("stats_settings", "axisfontsize", str(int(conf["stats_settings"]["axisfontsize"]) + 2))
                case "Reduce":
                    conf.set("stats_settings", "axisfontsize", str(int(conf["stats_settings"]["axisfontsize"]) - 2))
            with open('config.ini', 'w') as config:
                conf.write(config)

            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"↔️Размер текста для осей",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_font_markup("axisfontsize", "statsAxisFontSize")
            )
    
    elif callText[:18] == "statsTicksFontSize":
        if callText == "statsAxisFontSize":
            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"↔️Размер текста для делений",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_font_markup("ticksfontsize", "statsTicksFontSize")
            )
        else:
            match callText[18:]:
                case "Add":
                    conf.set("stats_settings", "ticksfontsize", str(int(conf["stats_settings"]["ticksfontsize"]) + 2))
                case "Reduce":
                    conf.set("stats_settings", "ticksfontsize", str(int(conf["stats_settings"]["ticksfontsize"]) - 2))
            with open('config.ini', 'w') as config:
                conf.write(config)

            await bot.delete_message(
                chat_id=chatid,
                message_id=callback_query.message.message_id
            )
            await bot.send_photo(
                caption=f"↔️Размер текста для делений",
                chat_id=chatid,
                photo=stats.get_random_graph(),
                reply_markup=markups.get_stats_font_markup("ticksfontsize", "statsTicksFontSize")
            )

    elif callText[:5] == 'order':
        orderMarkup = types.InlineKeyboardMarkup()
        order_id = callText[5:]
        supportOrder = types.InlineKeyboardButton(text='📱Открыть тикет в тех. поддержку', callback_data=f'support{order_id}')
        orderMarkup.add(supportOrder)
        orderMarkup.add(markups.get_orders_back())
        c.execute(f"SELECT * FROM orders WHERE order_id={order_id}")
        for order in c:
            pass
        c.execute(f"SELECT * FROM items WHERE id={order[2]}")
        for item in c:
            pass
        itemName = item[1]
        login = order[3].split(':')[0]
        password = order[3].split(':')[1]
        date = order[4]
        text = f'➖➖➖➖➖➖➖➖➖\nЗаказ номер {order_id}\n➖➖➖➖➖➖➖➖➖\n' \
               f'Товар: {itemName}\n' \
               f'Логин: {login}\n' \
               f'Пароль: {password}\n' \
               f'Дата заказа: {date}'
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=orderMarkup
        )

    elif callText[:7] == 'support':
        pass  # TODO: сделать саппорт через state_handler

    elif callText == 'seeSupportTickets':
        pass  # TODO: сделать вывод тиктов

    elif callText == 'botSettings':
        await bot.edit_message_text(
            text="⚙Настройки бота",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_settings_markup()
        )

    elif callText == "botSettingsDel":
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_message(
            text=f"⚙Настройки бота",
            chat_id=callback_query.message.chat.id,
            reply_markup=markups.get_settings_markup()
        )

    elif callText == 'disableNotif':
        user.disable_notif()
        markupProfile = markups.get_markup_profile(user_id=chatid)
        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markupProfile,
            text=f"➖➖➖➖➖➖➖➖➖➖\n"
                 f"📝id: {chatid}\n"
                 f"📈Кол-во заказов: {len(usr.get_user_orders(chatid))}\n"
                 f"💸Баланс: {user.get_balance()}руб.\n"
                 f"Дата регистрации: {user.get_register_date()}"
                 f"\n➖➖➖➖➖➖➖➖➖➖",
        )

    elif callText == 'backProfile':
        markupProfile = markups.get_markup_profile(user_id=chatid)

        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markupProfile,
            text=f"➖➖➖➖➖➖➖➖➖➖\n"
                 f"📝id: {chatid}\n"
                 f"📈Кол-во заказов: {len(usr.get_user_orders(chatid))}\n"
                 f"💸Баланс: {user.get_balance()}руб.\n"
                 f"Дата регистрации: {user.get_register_date()}"
                 f"\n➖➖➖➖➖➖➖➖➖➖",
        )

    elif callText == 'enableNotif':
        user.enable_notif()
        markupProfile = markups.get_markup_profile(user_id=chatid)
        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markupProfile,
            text=f"➖➖➖➖➖➖➖➖➖➖\n"
                 f"📝id: {chatid}\n"
                 f"📈Кол-во заказов: {len(usr.get_user_orders(chatid))}\n"
                 f"💸Баланс: {user.get_balance()}руб.\n"
                 f"Дата регистрации: {user.get_register_date()}"
                 f"\n➖➖➖➖➖➖➖➖➖➖",
        )

    elif callText == 'goBackFaq':
        markupFAQ = markups.get_faq_markup()
        text = f'➖➖➖➖➖➖➖➖➖➖\n' \
                f'ℹ️FAQ магазина {conf["shop_settings"]["shop_name"]}\n' \
                f'➖➖➖➖➖➖➖➖➖➖'
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markupFAQ
        )

    elif callText == 'backCat':
        catMarkup = types.InlineKeyboardMarkup()
        c.execute('SELECT * FROM cats')
        for category in c:
            btnCat = types.InlineKeyboardButton(text=category[1], callback_data=f"cat{category[0]}")
            catMarkup.add(btnCat)
        await bot.edit_message_text(
            text='➖➖➖➖➖➖➖➖➖➖\n🛍️Категории\n➖➖➖➖➖➖➖➖➖➖',
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=catMarkup
        )

    elif callText == 'changeShopName':
        text = f"{conf['shop_settings']['shop_name']}\nВведите новое название или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_main_settings(),
        )
        await state_handler.changeShopName.name.set()

    elif callText == 'changeContacts':
        text = f"{conf['shop_settings']['shop_contacts']}\nВведите новый текст для вкладки \"Контакты\" или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_main_settings(),
        )
        await state_handler.changeShopContacts.text.set()

    elif callText == 'changeRefund':
        text = f"{conf['shop_settings']['refund_policy']}\nВведите новый текст для вкладки \"Политика возврата\" или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_main_settings(),
        )
        await state_handler.changeShopRefund.text.set()

    elif callText == 'changeQiwiNumber':
        text = f"{conf['payment_settings']['qiwi_number']}\nВведите новый номер QIWI в формате \"+70000000000\" или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_qiwi_settings(),
        )
        await state_handler.changeQiwiNumber.number.set()

    elif callText == 'changeQiwiToken':
        text = f"{conf['payment_settings']['qiwi_token']}\nВведите новый токен QIWI или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_qiwi_settings(),
        )
        await state_handler.changeQiwiToken.token.set()

    elif callText == 'changeMainBtc':
        text = f"{conf['payment_settings']['main_btc_adress']}\nВведите основной Bitcoin кошелёк или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_btc_settings(),
        )
        await state_handler.changeMainBtc.wallet.set()

    elif callText == "addStock":
        markup = types.InlineKeyboardMarkup()
        c.execute(f"SELECT * FROM cats")
        for cat in list(c):
            markup.add(types.InlineKeyboardButton(text=f"[{cat[0]}] {cat[1]}", callback_data=f"addStockCat{cat[0]}"))
        markup.add(markups.goBackItems)
        await bot.edit_message_text(
            text=f"Выберите категорию товара",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markup
        )

    elif callText[:11] == "addStockCat":
        c.execute(f"SELECT * FROM items WHERE cat_id={callText[11:]}")
        markup = types.InlineKeyboardMarkup()
        for item in list(c):
            markup.add(types.InlineKeyboardButton(text=item[1], callback_data=f"addStockItem{item[0]}"))
        markup.add(types.InlineKeyboardButton(text="🔙Назад", callback_data="addStock"))
        await bot.edit_message_text(
            text=f"Выберите товар",
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markup
        )

    elif callText[:12] == "addStockItem":
        c.execute(f"SELECT * FROM items WHERE id={callText[12:]}")
        item = list(c)[0]
        await bot.edit_message_text(
            text=f"Введите данные от аккаунтов в формате:\nlogin:pass\nlogin:pass",
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.cancel_states_addaccounts(item[3])
        )
        await state_handler.AddAccounts.details.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(itemid=item[0])


    elif callText == 'clientManagement':
        pass


@dp.message_handler(state=state_handler.addCat.name)
async def addCat(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat_name = message.text

    try:
        item.create_cat(cat_name)
        text = tt.get_category_was_created_successfuly(cat_name)
    except:
        text = tt.error

    await bot.delete_message(
        message_id=data["state_message"],
        chat_id=message.chat.id
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=markups.single_button(markups.btnBackItemManagement),
    )
    await state.finish()

@dp.callback_query_handler(state='*')
async def cancelState(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id
    call_data = callback_query.data
    
    if call_data[:6] == "admin_":
        call_data = call_data[6:]
        
        if call_data == "itemManagement":
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=callback_query.message.message_id,
                text=tt.item_management,
                reply_markup=markups.get_markup_itemManagement(),
            )
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)