from random import choice, randint


def gen_table(table: list, attrs: list, max_w: int, max_h: int, char_lim=100):
    # Trim table according to length of attrs
    table = [row[: len(attrs)] for row in table]

    CARDINALITY = len(table)
    DEGREE = len(attrs)

    # Rotates the table
    columns = list(zip(*table[::-1]))

    # Calculates the max lengths each column has values for
    max_lengths = {
        attrs[n]: max(map(lambda x: len(str(x)), col[:] + (attrs[n],)))
        for n, col in enumerate(columns)
    }

    # Adjust max lengths to fit the screen
    max_usable_w = max_w - (len(attrs) * 3) - 1
    total_length = sum(max_lengths[a] for a in max_lengths)
    if total_length < max_usable_w:
        foreach, remaining = divmod((max_usable_w - total_length), DEGREE)
        for attr in max_lengths:
            max_lengths[attr] += foreach

        if remaining:
            top_keys = sorted(max_lengths, key=lambda x: max_lengths[x])[:remaining]
            for key in top_keys:
                max_lengths[key] += 1

    # Initialize the strings
    ROOF_STR = ""
    SEP_STR = ""
    FLOOR_STR = ""
    SPACE_STR = ""

    # Making the base strings depending on max_lengths
    attr_lengths = []
    for attr in max_lengths:
        attr_lengths.append(min(max_lengths[attr], char_lim))
        ROOF_STR += f"┬{'─' * (attr_lengths[-1] + 2)}"
        SEP_STR += f"┼{'─' * (attr_lengths[-1] + 2)}"
        FLOOR_STR += f"┴{'─' * (attr_lengths[-1] + 2)}"
        SPACE_STR += f"│{' ' * (attr_lengths[-1] + 2)}"

    ROOF_STR = f"╭{ROOF_STR[1:]}╮"
    SEP_STR = f"├{SEP_STR[1:]}┤"
    FLOOR_STR = f"╰{FLOOR_STR[1:]}╯"
    SPACE_STR = f"│{SPACE_STR[1:]}│"

    body = [ROOF_STR]

    # Populating the body with data
    for rcount, row in enumerate([attrs, *table]):
        rowstr = ""
        for ccount, col in enumerate(row):
            col = str(col)
            if len(col) > char_lim:
                col = f"{col[:char_lim - 1]}…"
            rowstr += f"│ {col}{' ' * (attr_lengths[ccount] - len(col))} "
        body.extend((f"{rowstr}│", SEP_STR if rcount < CARDINALITY else FLOOR_STR))

    height = len(body)
    length_remaining = max_h - height - 1
    if length_remaining > 1:
        body[-1] = SEP_STR
        body.extend(SPACE_STR for _ in range(length_remaining))
        body[-1] = FLOOR_STR

    return body


if __name__ == "__main__":
    sample_table = [
        (
            randint(1000, 9999),
            "Nandagopal Menon",
            randint(1, 12),
            choice(["A", "B", "C", "D"]),
        )
        for _ in range(10)
    ]

    table = gen_table(sample_table, ["roll", "name", "class", "div"], 99, 100)
    for row in table:
        print(row)
