import os
from time import sleep

from mysql.connector import connect
from rich.console import Console
from rich.prompt import Prompt

from db import DatabaseManager
from startup import get_config, startup


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
            self.console.print("[green b u]LIBRARY MANAGEMENT SYSTEM[/]\n\n")
            self.console.print(f"{self.get_path_str()}\n\n")

            for n, option in enumerate(options, 1):
                self.console.print(f"[magenta u]{n}[/]. {option}")

            choice = Prompt.ask(
                f"\n\n[red b]{err}[/]\n[cyan b]Enter a choice [1-{len(options)}]"
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
                self.console.print("[green b]Closing app...")
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


if __name__ == "__main__":
    startup()
    App()
