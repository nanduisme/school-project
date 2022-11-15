from datetime import datetime, timedelta
from time import sleep
import pickle
import os

try:
    from mysql.connector import connect
    from rich.console import Console
    from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
    from rich.table import Table
    from rich import box

    from db import DatabaseManager
    from startup import (
        get_config,
        startup,
        FINE_PROMPT,
        MBKS_PROMPT,
        MDAYS_PROMPT,
        PWD_PROMPT,
        USER_PROMPT,
    )
except ImportError:
    print("Please install required libraries for this app.")
    path = os.path.dirname(os.path.realpath(__file__))
    print(
        "Please open your terminal and type the following commands:\n",
        f"\tcd '{path}'",
        f"\tpython -m pip install -r requirements.txt\n",
        "and re-run the file.",
        sep="\n",
    )
    input("Hit enter to quit...")
    quit()

PROMPT = "yellow"
ERROR = "red b"
SUCESS = "green b"
HEADER = "green b u"
CHOICE = "cyan b"
OPTION = "#326fa8"
HL = "magenta"


class App:
    def __init__(self) -> None:
        self.console = Console()
        self.path = ["Home"]

        self.print = self.console.print

        self.config = get_config()
        self.db = DatabaseManager(
            connect(
                host="localhost",
                user=self.config.username,
                password=self.config.password,
                charset="utf8",
            )
        )

        self.run()

    def clear(self):
        os.system("cls")

    def header(self):
        self.print(f"[{HEADER}]LIBRARY MANAGEMENT SYSTEM[/]\n\n")
        self.print(f"{self.get_path_str()}\n\n")

    def set_screen(self):
        self.clear()
        self.header()

    def proceed(self):
        self.print(f"[{SUCESS}]Press enter to proceed...")
        input()

    def end(self):
        self.proceed()
        self.path.pop()

    def get_path_str(self):
        s = "[blue][b]Home[/]"
        for p in self.path[1:]:
            s += f" > {p}"
        s += "[/]"
        return s

    def transaction_table(self, dataset):
        table = Table(
            "Borrow ID",
            "Student Name",
            "Book Name",
            "Borrow date",
            "Return date",
            "Fine",
            title="Transaction history",
            box=box.ROUNDED,
            show_lines=True,
        )

        for n, row in enumerate(dataset[:]):
            name = self.db.search_students_name_adm(f"#{row[3]}")[0][1]
            book = self.db.search_books(f"#{row[4]}")[0][1]
            current = datetime.now().date() or row[3]
            days = (current - row[1]).days
            fine = days * self.config.fine if days > self.config.max_days else 0
            dataset[n] = [row[0], name, book, row[1], row[2], fine]

        return table

    def menu(self, options):
        err = ""
        while True:
            self.set_screen()

            for n, option in enumerate(options, 1):
                self.print(f"[{OPTION}][u]{n}[/]. {option}")

            choice = Prompt.ask(
                f"\n\n[{ERROR}]{err}[/]\n[{CHOICE}]Enter a choice [1-{len(options)}][/]",
                default="b",
                show_default=False,
            )

            if choice in "qQ":
                self.clear()
                self.print(f"[{SUCESS}]Closing app...[/]")
                sleep(1)
                self.clear()
                quit()

            elif choice in "bB":
                return 0

            if choice not in [str(x) for x in range(1, len(options) + 1)]:
                err = "Please enter a valid choice"
                continue

            choice = int(choice)

            self.path.append(options[choice - 1].replace("...", ""))
            return choice

    def run(self):
        while True:
            OPTIONS = [
                "Books...",
                "Students...",
                "Search...",
                "Borrow book",
                "Return book",
                f"Overdue ({self.db.overdue_n()})",
                "Edit settings",
                "Info and help",
            ]

            choice = self.menu(OPTIONS)

            if choice == 1:
                self.books()
            elif choice == 2:
                self.students()
            elif choice == 3:
                self.search()
            elif choice == 4:
                self.borrow()
            elif choice == 5:
                self.return_book()
            elif choice == 6:
                self.overdue()
            elif choice == 7:
                self.edit_settings()
            elif choice == 8:
                self.info()
            elif choice == 0:
                break

        self.clear()
        self.print(f"[{SUCESS}]Closing app...[/]")
        sleep(1)
        self.clear()

    def info(self):
        self.set_screen()

        self.print(
            "Run [green u]./db.py[/] to populate the database with sample data.",
            "Run only once to avoid duplicate records.",
            "",
            f"Leave choices empty or type '[{HL}]b[/]' to go back.",
            f"Enter '[{HL}]q[/]' to quit the program at any point.",
            "",
            sep="\n",
            style="blue b"
        )

        self.end()

    def books(self):
        OPTIONS = ["New Book", "Remove Book", "Update Book", "All Books"]
        while True:
            choice = self.menu(OPTIONS)

            if choice == 0:
                self.path.pop()
                break

            if choice == 1:
                self.set_screen()

                name = Prompt.ask(f"[{PROMPT}]Enter name of the book[/]")
                author = Prompt.ask(f"[{PROMPT}]Enter name of the author[/]")
                genre = Prompt.ask(
                    f"[{PROMPT}]Enter book genres (seperated by space)[/]"
                )

                print("\n")

                table = Table(
                    "Name", "Author", "Genre", box=box.ROUNDED, show_lines=True
                )
                table.add_row(name, author, genre, style="green")
                self.print(table)

                confirm = Confirm.ask(
                    f"[{PROMPT}]Do you want to add the above record to the database?"
                )

                print("\n")

                if confirm:
                    book_id, name = self.db.book_new(name, author, genre)
                    self.print(
                        f"[{SUCESS}]Your book [{HL}]{name}[/] has been added to the database with the BookID of [{HL}]{book_id}[/]."
                    )
                else:
                    self.print(f"[{ERROR}]Entry cancelled.")

                self.end()

            elif choice == 2:
                self.set_screen()

                book_id = IntPrompt.ask(f"[{PROMPT}]Enter ID of book to remove")

                print("\n")

                output = self.db.book_remove(book_id)

                if output == -1:
                    self.print(
                        f"[{ERROR}]Book with ID [{HL}]{book_id}[/] does not exist on the database"
                    )
                else:
                    self.print(
                        f"[{SUCESS}]Book with ID [{HL}]{book_id}[/] has been deleted"
                    )

                self.end()

            elif choice == 3:
                self.set_screen()

                book_id = IntPrompt.ask(f"[{PROMPT}]Enter ID of book to edit")

                print("\n")

                rec = self.db.search_books(f"#{book_id}")
                if not rec:
                    self.print(f"[{ERROR}]No book with ID [{HL}]{book_id}[/].")
                    self.end()
                    continue

                rec = rec[0]

                table = Table(
                    "ID", "Name", "Author", "Genres", box=box.ROUNDED, show_lines=True
                )
                table.add_row(*[str(x) for x in rec], style="blue")

                self.print(table)
                confirm = Confirm.ask(f"[{PROMPT}]Is this the record you want to edit?")

                if not confirm:
                    self.print(f"[{ERROR}]Cancelling...")
                    self.end()
                    continue

                print("\n")

                self.print(
                    f"[{OPTION}]Enter updated values below. Leave empty for no change."
                )
                name = Prompt.ask(f"[{PROMPT}]Enter new book name", default=rec[1])
                author = Prompt.ask(f"[{PROMPT}]Enter new author", default=rec[2])
                genres = Prompt.ask(f"[{PROMPT}]Enter new genres", default=rec[3])

                print("\n")

                table = Table(
                    "ID", "Name", "Author", "Genres", box=box.ROUNDED, show_lines=True
                )
                table.add_row(str(book_id), name, author, genres, style="green")

                self.print(table)
                if confirm := Confirm.ask(f"[{PROMPT}]Update record?"):
                    self.db.book_update(book_id, name, author, genres)
                    self.print(
                        f"[{SUCESS}]Record with ID [{HL}]{book_id}[/] has been updated."
                    )

                else:
                    self.print(f"[{ERROR}]Cancelling...")

                self.end()

            elif choice == 4:
                self.set_screen()

                dataset = self.db.book_all()
                table = Table(
                    "ID",
                    "Name",
                    "Author",
                    "Genres",
                    "Availability",
                    box=box.ROUNDED,
                    show_lines=True,
                )
                for n, rec in enumerate(dataset):
                    availablity = (
                        "Available" if self.db.is_book_available(rec[0]) else "Taken"
                    )
                    dataset[n] = [*rec[:4], availablity]

                for rec in dataset:
                    table.add_row(*[str(x) for x in rec[:5]])

                self.print(table)
                print("\n\n")

                self.end()

    def students(self):
        OPTIONS = ["New Student", "Remove Student", "Update Student", "All Students"]
        while True:
            choice = self.menu(OPTIONS)

            if choice == 0:
                self.path.pop()

            elif choice == 1:
                self.set_screen()

                adm_no = IntPrompt.ask(f"[{PROMPT}]Enter addmission number of student")

                if self.db.search_students_name_adm(f"#{adm_no}"):
                    self.print(
                        f"[{ERROR}]Admission number [{HL}]{adm_no}[/] already exists."
                    )
                    self.end()
                    continue

                name = Prompt.ask(f"[{PROMPT}]Enter name of the student[/]")
                grade = IntPrompt.ask(f"[{PROMPT}]Enter class of student[/]")
                div = Prompt.ask(
                    f"[{PROMPT}]Enter division of student[/]",
                    choices=list("ABCDEF"),
                )

                print("\n")

                table = Table(
                    "Adm. Number", "Name", "Class", box=box.ROUNDED, show_lines=True
                )
                table.add_row(str(adm_no), name, f"{grade} {div}", style="green")
                self.print(table)

                confirm = Confirm.ask(
                    f"[{PROMPT}]Do you want to add the above record to the database?"
                )

                print("\n")

                if confirm:
                    self.db.student_new(adm_no, name, grade, div)
                    self.print(
                        f"[{SUCESS}]Student '[{HL}]{name}[/]' has been added to the database"
                    )
                else:
                    self.print(f"[{ERROR}]Entry cancelled.")

                self.end()

            elif choice == 2:
                self.set_screen()

                adm_no = IntPrompt.ask(
                    f"[{PROMPT}]Enter admission number of student to remove"
                )

                print("\n")

                output = self.db.student_remove(adm_no)

                if output == -1:
                    self.print(
                        f"[{ERROR}]Book with adm. number [{HL}]{adm_no}[/] does not exist on the database"
                    )
                else:
                    self.print(
                        f"[{SUCESS}]Student with adm. number [{HL}]{adm_no}[/] has been deleted"
                    )

                self.end()

            elif choice == 3:
                self.set_screen()

                adm_no_old = IntPrompt.ask(
                    f"[{PROMPT}]Enter adm. number of student to edit"
                )

                print("\n")

                rec = self.db.search_students_name_adm(f"#{adm_no_old}")
                if not rec:
                    self.print(
                        f"[{ERROR}]No student with adm. number [{HL}]{adm_no_old}[/]."
                    )
                    self.end()
                    continue

                rec = rec[0]

                table = Table(
                    "Adm. Number", "Name", "Class", box=box.ROUNDED, show_lines=True
                )
                table.add_row(
                    str(adm_no_old), rec[1], f"{rec[2]} {rec[3]}", style="blue"
                )

                self.print(table)
                confirm = Confirm.ask(f"[{PROMPT}]Is this the record you want to edit?")

                if not confirm:
                    self.print(f"[{ERROR}]Cancelling...")
                    self.end()
                    continue

                print("\n")

                self.print(
                    f"[{OPTION}]Enter updated values below. Leave empty for no change."
                )
                adm_no = IntPrompt.ask(
                    f"[{PROMPT}]Enter new adm. number", default=rec[0]
                )

                if len(self.db.search_students_name_adm(f"#{adm_no}")) - 1:
                    self.print(
                        f"[{ERROR}]Admission number [{HL}]{adm_no}[/] already exists."
                    )
                    self.end()
                    continue

                name = Prompt.ask(f"[{PROMPT}]Enter new student name", default=rec[1])
                grade = IntPrompt.ask(f"[{PROMPT}]Enter new class", default=rec[2])
                div = Prompt.ask(
                    f"[{PROMPT}]Enter new division",
                    default=rec[3],
                    choices=list("ABCDEF"),
                )

                print("\n")

                table = Table(
                    "Adm. Number", "Name", "Class", box=box.ROUNDED, show_lines=True
                )
                table.add_row(str(adm_no), name, f"{grade} {div}", style="green")

                self.print(table)
                if confirm := Confirm.ask(f"[{PROMPT}]Update record?"):
                    self.db.student_update(adm_no_old, adm_no, name, grade, div)
                    self.print(
                        f"[{SUCESS}]Record with adm. number [{HL}]{adm_no_old}[/] has been updated."
                    )

                else:
                    self.print(f"[{ERROR}]Cancelling...")

                self.end()

            elif choice == 4:
                self.set_screen()

                data = self.db.student_all()
                table = Table(
                    "Adm. No",
                    "Name",
                    "Class",
                    title="Students",
                    box=box.ROUNDED,
                    show_lines=True,
                )
                for rec in data:
                    rec = list(rec)
                    rec[2] = f"{rec[2]} {rec[3]}"
                    rec.pop(3)
                    table.add_row(*[str(x) for x in rec[:4]])

                self.print(table)
                print("\n\n")
                self.end()

    def search(self):
        OPTIONS = ["Books", "Students...", "Transactions..."]
        while True:
            choice = self.menu(OPTIONS)

            if choice == 0:
                self.path.pop()

            if choice == 1:
                self.set_screen()

                self.print(
                    f"[blue b]Start your query with [{HL}]#[/] to search by ID.[/]",
                    "[blue b]Simply type a query to search by name, author or genre[/]",
                    "",
                    sep="\n",
                )

                query = Prompt.ask(f"[{PROMPT}]Enter your query[/]")
                dataset = self.db.search_books(query)
                print("\n")
                if not dataset:
                    self.print(f"[{ERROR}]Empty dataset!")
                    self.end()
                    continue

                table = Table(
                    "ID",
                    "Name",
                    "Author",
                    "Genres",
                    "Availability",
                    box=box.ROUNDED,
                    show_lines=True,
                )
                for n, rec in enumerate(dataset):
                    availablity = (
                        "Available" if self.db.is_book_available(rec[0]) else "Taken"
                    )
                    dataset[n] = [*rec[:4], availablity]

                for rec in dataset:
                    table.add_row(*[str(x) for x in rec[:5]])

                self.print(table)
                print("\n")
                self.end()

            elif choice == 2:
                self.search_students()

            elif choice == 3:
                self.search_transactions()

    def search_students(self):
        OPTIONS = ["By adm. number or name", "By class and/or division", "Back"]
        while True:
            choice = self.menu(OPTIONS)

            if choice == 3:
                self.path.pop()
                break

            if choice == 1:
                self.set_screen()

                self.print(
                    f"[blue b]Start your query with [{HL}]#[/] to search by adm. number.[/]",
                    "[blue b]Simply type a query to search by name.[/]",
                    "",
                    sep="\n",
                )

                query = Prompt.ask(f"[{PROMPT}]Enter your query[/]")
                dataset = self.db.search_students_name_adm(query)
                print("\n")
                if not dataset:
                    self.print(f"[{ERROR}]Empty dataset!")
                    self.end()
                    continue

                table = Table(
                    "Adm Number", "Name", "Class", box=box.ROUNDED, show_lines=True
                )

                for rec in dataset:
                    rec = list(rec)
                    rec[2] = f"{rec[2]} {rec[3]}"
                    rec.pop(3)
                    table.add_row(*[str(x) for x in rec[:4]])

                self.print(table)
                self.end()

            elif choice == 2:
                self.set_screen()

                self.print(
                    "Enter grade and division to search.",
                    "Leave grade empty to get all records with given division and vice versa.\n",
                    sep="\n",
                    style="blue b",
                )

                grade = IntPrompt.ask(
                    f"[{PROMPT}]Enter grade", default=0, show_default=False
                )
                div = Prompt.ask(
                    f"[{PROMPT}]Enter division", choices=list("ABCDEF") + ["None"]
                )

                dataset = self.db.search_students_gradediv(grade, div)

                if not dataset:
                    self.print(f"[{ERROR}]Empty dataset!")
                    self.end()
                    continue

                table = Table(
                    "Adm Number", "Name", "Class", box=box.ROUNDED, show_lines=True
                )
                for rec in dataset:
                    rec = list(rec)
                    rec[2] = f"{rec[2]} {rec[3]}"
                    rec.pop(3)
                    table.add_row(*[str(x) for x in rec[:4]])

                self.print(table)
                self.end()

    def search_transactions(self):
        OPTIONS = [
            "Full history",
            "By borrow date",
            "By return date",
            "By book",
            "By student",
        ]

        while True:
            choice = self.menu(OPTIONS)

            if choice == 0:
                self.path.pop()

            elif choice == 1:
                self.set_screen()

                if dataset := self.db.search_t_full():
                    table = self.transaction_table(dataset)

                    for row in dataset:
                        table.add_row(
                            *[str(x) if x is not None else "Not returned" for x in row]
                        )

                    self.print(table)
                    print("\n")

                else:
                    self.print(f"[{ERROR}]Empty dataset.[/]")
                self.end()

            elif choice == 2:
                self.set_screen()

                self.print(
                    f"[blue b]Enter date in [{HL}]YYYY-MM-DD[/] form. Enter 0 for all."
                )

                year = IntPrompt.ask(f"[{PROMPT}]Enter year [{HL}]YYYY")
                month = IntPrompt.ask(f"[{PROMPT}]Enter month [{HL}]MM")
                date = IntPrompt.ask(f"[{PROMPT}]Enter date [{HL}]DD")

                if dataset := self.db.search_t_date_borrowed(year, month, date):
                    table = self.transaction_table(dataset)

                    for row in dataset:
                        table.add_row(
                            *[str(x) if x is not None else "Not returned" for x in row]
                        )

                    self.print(table)
                    print("\n")

                else:
                    self.print(f"[{ERROR}]Empty dataset.[/]")
                self.end()

            elif choice == 3:
                self.set_screen()

                self.print(
                    f"[blue b]Enter date in [{HL}]YYYY-MM-DD[/] form. Enter 0 for all."
                )

                year = IntPrompt.ask(f"[{PROMPT}]Enter year [{HL}]YYYY")
                month = IntPrompt.ask(f"[{PROMPT}]Enter month [{HL}]MM")
                date = IntPrompt.ask(f"[{PROMPT}]Enter date [{HL}]DD")

                if dataset := self.db.search_t_date_returned(year, month, date):
                    table = Table(
                        "Borrow ID",
                        "Student Name",
                        "Book Name",
                        "Borrow date",
                        "Return date",
                        "Fine",
                        title="Transaction history",
                        box=box.ROUNDED,
                        show_lines=True,
                    )
                    for n, row in enumerate(dataset[:]):
                        name = self.db.search_students_name_adm(f"#{row[3]}")[0][1]
                        book = self.db.search_books(f"#{row[4]}")[0][1]
                        current = datetime.now().date() or row[3]
                        days = (current - row[1]).days
                        fine = (
                            days * self.config.fine
                            if days > self.config.max_days
                            else 0
                        )
                        dataset[n] = [row[0], name, book, row[1], row[2], fine]

                    for row in dataset:
                        table.add_row(
                            *[str(x) if x is not None else "Not returned" for x in row]
                        )

                    self.print(table)
                    print("\n")

                else:
                    self.print(f"[{ERROR}]Empty dataset.[/]")
                self.end()

            elif choice == 4:
                self.set_screen()

                book_id = IntPrompt.ask(f"[{PROMPT}]Enter book ID to search by")

                if dataset := self.db.search_t_book(book_id):
                    table = self.transaction_table(dataset)

                    for row in dataset:
                        table.add_row(
                            *[str(x) if x is not None else "Not returned" for x in row]
                        )

                    self.print(table)
                    print("\n")

                else:
                    self.print(f"[{ERROR}]Empty dataset.[/]")

                self.end()
                continue

            elif choice == 5:
                self.set_screen()

                adm_no = IntPrompt.ask(
                    f"[{PROMPT}]Enter student adm. number to search by"
                )

                if dataset := self.db.search_t_student(adm_no):
                    table = self.transaction_table(dataset)

                    for row in dataset:
                        table.add_row(
                            *[str(x) if x is not None else "Not returned" for x in row]
                        )

                    self.print(table)
                    print("\n")

                else:
                    self.print(f"[{ERROR}]Empty dataset.[/]")

                self.end()
                continue

    def borrow(self):
        self.set_screen()

        adm_no = IntPrompt.ask(f"[{PROMPT}]Enter students adm. number")
        student = self.db.search_students_name_adm(f"#{adm_no}")
        if not student:
            self.print(f"[{ERROR}]Student with ID [{HL}]{adm_no}[/] does not exist.")
            self.end()
            return
        student = student[0]
        no_books = self.db.get_no_books_taken_by_student(adm_no)
        if no_books >= self.config.max_books:
            self.print(
                f"[{ERROR}]Student has already taken maximum amount of books ([{HL}]{self.config.max_books}[/]).",
                f"[{ERROR}]Please return a book to take another.",
                "",
                sep="\n",
            )
            self.end()
            return

        book_id = IntPrompt.ask(f"[{PROMPT}]Enter book ID")
        book = self.db.search_books(f"#{book_id}")
        if not book:
            self.print(f"[{ERROR}]Book with ID [{HL}]{book_id}[/] does not exist.")
            self.end()
            return
        book = book[0]
        if not self.db.is_book_available(book_id):
            self.print(f"[{ERROR}]The book [{HL}]{book[1]}[/] is already taken.")
            self.end()
            return

        print("\n")

        confirm = Confirm.ask(
            f"[blue b]Is [{HL}]{student[1]}[/] borrowing [{HL}]{book[1]}[/]?"
        )
        if not confirm:
            self.print(f"[{ERROR}]Cancelling...")
            self.end()
            return
        print("\n")

        self.db.borrow(adm_no, book_id)

        return_date = datetime.now() + timedelta(days=self.config.max_days)

        self.print(
            f"[blue b]Return date for the book is [{HL}]{return_date.date()!s}[/].",
            f"[blue b]After that there will be a fine of [{HL}]{self.config.fine}[/] per day.",
            "",
            sep="\n",
        )

        self.end()

    def return_book(self):
        self.set_screen()

        adm_no = IntPrompt.ask(f"[{PROMPT}]Enter students adm. number")
        student = self.db.search_students_name_adm(f"#{adm_no}")
        if not student:
            self.print(f"[{ERROR}]Student with ID [{HL}]{adm_no}[/] does not exist.")
            self.end()
            return
        student = student[0]

        book_id = IntPrompt.ask(f"[{PROMPT}]Enter book ID")
        book = self.db.search_books(f"#{book_id}")
        if not book:
            self.print(f"[{ERROR}]Book with ID [{HL}]{book_id}[/] does not exist.")
            self.end()
            return
        book = book[0]

        is_valid = self.db.is_valid_return(adm_no, book_id)
        if not is_valid:
            self.print(
                f"[{ERROR}][{HL}]{student[1]}[/] has not borrowed [{HL}]{book[1]}[/]."
            )
            self.end()
            return

        print("\n")

        fine = self.db.get_fine(adm_no, book_id)

        confirm = Confirm.ask(
            f"[blue b]Is [{HL}]{student[1]}[/] returning [{HL}]{book[1]}[/] with fine '{fine}'?"
        )
        if not confirm:
            self.print(f"[{ERROR}]Cancelling...")
            self.end()
            return
        print("\n")

        self.db.return_book(adm_no, book_id)
        self.print(f"[blue b]Return Confirmed\n")

        self.end()

    def overdue(self):
        self.set_screen()

        dataset = self.db.overdue_data()

        if not dataset:
            self.print(f"[{ERROR}]Empty Dataset.\n")
            self.end()
            return

        table = Table(
            "Borrow ID",
            "Student Name",
            "Book Name",
            "Borrow date",
            "Fine",
            title="Transaction history",
            box=box.ROUNDED,
            show_lines=True,
        )

        for n, row in enumerate(dataset[:]):
            name = self.db.search_students_name_adm(f"#{row[3]}")[0][1]
            book = self.db.search_books(f"#{row[4]}")[0][1]
            current = datetime.now().date() or row[3]
            days = (current - row[1]).days
            fine = days * self.config.fine if days > self.config.max_days else 0
            dataset[n] = [row[0], name, book, row[1], fine]

        for row in dataset:
            table.add_row(*[str(x) for x in row])

        self.print(table)
        print("\n")

        self.end()

    def edit_settings(self):
        self.set_screen()

        self.print(
            "[blue b]Enter the setting you want to change. Leave empty for no change.\n"
        )

        username = Prompt.ask(USER_PROMPT, default=self.config.username)
        password = Prompt.ask(PWD_PROMPT, password=True, default=self.config.password)
        max_books = IntPrompt.ask(MBKS_PROMPT, default=self.config.max_books)
        max_days = IntPrompt.ask(MDAYS_PROMPT, default=self.config.max_days)
        fine_per_day = FloatPrompt.ask(FINE_PROMPT, default=self.config.fine)

        with open(".config", "wb") as f:
            pickle.dump([username, password, max_books, max_days, fine_per_day], f)

        self.config = get_config()

        print("\n")
        self.end()


if __name__ == "__main__":
    startup()
    App()
