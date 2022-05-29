import sqlite3
from prettytable import PrettyTable
from art import tprint
from database import *
from getpass import getpass

#Initilize connection to data base
db = sqlite3.connect("data.db")
cursor = db.cursor()
#Initilize pretty table formatting
tb = PrettyTable()
tb.field_names = ["Website", "Email", "Username", "Password"]


def main():
    create_database(db, cursor)

    tprint("Password Saver")  # displays logo
    match input("1. Register \n2. Login\nWhat would you like to do: "):
        case "1":
            register()
        case "2":
            login()


def register():
    if not is_registered(cursor):  # check if person is registered
        password = getpass("Create master password: ")  # creates master password
        password_confirmation = getpass("Confirm  master password: ")
        if password == password_confirmation:  # checks matching
            create_master_pwd(db, cursor, password)
            generate_key(db, cursor)  # generate unique key for encryption
            print("\n[+] Your account successfully created\n")
            main()
        else:
            print("[-] Sorry inputed passwords do not match")
    else:
        print("[-] It seems that you have already registered")


def login():
    if check_master_pwd(cursor, getpass("Enter master password: ")):  #checks matching of masterpwd in database
        print("\n[+] Successfully logged\n")
        menu()
    else:
        print("[-] Your master password is incorrect")


def menu():
    while True:
        print("1. Add new record\n2. Search record\n3. Delete record\n4. Exit")
        match input("Choose option: "):
            case "1":
                add_record()
            case "2":
                tb.clear_rows()  #clears prettytable from previous records
                show_record(input("Website name: "))
            case "3":
                delete_record(input("Website name: "))
            case "4":
                exit(0)


def add_record():
    webname = input("- Input name of website: ")
    email = input("- Input email: ")
    username = input("- Input username: ")
    password = getpass("- Input your password: ")
    data = [webname, email, username, password]
    added = add_new(db, cursor, data)
    if not added:
        print("\n[-] Record already exists\n")
    else: 
        print("\n[+] Record was successfully added\n")


def show_record(webname):
    to_show = show_data(cursor, webname)  #searches record in database
    if not to_show:
        print("\n[-] No record found\n")
    else:
        tb.add_row(to_show)  #adds record to prettytable
        print(f"\n{tb}\n")


def delete_record(webname):
    delete(db, cursor, webname)
    print("\n[+] Record was successfully deleted\n")


if __name__ == '__main__':
    main()
