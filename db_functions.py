import psycopg2, json
from contextlib import closing
from config import dbname, user, password, host, table_name


def create_table(table_name):
    with closing(psycopg2.connect(dbname=dbname, user=user, password=password, host=host)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""CREATE TABLE {table_name} (
                    data json NOT NULL
                );""")
            conn.commit()


def delete_table(table_name):
    with closing(psycopg2.connect(dbname=dbname, user=user, password=password, host=host)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""DROP TABLE {table_name};""")
            conn.commit()


def put_to_base(table_name, data):
    with closing(psycopg2.connect(dbname=dbname, user=user, password=password, host=host)) as conn:
        with conn.cursor() as cursor:
            data = json.dumps(data, ensure_ascii=False).replace("'", '"')

            cursor.execute(f"""SELECT * FROM {table_name};""")
            db_data = cursor.fetchall()

            if len(db_data) != 0:
                cursor.execute(f"""UPDATE {table_name} SET data = '{data}';""")
            else:
                cursor.execute(f"""INSERT INTO {table_name} (data)
                    VALUES ('{data}')
                ;""")
            conn.commit()


def get_from_base(table_name):
    try:
        with closing(psycopg2.connect(dbname=dbname, user=user, password=password, host=host)) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""SELECT * FROM {table_name};""")
                data = cursor.fetchall()
        if len(data) == 0:
            return data
        else:
            return data[0][0]
    except:
        return None


def save_all(bot):
    res_dict = {}

    res_dict['REQUISITS_COUNTER'] = bot.REQUISITS_COUNTER

    tmp_dict = {}
    for key in bot.user_faq_messages:
        tmp_dict[key] = bot.user_faq_messages[key]
    res_dict['user_faq_messages'] = tmp_dict

    tmp_dict = {}
    for key in bot.start_expert_text:
        tmp_dict[key] = bot.start_expert_text[key]
    res_dict['start_expert_text'] = tmp_dict

    tmp_list = []
    for user in bot.users:
        tmp_levels = {}
        for key in user.levels:
            tmp_levels[key] = user.levels[key]

        tmp_dict = {}
        tmp_dict["id"] = user.id
        tmp_dict["privacy_accept"] = user.privacy_accept
        tmp_dict["is_eighteen"] = user.is_eighteen
        tmp_dict["username"] = user.username
        tmp_dict["phone"] = user.phone
        tmp_dict["refs_cnt"] = user.refs_cnt
        tmp_dict["from_user_id"] = user.from_user_id
        tmp_dict["cur_level"] = user.cur_level
        tmp_dict["levels"] = tmp_levels
        tmp_dict["ref_link"] = user.ref_link
        tmp_dict["left"] = user.left
        tmp_dict["middle"] = user.middle
        tmp_dict["right"] = user.right
        tmp_dict["leader"] = user.leader
        tmp_dict["expert"] = user.expert
        tmp_dict["expert_confirm"] = user.expert_confirm
        tmp_dict["texted_to_leader"] = user.texted_to_leader
        tmp_dict["send_gift_sum"] = user.send_gift_sum
        tmp_dict["get_gift_sum"] = user.get_gift_sum

        tmp_list.append(tmp_dict)
    res_dict['users'] = tmp_list

    put_to_base(table_name, res_dict)


# delete_table(table_name)
# create_table(table_name)