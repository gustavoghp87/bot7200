import sqlite3
from sqlite3 import Error
import time
from datetime import datetime

datetimenow = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
print(datetimenow)

def connectDb():
    try:
        connection = sqlite3.connect('database.db')
        print("Connection established")
        cursor = connection.cursor()

        # cursor.execute('CREATE TABLE IF NOT EXISTS lastTime (id integer PRIMARY KEY, timestamp int, date text, date2 date);')
        # try:
        #     cursor.execute(f"INSERT INTO lastTime(timestamp, date, date2) VALUES ({int(time.time())}, '25/04/2021', '{datetimenow}');")
        #     connection.commit()
        # except AssertionError as error:
        #     print("ERROR", error)

        cursor.execute("SELECT * FROM lastTime;")
        query = cursor.fetchall()
        print(query)
        for row in query:
            print("Row:")
            print(row)
        
        cursor.execute("SELECT * FROM lastTime WHERE id=2;")
        data = cursor.fetchone()
        print("\n\n", data, "..............", str(int((time.time() - data[1])/60)) + " minutes", data[2], data[3])
    except AssertionError as error:
        print(error)
    finally:
        connection.close()
        print("Closed connection\n\n")

def connectInMemoryDb():
    connection = sqlite3.connect(':memory:')
    print("In-Memory database connected")
    connection.close()
    print("Closed connection 2")

connectDb()
connectInMemoryDb()
