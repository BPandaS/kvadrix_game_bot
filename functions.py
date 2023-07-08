from datetime import datetime
import keyboard, time


def get_today_date():
    minute = '0' * (len(str(datetime.today().minute)) < 2) + str(datetime.today().minute)
    hour = '0' * (len(str(datetime.today().hour)) < 2) + str(datetime.today().hour)
    day = '0' * (len(str(datetime.today().day)) < 2) + str(datetime.today().day)
    month = '0' * (len(str(datetime.today().month)) < 2) + str(datetime.today().month)
    year = str(datetime.today().year)
    return f'{hour}:{minute}  {day}.{month}.{year}'


# Check if sturcture is done
def check_structure_loop(bot):
    while True:
        try:
            all_users = bot.users
            for expert in all_users:
                producer_1, producer_2 = expert.left, expert.right

                if producer_1 is not None and producer_2 is not None:

                    producer_1, producer_2 = bot.user_exists(id=producer_1), bot.user_exists(id=producer_2)
                    if producer_1 is False or producer_2 is False:
                        return
                    
                    client_1, client_2, client_3, client_4 = producer_1.left, producer_1.right, producer_2.left, producer_2.right
                    
                    if producer_1 is not None and producer_2 is not None and client_1 is not None and client_2 is not None and \
                        client_3 is not None and client_4 is not None:
                        
                        client_1 = bot.user_exists(id=client_1)
                        client_2 = bot.user_exists(id=client_2)
                        client_3 = bot.user_exists(id=client_3)
                        client_4 = bot.user_exists(id=client_4)
                        
                        all_texted_to_leader = True
                        for one in [client_1, client_2, client_3, client_4, producer_1, producer_2]:
                            if one is False or not one.texted_to_leader:
                                all_texted_to_leader = False
                                break

                        if expert.id in bot.system_accounts:
                            expert.left = None
                            expert.right = None

                            expert.levels[expert.cur_level] += 1

                            # GAME-1 or GAME-2
                            try:
                                bot.bot.send_message(chat_id=expert.id,
                                                    text=f'Поздравляю, Вы завершили структуру!\n\nТеперь ты - в новой игре👊 🔥\n\n'
                                                    '«Верь в себя, даже если не верит больше никто»\n\n'
                                                    'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                                    'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                                    'конечно - много-много подарков😻🎁\n\n'
                                                    f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                                    reply_markup=keyboard.text_to_leader(lider.id))
                            except Exception as e:
                                print(f'[ERROR] Expert end FALSE - {expert.id}\n{e}')
                        elif all_texted_to_leader:
                            expert.left = None
                            expert.right = None

                            expert.levels[expert.cur_level] += 1

                            if expert.game == 3:
                                expert.leader = expert.username
                                expert.game = 1
                                bot.bot.send_message(chat_id=expert.id,
                                        text='Вы закончили игру START\n... Переход в игру GAME-1 ...')
                                
                                msg = bot.bot.send_message(chat_id=expert.id,
                                                    text='Выберите уровень:',
                                                    reply_markup=keyboard.level_choice())
                                bot.bot.register_next_step_handler(msg, level_choice, bot, True)
                            else:
                                if expert.from_user_id is None:
                                    expert.leader = expert.username
                                    msg = bot.bot.send_message(chat_id=expert.id,
                                                        text='Теперь Вы можете начать игру заново.\nВыберите уровень:',
                                                        reply_markup=keyboard.level_choice())
                                    bot.bot.register_next_step_handler(msg, level_choice, bot, True)
                                else:
                                    # Place-new-user function
                                    new_leader = expert
                                    while True:
                                        if new_leader.from_user_id is None:
                                            expert.leader = expert.username
                                            break

                                        new_leader = bot.user_exists(id=new_leader.from_user_id)
                                        if new_leader.left is None and new_leader.right is None:
                                            new_leader.left = expert.id
                                            expert.leader = new_leader.id
                                            break
                                        elif new_leader.left is None:
                                            new_leader.left = expert.id
                                            expert.leader = new_leader.id
                                            break
                                        elif new_leader.right is None:
                                            new_leader.right = expert.id
                                            expert.leader = new_leader.id
                                            break
                                        else:
                                            producer_1, producer_2 = bot.user_exists(id=new_leader.left), bot.user_exists(id=new_leader.right)
                                            client_1, client_2, client_3, client_4 = bot.user_exists(id=producer_1.left), bot.user_exists(id=producer_1.right), bot.user_exists(id=producer_2.left), bot.user_exists(id=producer_2.right)

                                            if client_1 is False:
                                                producer_1.left = expert.id
                                                expert.leader = new_leader.id
                                                break
                                            elif client_2 is False:
                                                producer_1.right = expert.id
                                                expert.leader = new_leader.id
                                                break
                                            elif client_3 is False:
                                                producer_2.left = expert.id
                                                expert.leader = new_leader.id
                                                break
                                            elif client_4 is False:
                                                producer_2.right = expert.id
                                                expert.leader = new_leader.id
                                                break
                                        

                                    lider = bot.user_exists(id=bot.user_exists(id=expert.leader).leader)
                                    if expert.game == 1 or expert.game == 2:
                                        # GAME-1 or GAME-2
                                        bot.bot.send_message(chat_id=expert.id,
                                                            text=f'Поздравляю, Вы завершили структуру!\n\nТеперь ты - в новой команде👊 🔥\n\n'
                                                            '«Верь в себя, даже если не верит больше никто»\n\n'
                                                            'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                                            'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                                            'конечно - много-много подарков😻🎁\n\n'
                                                            f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                                            reply_markup=keyboard.text_to_leader(lider.id))
        except:
            continue

        time.sleep(0.5)



# Check if sturcture is done (only 1 check)
def check_structure_once(bot, expert_id, game=1):
    expert = bot.user_exists(id=expert_id)
    if expert is False:
        return True

    if game == 1:
        # GAME-1 or START
        producer_1, producer_2 = expert.left, expert.right

        if producer_1 is not None and producer_2 is not None:

            producer_1, producer_2 = bot.user_exists(id=producer_1), bot.user_exists(id=producer_2)
            client_1, client_2, client_3, client_4 = producer_1.left, producer_1.right, producer_2.left, producer_2.right
            
            if producer_1 is not None and producer_2 is not None and client_1 is not None and client_2 is not None and \
                client_3 is not None and client_4 is not None:
                
                client_1 = bot.user_exists(id=client_1)
                client_2 = bot.user_exists(id=client_2)
                client_3 = bot.user_exists(id=client_3)
                client_4 = bot.user_exists(id=client_4)
                
                all_texted_to_leader = True
                for one in [client_1, client_2, client_3, client_4, producer_1, producer_2]:
                    if not one.texted_to_leader:
                        all_texted_to_leader = False
                        break

                return all_texted_to_leader
        return False
    elif game == 2:
        # GAME-2
        producer_1, producer_2, producer_3 = expert.left, expert.middle, expert.right

        if producer_1 is not None and producer_2 is not None and producer_3 is not None:

            producer_1, producer_2, producer_3 = bot.user_exists(id=producer_1), bot.user_exists(id=producer_2), bot.user_exists(id=producer_3)
            client_1, client_2, client_3, client_4, client_5, client_6, client_7, client_8, client_9 = producer_1.left, producer_1.middle, producer_1.right, producer_2.left, producer_2.middle, producer_2.right, producer_3.left, producer_3.middle, producer_3.right
            
            if producer_1 is not None and producer_2 is not None and producer_3 is not None \
                and client_1 is not None and client_2 is not None and client_3 is not None \
                and client_4 is not None and client_5 is not None and client_6 is not None \
                and client_7 is not None and client_8 is not None and client_9 is not None:
                
                client_1 = bot.user_exists(id=client_1)
                client_2 = bot.user_exists(id=client_2)
                client_3 = bot.user_exists(id=client_3)
                client_4 = bot.user_exists(id=client_4)
                client_5 = bot.user_exists(id=client_5)
                client_6 = bot.user_exists(id=client_6)
                client_7 = bot.user_exists(id=client_7)
                client_8 = bot.user_exists(id=client_8)
                client_9 = bot.user_exists(id=client_9)
                
                all_texted_to_leader = True
                for one in [client_1, client_2, client_3, client_4, client_5, client_6, client_7, client_8, client_9, producer_1, producer_2, producer_3]:
                    if not one.texted_to_leader:
                        all_texted_to_leader = False
                        break

                return all_texted_to_leader
        return False



def level_choice(message, bot, end_game=False):
    cur_user = bot.user_exists(id=message.chat.id)

    if message.text in ['1', '2', '3', '4']:
        cur_user.cur_level = int(message.text)

        if cur_user.cur_level == 4 and (cur_user.levels[1] == 0 or \
             cur_user.levels[2] == 0 or cur_user.levels[3] == 0):
                msg = bot.bot.send_message(chat_id=message.chat.id,
                                    text='Пока Вы не пройдете 1-3 уровни, доступ к 4-му уровню будет закрыт!',
                                    reply_markup=keyboard.level_choice())
                bot.bot.register_next_step_handler(msg, level_choice, bot, end_game)
                return
        
        if end_game:
            lider = bot.user_exists(id=bot.user_exists(id=cur_user.leader).leader)
            if lider.id != cur_user.id:
                if cur_user.game == 1 or cur_user.game == 2:
                    # GAME-1 or GAME-2
                    with open('images/main_menu_img.jpg', 'rb') as file:
                        main_menu_photo = file.read()
                    bot.bot.send_photo(chat_id=message.chat.id,
                                        photo=main_menu_photo,
                                        caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                        'не верит больше никто»\n\n'
                                        'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                        'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                        'конечно - много-много подарков😻🎁\n\n'
                                        f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                        reply_markup=keyboard.text_to_leader(lider.id))
                elif cur_user.game == 3:
                    # START
                    with open('images/main_menu_img.jpg', 'rb') as file:
                        main_menu_photo = file.read()
                    bot.bot.send_photo(chat_id=message.chat.id,
                                        photo=main_menu_photo,
                                        caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                        'не верит больше никто»\n\n'
                                        'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                        'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                        'конечно - много-много подарков😻🎁\n\n'
                                        f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                        reply_markup=keyboard.menu(bot, cur_user.id))
            else:
                bot.bot.send_message(chat_id=message.chat.id,
                            text='... Переход на выбранный уровень ...',
                            reply_markup=keyboard.menu(bot, cur_user.id))
            return
        else:
            bot.bot.send_message(chat_id=message.chat.id,
                            text='... Переход на выбранный уровень ...',
                            reply_markup=keyboard.none())

        # If user comes NOT for referal-link
        if cur_user.from_user_id is None:
            # Place-new-user function
            root_user = None
            for user in bot.users:
                if user.cur_level == cur_user.cur_level and user.leader == user.username and cur_user != user:
                    root_user = user
                    break
            if root_user is None:
                root_user = bot.users[0]    

            bot.place_new_user_lst[cur_user.id] = [root_user]   
            bot.place_new_user(new_user=bot.user_exists(message.chat.id))

            lider = bot.user_exists(id=bot.user_exists(id=cur_user.leader).leader)
            if cur_user.game == 1 or cur_user.game == 2:
                # GAME-1 or GAME-2
                bot.bot.send_message(chat_id=message.chat.id,
                                    text=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                    'не верит больше никто»\n\n'
                                    'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                    'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                    'конечно - много-много подарков😻🎁\n\n'
                                    f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                    reply_markup=keyboard.text_to_leader(lider.id))
            elif cur_user.game == 3:
                # START
                lider = bot.user_exists(id=bot.user_exists(id=cur_user.leader).leader)
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                bot.bot.send_photo(chat_id=message.chat.id,
                                    photo=main_menu_photo,
                                    caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                    'не верит больше никто»\n\n'
                                    'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                    'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                    'конечно - много-много подарков😻🎁\n\n'
                                    f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                    reply_markup=keyboard.menu(bot, cur_user.id))
        else:
            bot.bot.send_message(chat_id=message.chat.id,
                                text=f'Твой пригласитель - @{bot.user_exists(id=cur_user.from_user_id).username}',
                                reply_markup=keyboard.none())
            
            cur_user = bot.user_exists(id=message.chat.id)
            from_user = bot.user_exists(id=cur_user.from_user_id)

            if from_user.left is not None and from_user.right is not None:
                msg = bot.bot.send_message(chat_id=message.chat.id,
                                    text=f'Вы не можете зарегистрироваться в команду '
                                    f'к @{from_user.username}, так как у него нет мест',
                                    reply_markup=keyboard.full_choose_group())
                bot.bot.register_next_step_handler(msg, full_choose_group, bot)
            else:
                if from_user.left is None:
                    from_user.left = message.chat.id
                else:
                    from_user.right = message.chat.id
                
                if 'system' in from_user.username:
                    cur_user.leader = bot.user_exists(id=from_user.username).id
                else:
                    cur_user.leader = bot.user_exists(id=from_user.id).id
                
                lider = bot.user_exists(id=bot.user_exists(id=cur_user.leader).leader)
                if cur_user.game == 1 or cur_user.game == 2 or \
                    (cur_user.game == 3 and from_user.id in bot.system_accounts):
                    # GAME-1 or GAME-2
                    bot.bot.send_message(chat_id=message.chat.id,
                                        text=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                        'не верит больше никто»\n\n'
                                        'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                        'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                        'конечно - много-много подарков😻🎁\n\n'
                                        f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                        reply_markup=keyboard.text_to_leader(lider.id))
                elif cur_user.game == 3:
                    # START
                    lider = bot.user_exists(id=bot.user_exists(id=cur_user.leader).leader)
                    with open('images/main_menu_img.jpg', 'rb') as file:
                        main_menu_photo = file.read()
                    bot.bot.send_photo(chat_id=message.chat.id,
                                        photo=main_menu_photo,
                                        caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                        'не верит больше никто»\n\n'
                                        'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                        'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                        'конечно - много-много подарков😻🎁\n\n'
                                        f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                        reply_markup=keyboard.menu(bot, cur_user.id))
    else:
        msg = bot.bot.send_message(chat_id=message.chat.id,
                            text='Данного уровня нет!',
                            reply_markup=keyboard.level_choice())
        bot.bot.register_next_step_handler(msg, level_choice, bot)



def full_choose_group(message, bot):
    cur_user = bot.user_exists(id=message.chat.id)
    from_user = bot.user_exists(id=cur_user.from_user_id)

    if message.text == 'Зарегистрироваться в команду ближайшего игрока':
        # Place-new-user function
        bot.place_new_user_lst[cur_user.id] = [from_user]
        bot.place_new_user(new_user=cur_user, nearest=True)
    

        lider = bot.user_exists(id=bot.user_exists(id=cur_user.leader).leader)
        if cur_user.game == 1 or cur_user.game == 2:
            # GAME-1 or GAME-2
            bot.bot.send_message(chat_id=message.chat.id,
                                text=f'Поздравляю, ты - в команде👊 🔥\n\n'
                                '«Верь в себя, даже если не верит больше никто»\n\n'
                                'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                'конечно - много-много подарков😻🎁\n\n'
                                f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                reply_markup=keyboard.text_to_leader(lider.id))
        else:
            # START
            lider = bot.user_exists(id=bot.user_exists(id=cur_user.leader).leader)
            with open('images/main_menu_img.jpg', 'rb') as file:
                main_menu_photo = file.read()
            bot.bot.send_photo(chat_id=message.chat.id,
                                photo=main_menu_photo,
                                caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                'не верит больше никто»\n\n'
                                'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                'конечно - много-много подарков😻🎁\n\n'
                                f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                reply_markup=keyboard.menu(bot, cur_user.id))
    elif message.text == 'Пойду в команду к другому игроку':
        msg = bot.bot.send_message(chat_id=message.chat.id,
                            text='Введите вручную имя игрока:')
        bot.bot.register_next_step_handler(msg, other_choose_group)
    else:
        bot.bot.send_message(chat_id=message.chat.id,
                            text='Данного пункта не существует!',
                            reply_markup=keyboard.full_choose_group())
        bot.bot.register_next_step_handler(message, full_choose_group, bot)



def other_choose_group(message, bot):
    root_user_exists = bot.user_exists(username=message.text)
    if not root_user_exists:
        msg = bot.bot.send_message(chat_id=message.chat.id,
                            text='Такого пользователя не существует, повторите попытку ещё раз, либо вступите в ближайшую команду',
                            reply_markup=keyboard.not_exists_choose_group())
        bot.bot.register_next_step_handler(msg, next_other_choose_group, bot)
    else:
        cur_user = bot.user_exists(id=message.chat.id)

        bot.place_new_user_lst[cur_user.id] = [root_user_exists]
        bot.place_new_user(new_user=cur_user,
                            nearest=True)
        
        lider = bot.user_exists(id=bot.user_exists(id=cur_user.leader).leader)
        if cur_user.game == 1 or cur_user.game == 2:
            # GAME-1 or GAME-2
            bot.bot.send_message(chat_id=message.chat.id,
                                text=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                'не верит больше никто»\n\n'
                                'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                'конечно - много-много подарков😻🎁\n\n'
                                f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                reply_markup=keyboard.text_to_leader(lider.id))
        elif cur_user.game == 3:
            # START
            with open('images/main_menu_img.jpg', 'rb') as file:
                main_menu_photo = file.read()
            bot.bot.send_photo(chat_id=message.chat.id,
                                photo=main_menu_photo,
                                caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                'не верит больше никто»\n\n'
                                'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                'конечно - много-много подарков😻🎁\n\n',
                                reply_markup=keyboard.menu(bot, cur_user.id))


def next_other_choose_group(message, bot):
    if message.text == 'Ввести имя пользователя':
        msg = bot.bot.send_message(chat_id=message.chat.id,
                            text='Введите вручную имя игрока:')
        bot.bot.register_next_step_handler(msg, other_choose_group)
    elif message.text == 'Вступить в другую команду':
        cur_user = bot.user_exists(id=message.chat.id)

        # Place-new-user function
        root_user = None
        for user in bot.users:
            if user.left is None and user.right is None:
                root_user = user
                break
        if root_user is None:
            root_user = bot.users[0]
        
        bot.place_new_user_lst[cur_user.id] = [root_user]
        bot.place_new_user(new_user=bot.user_exists(message.chat.id))
        
        
        lider = bot.user_exists(id=bot.user_exists(id=cur_user.leader).leader)
        if cur_user.game == 1 or cur_user.game == 2:
            # GAME-1 or GAME-2
            bot.bot.send_message(chat_id=message.chat.id,
                                text=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                'не верит больше никто»\n\n'
                                'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                'конечно - много-много подарков😻🎁\n\n'
                                f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                reply_markup=keyboard.text_to_leader(lider.id))
        elif cur_user.game == 3:
            # START
            with open('images/main_menu_img.jpg', 'rb') as file:
                main_menu_photo = file.read()
            bot.bot.send_photo(chat_id=message.chat.id,
                                photo=main_menu_photo,
                                caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                'не верит больше никто»\n\n'
                                'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                'конечно - много-много подарков😻🎁\n\n',
                                reply_markup=keyboard.menu(bot, cur_user.id))
    else:
        bot.bot.send_message(chat_id=message.chat.id,
                            text='Данного пункта не существует!',
                            reply_markup=keyboard.not_exists_choose_group())
