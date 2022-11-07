import pickle
from time import sleep

from rich.console import Console
from rich.prompt import Prompt, IntPrompt, FloatPrompt

console = Console()


def get_input_if_currupt(value, type_, prompt, prompt_type):
    if isinstance(value, type_):
        return value
    console.print(
        "Existing data is not of the right format, please enter it again.",
        style="red bold",
    )
    return prompt_type.ask(prompt)


USERNAME_PROMPT = "[blue bold]MySQL user name[/]"
PASSWORD_PROMPT = "[blue bold]MySQL password[/]"
MAX_BOOKS_PROMPT = "[blue bold]Number of books that can be borrowed at a time[/]"
MAX_DAYS_PROMPT = "[blue bold]Number of days to keep book (without fine)[/]"
FINE_PER_DAY_PROMPT = "[blue bold]Fine per day after the due date[/]"


def startup():
    # Check if file exists else creates
    try:
        f = open(".config", "rb+")
    except FileNotFoundError:
        f = open(".config", "wb+")

    # Check if data exists else gathers data and creates file
    try:
        data = pickle.load(f)
    except EOFError:
        username = Prompt.ask(USERNAME_PROMPT, default="root")
        password = Prompt.ask(PASSWORD_PROMPT, password=True)
        max_books = IntPrompt.ask(MAX_BOOKS_PROMPT)
        max_days = IntPrompt.ask(MAX_DAYS_PROMPT)
        fine_per_day = FloatPrompt.ask(FINE_PER_DAY_PROMPT)

        pickle.dump([username, password, max_books, max_days, fine_per_day], f)
        console.print("Opening program...", style="green")
        sleep(1)

        return

    # Checks if file data is valid else gets new values and dumps to file
    username = get_input_if_currupt(data[0], str, USERNAME_PROMPT, Prompt)
    password = get_input_if_currupt(data[1], PASSWORD_PROMPT, str)
    max_books = get_input_if_currupt(data[2], MAX_BOOKS_PROMPT, int)
    max_days = get_input_if_currupt(data[3], MAX_DAYS_PROMPT, int)
    fine_per_day = get_input_if_currupt(data[4], FINE_PER_DAY_PROMPT, int)

    f.close()
    f = open(".config", "wb+")

    pickle.dump([username, password, max_books, max_days, fine_per_day], f)

    return data


def get_config():
    with open(".config", "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    startup()
