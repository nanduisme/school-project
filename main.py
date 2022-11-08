import os
from time import sleep

from mysql.connector import connect
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich import box

from db import DatabaseManager
from startup import get_config, startup

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

        self.config = get_config()
        self.db = DatabaseManager(
            connect(
                host="localhost",
                user=self.config[0],
                password=self.config[1],
                charset="utf8",
            )
        )

        self.run()

    def clear(self):
        os.system("cls")

    def header(self):
        self.console.print(f"[{HEADER}]LIBRARY MANAGEMENT SYSTEM[/]\n\n")
        self.console.print(f"{self.get_path_str()}\n\n")

    def proceed(self):
        self.console.print(F"[{SUCESS}]Press enter to proceed...")
        input()

    def get_path_str(self):
        s = "[blue][b]Home[/]"
        for p in self.path[1:]:
            s += f" > {p}"
        s += "[/]"
        return s

    def menu(self, options):
        err = ""
        while True:
            self.clear()
            self.header()

            for n, option in enumerate(options, 1):
                self.console.print(f"[{OPTION}][u]{n}[/]. {option}")

            choice = Prompt.ask(
                f"\n\n[{ERROR}]{err}[/]\n[{CHOICE}]Enter a choice [1-{len(options)}][/]"
            )

            if choice not in [str(x) for x in range(1, len(options) + 1)]:
                err = "Please enter a valid choice"
                continue

            return int(choice)

    def run(self):
        OPTIONS = [
            "Books...",
            "Students...",
            "Search...",
            "Borrow book",
            "Return book",
            f"Overdue ({self.db.overdue()})",
            "Edit settings",
            "Quit",
        ]
        while True:
            choice = self.menu(OPTIONS)

            if choice == 8:
                self.clear()
                self.console.print(F"[{SUCESS}]Closing app...[/]")
                sleep(1)
                break

            self.path.append(OPTIONS[choice - 1].replace("...", ""))

            if choice == 1:
                self.books()

    def books(self):
        OPTIONS = ["New Book", "Remove Book", "Update Book", "All Books", "Back"]
        while True:
            choice = self.menu(OPTIONS)

            if choice == 5:
                self.path.pop()
                break

            self.path.append(OPTIONS[choice - 1].replace(" ...", ""))

            if choice == 1:
                self.clear()
                self.header()

                name = Prompt.ask(F"[{PROMPT}]Enter name of the book[/]")
                author = Prompt.ask(F"[{PROMPT}]Enter name of the author[/]")
                genre = Prompt.ask(F"[{PROMPT}]Enter book genres (seperated by space)[/]")

                print("\n")

                table = Table("Name", "Author", "Genre", box=box.ROUNDED)
                table.add_row(name, author, genre, style="green")
                self.console.print(table)

                confirm = Confirm.ask(
                    f"[{PROMPT}]Do you want to add the above record to the database?"
                )

                print("\n")

                if confirm:
                    book_id, name = self.db.book_new(name, author, genre)
                    self.console.print(
                        f"[{SUCESS}Your book [{HL}]{name}[/] has been added to the database with the BookID of [{HL}]{book_id}[/]."
                    )
                else:
                    self.console.print(F"[{ERROR}]Entry cancelled.")

                self.proceed()

                self.path.pop()
                continue

            elif choice == 2:
                self.clear()
                self.header()

                book_id = IntPrompt.ask(F"[{PROMPT}]Enter ID of book to remove")

                print("\n")

                output = self.db.book_remove(book_id)

                if output == -1:
                    self.console.print(
                        f"[{ERROR}]Book with ID [{HL}]{book_id}[/] does not exist on the database"
                    )
                else:
                    self.console.print(
                        f"[{SUCESS}]Book with ID [{HL}]{book_id}[/] has been deleted"
                    )

                self.proceed()

                self.path.pop()
                continue

            elif choice == 3:
                self.clear()
                self.header()

                book_id = IntPrompt.ask(F"[{PROMPT}]Enter ID of book to edit")

                print("\n")

                rec = self.db.search_books(f"#{book_id}")
                if not rec:
                    self.console.print(f"[{ERROR}]No book with ID [{HL}]{book_id}[/].")
                    self.proceed()
                    self.path.pop()
                    continue

                rec = rec[0]

                table = Table("ID", "Name", "Author", "Genres", box=box.ROUNDED)
                table.add_row(*[str(x) for x in rec], style="blue")

                self.console.print(table)
                confirm = Confirm.ask(f"[{PROMPT}]Is this the record you want to edit?")

                if not confirm:
                    self.console.print(f"[{ERROR}]Cancelling...")
                    self.proceed()
                    self.path.pop()
                    continue

                print("\n")

                self.console.print(f"[{OPTION}]Enter updated values below. Leave empty for no change.")
                name = Prompt.ask(f"[{PROMPT}]Enter new book name", default=rec[1])
                author = Prompt.ask(f"[{PROMPT}]Enter new author", default=rec[2])
                genres = Prompt.ask(f"[{PROMPT}]Enter new genres", default=rec[3])

                print("\n")

                table = Table("ID", "Name", "Author", "Genres", box=box.ROUNDED)
                table.add_row(str(book_id), name, author, genres, style="green")

                self.console.print(table)
                confirm = Confirm.ask(f"[{PROMPT}]Update record?")

                if not confirm:
                    self.console.print(f"[{ERROR}]Cancelling...")
                else:
                    self.db.book_update(book_id, name, author, genres)
                    self.console.print(f"[{SUCESS}]Record with ID [{HL}]{book_id}[/] has been updated.")

                self.proceed()
                self.path.pop()
                continue

            elif choice == 4:
                self.clear()
                self.header()

                data = self.db.book_all()
                table = Table("ID", "Name", "Author", "Genres", title="Books", box=box.ROUNDED)
                for rec in data:
                    table.add_row(*[str(x) for x in rec[:4]])
                
                self.console.print(table)
                print("\n\n")
                self.proceed()
                self.path.pop()
                continue

if __name__ == "__main__":
    startup()
    App()
