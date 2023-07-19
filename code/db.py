import sqlite3


class Database:
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def get_users(self) -> list:
        queue = 'SELECT * FROM USERS'
        res: list = self.cursor.execute(queue).fetchall()
        return res

    def get_user(self, uid):
        queue = f'SELECT * FROM users WHERE tg_id={uid}'
        res = self.cursor.execute(queue).fetchone()
        return res

    def add_user(self, uid, snils):
        queue = f'INSERT INTO users(tg_id, last_snils) VALUES({uid}, "{snils}")'
        self.cursor.execute(queue)
        self.connection.commit()

    def change_last_snils(self, uid, snils):
        queue = f'UPDATE users SET last_snils="{snils}" WHERE tg_id={uid}'
        self.cursor.execute(queue)
        self.connection.commit()
