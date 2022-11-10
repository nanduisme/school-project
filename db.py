from datetime import datetime
from startup import get_config


class DatabaseManager:
    def __init__(self, connection):
        self.con = connection
        self.cur = connection.cursor()

        self.config = get_config()

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

    def is_book_available(self, book_id):
        self.execute(
            f"select count(*) from transactions where book_id={book_id} and date_returned is null"
        )

        return not self.cur.fetchall()[0][0]

    def student_new(self, addm_no, name, grade, division):
        self.execute(
            f"""INSERT INTO STUDENTS VALUES (
                {addm_no}, '{name}', {grade}, '{division}'   
            )"""
        )

        self.commit()

    def student_all(self):
        self.execute("SELECT * FROM STUDENTS")
        return self.cur.fetchall()

    def student_remove(self, adm_no):
        self.execute(f"DELETE FROM STUDENTS WHERE ADDM_NO = {adm_no}")
        self.commit()

        return self.cur.rowcount or -1

    def student_update(self, addm_no_old, addm_no_new, name, grade, division):
        self.execute(
            f"""UPDATE STUDENTS SET 
            ADDM_NO={addm_no_new}, NAME='{name}', CLASS={grade}, DIVISION='{division}'
            WHERE ADDM_NO={addm_no_old}
            """
        )
        self.commit()

    def get_no_books_taken_by_student(self, adm_no):
        self.execute(
            f"select count(*) from transactions where addm_no={adm_no} and date_returned is null"
        )

        return self.cur.fetchall()[0][0]

    def get_fine(self, adm_no, book_id):
        self.execute(
            f"select * from transactions where addm_no={adm_no} and book_id={book_id} and date_returned is null"
        )

        t = self.cur.fetchall()[0]
        days = (datetime.now().date() - t[1]).days
        return days * self.config.fine_per_day if days >= self.config.max_days else 0

    def borrow(self, adm_no, book_id):
        date = datetime.now().date()

        self.execute(
            f"""
            insert into transactions(DATE_BORROWED, ADDM_NO, BOOK_ID) values (
                '{date!s}', {adm_no}, {book_id}
            )
            """
        )

        self.commit()

    def return_book(self, adm_no, book_id):
        self.execute(
            f"""
            update transactions set date_returned='{datetime.now().date()!s}'
            where addm_no={adm_no} and book_id={book_id}
            """
        )

        self.commit()

    def is_valid_return(self, adm_no, book_id):
        self.execute(
            f"""
            select * from transactions where
            addm_no={adm_no} and book_id={book_id} and date_returned is null
            """
        )

        return bool(self.cur.fetchall())

    def search_books(self, query):
        if not query:
            return []

        if query[0] == "#":
            self.execute(
                f"select ID, NAME, AUTHOR, GENRE from books where ID={query[1:] if query != '#' else '0'}"
            )
        else:
            self.execute(
                f"""
                select ID, NAME, AUTHOR, GENRE from books where 
                NAME LIKE '%{query}%'
                OR AUTHOR LIKE '%{query}%'
                OR GENRE LIKE '%{query}%'
                """
            )

        return self.cur.fetchall()

    def search_students_name_adm(self, query):
        if not query:
            return []

        if query[0] == "#":
            self.execute(
                f"select ADDM_NO, NAME, CLASS, DIVISION from STUDENTS where ADDM_NO={query[1:]}"
            )
        else:
            self.execute(
                f"select ADDM_NO, NAME, CLASS, DIVISION from STUDENTS where NAME LIKE '%{query}%'"
            )

        return self.cur.fetchall()

    def search_students_gradediv(self, grade=None, div=None):
        self.execute(
            f"""select ADDM_NO, NAME, CLASS, DIVISION from STUDENTS 
            where CLASS LIKE {grade or '%'} OR DIVISION LIKE {div or '_'}
            """
        )

        return self.cur.fetchall()

    def search_t_full(self):
        self.execute(
            "select ID, DATE_BORROWED, DATE_RETURNED, ADDM_NO, BOOK_ID FROM TRANSACTIONS"
        )
        return self.cur.fetchall()

    def search_t_date_borrowed(self, year=None, month=None, date=None):
        year = year or "____"
        month = month or "__"
        date = date or "__"

        self.execute(
            f"""
            select ID, DATE_BORROWED, DATE_RETURNED, ADDM_NO, BOOK_ID FROM TRANSACTIONS
            WHERE DATE_BORROWED LIKE '{year}-{month}-{date}'
            """
        )

        return self.cur.fetchall()

    def search_t_date_returned(self, year=None, month=None, date=None):
        year = year or "____"
        month = month or "__"
        date = date or "__"

        self.execute(
            f"""
            select ID, DATE_BORROWED, DATE_RETURNED, ADDM_NO, BOOK_ID FROM TRANSACTIONS
            WHERE DATE_RETURNED LIKE '{year}-{month}-{date}'
            """
        )

        return self.cur.fetchall()

    def search_t_book(self, book_id):
        self.execute(
           f"""
           select * from transactions where book_id={book_id}
           """
        )

        return self.cur.fetchall()

    def search_t_student(self, adm_no):
        self.execute(
            f"""
            select * from transactions where addm_no={adm_no}
            """
        )

        return self.cur.fetchall()

    def overdue_n(self):
        ret = self.overdue_data()
        return len(ret) if ret else 0

    def overdue_data(self):
        self.execute("SELECT * FROM TRANSACTIONS WHERE DATE_RETURNED IS NULL")
        ret = self.cur.fetchall()
        ret = filter(
            lambda x: (datetime.now().date() - x[1]).days >= self.config.max_days,
            ret,
        )

        return list(ret)


if __name__ == "__main__":
    from mysql.connector import connect

    db = DatabaseManager(
        connect(host="localhost", user="root", passwd="root", charset="utf8")
    )

    db.book_new("Newbook", "me", "Nice")
