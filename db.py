from datetime import datetime


class DatabaseManager:
    def __init__(self, connection):
        self.con = connection
        self.cur = connection.cursor()

        self.books = {
            "new": self.book_new,
            "remove": self.book_remove,
            "update": self.book_update,
            "all": self.book_all,
        }

        self.execute("CREATE DATABASE IF NOT EXISTS LIBDB")
        self.execute("USE LIBDB")
        self.execute(
            """CREATE TABLE IF NOT EXISTS BOOKS (
                ID INT(5) PRIMARY KEY AUTO_INCREMENT, 
                NAME VARCHAR(255) NOT NULL,
                AUTHOR VARCHAR(255) NOT NULL,
                GENRE VARCHAR(255),
                TIMESTAMP TIMESTAMP NOT NULL
            )"""
        )
        self.execute(
            """CREATE TABLE IF NOT EXISTS STUDENTS (
                ADDM_NO INT(5) PRIMARY KEY,
                NAME VARCHAR(30) NOT NULL,
                CLASS INT(2) NOT NULL, 
                DIVISION VARCHAR(1) NOT NULL
            )"""
        )
        self.execute(
            """CREATE TABLE IF NOT EXISTS TRANSACTIONS (
                ID INT(5) PRIMARY KEY AUTO_INCREMENT,
                DATE_BORROWED DATE,
                DATE_RETURNED DATE,
                ADDM_NO INT(5) NOT NULL,
                BOOK_ID INT(5) NOT NULL
            )"""
        )

    def execute(self, query):
        self.cur.execute(query)

    def commit(self):
        self.con.commit()

    def book_new(self, name, author, genres):
        timestamp = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        self.execute(
            f"""INSERT INTO BOOKS(NAME, AUTHOR, GENRE, TIMESTAMP) VALUES (
                '{name}', '{author}', '{genres}', '{timestamp}'
            )"""
        )

        self.commit()

        self.execute(f"SELECT ID, NAME FROM BOOKS WHERE TIMESTAMP = '{timestamp}'")
        return self.cur.fetchall()[0]

    def book_all(self):
        self.execute("SELECT * FROM BOOKS")
        return self.cur.fetchall()

    def book_remove(self, id):  # sourcery skip: class-extract-method
        self.execute(f"DELETE FROM BOOKS WHERE ID = {id}")
        self.commit()

        return self.cur.rowcount or -1

    def book_update(self, id, name, author, genres):
        timestamp = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        self.execute(
            f"""UPDATE BOOKS SET 
            NAME='{name}', AUTHOR='{author}', GENRE='{genres}', TIMESTAMP='{timestamp}'
            WHERE ID={id}
            """
        )

        self.commit()

    def student_new(self, addm_no, name, class_, division):
        self.execute(
            f"""INSERT INTO STUDENTS VALUES (
                {addm_no}, '{name}', {class_}, '{division}'   
            )"""
        )

        self.commit()

    def student_all(self):
        self.execute("SELECT * FROM STUDENTS")
        return self.cur.fetchall()

    def student_remove(self, addm_no):
        self.execute(f"DELETE FROM STUDENTS WHERE ADDM_NO = {addm_no}")
        self.commit()

        return self.cur.rowcount or -1

    def student_update(self, addm_no_old, addm_no_new, name, class_, division):
        self.execute(
            f"""UPDATE STUDENTS SET 
            ADDM_NO={addm_no_new}, NAME='{name}', CLASS={class_}, DIVISION='{division}'
            WHERE ADDM_NO={addm_no_old}
            """
        )
        self.commit()

    def search_books(self, query):
        if query[0] == "#":
            self.execute(
                f"select ID, NAME, AUTHOR, GENRE from books where ID={query[1:]}"
            )
            return self.cur.fetchall()
        else:
            self.execute(
                f"select ID, NAME, AUTHOR, GENRE from books where NAME LIKE '%{query}%'"
            )
            dataset = list(self.cur.fetchall())
            self.execute(
                f"select ID, NAME, AUTHOR, GENRE from books where AUTHOR LIKE '%{query}%'"
            )
            dataset.extend(iter(self.cur.fetchall()))
            self.execute(
                f"select ID, NAME, AUTHOR, GENRE from books where GENRE LIKE '%{query}%'"
            )
            dataset.extend(iter(self.cur.fetchall()))
            return set(dataset)

    def search_students_name_adm(self, query):
        if query[0] == "#":
            self.execute(
                f"select ADDM_NO, NAME, CLASS, DIVISION from STUDENTS where ADDM_NO={query[1:]}"
            )
            return self.cur.fetchall()
        else:
            self.execute(
                f"select ADDM_NO, NAME, CLASS, DIVISION from STUDENTS where NAME LIKE '%{query}%'"
            )
            dataset = list(self.cur.fetchall())
            return set(dataset)

    def search_students_class_div(self, query):
        ...

    def overdue(self):
        self.execute("SELECT * FROM TRANSACTIONS WHERE DATE_RETURNED IS NULL")
        return ret if ((ret := self.cur.fetchall())) else 0


if __name__ == "__main__":
    from mysql.connector import connect

    db = DatabaseManager(
        connect(host="localhost", user="root", passwd="root", charset="utf8")
    )

    db.book_new("Newbook", "me", "Nice")
