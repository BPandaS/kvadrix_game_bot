from collections import defaultdict
from random import randint
import threading, json
from telebot import TeleBot, types
from config import access_token, table_name
import keyboard, functions, db_functions, logger


# REVERAL-LINK: https://t.me/kvadrix_game_bot?start={USER-ID}
MAIN_BOT_LINK = 'https://t.me/kvadrix_game_bot'
NOW_DIALOGS = []


class User:
    def __init__(self, id=None, username=None, phone=None, privacy_accept=False, left=None, right=None, leader=None, texted_to_leader=False, expert=None, expert_confirm=False, middle=None, game=1, cur_level=1, is_eighteen=False):
        # Main user information
        self.id = id
        self.privacy_accept = privacy_accept
        self.is_eighteen = is_eighteen
        self.username = username
        self.phone = phone

        # Referal/Levels system
        self.refs_cnt = 0
        self.from_user_id = None # referal-part
        self.cur_level = cur_level
        self.levels = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
        }
        self.ref_link = None

        # Levels-Tree
        self.left = left
        self.middle = middle # For 'GAME-2'
        self.right = right
        self.leader = leader
 
        # for 'start-game' part
        self.expert = expert
        self.expert_confirm = expert_confirm

        # Check if user text to his leader
        self.texted_to_leader = texted_to_leader

        # Statistic data
        self.send_gift_sum = 0
        self.get_gift_sum = 0

        # Games
        self.game = game


class Bot:
    def __init__(self):
        # Main variables
        self.bot = TeleBot(token=access_token)
        self.REQUISITS_COUNTER = []

        # FAQ
        self.admins = [1592698823, 474253096]
        self.START_GAME_ROOT = 474253096        # self.START_GAME_ROOT = 474253096
        self.START_GAME_ROOT_PRODUCERS = []
        self.user_faq_messages = defaultdict(list)

        # Levels (7 system accounts)
        self.system_accounts = [5589463177, 1883323497, 247819864, 474253096, 1752205871,
                                'system_5589463177', 'system_1883323497', 'system_247819864', 'system_474253096', 'system_1752205871',
                                'system_1', 'system_2', 'system_3', 'system_4', 'system_5', 'system_6']
        self.system_requisits = ['Номер карты Эксперта:\n4276 6900 1905 7931\nСбербанк\nМаргарита Васильевна', 'Номер карты Эксперта:\n4377 7237 6759 5170']

        # Expert start-text
        self.start_expert_text = dict()

        # Place-new user data
        self.place_new_user_lst = dict()

        self.gift_payed = {
                        1: (1, 1),
                        2: (3, 3),
                        3: (10, 10),
                        4: (30, 30),
                    }


        # Texts
        self.hello_message = 'KVΛDRIX - игра, использующая систему дарения как инструмент запуска инфопродукта:\n\n💎 Пользователи дарят друг другу подарки, а мы создаём большую клиентскую базу, с которой поделимся нашей первой версией обучающих курсов\n\nДа-да, ты все правильно понял(а)!😼\nМы создаём продукт, а после - дарим доступ всем клиентам, сделавшим хотя бы 1 подарок 🎁\n\nKVΛDRIX - Твой проводник в мир инфобизнеса!🔛'

        self.base_texts = [ 
                    '1. Как составить список ч.1\n\nКого приглашать?🤔\n⤵️ Первый ролик из раздела, посвящённого составлению списка аудитории (сначала проводим подготовку!)\nhttps://youtu.be/kiULdTSE7g0', 
                    '2. Как составить список ч.2\n\nА теперь давай разгруппируем всех потенциальных партнёров по категориям, чтобы четко понимать, с кем предстоит работать😼\nhttps://youtu.be/eBiIAKLF8NM', 
                    '3. Приглашение на созвон\n\nСамый эффективный способ начать вести переговоры о сделке - это созвон! (Не переписка - созвон!)\n\n«А… Как пригласить на созвон?😱\nЧто говорить?! Сразу отправить презентацию?? Может, рассказать о маркетинг-плане?»\n\nСтоп-стоп… Давай разбираться со всем пошагово\n\nСмотри ролик ⤵️\n\nhttps://youtu.be/MmsJWQshqOc', 
                    '4. Презентация\n\nОтлично!) Ты дошёл до этапа, когда потенциальный партнёр (запомни, далее - ПП) согласился созвониться и пообщаться о твоей идее🙏\n\nТеперь твоя задача - правильно провести презентацию проекта\n\nСмотри, как это можно сделать ⤵️\n\nhttps://youtu.be/xko5EnZb_qk', 
                    '5. Триггеры\n\nТриггер - психологический посыл, позволяющий ненавязчиво подводить ПП к сделке 🤝\n\nСмотри, какие триггеры продаж существуют, и как ты можешь их использовать ⤵️\n\nhttps://youtu.be/t5JTyx7RkR8', 
                    '6. Продажа\n\nОСТАЛОСЬ ЛИШЬ… ПРОДАТЬ🔥\n\nТо есть - закрыть сделку и подключить ПП в систему😎\n\nЧто тебе поможет в этом ⤵️\n\nhttps://youtu.be/ctiJxDl-FPk', 
                    '7. Отработка возражений\n\n🛡Возражения…Куда же без них…)\n\nНо, это не так страшно, как звучит, если ты знаешь, как правильно их отрабатывать ⚔️\n\nСмотри ролик ⤵️ (ч.1)\n\nhttps://youtu.be/5blaUa26HFU', 
                    '8. Что делать, если ПП отказался\n\n❌ ОТКАЗ ❌\n\n«Этот человек отказался, значит, я буду спамить и уговаривать его каждый день, чтобы он одумался!»\n\n- Ты рассуждаешь так же?)\n\n⤵️ Смотри, как оставить ПП в списке даже после отказа, при этом, действуя этично и не разрушая взаимоотношения;)\nhttps://youtu.be/OjgNZNGUHKA', 
                    'Поздравляю тебя!🔥\n\nТы прошёл Базу Знаний, применяй полученные навыки на практике, обучай свою команду, и ты будешь обречён на успех 🙌✨' 
                ]

        # All users
        self.users = [
            # User(5589463177, 'system_1', '-', True, texted_to_leader=True, expert_confirm=True, leader='system_1', game=3, cur_level=1, left='system_2', right='system_3', is_eighteen=True),
            # User(5589463177, 'system_2', '-', True, texted_to_leader=True, expert_confirm=True, leader='system_1', game=3, cur_level=1, left='system_4', right='system_5', is_eighteen=True),
            # User(5589463177, 'system_3', '-', True, texted_to_leader=True, expert_confirm=True, leader='system_1', game=3, cur_level=1, left='system_6', is_eighteen=True),
            # User(5589463177, 'system_4', '-', True, texted_to_leader=True, expert_confirm=True, leader='system_2', game=3, cur_level=1, is_eighteen=True),
            # User(5589463177, 'system_5', '-', True, texted_to_leader=True, expert_confirm=True, leader='system_2', game=3, cur_level=1, is_eighteen=True),
            # User(5589463177, 'system_6', '-', True, texted_to_leader=True, expert_confirm=True, leader='system_3', game=3, cur_level=1, is_eighteen=True),            

            User(1883323497, 'system_1883323497', privacy_accept=True, texted_to_leader=True, expert_confirm=True, leader='system_1883323497', game=1, cur_level=1, is_eighteen=True),
            User(247819864, 'system_247819864', privacy_accept=True, texted_to_leader=True, expert_confirm=True, leader='system_247819864', game=1, cur_level=2, is_eighteen=True),
            User(474253096, 'system_474253096', privacy_accept=True, texted_to_leader=True, expert_confirm=True, leader='system_474253096', game=1, cur_level=3, is_eighteen=True),
            User(1752205871, 'system_1752205871', privacy_accept=True, texted_to_leader=True, expert_confirm=True, leader='system_1752205871', game=1, cur_level=4, is_eighteen=True),
            User(5589463177, 'system_5589463177', privacy_accept=True, texted_to_leader=True, expert_confirm=True, leader='system_5589463177', game=3, cur_level=1, is_eighteen=True),

            #User(5589463177, 'system_5', '-', True, texted_to_leader=True, expert_confirm=True, leader='system_247819864', game=1),
            #User(5589463177, 'system_6', '-', True, texted_to_leader=True, expert_confirm=True, leader='system_247819864', game=1),
        ]

    

    def user_exists(self, id=None, username=None):
        if type(id) == str:
            username = id
            id = None
        if id is None:
            for user in self.users:
                if user.username == username:
                    return user
        else:
            for user in self.users:
                if user.id == id:
                    return user
        return False


    def faq_msgs_exist(self):
        for user_id in self.user_faq_messages:
            if len(self.user_faq_messages[user_id]) != 0:
                return True
        return False
    

    def place_new_user(self, new_user, from_user=None, nearest=None):
        if new_user.leader is not None:
            return
        
        if not nearest:
            if new_user.game == 1 or new_user.game == 3:
                # GAME-1 or START
                tmp_lst = []
                for root in self.place_new_user_lst[new_user.id]:
                    if root.left is None and root.right is None:
                        root.left = new_user.id
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    elif root.right is None:
                        root.right = new_user.id
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    tmp_lst.append(self.user_exists(id=root.left))
                    tmp_lst.append(self.user_exists(id=root.right))
                
                # Pop fst elem
                self.place_new_user_lst[new_user.id].pop(0)
                self.place_new_user_lst[new_user.id] += tmp_lst
                self.place_new_user(new_user, from_user, nearest)
            elif new_user.game == 2:
                # GAME-2
                tmp_lst = []
                for root in self.place_new_user_lst[new_user.id]:
                    if root.left is None and root.right is None and root.middle is None:
                        root.left = new_user.id
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    elif root.middle is None:
                        root.middle = new_user.id
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    elif root.right is None:
                        root.right = new_user.id
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    tmp_lst.append(self.user_exists(id=root.left))
                    tmp_lst.append(self.user_exists(id=root.middle))
                    tmp_lst.append(self.user_exists(id=root.right))

                # Pop fst elem
                self.place_new_user_lst[new_user.id].pop(0)
                self.place_new_user_lst[new_user.id] += tmp_lst
                self.place_new_user(new_user, from_user, nearest)
        else:
            if new_user.game == 1 or new_user.game == 3:
                # GAME-1 or START
                tmp_lst = []
                for root in self.place_new_user_lst[new_user.id]:
                    if root.left is None and root.right is None:
                        # Choose random number (left || right)
                        random_user_num = randint(1, 2)

                        if random_user_num == 1:
                            root.left = new_user.id
                        else:
                            root.right = new_user.id
                        
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    elif root.right is None:
                        root.right = new_user.id
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    tmp_lst.append(self.user_exists(id=root.left))
                    tmp_lst.append(self.user_exists(id=root.right))
                
                # Pop fst elem
                self.place_new_user_lst[new_user.id].pop(0)
                self.place_new_user_lst[new_user.id] += tmp_lst
                self.place_new_user(new_user, from_user, nearest)
            elif new_user.game == 2:
                # GAME-2
                tmp_lst = []
                for root in self.place_new_user_lst[new_user.id]:
                    if root.left is None and root.right is None and root.middle is None:  
                        # Choose random number (left || right)
                        random_user_num = randint(1, 3)

                        if random_user_num == 1:
                            root.left = new_user.id
                        elif random_user_num == 2:
                            root.middle = new_user.id
                        else:
                            root.right = new_user.id
                        
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    elif root.middle is None:
                        root.middle = new_user.id
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    elif root.right is None:
                        root.right = new_user.id
                        if root.id in self.system_accounts:
                            new_user.leader = root.username
                        else:
                            new_user.leader = root.id
                        return
                    tmp_lst.append(self.user_exists(id=root.left))
                    tmp_lst.append(self.user_exists(id=root.middle))
                    tmp_lst.append(self.user_exists(id=root.right))

                # Pop fst elem
                self.place_new_user_lst[new_user.id].pop(0)
                self.place_new_user_lst[new_user.id] += tmp_lst
                self.place_new_user(new_user, from_user, nearest)
            
    
    def get_levels_player_cnt(self):
        res = defaultdict(int)
        for user in self.users:
            res[user.cur_level] += 1
        return res
    

    def get_command_players_cnt(self, root_user):
        try:
            if root_user.game == 1 or root_user.game == 3:
                # GAME-1 or START
                left_user, right_user = self.user_exists(id=root_user.left), self.user_exists(id=root_user.right)
                if (not left_user) and (not right_user):
                    return 1
                return self.get_command_players_cnt(root_user=left_user) + self.get_command_players_cnt(root_user=right_user)
            elif root_user.game == 2:
                # GAME-2
                left_user, middle_user, right_user = self.user_exists(id=root_user.left), self.user_exists(id=root_user.middle), self.user_exists(id=root_user.right)
                if (not left_user) and (not middle_user) and (not right_user):
                    return 1
                return self.get_command_players_cnt(root_user=left_user) + self.get_command_players_cnt(root_user=middle_user) + self.get_command_players_cnt(root_user=right_user)
        except:
            return -1
    

    def load_from_db(bot):
        try:
            data = db_functions.get_from_base(table_name)

            if len(data) == 0:
                return

            bot.REQUISITS_COUNTER = data['REQUISITS_COUNTER']

            bot.user_faq_messages = defaultdict(list)
            for key in data['user_faq_messages']:
                bot.user_faq_messages[int(key)] = data['user_faq_messages'][key]
                for i in range(len(bot.user_faq_messages[int(key)])):
                    bot.user_faq_messages[int(key)][i][0][0] = int(bot.user_faq_messages[int(key)][i][0][0])
            
            tmp_dict = {}
            for key in data['start_expert_text']:
                tmp_dict[int(key)] = data['start_expert_text'][key]
            bot.start_expert_text = tmp_dict

            bot.users = data['users']

            users_list = list()
            for one in bot.users:
                if 'id' not in one:
                    continue

                # Other params
                refs_cnt = int(one['refs_cnt'])
                from_user_id = one['from_user_id']
                send_gift_sum = int(one['send_gift_sum'])
                get_gift_sum = int(one['get_gift_sum'])
                levels = one['levels']
                ref_link=one['ref_link']

                one = User(id=one['id'], 
                            privacy_accept=one['privacy_accept'],
                            is_eighteen=one['is_eighteen'],
                            username=one['username'],
                            phone=one['phone'],
                            cur_level=int(one['cur_level']), 
                            left=one['left'],
                            middle=one['middle'],
                            right=one['right'],
                            leader=one['leader'],
                            expert=one['expert'],
                            expert_confirm=one['expert_confirm'],
                            texted_to_leader=one['texted_to_leader'])

                one.refs_cnt = refs_cnt
                one.from_user_id = from_user_id
                one.send_gift_sum = send_gift_sum
                one.get_gift_sum = get_gift_sum
                one.levels = levels
                one.ref_link = ref_link

                if one.leader not in bot.system_accounts and one.leader != None:
                    one.leader = int(one.leader)
                if one.expert not in bot.system_accounts and one.expert != None:
                    one.expert = int(one.expert)
                if one.id not in bot.system_accounts:
                    one.id = int(one.id)
                if one.left not in bot.system_accounts and one.left != None:
                    one.left = int(one.left)
                if one.middle not in bot.system_accounts and one.middle != None:
                    one.middle = int(one.middle)
                if one.right not in bot.system_accounts and one.right != None:
                    one.right = int(one.right)


                # Levels
                tmp_dict = {}
                for key in one.levels:
                    tmp_dict[int(key)] = int(one.levels[key])
                one.levels = tmp_dict

                users_list.append(one)
            bot.users = users_list
        except Exception as e:
            print(e)


    def start(self):
        # self.load_from_db()

        @self.bot.message_handler(commands=['get_logs'])
        def get_logs(message):
            if message.chat.id in self.admins:
                file = open('test.log', 'rb')
                try:
                    self.bot.send_document(chat_id=message.chat.id,
                                        document=file)
                except:
                    pass
                file.close()
                file = open('info.log', 'rb')
                try:
                    self.bot.send_document(chat_id=message.chat.id,
                                        document=file)
                except:
                    pass
                file.close()
                file = open('error.log', 'rb')
                try:
                    self.bot.send_document(chat_id=message.chat.id,
                                        document=file)
                except:
                    pass
                file.close()
                file = open('debug.log', 'rb')
                try:
                    self.bot.send_document(chat_id=message.chat.id,
                                        document=file)
                except:
                    pass
                file.close()

        @self.bot.message_handler(commands=['start'])
        def start_msg(message):
            # If not registered user
            if not self.user_exists(id=message.chat.id):
                self.users.append(User(id=message.chat.id))

            # Reveral-link part
            from_user_id = message.text.split(' ')
            cur_user = self.user_exists(id=message.chat.id)

            # Add username
            if cur_user.username is None:
                cur_user.username = message.from_user.username

            if len(from_user_id) != 1:
                try:
                    from_user_id = int(from_user_id[1])
                except:
                    from_user_id = from_user_id[1]
                from_user = self.user_exists(id=from_user_id)
                from_user.refs_cnt += 1
                if from_user.id in self.system_accounts:
                    cur_user.from_user_id = from_user.username
                else:
                    cur_user.from_user_id = from_user.id
                cur_user.cur_level = from_user.cur_level 

            if not cur_user.is_eighteen:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Подтвердите, что Вам есть 18 лет:',
                                        reply_markup=keyboard.yes_no())
                    
                self.bot.register_next_step_handler(msg, is_eighteen)
            elif not cur_user.privacy_accept:
                self.bot.send_message(chat_id=message.chat.id,
                                                text='Перед регистрацией тебе необходимо принять пользовательское соглашение ⤵️\nhttps://telegra.ph/Polzovatelskoe-soglashenie-i-politika-konfidencialnosti-08-20',
                                                reply_markup=keyboard.privacy_accept())
            else:
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                self.bot.send_photo(chat_id=message.chat.id,
                                    photo=main_menu_photo,
                                    caption=
                                    """Рад тебя приветствовать!\n\nТы уже слышал, что мы запускаем
новое направление, посвящённое личностному росту и саморазвитию?!\n
Прямо сейчас, пока мы готовим наш продукт, ты можешь приобрести промо
версию, связавшись со своим Пригласителем, а после - получить его в
числе первых🚀!""",
                                    reply_markup=keyboard.menu(self, message.chat.id))
            
            # SAVE
            db_functions.save_all(self)
        

# Callback query handler --------------------------------------------------------------------------

        @self.bot.callback_query_handler(func=lambda x: True)
        def callback_handler(call):
            # Split data for PREFIX and DATA
            prefix, data = call.data.split('|')
            
            # Check if None-call
            if prefix is None:
                self.bot.answer_callback_query(callback_query_id=call.id)

            # If not registered user
            if not self.user_exists(id=call.message.chat.id):
                self.bot.answer_callback_query(callback_query_id=call.id,
                                                text='Вы не зарегестированы!')
                return

            if prefix == 'privacy':
                if data == 'deny':
                    self.bot.delete_message(chat_id=call.message.chat.id,
                                            message_id=call.message.id)
                    self.bot.send_message(chat_id=call.message.chat.id,
                                        text='До свидания!',
                                        reply_markup=keyboard.none())
                elif data == 'accept':
                    cur_user = self.user_exists(id=call.message.chat.id)
                    cur_user.privacy_accept = True

                    self.bot.delete_message(chat_id=call.message.chat.id,
                                            message_id=call.message.id)
                    
                    msg = self.bot.send_message(chat_id=call.message.chat.id,
                                        text='Игрок, для регистрации отправь свои контактные данные '
                                        '📇 (обещаем, что тревожить не будем) ',
                                        reply_markup=keyboard.get_user_data())
                    
                    self.bot.register_next_step_handler(msg, request_contacts)
                
            elif prefix == 'text_to_leader':
                cur_user = self.user_exists(id=call.message.chat.id)
                leader = self.user_exists(id=self.user_exists(id=cur_user.leader).leader)

                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                message_id=call.message.id,
                                                reply_markup=keyboard.text_to_leader(leader.id, clicked=True))

                # Level-info
                if cur_user.game == 1 or cur_user.game == 2:
                    # GAME-1 or GAME-2
                    self.bot.send_message(chat_id=cur_user.id,
                                            text=f'Вы находитесь на {cur_user.cur_level}-м уровне игры.\nПодарок для входа в игру - {self.gift_payed[cur_user.cur_level][0] * 1000} ₽')
                elif cur_user.game == 3:
                    # START
                    self.bot.send_message(chat_id=cur_user.id,
                                            text=f'Вы находитесь на {cur_user.cur_level}-м уровне игры.\nПодарок для входа в игру - 500 ₽')

                # Start expert text
                if leader.id in self.system_accounts:
                    sent_requisits = self.system_requisits[randint(0, 1)]
                    self.bot.send_message(chat_id=cur_user.id,
                                        text=sent_requisits)
                    self.REQUISITS_COUNTER.append(sent_requisits)
                elif leader.id in self.start_expert_text:
                    self.bot.send_message(chat_id=cur_user.id,
                                        text=self.start_expert_text[leader.id])

                # For expert
                msg_leader = self.bot.send_message(chat_id=leader.id,
                                                text=f'Вы были приглашены в диалог с @{cur_user.username}.\n'
                                                'Напишите сообщение:',
                                                reply_markup=keyboard.end_dialog(self, 'leader'))
                # For client
                msg_client = self.bot.send_message(chat_id=call.message.chat.id,
                                    text=f'Вы перешли в диалог с @{leader.username}.\nНапишите сообщение:',
                                    reply_markup=keyboard.end_dialog(self, 'client'))

                self.bot.register_next_step_handler(msg_leader, expert_dialog, msg_client, msg_leader)
                self.bot.register_next_step_handler(msg_client, expert_dialog, msg_client, msg_leader)
            # elif prefix == 'yes_no_text_to_leader':
            #     cur_user = self.user_exists(id=call.message.chat.id)
            #     if data == 'yes':
            #         msg = self.bot.send_message(chat_id=call.message.chat.id,
            #                         text='Введите начальный текст для эксперта:',
            #                         reply_markup=keyboard.none())
            #         self.bot.register_next_step_handler(msg, start_expert_text)
            #     else:
            #         self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
            #                                         message_id=call.message.id,
            #                                         reply_markup=keyboard.text_to_leader(cur_user.leader, False))
            #         self.bot.answer_callback_query(call.id)
            elif prefix == 'text_to_leader_success':
                user_id = int(data.split()[0])
                client = self.user_exists(id=user_id)
                expert = self.user_exists(id=self.user_exists(id=client.leader).leader)

                self.bot.clear_step_handler_by_chat_id(client.id)
                self.bot.clear_step_handler_by_chat_id(expert.id)

                msg = self.bot.send_message(chat_id=call.message.chat.id,
                                    text='Подтвердите Ваше действие:',
                                    reply_markup=keyboard.yes_no())

                self.bot.register_next_step_handler(msg, text_to_leader_success_verify, data)
            elif prefix == 'get_referal_link':
                ref_link = MAIN_BOT_LINK + f'?start={data}'
                cur_user = self.user_exists(id=call.message.chat.id)
                cur_user.ref_link = ref_link
                self.bot.edit_message_caption(chat_id=call.message.chat.id,
                                        message_id=call.message.id,
                                        caption=f'Ваша партнерская ссылка готова ✅\n\n{ref_link}')
            elif prefix == 'answer_faq':
                msg = self.bot.send_message(chat_id=call.message.chat.id,
                                    text='Введите ответ пользователю:',
                                    reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, faq_answer, int(data.split()[0]), int(data.split()[1]))
                self.bot.answer_callback_query(call.id)
            elif prefix == 'know_base_test_done':
                is_done, test_num = data.split()
                if is_done == 'False':
                    self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                    message_id=call.message.id,
                                                    reply_markup=keyboard.know_base_test(True, data.split()[1], len(self.base_texts)))
                    if int(test_num) == len(self.base_texts) - 1:
                        with open('images/main_menu_img.jpg', 'rb') as file:
                            main_menu_photo = file.read()
                        self.bot.send_photo(chat_id=call.message.chat.id,
                                        photo=main_menu_photo,
                                        caption=self.hello_message,
                                        reply_markup=keyboard.menu(self, call.message.chat.id))
                        self.bot.clear_step_handler_by_chat_id(call.message.chat.id)
                self.bot.answer_callback_query(call.id)
            elif prefix == 'know_base_next':
                is_done, test_num = data.split()
                if is_done == 'True':
                    is_done = True
                else:
                    is_done = False
                test_num = int(test_num)
                if not is_done:
                    self.bot.answer_callback_query(callback_query_id=call.id,
                                        text='Сначала подтвердите, что вы ознакомились с уроком, нажав кнопку Готово!',
                                        show_alert=True)
                    return
                else:
                    test_num += 1

                if len(self.base_texts) <= test_num:
                    with open('images/main_menu_img.jpg', 'rb') as file:
                        main_menu_photo = file.read()
                    self.bot.send_photo(chat_id=call.message.chat.id,
                                    photo=main_menu_photo,
                                    caption=self.hello_message,
                                    reply_markup=keyboard.menu(self, call.message.chat.id))
                else:
                    self.bot.send_message(chat_id=call.message.chat.id,
                                            text=self.base_texts[test_num],
                                            reply_markup=keyboard.know_base_test(False, test_num, len(self.base_texts)))
                    self.bot.answer_callback_query(call.id) 
            elif prefix == 'team_control_delete':
                try:
                    producer_id = int(data) 
                except:
                    producer_id = data
                cur_user = self.user_exists(id=call.message.chat.id)
                if cur_user.left == producer_id:
                    cur_user.left = None
                elif cur_user.right == producer_id:
                    cur_user.right = None

                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                message_id=call.message.id,
                                                reply_markup=keyboard.team_control(self, call.message.chat.id))
            elif prefix == 'about_game':
                self.bot.answer_callback_query(call.id)
                self.bot.clear_step_handler_by_chat_id(call.message.chat.id)
                if data == 'presentations':
                    with open('images/presentation_img.jpg', 'rb') as file:
                        presentation_photo = file.read()
                    self.bot.edit_message_media(chat_id=call.message.chat.id,
                                        message_id=call.message.id,
                                        media=types.InputMedia(type='photo', media=presentation_photo, caption='Внимательно '
                                        'изучи нашу игру, мы подготовили для тебя несколько форматов презентентации📀💿💾\n'
                                        'https://telegra.ph/Prezentaciya-KV%CE%9BDRIX-08-21'),
                                        reply_markup=keyboard.back_about_game())
                elif data == 'status':
                    with open('images/status_img.jpg', 'rb') as file:
                        status_photo = file.read()
                    self.bot.edit_message_media(chat_id=call.message.chat.id,
                                        message_id=call.message.id,
                                        media=types.InputMedia(type='photo', media=status_photo, caption='По мере игры, ты будешь перемещаться по уровням, занимая разные позиции ⤵️\n\n'
                                        '⚫️ Клиент - дарит подарок Эксперту (единственный раз, когда пользователь дарит '
                                        'собственные средства)\n\n⚫️ Продюсер - приглашает двух клиентов, чтобы '
                                        'отблагодарить своего Эксперта 🙏\n\n⚫️ Эксперт - получает подарки от клиентов\n\n\n'
                                        'Пройди весь путь и почувствуй себя в каждой роли, а мы - поможем тебе в этом ;)'),
                                        reply_markup=keyboard.back_about_game())
                elif data == 'levels':
                    with open('images/levels_img.jpg', 'rb') as file:
                        levels_photo = file.read()
                    self.bot.edit_message_media(chat_id=call.message.chat.id,
                                        message_id=call.message.id,
                                        media=types.InputMedia(type='photo', media=levels_photo, caption='Уровни:\n\n '

                                            '⚜️ На выбор 2 игры (и по 4 уровня в каждой):\n\n '

                                            '⚫️ GAME 1 (2 личных и 4 во второй линии)\n\n '

                                            '📍LVL1: 1к(подарил) - 4к(получил) 🎁\n '
                                            '📍 LVL2: 3к - 12к\n '
                                            '📍 LVL3: 10к - 40к\n '
                                            '📍 LVL4: 30к - 120к\n\n '

                                            '⚫️ GAME 2 (3 личных и 9 во второй линии)\n\n '

                                            '📍 LVL1: 1к(подарил) - 9к(получил)🎁\n '
                                            '📍 LVL2: 5к - 45к\n '
                                            '📍 LVL3: 30к - 270к\n '
                                            '📍 LVL4: 100к - 900к\n\n '

                                            'Можно участвовать в обоих GAMES параллельно😎🔥'),
                                        reply_markup=keyboard.back_about_game())
                elif data == 'rules':
                    with open('images/rules_img.jpg', 'rb') as file:
                        rules_photo = file.read()
                    self.bot.edit_message_media(chat_id=call.message.chat.id,
                                        message_id=call.message.id,
                                        media=types.InputMedia(type='photo', media=rules_photo, caption='Как играть, если не знаешь правил?🤔\n\nДавай разбираться!\n\n'
                                            '💎 После регистрации свяжись с Экспертом и сделай ему подарок (связаться '
                                            'с ним можно из раздела «Начать/продолжить игру»)\n\n'
                                            '↪️Как только ты отправишь подарок, ты становишься клиентом (и сразу '
                                            'попадаешь в white-лист для получения продукта)\n\n'
                                            '↪️Вместе с этим, ты автоматически занимаешь роль продюсера и '
                                            'сразу получаешь возможность приглашать клиентов\n\n'
                                            '↪️После того, как в твоей команде появится первый клиент, ты '
                                            'автоматически становишься экспертом и начинаешь получать '
                                            'подарки от клиентов, которых пригласят твои продюсеры 🥳'),
                                        reply_markup=keyboard.back_about_game())
                elif data == 'back':
                    with open('images/aboutgame_img.jpg', 'rb') as file:
                        about_game_photo = file.read()
                    self.bot.edit_message_media(chat_id=call.message.chat.id,
                                        message_id=call.message.id,
                                        media=types.InputMedia(type='photo', media=about_game_photo, caption='Выберите раздел:'),
                                        reply_markup=keyboard.about_game())
            # SAVE
            db_functions.save_all(self)


        def about_game_back(message):
            if message.text == '<< Назад':
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                self.bot.send_photo(chat_id=message.chat.id,
                                photo=main_menu_photo,
                                caption=self.hello_message,
                                reply_markup=keyboard.menu(self, message.chat.id))
                self.bot.clear_step_handler_by_chat_id(message.chat.id)
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Неизвестная команда!',
                                    reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, about_game_back)
                

# -------------------------------------------------------------------------------------------------


# Next step handlers ------------------------------------------------------------------------------

        def request_contacts(message):
            cur_user = self.user_exists(id=message.chat.id)

            if message.text is not None:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Игрок, для регистрации отправь свои контактные данные '
                                        '📇 (обещаем, что тревожить не будем) ',
                                        reply_markup=keyboard.get_user_data())
                self.bot.register_next_step_handler(msg, request_contacts)
                return

            try:
                cur_user.phone = message.contact.phone_number
                cur_user.username = message.from_user.username
            except:
                self.bot.send_message(chat_id=message.chat.id,
                                        text='❌ Ошибка регистрации - измени имя пользователя',
                                        reply_markup=keyboard.username_exists())
                return

            # Check if username is exists
            if cur_user.username is None:
                self.bot.send_message(chat_id=message.chat.id,
                                        text='❌ Ошибка регистрации - измени имя пользователя',
                                        reply_markup=keyboard.username_exists())
            else:
                self.bot.send_message(chat_id=message.chat.id,
                                        text='☑️ Вы успешно зарегистрировались',
                                        reply_markup=keyboard.none())
                
                # Games
                # msg = self.bot.send_message(chat_id=message.chat.id,
                #                     text='Выберите игру:',
                #                     reply_markup=keyboard.game_list())
                # self.bot.register_next_step_handler(msg, game_choice)

                # If user comes NOT for referal-link
                cur_user.game = 1
                msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Выберите уровень:',
                                        reply_markup=keyboard.level_choice())
                self.bot.register_next_step_handler(msg, functions.level_choice, self)
            
            # SAVE
            db_functions.save_all(self)


        def start_game(message):
            if message.text == '<< Назад':
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                self.bot.send_photo(chat_id=message.chat.id,
                                    photo=main_menu_photo,
                                    caption=self.hello_message,
                                    reply_markup=keyboard.menu(self, message.chat.id))
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Неизвестная команда!',
                                        reply_markup=keyboard.start_game())
                self.bot.register_next_step_handler(msg, start_game)
        

        def expert_dialog(message, user_message, expert_message):
            cur_user = self.user_exists(id=message.chat.id)

            if cur_user.id == user_message.chat.id:
                other = self.user_exists(id=expert_message.chat.id)
            else:
                other = self.user_exists(id=user_message.chat.id)

            NOW_DIALOGS.append([cur_user.id, other.id])

            # Gifts_cnt
            if message.text == '🎁 Подарок отправлен' or message.text == 'Завершить диалог' and \
                ([cur_user.id, other.id] not in NOW_DIALOGS and [other.id, cur_user.id] not in NOW_DIALOGS):
                if cur_user.game == 1 or cur_user.game == 2:
                    # GAME-1 or GAME-2
                    if other.texted_to_leader:
                        other.get_gift_sum += self.gift_payed[other.cur_level][1] * 1000
                        cur_user.send_gift_sum += self.gift_payed[cur_user.cur_level][0] * 1000
                    else:
                        other.send_gift_sum += self.gift_payed[other.cur_level][0] * 1000
                        cur_user.get_gift_sum += self.gift_payed[cur_user.cur_level][1] * 1000
                elif cur_user.game == 3:
                    # START
                    if other.texted_to_leader:
                        other.get_gift_sum += 500
                        cur_user.send_gift_sum += 500
                    else:
                        other.send_gift_sum += 500
                        cur_user.get_gift_sum += 500
                
                # SAVE
                db_functions.save_all(self)
    
            if message.text == '🎁 Подарок отправлен' or message.text == 'Завершить диалог':
                if other.texted_to_leader:
                    self.bot.send_message(chat_id=other.id,
                                        text='Вам отправили подарок 🎁',
                                        reply_markup=keyboard.text_to_leader_success(cur_user.id, other.id))
                    self.bot.send_message(chat_id=cur_user.id,
                                        text='Подарок отправлен ✅\nОжидайте подтверждение эксперта!',
                                        reply_markup=keyboard.none())
                else:
                    self.bot.send_message(chat_id=other.id,
                                        text='Эксперт завершил диалог.\nОжидайте подтверждение эксперта!',
                                        reply_markup=keyboard.none())
                    self.bot.send_message(chat_id=cur_user.id,
                                        text='Вы завершили диалог',
                                        reply_markup=keyboard.text_to_leader_success(other.id, cur_user.id))
            else:
                if expert_message.chat.id == other.id:
                    self.bot.send_message(chat_id=other.id,
                                        text=f'<b>@{cur_user.username}:</b> ' + message.text,
                                        parse_mode='HTML',
                                        reply_markup=keyboard.end_dialog(self, 'leader'))
                else:
                    self.bot.send_message(chat_id=other.id,
                                        text=f'<b>@{cur_user.username}:</b> ' + message.text,
                                        parse_mode='HTML',
                                        reply_markup=keyboard.end_dialog(self, 'client'))
                
            self.bot.clear_step_handler_by_chat_id(other.id)
            self.bot.clear_step_handler_by_chat_id(message.chat.id)

            self.bot.register_next_step_handler_by_chat_id(user_message.chat.id, expert_dialog, user_message, expert_message)
            self.bot.register_next_step_handler_by_chat_id(expert_message.chat.id, expert_dialog, user_message, expert_message)


        def faq(message):
            if message.text == '<< Назад':
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                self.bot.send_photo(chat_id=message.chat.id,
                                    photo=main_menu_photo,
                                    caption=self.hello_message,
                                    reply_markup=keyboard.menu(self, message.chat.id))
            elif message.text == 'Написать в тех. поддержку':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Введите Ваше сообщение:',
                                            reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, faq_message)
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Неизвестная команда!',
                                    reply_markup=keyboard.faq())
                self.bot.register_next_step_handler(msg, faq)


        def faq_message(message):
            if message.text == '<< Назад':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Мы стараемся обеспечивать бесперебойную работу системы 24/7 и '
                                        'следим за тем, чтобы она работала так же стабильно, как и твоё желание '
                                        'расти и развиваться (а это значит - постоянно🚀)\n\nНо, если возникли '
                                        'трудности и тебе нужна помощь - мы на связи 📲',
                                        reply_markup=keyboard.faq())
                self.bot.register_next_step_handler(msg, faq)
            else:
                # Add to db
                self.user_faq_messages[message.chat.id].append([[message.chat.id, message.text], functions.get_today_date()])

                # SAVE
                db_functions.save_all(self)

                # Send to admins
                for admin_id in self.admins:
                    msg_id = len(self.user_faq_messages[message.chat.id]) - 1
                    self.bot.send_message(chat_id=admin_id,
                                        text=f'<b>Сообщение от пользователя (тех. поддержка):</b>\nПользователь: @{self.user_exists(id=message.chat.id).username}\nСообщение: {message.text}',
                                        parse_mode='HTML',
                                        reply_markup=keyboard.answer_faq(message.chat.id, msg_id))
                        
                self.bot.send_message(chat_id=message.chat.id,
                                    text='Ваше сообщение успешно доставлено администраторам!\n'
                                    'В ближайшее время Вы получите от них ответ, пожалуйста, ожидайте.',
                                    reply_markup=keyboard.menu(self, message.chat.id))
        

        def faq_answer(message, user_id, msg_id):
            if message.text == '<< Назад':
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                self.bot.send_photo(chat_id=message.chat.id,
                                    photo=main_menu_photo,
                                    caption=self.hello_message,
                                    reply_markup=keyboard.menu(self, message.chat.id))
            else:
                question_message = self.user_faq_messages[user_id].pop(msg_id)
                self.bot.send_message(chat_id=user_id,
                                    text=f'<b>Ваш вопрос:</b>\n{question_message[0][1]}\n<b>Ответ от тех. поддержки:</b>\n{message.text}',
                                    parse_mode='HTML',
                                    reply_markup=keyboard.menu(self, user_id))
                self.bot.send_message(chat_id=message.chat.id,
                                    text='Ваш ответ успешно доставлен пользователю!',
                                    reply_markup=keyboard.menu(self, message.chat.id))
                self.bot.clear_step_handler_by_chat_id(user_id)
                self.bot.clear_step_handler_by_chat_id(message.chat.id)

                # SAVE
                db_functions.save_all(self)
            
        
        def know_base(message):
            if message.text == '<< Назад':
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                self.bot.send_photo(chat_id=message.chat.id,
                                    photo=main_menu_photo,
                                    caption=self.hello_message,
                                    reply_markup=keyboard.menu(self, message.chat.id))
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Неизвестная команда!',
                                    reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, know_base)
        

        def team_control(message):
            if message.text == '<< Назад':
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                self.bot.send_photo(chat_id=message.chat.id,
                                    photo=main_menu_photo,
                                    caption=self.hello_message,
                                    reply_markup=keyboard.menu(self, message.chat.id))
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Неизвестная команда!',
                                    reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, know_base)


        def start_expert_text(message):
            if message.text == '<< Назад':
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                self.bot.send_photo(chat_id=message.chat.id,
                                    photo=main_menu_photo,
                                    caption=self.hello_message,
                                    reply_markup=keyboard.menu(self, message.chat.id))
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Подтвердить введенный текст?',
                                    reply_markup=keyboard.yes_no())
                self.bot.register_next_step_handler(msg, start_expert_text_confirm, message.text)
        

        def start_expert_text_confirm(message, expert_text):
            if message.text == 'Да':
                cur_user = self.user_exists(id=message.chat.id)

                self.start_expert_text[cur_user.id] = expert_text

                # SAVE
                db_functions.save_all(self)

                self.bot.send_message(chat_id=message.chat.id,
                                    text='Начальный текст успешно установлен!',
                                    reply_markup=keyboard.menu(self, message.chat.id))
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Введите начальный текст для клиента:',
                                    reply_markup=keyboard.none())
                self.bot.register_next_step_handler(msg, start_expert_text)
        

        def text_to_leader_success_verify(message, data):
            user_id = int(data.split()[0])
            client = self.user_exists(id=user_id)
            expert = self.user_exists(id=self.user_exists(id=client.leader).leader)
            
            if message.text == 'Да':
                if [client.id, expert.id] in NOW_DIALOGS:
                    NOW_DIALOGS.pop(NOW_DIALOGS.index([client.id, expert.id]))
                elif [expert.id, client.id] in NOW_DIALOGS:
                    NOW_DIALOGS.pop(NOW_DIALOGS.index([expert.id, client.id]))
                client.texted_to_leader = True
                
                # Client
                self.bot.send_message(chat_id=client.id,
                                    text=f'Поздравляю, Ваш эксперт @{expert.username} - '
                                    'успешно подтвердил, что Вы связались с ним!',
                                    reply_markup=keyboard.menu(self, client.id))
                
                self.bot.send_message(chat_id=client.id,
                                        text='Не забудь вступить в наш чат Экспертов - https://t.me/+obxJYB0Y7QpiNDdi')

                # Add expert for user
                client.expert = expert.id
                
                if client.game == 1 or client.game == 3:
                    # GAME-1 or START
                    if client.left is None:
                        producer_1 = 'Свободно'
                    else:
                        producer_1 = self.user_exists(id=client.left)
                    if client.right is None:
                        producer_2 = 'Свободно'
                    else:
                        producer_2 = self.user_exists(id=client.right)
                    if producer_1 == 'Свободно':
                        client_1 = 'Свободно'
                        client_2 = 'Свободно'
                    else:
                        if producer_1.left is None:
                            client_1 = 'Свободно'
                        else:
                            client_1 = self.user_exists(id=producer_1.left)
                        if producer_1.right is None:
                            client_2 = 'Свободно'
                        else:
                            client_2 = self.user_exists(id=producer_1.right)
                    if producer_2 == 'Свободно':
                        client_3 = 'Свободно'
                        client_4 = 'Свободно'
                    else:
                        if producer_2.left is None:
                            client_3 = 'Свободно'
                        else:
                            client_3 = self.user_exists(id=producer_2.left)
                        if producer_2.right is None:
                            client_4 = 'Свободно'
                        else:
                            client_4 = self.user_exists(id=producer_2.right)
                    
                    if producer_1 != 'Свободно':
                        producer_1 = f'@{producer_1.username}'
                    if producer_2 != 'Свободно':
                        producer_2 = f'@{producer_2.username}'
                    if client_1 != 'Свободно':
                        client_1 = f'@{client_1.username}'
                    if client_2 != 'Свободно':
                        client_2 = f'@{client_2.username}'
                    if client_3 != 'Свободно':
                        client_3 = f'@{client_3.username}'
                    if client_4 != 'Свободно':
                        client_4 = f'@{client_4.username}'
                    
                elif client.game == 2:
                    # GAME-2
                    if client.left is None:
                        producer_1 = 'Свободно'
                    else:
                        producer_1 = self.user_exists(id=client.left)
                    if client.middle is None:
                        producer_2 = 'Свободно'
                    else:
                        producer_2 = self.user_exists(id=client.middle)
                    if client.right is None:
                        producer_3 = 'Свободно'
                    else:
                        producer_3 = self.user_exists(id=client.right)

                    if producer_1 == 'Свободно':
                        client_1 = 'Свободно'
                        client_2 = 'Свободно'
                        client_3 = 'Свободно'
                    else:
                        if producer_1.left is None:
                            client_1 = 'Свободно'
                        else:
                            client_1 = self.user_exists(id=producer_1.left)
                        if producer_1.middle is None:
                            client_2 = 'Свободно'
                        else:
                            client_2 = self.user_exists(id=producer_1.middle)
                        if producer_1.right is None:
                            client_3 = 'Свободно'
                        else:
                            client_3 = self.user_exists(id=producer_1.right)

                    if producer_2 == 'Свободно':
                        client_4 = 'Свободно'
                        client_5 = 'Свободно'
                        client_6 = 'Свободно'
                    else:
                        if producer_2.left is None:
                            client_4 = 'Свободно'
                        else:
                            client_4 = self.user_exists(id=producer_2.left)
                        if producer_2.middle is None:
                            client_5 = 'Свободно'
                        else:
                            client_5 = self.user_exists(id=producer_2.middle)
                        if producer_2.right is None:
                            client_6 = 'Свободно'
                        else:
                            client_6 = self.user_exists(id=producer_2.right)

                    if producer_3 == 'Свободно':
                        client_7 = 'Свободно'
                        client_8 = 'Свободно'
                        client_9 = 'Свободно'
                    else:
                        if producer_3.left is None:
                            client_7 = 'Свободно'
                        else:
                            client_7 = self.user_exists(id=producer_3.left)
                        if producer_3.middle is None:
                            client_8 = 'Свободно'
                        else:
                            client_8 = self.user_exists(id=producer_3.middle)
                        if producer_3.right is None:
                            client_9 = 'Свободно'
                        else:
                            client_9 = self.user_exists(id=producer_3.right)
                    
                    if producer_1 != 'Свободно':
                        producer_1 = f'@{producer_1.username}'
                    if producer_2 != 'Свободно':
                        producer_2 = f'@{producer_2.username}'
                    if producer_3 != 'Свободно':
                        producer_3 = f'@{producer_3.username}'
                    if client_1 != 'Свободно':
                        client_1 = f'@{client_1.username}'
                    if client_2 != 'Свободно':
                        client_2 = f'@{client_2.username}'
                    if client_3 != 'Свободно':
                        client_3 = f'@{client_3.username}'
                    if client_4 != 'Свободно':
                        client_4 = f'@{client_4.username}'
                    if client_5 != 'Свободно':
                        client_5 = f'@{client_5.username}'
                    if client_6 != 'Свободно':
                        client_6 = f'@{client_6.username}'
                    if client_7 != 'Свободно':
                        client_7 = f'@{client_7.username}'
                    if client_8 != 'Свободно':
                        client_8 = f'@{client_8.username}'
                    if client_9 != 'Свободно':
                        client_9 = f'@{client_9.username}'

                self.bot.send_message(chat_id=expert.id,
                                    text='Вы подтвердили получение подарка!',
                                    reply_markup=keyboard.menu(self, expert.id))
                
                # SAVE
                db_functions.save_all(self)
            elif message.text == 'Нет':
                self.bot.send_message(chat_id=expert.id,
                                    text='Вы отклонили получение подарка!',
                                    reply_markup=keyboard.menu(self, expert.id))
                try:
                    self.bot.send_message(chat_id=client.id,
                                        text='Эксперт отклонил Ваш подарок, свяжитесь с ним еще раз для выяснений обстоятельств:',
                                        reply_markup=keyboard.text_to_leader(expert.id, False))
                except:
                    pass
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Подтвердите Ваше действие:',
                                    reply_markup=keyboard.yes_no())
                self.bot.register_next_step_handler(msg, text_to_leader_success_verify, data)


        def my_account(message):
            if message.text == '<< Назад':
                with open('images/main_menu_img.jpg', 'rb') as file:
                    main_menu_photo = file.read()
                self.bot.send_photo(chat_id=message.chat.id,
                                    photo=main_menu_photo,
                                    caption=self.hello_message,
                                    reply_markup=keyboard.menu(self, message.chat.id))
            #elif message.text == 'Управление аккаунтами':
            #    # TO DO
            #    pass
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Неизвестная команда!',
                                    reply_markup=keyboard.my_account())
                self.bot.register_next_step_handler(msg, my_account)
        

        def game_choice(message):
            cur_user = self.user_exists(id=message.chat.id)

            if message.text == 'GAME-1':
                cur_user.game = 1
            #elif message.text == 'GAME-2':
            #    cur_user.game = 2
            elif message.text == 'START':
               cur_user.game = 3
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Данной игры нет в списке!',
                                    reply_markup=keyboard.game_list())
                self.bot.register_next_step_handler(msg, game_choice)
                return
                
            if message.text in ['GAME-1', 'GAME-2', 'START']:
                if cur_user.from_user_id is None and cur_user.game != 3:
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Выберите уровень:',
                                        reply_markup=keyboard.level_choice())
                    self.bot.register_next_step_handler(msg, functions.level_choice, self)
                elif cur_user.from_user_id is None and cur_user.game == 3:
                    # START
                    cur_user.texted_to_leader = True

                    # Place-new-user function
                    root_user = self.user_exists(id=self.START_GAME_ROOT)  
                    self.place_new_user_lst[cur_user.id] = [root_user]   
                    cur_user.leader = root_user.id

                    lider = self.user_exists(id=cur_user.leader)
                    with open('images/main_menu_img.jpg', 'rb') as file:
                        main_menu_photo = file.read()
                    self.bot.send_photo(chat_id=message.chat.id,
                                        photo=main_menu_photo,
                                        caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                        'не верит больше никто»\n\n'
                                        'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                        'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                        'конечно - много-много подарков😻🎁\n\n'
                                        f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                        reply_markup=keyboard.menu(self, message.chat.id))
                else:
                    # If user comes NOT for referal-link
                    if cur_user.from_user_id is None:
                        # Place-new-user function
                        root_user = None
                        for user in self.users:
                            if user.cur_level == cur_user.cur_level and user.leader == user.username and \
                                 cur_user != user and user.game == cur_user.game:
                                root_user = user
                                break
                        if root_user is None:
                            root_user = self.users[0]    

                        self.place_new_user_lst[cur_user.id] = [root_user]   
                        self.place_new_user(new_user=self.user_exists(message.chat.id))

                        lider = self.user_exists(id=self.user_exists(id=cur_user.leader).leader)
                        if cur_user.game == 1 or cur_user.game == 2:
                            # GAME-1 or GAME-2
                            self.bot.send_message(chat_id=message.chat.id,
                                                text=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                                'не верит больше никто»\n\n'
                                                'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                                'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                                'конечно - много-много подарков😻🎁\n\n'
                                                f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                                reply_markup=keyboard.text_to_leader(lider.id))
                        elif cur_user.game == 3:
                            # START
                            cur_user.texted_to_leader = True

                            lider = self.user_exists(id=self.user_exists(id=cur_user.leader).leader)
                            with open('images/main_menu_img.jpg', 'rb') as file:
                                main_menu_photo = file.read()
                            self.bot.send_photo(chat_id=message.chat.id,
                                                photo=main_menu_photo,
                                                caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                                'не верит больше никто»\n\n'
                                                'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                                'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                                'конечно - много-много подарков😻🎁\n\n'
                                                f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                                reply_markup=keyboard.menu(self, message.chat.id))
                    else:
                        self.bot.send_message(chat_id=message.chat.id,
                                            text=f'Твой пригласитель - @{self.user_exists(id=cur_user.from_user_id).username}',
                                            reply_markup=keyboard.none())
                        
                        cur_user = self.user_exists(id=message.chat.id)
                        from_user = self.user_exists(id=cur_user.from_user_id)

                        if from_user.left is not None and from_user.right is not None:
                            msg = self.bot.send_message(chat_id=message.chat.id,
                                                text=f'Вы не можете зарегистрироваться в команду '
                                                f'к @{from_user.username}, так как у него нет мест',
                                                reply_markup=keyboard.full_choose_group())
                            self.bot.register_next_step_handler(msg, functions.full_choose_group, self)
                        else:
                            if from_user.left is None:
                                from_user.left = message.chat.id
                            else:
                                from_user.right = message.chat.id
                            
                            # if 'system' in from_user.username:
                            #     cur_user.leader = self.user_exists(id=from_user.username).id
                            # else:

                            cur_user.leader = self.user_exists(id=from_user.id).id   
                            lider = self.user_exists(id=self.user_exists(id=cur_user.leader).leader)
    
                            if cur_user.game == 1 or cur_user.game == 2 or \
                                (cur_user.game == 3 and from_user.id in self.system_accounts):
                                # GAME-1 or GAME-2                   
                                self.bot.send_message(chat_id=message.chat.id,
                                                    text=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                                    'не верит больше никто»\n\n'
                                                    'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                                    'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                                    'конечно - много-много подарков😻🎁\n\n'
                                                    f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}\n',
                                                    reply_markup=keyboard.text_to_leader(lider.id))
                            elif cur_user.game == 3:
                                # START
                                with open('images/main_menu_img.jpg', 'rb') as file:
                                    main_menu_photo = file.read()
                                self.bot.send_photo(chat_id=message.chat.id,
                                                    photo=main_menu_photo,
                                                    caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                                    'не верит больше никто»\n\n'
                                                    'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                                    'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                                    'конечно - много-много подарков😻🎁\n\n'
                                                    f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}\n',
                                                    reply_markup=keyboard.menu(self, message.chat.id))
            # SAVE
            db_functions.save_all(self)


        def is_eighteen(message):
            if message.text == 'Нет':
                self.bot.send_message(chat_id=message.chat.id,
                                    text='Игра доступна только лицам старше 18 лет',
                                    reply_markup=keyboard.none())
            elif message.text == 'Да':
                cur_user = self.user_exists(id=message.chat.id)
                cur_user.is_eighteen = True

                # SAVE
                db_functions.save_all(self)

                self.bot.send_message(chat_id=message.chat.id,
                                    text='Успешно!\nДобро пожаловать!',
                                    reply_markup=keyboard.none())

                self.bot.send_message(chat_id=message.chat.id,
                                        text='Перед регистрацией тебе необходимо принять пользовательское соглашение ⤵️\nhttps://telegra.ph/Polzovatelskoe-soglashenie-i-politika-konfidencialnosti-08-20',
                                        reply_markup=keyboard.privacy_accept())
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                    text='Неизвестная команда!\nИгра доступна только лицам старше 18 лет!',
                                    reply_markup=keyboard.yes_no())
                self.bot.register_next_step_handler(msg, is_eighteen)

# -------------------------------------------------------------------------------------------------


# Message handler ---------------------------------------------------------------------------------

        @self.bot.message_handler(content_types=['text'])
        def message_handler(message):
            # If not registered user
            if not self.user_exists(id=message.chat.id):
                self.users.append(User(id=message.chat.id))

            cur_user = self.user_exists(id=message.chat.id)

            # Add username
            if cur_user.username is None:
                cur_user.username = message.from_user.username

            if not cur_user.is_eighteen:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Подтвердите, что Вам есть 18 лет:',
                                        reply_markup=keyboard.yes_no())
                    
                self.bot.register_next_step_handler(msg, is_eighteen)
            elif not cur_user.privacy_accept:
                self.bot.send_message(chat_id=message.chat.id,
                                        text='Перед регистрацией тебе необходимо принять пользовательское соглашение ⤵️\nhttps://telegra.ph/Polzovatelskoe-soglashenie-i-politika-konfidencialnosti-08-20',
                                        reply_markup=keyboard.privacy_accept())
            else:
                # For registered users
                if message.text == 'Начать':
                    with open('images/main_menu_img.jpg', 'rb') as file:
                        main_menu_photo = file.read()
                    self.bot.send_photo(chat_id=message.chat.id,
                                        photo=main_menu_photo,
                                        caption=self.hello_message,
                                        reply_markup=keyboard.menu(self, message.chat.id))
                elif message.text == 'Имя пользователя есть' and (cur_user.phone is None or cur_user.username is None):
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Игрок, для регистрации отправь свои контактные данные 📇 (обещаем, что тревожить не будем) ',
                                        reply_markup=keyboard.get_user_data())
                    self.bot.register_next_step_handler(msg, request_contacts)
                elif message.text == '💡 База знаний':
                    # if not cur_user.texted_to_leader:
                    #     self.bot.send_message(chat_id=message.chat.id,
                    #                         text='Вы не связались с Вашим лидером, или Ваш лидер еще не подтвердил Вашу связь!\nВам пока закрыт доступ в этот раздел!',
                    #                         reply_markup=keyboard.menu(self, message.chat.id))
                    # else:
                    with open('images/knowbase_img.jpg', 'rb') as file:
                        know_base_photo = file.read()
                    self.bot.send_photo(chat_id=message.chat.id,
                                        photo=know_base_photo,
                                        reply_markup=keyboard.back())
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='1. Как составить список ч.1\n\n'
                                            'Кого приглашать?🤔\n'
                                            '⤵️ Первый ролик из раздела, посвящённого составлению списка '
                                            'аудитории (сначала проводим подготовку!)\n'
                                            'https://youtu.be/kiULdTSE7g0',
                                        reply_markup=keyboard.know_base_test(False, 0, len(self.base_texts)))
                    self.bot.register_next_step_handler(msg, know_base)
                elif message.text == 'Об игре 🎲':
                    with open('images/aboutgame_img.jpg', 'rb') as file:
                        about_game_photo = file.read()
                    self.bot.send_photo(chat_id=message.chat.id,
                                        caption='Выберите раздел:',
                                        photo=about_game_photo,
                                        reply_markup=keyboard.about_game())
                elif message.text == '🎁 KVΛDRIX GAME 🎁':
                    if cur_user.game == 1 or cur_user.game == 3:
                        # GAME-1 or START
                        if cur_user.left is None:
                            producer_1 = 'Свободно'
                        else:
                            producer_1 = self.user_exists(id=cur_user.left)
                        if cur_user.right is None:
                            producer_2 = 'Свободно'
                        else:
                            producer_2 = self.user_exists(id=cur_user.right)
                        if producer_1 == 'Свободно':
                            client_1 = 'Свободно'
                            client_2 = 'Свободно'
                        else:
                            if producer_1.left is None:
                                client_1 = 'Свободно'
                            else:
                                client_1 = self.user_exists(id=producer_1.left)
                            if producer_1.right is None:
                                client_2 = 'Свободно'
                            else:
                                client_2 = self.user_exists(id=producer_1.right)
                        if producer_2 == 'Свободно':
                            client_3 = 'Свободно'
                            client_4 = 'Свободно'
                        else:
                            if producer_2.left is None:
                                client_3 = 'Свободно'
                            else:
                                client_3 = self.user_exists(id=producer_2.left)
                            if producer_2.right is None:
                                client_4 = 'Свободно'
                            else:
                                client_4 = self.user_exists(id=producer_2.right)
                        
                        if producer_1 != 'Свободно':
                            producer_1 = f'@{producer_1.username}'
                        if producer_2 != 'Свободно':
                            producer_2 = f'@{producer_2.username}'
                        if client_1 != 'Свободно':
                            client_1 = f'@{client_1.username}'
                        if client_2 != 'Свободно':
                            client_2 = f'@{client_2.username}'
                        if client_3 != 'Свободно':
                            client_3 = f'@{client_3.username}'
                        if client_4 != 'Свободно':
                            client_4 = f'@{client_4.username}'
                        
                        with open('images/game_img.jpg', 'rb') as file:
                            game_photo = file.read() 
                        msg = self.bot.send_photo(chat_id=message.chat.id,
                                            photo=game_photo,
                                            caption=f'⚜️Твой статус - Эксперт⚜️\n\n🔵Продюсер 1 - {producer_1}\n'
                                            f'🔵Продюсер 2 - {producer_2}\n\n🟢Клиент 1 - {client_1}\n'
                                            f'🟢Клиент 2 - {client_2}\n🟢Клиент 3 - {client_3}\n🟢Клиент 4 - {client_4}',
                                            reply_markup=keyboard.menu(self, message.chat.id))
                    elif cur_user.game == 2:
                        # GAME-2 
                        if cur_user.left is None:
                            producer_1 = 'Свободно'
                        else:
                            producer_1 = self.user_exists(id=cur_user.left)
                        if cur_user.middle is None:
                            producer_2 = 'Свободно'
                        else:
                            producer_2 = self.user_exists(id=cur_user.middle)
                        if cur_user.right is None:
                            producer_3 = 'Свободно'
                        else:
                            producer_3 = self.user_exists(id=cur_user.right)

                        if producer_1 == 'Свободно':
                            client_1 = 'Свободно'
                            client_2 = 'Свободно'
                            client_3 = 'Свободно'
                        else:
                            if producer_1.left is None:
                                client_1 = 'Свободно'
                            else:
                                client_1 = self.user_exists(id=producer_1.left)
                            if producer_1.middle is None:
                                client_2 = 'Свободно'
                            else:
                                client_2 = self.user_exists(id=producer_1.middle)
                            if producer_1.right is None:
                                client_3 = 'Свободно'
                            else:
                                client_3 = self.user_exists(id=producer_1.right)

                        if producer_2 == 'Свободно':
                            client_4 = 'Свободно'
                            client_5 = 'Свободно'
                            client_6 = 'Свободно'
                        else:
                            if producer_2.left is None:
                                client_4 = 'Свободно'
                            else:
                                client_4 = self.user_exists(id=producer_2.left)
                            if producer_2.middle is None:
                                client_5 = 'Свободно'
                            else:
                                client_5 = self.user_exists(id=producer_2.middle)
                            if producer_2.right is None:
                                client_6 = 'Свободно'
                            else:
                                client_6 = self.user_exists(id=producer_2.right)

                        if producer_3 == 'Свободно':
                            client_7 = 'Свободно'
                            client_8 = 'Свободно'
                            client_9 = 'Свободно'
                        else:
                            if producer_3.left is None:
                                client_7 = 'Свободно'
                            else:
                                client_7 = self.user_exists(id=producer_3.left)
                            if producer_3.middle is None:
                                client_8 = 'Свободно'
                            else:
                                client_8 = self.user_exists(id=producer_3.middle)
                            if producer_3.right is None:
                                client_9 = 'Свободно'
                            else:
                                client_9 = self.user_exists(id=producer_3.right)
                        
                        if producer_1 != 'Свободно':
                            producer_1 = f'@{producer_1.username}'
                        if producer_2 != 'Свободно':
                            producer_2 = f'@{producer_2.username}'
                        if producer_3 != 'Свободно':
                            producer_3 = f'@{producer_3.username}'
                        if client_1 != 'Свободно':
                            client_1 = f'@{client_1.username}'
                        if client_2 != 'Свободно':
                            client_2 = f'@{client_2.username}'
                        if client_3 != 'Свободно':
                            client_3 = f'@{client_3.username}'
                        if client_4 != 'Свободно':
                            client_4 = f'@{client_4.username}'
                        if client_5 != 'Свободно':
                            client_5 = f'@{client_5.username}'
                        if client_6 != 'Свободно':
                            client_6 = f'@{client_6.username}'
                        if client_7 != 'Свободно':
                            client_7 = f'@{client_7.username}'
                        if client_8 != 'Свободно':
                            client_8 = f'@{client_8.username}'
                        if client_9 != 'Свободно':
                            client_9 = f'@{client_9.username}'
                        
                        with open('images/game_img.jpg', 'rb') as file:
                            game_photo = file.read() 
                        self.bot.send_photo(chat_id=cur_user.id,
                                            photo=game_photo,
                                            caption=f'⚜️Твой статус - Эксперт⚜️\n\n🔵Продюсер-1 - {producer_1}\n'
                                            f'🔵Продюсер-2 - {producer_2}\nПродюсер-3 - {producer_3}\n\n🟢Клиент-1 - {client_1}\n'
                                            f'🟢Клиент-2 - {client_2}\n🟢Клиент-3 - {client_3}\n🟢Клиент-4 - {client_4}\nКлиент-5 - {client_5}\n'
                                            f'Клиент-6 - {client_6}\nКлиент-7 - {client_7}\nКлиент-8 - {client_8}\nКлиент-9 - {client_9}',
                                            reply_markup=keyboard.menu(self, cur_user.id))
                    # self.bot.register_next_step_handler(msg, start_game)
                elif message.text == 'Управление командой':
                    cur_user = self.user_exists(id=message.chat.id)
                    if cur_user.left is not None or cur_user.right is not None:
                        self.bot.send_message(chat_id=message.chat.id,
                                            text='... Переход к управлению командой ...',
                                            reply_markup=keyboard.back())
                        msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Список продюсеров на Вашем уровне:',
                                            reply_markup=keyboard.team_control(self, message.chat.id))
                        self.bot.register_next_step_handler(msg, team_control)
                    else:
                        self.bot.send_message(chat_id=message.chat.id,
                                            text='У Вас еще нет продюсеров на Вашем уровне!',
                                            reply_markup=keyboard.menu(self, message.chat.id))
                elif message.text == '⚙️ Тех. Поддержка':
                    with open('images/faq_img.jpg', 'rb') as file:
                        faq_photo = file.read()
                    msg = self.bot.send_photo(chat_id=message.chat.id,
                                        photo=faq_photo,
                                        caption='Мы стараемся обеспечивать бесперебойную работу системы 24/7 и следим за тем, чтобы она работала так же стабильно, как и твоё желание расти и развиваться (а это значит - постоянно🚀)\n\nНо, если возникли трудности и тебе нужна помощь - мы на связи 📲',
                                        reply_markup=keyboard.faq())
                    self.bot.register_next_step_handler(msg, faq)
                elif message.text == 'Партнерская ссылка 🕸':
                    with open('images/ref_link_img.jpg', 'rb') as file:
                        ref_link_photo = file.read()
                    if cur_user.ref_link is None:
                        self.bot.send_photo(chat_id=message.chat.id,
                                            photo=ref_link_photo,
                                            caption='«Если народ един - он непобедим!»🏆\n\n💎 Ты можешь ждать, пока выйдет наш продукт и предвкушать его появление, а можешь - начать строить команду и получать подарки, многократно окупая стоимость собственного 🎁\n\n⤵️ Отправь партнерскую ссылку своему другу и продолжите вместе это увлекательное путешествие',
                                            reply_markup=keyboard.get_referal_link(message.chat.id))
                    else:
                        self.bot.send_photo(chat_id=message.chat.id,
                                            photo=ref_link_photo,                                            
                                            caption=f'Ваша партнерская ссылка готова ✅\n\n{cur_user.ref_link}',
                                            reply_markup=keyboard.menu(self, message.chat.id))
                    # SAVE
                    db_functions.save_all(self)
                elif message.text == 'Сообщения в тех. поддержку (только для админов)':
                    if not self.faq_msgs_exist():
                        self.bot.send_message(chat_id=message.chat.id,
                                            text='Нет ни одного сообщения в тех. поддержку')
                    else:
                        for user_id in self.user_faq_messages:
                            for faq_msg_i in range(len(self.user_faq_messages[user_id])):
                                faq_msg = self.user_faq_messages[user_id][faq_msg_i]
                                self.bot.send_message(chat_id=message.chat.id,
                                                    text=f'<b>{faq_msg[1]}</b>\nПользователь: @{self.user_exists(id=faq_msg[0][0]).username}\nСообщение: {faq_msg[0][1]}',
                                                    parse_mode='HTML',
                                                    reply_markup=keyboard.answer_faq(user_id, faq_msg_i))
                elif message.text == '💳 Мои реквизиты 💳':
                    if cur_user.id not in self.start_expert_text:
                        msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='У Вас пока нет начальных текстов!\n\nВведите начальный текст для клиента:',
                                            reply_markup=keyboard.back())
                    else: 
                        msg = self.bot.send_message(chat_id=message.chat.id,
                                                text=f'Предыдущий начальный текст для клиента: <b>{self.start_expert_text[cur_user.id]}</b>\n\nВведите начальный текст для клиента:',
                                                parse_mode='HTML',
                                                reply_markup=keyboard.back())
                    self.bot.register_next_step_handler(msg, start_expert_text)
                elif message.text == '👑 Мой аккаунт 👑':
                    command_players_cnt = self.get_command_players_cnt(cur_user)
                    levels_player_cnt = self.get_levels_player_cnt()

                    if cur_user.leader is None:
                        cur_game_expert = None
                    else:
                        cur_game_expert = self.user_exists(id=self.user_exists(id=cur_user.leader).leader).username

                    if cur_user.expert is None:
                        cur_level_expert = None
                    else:
                        cur_level_expert = self.user_exists(id=cur_user.expert).username
                    
                    if cur_user.from_user_id is None:
                        cur_game_inviter = cur_game_expert
                    else:
                        cur_game_inviter = self.user_exists(id=cur_user.from_user_id).username
                    
                    with open('images/my_acc_img.jpg', 'rb') as file:
                        my_acc_photo = file.read()
                    msg = self.bot.send_photo(chat_id=message.chat.id,
                                        photo=my_acc_photo,
                                        caption='👑 Мой аккаунт 👑\n\n' 

                                            f'<b>Логин:</b> {cur_user.username}\n'
                                            f'<b>ID:</b> {cur_user.id}\n'
                                            f'<b>Номер телефона:</b> {cur_user.phone}\n\n'

                                            f'Твой пригласитель в игру: <b>@{cur_game_inviter}</b>\n'.replace('@None', '---')+
                                            f'Твой пригласитель на текущем уровне: <b>@{cur_level_expert}</b>\n\n'.replace('@None', '---')+

                                            f'Отправлено подарков на сумму: <b>{cur_user.send_gift_sum}</b>\n'
                                            f'Получено подарков на сумму: <b>{cur_user.get_gift_sum}</b>\n\n' 

                                            f'Всего в команде: {command_players_cnt} игроков\n' 
                                            f'Лично приглашённых: {cur_user.refs_cnt} игроков\n' 
                                            f'Игроков на 1 уровне: {levels_player_cnt[1]}\n' 
                                            f'Игроков на 2 уровне: {levels_player_cnt[2]}\n' 
                                            f'Игроков на 3 уровне: {levels_player_cnt[3]}\n'
                                            f'Игроков на 4 уровне: {levels_player_cnt[4]}\n\n'
                                            
                                            'Пройдено уровней:\n' 
                                            f'1 уровень: {cur_user.levels[1]}\n' 
                                            f'2 уровень: {cur_user.levels[2]}\n'
                                            f'3 уровень: {cur_user.levels[3]}\n' 
                                            f'4 уровень: {cur_user.levels[4]}\n',
                                            parse_mode='HTML',
                                            reply_markup=keyboard.my_account())
                    self.bot.register_next_step_handler(msg, my_account)
                elif not cur_user.texted_to_leader:
                    lider = self.user_exists(id=self.user_exists(id=cur_user.leader).leader)
                    if cur_user.game == 1 or cur_user.game == 2:
                        # GAME-1 or GAME-2
                        self.bot.send_message(chat_id=message.chat.id,
                                            text=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                            'не верит больше никто»\n\n'
                                            'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                            'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                            'конечно - много-много подарков😻🎁\n\n'
                                            f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}\n',
                                            reply_markup=keyboard.text_to_leader(lider.id))
                    elif cur_user.game == 3:
                        # START
                        lider = self.user_exists(id=self.user_exists(id=cur_user.leader).leader)
                        with open('images/main_menu_img.jpg', 'rb') as file:
                            main_menu_photo = file.read()
                        self.bot.send_photo(chat_id=message.chat.id,
                                            photo=main_menu_photo,
                                            caption=f'Поздравляю, ты - в команде👊 🔥\n\n«Верь в себя, даже если '
                                            'не верит больше никто»\n\n'
                                            'Тебе предстоит очень насыщенный путь, будь сфокусирован и настойчив, '
                                            'тогда наша игра подарит тебе множество эмоций, полезных знакомств, и, '
                                            'конечно - много-много подарков😻🎁\n\n'
                                            f'P.S. Обязательно свяжись со своим Экспертом!😉 - @{lider.username}',
                                            reply_markup=keyboard.menu(self, message.chat.id))
                else:
                    self.bot.send_message(chat_id=message.chat.id,
                                            text='Неизвестная команда!',
                                            reply_markup=keyboard.menu(self, message.chat.id))
                

        self.bot.infinity_polling()

# -------------------------------------------------------------------------------------------------


def main():
    bot = Bot()
    threading.Thread(target=logger.main).start()
    threading.Thread(target=bot.start).start()
    threading.Thread(target=functions.check_structure_loop, args=(bot, )).start()


if __name__ == '__main__':
    main()

