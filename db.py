import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

# Table for Users Info
cursor.execute(f"CREATE TABLE IF NOT EXISTS users (id INT, refs INT DEFAULT 0)")
conn.commit()


def createKanallar():
    cursor.execute("CREATE TABLE kanallar (username VARCHAR(64), subs INT)")
    conn.commit()    

def drop_table(name):
    cursor.execute(f"DROP TABLE kanallar")
    conn.commit()

def add_channel(username, subs):
    cursor.execute("INSERT INTO kanallar (username, subs) VALUES (?,?)", (username, subs))
    conn.commit()

def get_users() -> list:
    """db dagi users tablesidagi id larni list ko'rinishida qaytaradi"""
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    users = [i[0] for i in users]
    return users

def get_channels():
    cursor.execute("SELECT * FROM kanallar")
    kanallar = cursor.fetchall()
    kanallar = [i for i in kanallar]
    return kanallar

def add_user(id):
    "db ga user qo'shish uchun method"
    cursor.execute("INSERT INTO users (id) VALUES (?)", (id,))
    conn.commit()

def set_ref(id):
    "user ning referalini bittaga oshiradi"
    cursor.execute("UPDATE users SET refs = refs + 1 WHERE id = ?", (id,))
    conn.commit()

def get_ref(id):
    "user ning referallar sonini qaytaradi"
    cursor.execute("SELECT refs FROM users WHERE id = ?", (id,))
    return cursor.fetchall()[0][0]

def get_statics():
    """statistikani chiqaradi eng kop referalga ega bo'lgan 10 tassini"""
    cursor.execute("SELECT id, refs FROM users ORDER BY refs DESC LIMIT 10")
    all = cursor.fetchall()
    all = [i for i in all]
    return all