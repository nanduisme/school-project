from datetime import datetime
from csv import reader

from startup import get_config


class DatabaseManager:
    def __init__(self, connection):
        self.con = connection
        self.cur = connection.cursor()
        self.fetchall = self.cur.fetchall
        self.config = get_config()

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
                ADM_NO INT(5) PRIMARY KEY,
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
                ADM_NO INT(5) NOT NULL,
                BOOK_ID INT(5) NOT NULL
            )"""
        )

    @property
    def rowcount(self):
        return self.cur.rowcount

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
        return self.fetchall()[0]

    def book_all(self):
        self.execute("SELECT * FROM BOOKS")
        return self.fetchall()

    def book_remove(self, id):  
        self.execute(f"DELETE FROM BOOKS WHERE ID = {id}")
        self.commit()

        return self.rowcount or -1

    def book_update(self, id, name, author, genres):
        ts = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        self.execute(
            f"""UPDATE BOOKS SET 
            NAME='{name}', AUTHOR='{author}', GENRE='{genres}', TIMESTAMP='{ts}'
            WHERE ID={id}
            """
        )

        self.commit()

    def is_book_available(self, book_id):
        self.execute(
            f"SELECT COUNT(*) FROM TRANSACTIONS WHERE BOOK_ID={book_id} AND DATE_RETURNED IS NULL"
        )

        return not self.fetchall()[0][0]

    def student_new(self, adm_no, name, grade, div):
        self.execute(
            f"""INSERT INTO STUDENTS VALUES (
                {adm_no}, '{name}', {grade}, '{div}'   
            )"""
        )

        self.commit()

    def student_all(self):
        self.execute("SELECT * FROM STUDENTS")
        return self.fetchall()

    def student_remove(self, adm_no):
        self.execute(f"DELETE FROM STUDENTS WHERE ADM_NO = {adm_no}")
        self.commit()

        return self.rowcount or -1

    def student_update(self, adm_no_old, adm_no_new, name, grade, div):
        self.execute(
            f"""UPDATE STUDENTS SET 
            ADM_NO={adm_no_new}, NAME='{name}', CLASS={grade}, DIVISION='{div}'
            WHERE ADM_NO={adm_no_old}
            """
        )
        self.commit()

    def get_no_books_taken_by_student(self, adm_no):
        self.execute(
            f"SELECT COUNT(*) FROM TRANSACTIONS WHERE ADM_NO={adm_no} AND DATE_RETURNED IS NULL"
        )

        return self.fetchall()[0][0]

    def get_fine(self, adm_no, book_id):
        self.execute(
            f"SELECT * FROM TRANSACTIONS WHERE ADM_NO={adm_no} AND BOOK_ID={book_id} AND DATE_RETURNED IS NULL"
        )

        t = self.fetchall()[0]
        days = (datetime.now().date() - t[1]).days
        return days * self.config.fine if days >= self.config.max_days else 0

    def borrow(self, adm_no, book_id):
        date = datetime.now().date()

        self.execute(
            f"""
            insert into TRANSACTIONS(DATE_BORROWED, ADM_NO, BOOK_ID) VALUES (
                '{date!s}', {adm_no}, {book_id}
            )
            """
        )

        self.commit()

    def return_book(self, adm_no, book_id):
        self.execute(
            f"""
            update TRANSACTIONS SET DATE_RETURNED='{datetime.now().date()!s}'
            WHERE ADM_NO={adm_no} AND BOOK_ID={book_id}
            """
        )

        self.commit()

    def is_valid_return(self, adm_no, book_id):
        self.execute(
            f"""
            SELECT * FROM TRANSACTIONS WHERE
            ADM_NO={adm_no} AND BOOK_ID={book_id} AND DATE_RETURNED IS NULL
            """
        )

        return bool(self.fetchall())

    def search_books(self, query):
        if not query:
            return []

        if query[0] == "#":
            self.execute(
                f"SELECT ID, NAME, AUTHOR, GENRE FROM BOOKS WHERE ID={query[1:] if query != '#' else '0'}"
            )
        else:
            self.execute(
                f"""
                SELECT ID, NAME, AUTHOR, GENRE FROM BOOKS WHERE 
                NAME LIKE '%{query}%'
                OR AUTHOR LIKE '%{query}%'
                OR GENRE LIKE '%{query}%'
                """
            )

        return self.fetchall()

    def search_students_name_adm(self, query):
        if not query:
            return []

        if query[0] == "#":
            self.execute(
                f"SELECT ADM_NO, NAME, CLASS, DIVISION FROM STUDENTS WHERE ADM_NO={query[1:]}"
            )
        else:
            self.execute(
                f"SELECT ADM_NO, NAME, CLASS, DIVISION FROM STUDENTS WHERE NAME LIKE '%{query}%'"
            )

        return self.fetchall()

    def search_students_gradediv(self, grade=None, div=None):
        self.execute(
            f"""SELECT ADM_NO, NAME, CLASS, DIVISION FROM STUDENTS 
            WHERE CLASS LIKE {grade or '%'} OR DIVISION LIKE {div or '_'}
            """
        )

        return self.fetchall()

    def search_t_full(self):
        self.execute(
            "SELECT ID, DATE_BORROWED, DATE_RETURNED, ADM_NO, BOOK_ID FROM TRANSACTIONS"
        )
        return self.fetchall()

    def search_t_date_borrowed(self, year=None, month=None, date=None):
        year = year or "____"
        month = month or "__"
        date = date or "__"

        self.execute(
            f"""
            SELECT ID, DATE_BORROWED, DATE_RETURNED, ADM_NO, BOOK_ID FROM TRANSACTIONS
            WHERE DATE_BORROWED LIKE '{year}-{month}-{date}'
            """
        )

        return self.fetchall()

    def search_t_date_returned(self, year=None, month=None, date=None):
        year = year or "____"
        month = month or "__"
        date = date or "__"

        self.execute(
            f"""
            SELECT ID, DATE_BORROWED, DATE_RETURNED, ADM_NO, BOOK_ID FROM TRANSACTIONS
            WHERE DATE_RETURNED LIKE '{year}-{month}-{date}'
            """
        )

        return self.fetchall()

    def search_t_book(self, book_id):
        self.execute(f"SELECT * FROM TRANSACTIONS WHERE book_id={book_id}")

        return self.fetchall()

    def search_t_student(self, adm_no):
        self.execute(f"SELECT * FROM TRANSACTIONS WHERE adm_no={adm_no}")

        return self.fetchall()

    def overdue_n(self):
        ret = self.overdue_data()
        return len(ret) if ret else 0

    def overdue_data(self):
        self.execute("SELECT * FROM TRANSACTIONS WHERE DATE_RETURNED IS NULL")
        ret = self.fetchall()
        ret = filter(
            lambda x: (datetime.now().date() - x[1]).days >= self.config.max_days,
            ret,
        )

        return list(ret)

    def drop_database(self):
        self.execute("DROP DATABASE LIBDB")
        self.commit()


if __name__ == "__main__":
    from mysql.connector import connect

    config = get_config()

    db = DatabaseManager(
        connect(
            host="localhost", user=config.user, password=config.password, charset="utf8"
        )
    )

    with open("students.csv", "r") as f:
        for e in list(reader(f)):
            db.student_new(*e)

    with open("books.csv", "r") as f:
        for e in list(reader(f)):
            db.book_new(*e)

    db.execute(
        "INSERT INTO TRANSACTIONS(DATE_BORROWED, ADM_NO, BOOK_ID)\
        VALUES('2022-06-01', 7079, 1)"
    )
    db.commit()
