from telebot import types


def none():
    return types.ReplyKeyboardRemove()


def create_keyboard(btn_lines):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for line in btn_lines:
        btn_arr = []
        for name in line:
            btn_arr.append(types.KeyboardButton(text=name))
        keyboard.add(*btn_arr)
    return keyboard


def create_inline_keyboard(btn_lines):
    keyboard = types.InlineKeyboardMarkup()
    for line in btn_lines:
        btn_arr = []
        for name, data in line:
            btn_arr.append(types.InlineKeyboardButton(text=name, callback_data=data))
        keyboard.add(*btn_arr)
    return keyboard


def start():
    return create_keyboard(
        [
            ['Начать']
        ]
    )


def back():
    return create_keyboard(
        [
            ['<< Назад']
        ]
    )


def end_dialog(bot, status=None):
    if status == 'leader':
        return create_keyboard(
            [
                ['Завершить диалог']
            ]
        )
    elif status == 'client':
        return create_keyboard(
            [
                ['🎁 Подарок отправлен']
            ]
        ) 


def privacy_accept():
    return create_inline_keyboard(
        [
            [('Отказаться', 'privacy|deny'), ('Принять', 'privacy|accept')]
        ]
    )


def get_user_data():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='📱Отправить свой контакт', request_contact=True))
    return keyboard


def username_exists():
    return create_keyboard(
        [
            ['Имя пользователя есть']
        ]
    )


def choose_group():
    return create_keyboard(
        [
            ['В команду того, кто меня пригласил'],
        ]
    )


def full_choose_group():
    return create_keyboard(
        [
            ['Зарегистрироваться в команду ближайшего игрока'],
            ['Пойду в команду к другому игроку']
        ]
    )


def not_exists_choose_group():
    return create_keyboard(
        [
            ['Ввести имя пользователя'],
            ['Вступить в другую команду']
        ]
    )


def text_to_leader(leader_id, clicked=False):
    if not clicked:
        return create_inline_keyboard(
            [
                [('Отправить подарок Эксперту', f'text_to_leader|{leader_id}')]
            ]
        )
    else:
        return create_inline_keyboard(
            [
                [('✅ Отправить подарок Эксперту', '|')]
            ]
        )


# def yes_no_text_to_leader():
#     return create_inline_keyboard(
#         [
#             [('Да', 'yes_no_text_to_leader|yes'), ('Нет', 'yes_no_text_to_leader|no')]
#         ]
#     )



def text_to_leader_success(client_id, expert_id, clicked=False):
    if not clicked:
        return create_inline_keyboard(
            [
                [('Подтвердить получение подарка', f'text_to_leader_success|{client_id} {expert_id}')]
            ]
        )
    else:
        return create_inline_keyboard(
            [
                [('✅ Подтвердить получение подарка', '|')]
            ]
        )


def expert_confirm(client_id, clicked=False):
    if not clicked:
        return create_inline_keyboard(
            [
                [('Подтвердить получение подарка', f'expert_confirm|{client_id}')]
            ]
        )
    else:
        return create_inline_keyboard(
            [
                [('✅ Подтвердить получение подарка', '|')]
            ]
        )


def menu(bot, user_id):
    user_id = int(user_id)
    if user_id in bot.system_accounts:
        return create_keyboard(
        [
            ['🎁 KVΛDRIX GAME 🎁'],
            ['👑 Мой аккаунт 👑'],
            ['💡 База знаний', 'Об игре 🎲'],
            ['⚙️ Тех. Поддержка', 'Партнерская ссылка 🕸'],
            ['Сообщения в тех. поддержку (только для админов)']
        ]
    )
    elif user_id in bot.admins:
        return create_keyboard(
        [
            ['🎁 KVΛDRIX GAME 🎁'],
            ['💳 Мои реквизиты 💳'],
            ['👑 Мой аккаунт 👑'],
            ['💡 База знаний', 'Об игре 🎲'],
            ['⚙️ Тех. Поддержка', 'Партнерская ссылка 🕸'],
            ['Сообщения в тех. поддержку (только для админов)']
        ]
    )
    else:
        return create_keyboard(
        [
            ['🎁 KVΛDRIX GAME 🎁'],
            ['💳 Мои реквизиты 💳'],
            ['👑 Мой аккаунт 👑'],
            ['💡 База знаний', 'Об игре 🎲'],
            ['⚙️ Тех. Поддержка', 'Партнерская ссылка 🕸']
        ]
    )


def about_game():
    return create_inline_keyboard(
        [
            [('🖥 Презентация ', 'about_game|presentations')],
            [('Статусы 🎗', 'about_game|status')],
            [('📶 Уровни', 'about_game|levels')],
            [('Правила 📖', 'about_game|rules')],
        ]
    )


def back_about_game():
    return create_inline_keyboard(
        [
            [('<< Назад', 'about_game|back')]
        ]
    )


def start_game():
    return create_keyboard(
        [
            ['Связаться с наставником'],
            ['Оповестить о связи'],
            ['<< Назад']
        ]
    )


def get_referal_link(user_id):
    return create_inline_keyboard(
        [
            [('Получить ссылку', f'get_referal_link|{user_id}')]
        ]
    )


def faq():
    return create_keyboard(
        [
            ['Написать в тех. поддержку'],
            ['<< Назад']
        ]
    )


def answer_faq(user_id, msg_id):
    return create_inline_keyboard(
        [
            [('Ответить', f'answer_faq|{user_id} {msg_id}')]
        ]
    )


def know_base_test(is_done, test_num, len_texts):
    if is_done:
        if int(test_num) == len_texts - 1:
            return create_inline_keyboard(
                [
                    [('Готово ✅', f'know_base_test_done|{is_done} {test_num}')],
                ]
            )
        else:
            return create_inline_keyboard(
                [
                    [('Готово ✅', f'know_base_test_done|{is_done} {test_num}')],
                    [('Следующий урок —>', f'know_base_next|{is_done} {test_num}')]
                ]
            )
    else:
        if int(test_num) == len_texts - 1:
            return create_inline_keyboard(
                [
                    [('Готово', f'know_base_test_done|{is_done} {test_num}')],
                ]
            )
        else:   
            return create_inline_keyboard(
                [
                    [('Готово', f'know_base_test_done|{is_done} {test_num}')],
                    [('Следующий урок —>', f'know_base_next|{is_done} {test_num}')]
                ]
            )


def team_control(bot, cur_user_id):
    keyboard = types.InlineKeyboardMarkup()

    cur_user = bot.user_exists(id=cur_user_id)
    producer_1, producer_2 = cur_user.left, cur_user.right
    if producer_1 is not None:
        keyboard.add(types.InlineKeyboardButton(text=f'@{bot.user_exists(id=producer_1).username}', callback_data='|'),
                        types.InlineKeyboardButton(text='Удалить', callback_data=f'team_control_delete|{producer_1}'))
    if producer_2 is not None:
        keyboard.add(types.InlineKeyboardButton(text=f'@{bot.user_exists(id=producer_2).username}', callback_data='|'),
                        types.InlineKeyboardButton(text='Удалить', callback_data=f'team_control_delete|{producer_2}'))

    return keyboard


def yes_no():
    return create_keyboard(
        [
            ['Да', 'Нет']
        ]
    )


def start_text_users(bot, users_start_text):
    keyboard = types.InlineKeyboardMarkup()
    
    for user_id in users_start_text:
        user = bot.user_exists(id=user_id)
        keyboard.add(types.InlineKeyboardButton(text=f'@{user.username}', callback_data=f'start_text_users|{user_id}'))

    return keyboard


def my_account():
    return create_keyboard(
        [
            # ['Управление аккаунтами'],
            ['<< Назад']
        ]
    )


def game_list():
    return create_keyboard(
        [
            ['GAME-1', 'START']
            # ['GAME-1', 'GAME-2', 'START']
        ]
    )


def level_choice():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    keyboard.add(types.KeyboardButton(text='1'), types.KeyboardButton(text='2'),
                types.KeyboardButton(text='3'), types.KeyboardButton(text='4'))
    return keyboard