import sqlite3

conn = sqlite3.connect("data.db")
c = conn.cursor()


class Item:
    def __init__(self, itemid):
        self.item_id = itemid

    def get_id(self):
        return self.item_id
    
    def clist(self):
        c.execute(f"SELECT * FROM items WHERE id={self.get_id()}")
        return list(c)[0]

    def get_name(self):
        return self.clist()[1]

    def set_name(self, value):
        c.execute(f"UPDATE items SET name=\"{value}\" WHERE id={self.get_id()}")
        conn.commit()

    def get_price(self):
        return self.clist()[2]

    def set_price(self, value):
        c.execute(f"UPDATE items SET price={value} WHERE id={self.get_id()}")
        conn.commit()

    def get_cat_id(self):
        return self.clist()[3]

    def set_cat_id(self, value):
        c.execute(f"UPDATE items SET cat_id={value} WHERE id={self.get_id()}")
        conn.commit()

    def get_desc(self):
        return self.clist()[4]

    def set_desc(self, value):
        c.execute(f"UPDATE items SET desc=\"{value}\" WHERE id={self.get_id()}")
        conn.commit()

    def is_active(self):
        return self.clist()[5] == 1

    def set_active(self, value):
        c.execute(f"UPDATE items SET active={value} WHERE id={self.get_id()}")
        conn.commit()


class Category:
    def __init__(self, cat_id):
        self.id = cat_id

    def get_id(self):
            return self.id

    def clist(self):
        c.execute(f"SELECT * FROM cats WHERE id={self.get_id()}")
        return list(c)[0]

    def get_name(self):
        return self.clist()[1]

    def set_name(self, value):
        c.execute(f"UPDATE cats SET name=\"{value}\" WHERE id={self.get_id()}")
        conn.commit()

    def delete(self):
        c.execute(f"DELETE FROM cats WHERE id={self.get_id()}")
        conn.commit()



def get_cat_list():
    c.execute(f"SELECT * FROM cats")
    return list(c)
    

def create_cat(cat_name):
    c.execute(f"INSERT INTO cats(name) VALUES(?)", [cat_name])
    conn.commit()