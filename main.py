import os

try:
    import curses
    from curses import wrapper
    from mysql.connector import connect
except ImportError:
    print(
        "Please install the necessary libraries to use this app\n",
        f"Open your terminal and type\n\n\tcd {os.path.dirname(os.path.abspath(__file__))}",
        "\tpip install -r requirements.txt\n",
        "and hit enter to install all the essential libraries.\n",
        "Use a monospace font for best experience.",
        sep="\n",
    )
    quit()

from curses.ascii import ESC
from time import sleep

from table import gen_table
from startup import startup, get_config
from db import DatabaseManager

Q = (ord("q"), ord("Q"))
W = (ord("w"), ord("W"))
S = (ord("s"), ord("S"))
DOWN = curses.KEY_DOWN
UP = curses.KEY_UP
ENTER = 10


class App:
    def __init__(self, stdscr) -> None:
        self.config = get_config()
        self.db = DatabaseManager(
            connect(
                host="localhost",
                user=self.config[0],
                password=self.config[1],
                charset="utf8",
            )
        )

        self.scr = stdscr
        self.scr.clear()
        self.clear(stdscr)

        MAX_H, MAX_W = stdscr.getmaxyx()
        mid = lambda str: MAX_W // 2 - len(str) // 2
        stdscr.addstr(0, mid(s := " LIBRARY MANAGEMENT SYSTEM "), s, curses.A_BOLD)

        self.main_win = curses.newwin(MAX_H - 5, MAX_W - 2, 4, 1)
        self.main_win.box()

        self.path = ["HOME"]
        self.path_win = curses.newwin(3, MAX_W - 2, 1, 1)
        self.update_path()

        self.HOME_OPTIONS = [
            "Search ...",
            "Borrow book",
            "Return book",
            "Overdue (n)",
            "Books ...",
            "Students ...",
            "Edit settings",
        ]

        self.run()

    # Clear and redraw a window
    def clear(self, win):
        win.erase()
        win.box()

    # Refresh all windows
    def refresh(self):
        self.scr.refresh()
        self.path_win.refresh()
        self.main_win.refresh()

    # Edit path
    def update_path(self):
        self.clear(self.path_win)
        self.path_win.addstr(1, 2, self.path[0], curses.A_BOLD)
        remaining_path = "".join(f" > {p}" for p in self.path[1:])

        self.path_win.addstr(1, 6, remaining_path)
        self.refresh()

    def add_to_path(self, submenu: str):
        if submenu.split()[-1] == "...":
            submenu = " ".join(submenu.split()[:-1])

        self.path.append(submenu)
        self.update_path()

    def step_back_path(self):
        self.path.pop()
        self.update_path()

    # Menu function
    def menu(self, options: list):
        # Selector postiion
        cy = 0
        # Highlight function
        hl = lambda row: curses.A_REVERSE if cy == row else 0

        while True:
            self.main_win.erase()
            self.main_win.box()

            self.main_win.addstr(cy + 1, 1, ">")

            for i, option in enumerate(options):
                self.main_win.addstr(i + 1, 3, option, hl(i))

            self.scr.move(cy + 5, 4)

            self.refresh()

            key = self.scr.getch()

            if (key == UP or key in W) and cy > 0:
                cy -= 1
            elif (key == DOWN or key in S) and cy < len(options) - 1:
                cy += 1

            # QUIT
            elif key in Q or key == ESC:
                self.clear(self.main_win)
                return -1

            # SUBMIT
            elif key == ENTER:
                self.clear(self.main_win)
                self.refresh()
                return cy

    # TODO: remove
    def nothing(self):
        self.menu([])
        self.step_back_path()

    # FUNCTIONS FOR HOME MENU OPTIONS

    def option_search(self):
        OPTIONS = ["Books", "Students ...", "Transactions ..."]
        while True:
            choice = self.menu(OPTIONS)

            if choice == -1:
                self.step_back_path()
                return

            self.add_to_path(OPTIONS[choice])

            choice_actions = [
                self.option_search_0,
                self.option_search_1,
                self.option_search_2,
            ]
            choice_actions[choice]()

    def option_borrow(self):
        self.nothing()

    def option_return(self):
        self.nothing()

    def option_overdue(self):
        self.nothing()

    def option_books(self):
        OPTIONS = ["New book", "All books", "Remove book", "Update book"]
        while True:
            choice = self.menu(OPTIONS)

            if choice == -1:
                self.step_back_path()
                return

            self.add_to_path(OPTIONS[choice])

            choice_actions = [
                self.option_books_0,
                self.option_books_1,
                self.option_books_2,
                self.option_books_3,
            ]
            choice_actions[choice]()

    def option_students(self):
        OPTIONS = ["New student", "All students", "Remove student", "Update student"]
        while True:
            choice = self.menu(OPTIONS)

            if choice == -1:
                self.step_back_path()
                return

            self.add_to_path(OPTIONS[choice])

            choice_actions = [
                self.option_students_0,
                self.option_students_1,
                self.option_students_2,
                self.option_students_3,
            ]
            choice_actions[choice]()

    def option_edit_settings(self):
        self.nothing()

    # FUNCTIONS FOR SUBMENUS

    # Submenus for search option

    def option_search_0(self):
        self.nothing()

    def option_search_1(self):
        OPTIONS = ["By name/addmission number", "By class"]
        while True:
            choice = self.menu(OPTIONS)

            if choice == -1:
                self.step_back_path()
                return

            self.add_to_path(OPTIONS[choice])

            choice_actions = [self.option_search_10, self.option_search_11]
            choice_actions[choice]()

    # Sub-submenus for search student

    def option_search_10(self):
        self.nothing()

    def option_search_11(self):
        self.nothing()

    def option_search_2(self):
        OPTIONS = [
            "Full history",
            "By borrow date",
            "By return date",
            "By student",
            "By book",
        ]
        while True:
            choice = self.menu(OPTIONS)

            if choice == -1:
                self.step_back_path()
                return

            self.add_to_path(OPTIONS[choice])

            choice_actions = [
                self.option_search_20,
                self.option_search_21,
                self.option_search_22,
                self.option_search_23,
                self.option_search_24,
            ]
            choice_actions[choice]()

    # Sub-submenus for search transactions

    def option_search_20(self):
        self.nothing()

    def option_search_21(self):
        self.nothing()

    def option_search_22(self):
        self.nothing()

    def option_search_23(self):
        self.nothing()

    def option_search_24(self):
        self.nothing()

    # Submenus for books option

    def option_books_0(self):
        self.nothing()

    # All books
    def option_books_1(self):
        data = self.db.book_all()
        if not data:
            self.main_win.addstr(1, 2, "Database Empty!", curses.A_BOLD)
            self.refresh()
            self.scr.getch()
            self.step_back_path()
            return

        page = 1
        cy = 0
        while True:
            self.main_win.clear()

            MAX_H, MAX_W = self.main_win.getmaxyx()

            table = gen_table(data, ["ID", "Name", "Author", "Genres"], MAX_W, MAX_H)
            for n, row in enumerate(table):
                self.main_win.addstr(n, 0, row, curses.A_REVERSE if n == cy * 2 + 1 else 0)
                self.scr.move(cy * 2 + 5, 3)

            self.refresh()
            key = self.scr.getch()

            if key == ESC:
                break
            elif key == UP and cy > 0:
                cy -= 1
            elif key == DOWN and cy < len(data):
                cy += 1

        self.step_back_path()

    def option_books_2(self):
        self.nothing()

    def option_books_3(self):
        self.nothing()

    # Submenus for students option

    def option_students_0(self):
        self.nothing()

    def option_students_1(self):
        self.nothing()

    def option_students_2(self):
        self.nothing()

    def option_students_3(self):
        self.nothing()

    def run(self):
        while True:
            choice = self.menu(self.HOME_OPTIONS)

            # Quit from program
            if choice == -1:
                self.main_win.addstr(5, 5, "QUITTING...", curses.A_BOLD)
                self.refresh()
                sleep(2)

                return

            self.add_to_path(self.HOME_OPTIONS[choice])

            choice_actions = [
                self.option_search,
                self.option_borrow,
                self.option_return,
                self.option_overdue,
                self.option_books,
                self.option_students,
                self.option_edit_settings,
            ]

            choice_actions[choice]()


if __name__ == "__main__":
    startup()

    @wrapper
    def main(stdscr):
        App(stdscr)
