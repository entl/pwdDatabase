from hashlib import sha256
from cryptography.fernet import Fernet
import sqlite3


def add_new(db, cursor, data):
    """Adds new record to the database

    Args:
        data (list): a list of data that has to be added

    Returns:
        list: returnes True in case of success
    """
    isExist = cursor.execute(f"SELECT * FROM data WHERE webname = '{data[0]}' ").fetchall()
    if isExist == []:
        data = encryption(cursor, data)
        cursor.execute("INSERT INTO data VALUES (?,?,?,?)", data)
        db.commit()
        return True
    return False


def show_data(cursor, webname):
    """function which finds row with asked webname

    Args:
        webname (str): name of the website for which user wants to get data

    Returns:
        list: decrypted asked data
    """
    selected = cursor.execute(f"SELECT * FROM data WHERE webname = '{webname}' ").fetchall()
    if selected != []:
        decrypted = decryption(cursor, *selected)
        return decrypted
    return False


def delete(db, cursor, webname):
        cursor.execute(f"DELETE FROM data WHERE webname = '{webname}' ")
        db.commit()
        return True


def is_registered(cursor):
    if cursor.execute(f"SELECT * FROM masterpwd").fetchall() == []:
        return False
    return True


def generate_key(db, cursor):
    """
    generates and saves into data base unique key which is used for encryption

    """
    key = Fernet.generate_key()

    cursor.execute("INSERT INTO key (key) VALUES (?)", (key,))
    db.commit()


def create_master_pwd(db, cursor,pwd):
    """creates and hashes master password which is used to access all the data in database

    Args:
        pwd (str): password which user would like to use
    """
    pwd_hashed = str(sha256(pwd.encode("utf8")).digest())
    
    cursor.execute("INSERT INTO masterpwd (password) VALUES (?)", (pwd_hashed,))
    db.commit()


def check_master_pwd(cursor, pwd):
    pwd_hashed = str(sha256(pwd.encode("utf8")).digest())
    stored_pwd = cursor.execute(f"SELECT * FROM masterpwd").fetchone()
    if pwd_hashed == stored_pwd[0]:
        return True
    return False


def encryption(cursor, data):
    """encryptes received data

    Args:
        data (list): _description_

    Returns:
        tuple: returns encrypted data in tuple (in case of insert data tuple is required by sqlite)
    """
    encrypt_data = []
    
    key = cursor.execute(f"SELECT * FROM key").fetchall()[0]
    crypter = Fernet(*key)

    for key, value in enumerate(data):
        if key == 0: 
            encrypt_data.append(value)
            continue
        encrypted = crypter.encrypt(value.encode('utf8'))
        encrypt_data.append(encrypted)   
    
    return tuple(encrypt_data)


def decryption(cursor, data):
    """decrypts passed data

    Args:
        data (tuple): tuple which was get from database

    Returns:
        list: decrypted list
    """
    decrypted_data = []

    key = cursor.execute(f"SELECT * FROM key").fetchall()[0]
    crypter = Fernet(*key)

    for key, value in enumerate(data):
        if key == 0: 
            decrypted_data.append(value)
            continue
        decrypted = crypter.decrypt(value)
        decrypted_data.append(decrypted.decode('utf8'))

    return decrypted_data

        
def create_database(db, cursor):
    # db = sqlite3.connect("data.db")
    # cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS data (
        webname TEXT,
        email TEXT,
        username TEXT,
        password TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS masterpwd (
        password TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS key (
        key TEXT
    )""")

    db.commit()
    # db.close()


def delete_table(db, cursor, table_name):
    cursor.execute(f"DROP TABLE {table_name}")
    db.commit()


if __name__ == '__main__':
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    create_database(db, cursor)