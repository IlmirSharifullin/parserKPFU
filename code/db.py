import sqlite3

con = sqlite3.connect('users.db')
cur = con.cursor()


def get_users() -> list:
    queue = 'SELECT * FROM USERS'
    res: list = cur.execute(queue).fetchall()
    return res


def add_user(tg_id, snils):
    queue = f'INSERT INTO users(tg_id, last_snils) VALUES({tg_id}, "{snils}")'
    cur.execute(queue)
    con.commit()


def change_last_snils(tg_id, snils):
    queue = f'UPDATE users SET last_snils="{snils}" WHERE tg_id={tg_id}'
    cur.execute(queue)
    con.commit()


def get_user(tg_id):
    queue = f'SELECT * FROM users WHERE tg_id={tg_id}'
    res = cur.execute(queue).fetchone()
    return res