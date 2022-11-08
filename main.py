import os
from time import sleep

from mysql.connector import connect
from rich.console import Console
from rich.prompt import Prompt
from rich.theme import Theme

from db import DatabaseManager
from startup import get_config, startup


class App:
    def __init__(self) -> None:
        self.THEME = Theme(
            {
                "header": "green b u",
                "choice": "cyan b",
                "error": "red b",
                "openquit": "green b",
                "option": "magenta",
                "input": "yellow",
            }
        )

        self.console = Console(theme=self.THEME)
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
        self.console.print("[header]LIBRARY MANAGEMENT SYSTEM[/]\n\n")
        self.console.print(f"{self.get_path_str()}\n\n")

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
                self.console.print(f"[option][u]{n}[/]. {option}")

            choice = Prompt.ask(
                f"\n\n[error]{err}[/]\n[choice]Enter a choice [1-{len(options)}][/]"
            )

            if choice not in [str(x) for x in range(1, len(options) + 1)]:
                err = "Please enter a valid choice"
                continue

            return int(choice)

    def run(self):
        OPTIONS = [
            "Books ...",
            "Students ...",
            "Search ...",
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
                self.console.print("[openquit]Closing app...[/]")
                sleep(1)
                break

            self.path.append(OPTIONS[choice - 1].replace(" ...", ""))

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

                name = Prompt.ask("[input]Enter name of the book[/]")
                author = Prompt.ask("[input]Enter name of the author[/]")
                genre = Prompt.ask("[input]Enter book genres (seperated by space)[/]")

                print("\n\n")

                id, name = self.db.book_new(name, author, genre)
                self.console.print(
                    f"[green b]Your book [magenta]{name}[/] has been added to the database with the BookID of [magenta]{id}[/].",
                    "[openquit]Press enter to proceed..."
                )

                input()

                self.path.pop()
                continue


if __name__ == "__main__":
    startup()
    App()
