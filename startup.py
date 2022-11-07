import pickle


def get_input(prompt, type_):
    while True:
        try:
            return type_(input(prompt))
        except ValueError:
            print("The data you have entered is not of the right format!")


def get_input_if_currupt(value, prompt, type_):
    if isinstance(value, type_):
        return value
    print("Existing data is not of the right format, please enter it again.")
    return get_input(prompt)


USERNAME_PROMPT = "MySQL user name: "
PASSWORD_PROMPT = "MySQL password: "
MAX_BOOKS_PROMPT = "Number of books that can be borrowed at a time: "
MAX_DAYS_PROMPT = "Number of days to keep book (without fine): "
FINE_PER_DAY_PROMPT = "Fine per day after the due date: "


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
        username = get_input(USERNAME_PROMPT, str)
        password = get_input(PASSWORD_PROMPT, str)
        max_books = get_input(MAX_BOOKS_PROMPT, int)
        max_days = get_input(MAX_DAYS_PROMPT, int)
        fine_per_day = get_input(FINE_PER_DAY_PROMPT, int)

        pickle.dump([username, password, max_books, max_days, fine_per_day], f)
        print("Opening program...")

        return

    # Checks if file data is valid else gets new values and dumps to file
    username = get_input_if_currupt(data[0], USERNAME_PROMPT, str)
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
