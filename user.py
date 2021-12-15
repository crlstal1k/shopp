import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()


class User:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_id(self):
        return self.user_id

    def clist(self):
        c.execute(f"SELECT * FROM users WHERE user_id={self.get_id()}")
        return list(c)

    def get_balance(self):
        return self.clist()[1]

    def is_admin(self):
        return self.clist()[2] == 1

    def set_admin(self, value):
        c.execute(f"UPDATE users SET is_admin={value} WHERE user_id={self.get_id()}")
        conn.commit()

    def is_support(self):
        return self.clist()[4] == 1

    def set_support(self, value):
        c.execute(f"UPDATE users SET is_support={value} WHERE user_id={self.get_id()}")
        conn.commit()

    def get_register_date(self):
        return self.clist()[6]

    def notif_on(self):
        return self.clist()[5] == 1

    def enable_notif(self):
        c.execute(f"UPDATE users SET notification=1 WHERE user_id={self.get_id()}")

    def disable_notif(self):
        c.execute(f"UPDATE users SET notification=0 WHERE user_id={self.get_id()}")

    def get_orders(self):
        c.execute(f"SELECT * FROM orders WHERE user_id=\"{self.get_id()}\"")
        return list(c)

    def set_balance(self, value):
        c.execute(f"UPDATE users SET balance={value} WHERE user_id={self.get_id()}")


def does_user_exist(user_id):
    c.execute(f"SELECT * FROM users WHERE user_id=\"{user_id}\"")
    return len(list(c)) != 0


def get_notif_list():
    c.execute(f"SELECT * FROM users WHERE notification=1")
    return list(c)


def get_user_login(message):
    return message.from_user.username


def get_user_list():
    c.execute("SELECT * FROM users")
    return list(c)

