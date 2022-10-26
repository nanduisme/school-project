import curses
from curses import wrapper

DOWN = curses.KEY_DOWN
Q = (ord("q"), ord("Q"))
UP = curses.KEY_UP
    

@wrapper
def main(stdscr):
    # while True:
        stdscr.clear()
        stdscr.box()
        h, w = stdscr.getmaxyx()
        mid = lambda str: w // 2 - len(str) // 2
        stdscr.addstr(0, mid(s:=" LIBRARY MANAGEMENT SYSTEM "), s, curses.A_BOLD)

        path = "HOME"

        path_win = curses.newwin(3, w - 2, 1, 1)
        path_win.box()
        path_win.addstr(1, 2, path, curses.A_BOLD)

        main_win = curses.newwin(h - 5, w - 2, 4, 1)
        main_win.box()
        

        cy = 0
        hl = lambda row: curses.A_REVERSE if cy == row else 0

        options = [str(x) for x in range(5)]

        while True:
            main_win.erase()
            main_win.addstr(cy, 0, ">")

            for i, option in enumerate(options):
                main_win.addstr(i, 2, option, hl(i))

            main_win.addstr(len(options) + 5, 0, "UP and DOWN to navigate")
            main_win.addstr(len(options) + 6, 0, "Q to quit")
            main_win.addstr(len(options) + 7, 0, "ENTER to submit")

            key = main_win.getch()

            if key == UP and cy > 0:
                cy -= 1
            elif key == DOWN and cy < len(options) - 1:
                cy += 1
            elif key == 10 or key in Q: #Enter
                break

            main_win.refresh()

        # option_picker(stdscr, 0, [str(x) for x in range(5)])

        stdscr.refresh()
        path_win.refresh()
        main_win.refresh()

        stdscr.getch()
