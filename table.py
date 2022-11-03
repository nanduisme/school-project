from random import choice, randint


def gen_table(table: list, attrs: list, char_lim=100):
    CARDINALITY = len(table)

    # Rotates the table
    columns = list(zip(*table[::-1]))

    # Calculates the max lengths each column has values for
    max_lengths = {
        attrs[n]: max(map(lambda x: len(str(x)), col[:] + (attrs[n],)))
        for n, col in enumerate(columns)
    }

    ROOF_STR = ""
    SEP_STR = ""
    FLOOR_STR = ""

    attr_lengths = []
    for attr in max_lengths:
        attr_lengths.append(min(max_lengths[attr], char_lim))
        ROOF_STR += f"┬{'─' * (attr_lengths[-1] + 2)}"
        SEP_STR += f"┼{'─' * (attr_lengths[-1] + 2)}"
        FLOOR_STR += f"┴{'─' * (attr_lengths[-1] + 2)}"

    ROOF_STR = f"╭{ROOF_STR[1:]}╮"
    SEP_STR = f"├{SEP_STR[1:]}┤"
    FLOOR_STR = f"╰{FLOOR_STR[1:]}╯"

    body = [ROOF_STR]

    for rcount, row in enumerate([attrs, *table]):
        rowstr = ""
        for ccount, col in enumerate(row):
            col = str(col)
            if len(col) > char_lim:
                col = f"{col[:char_lim - 1]}…"
            rowstr += f"│ {col}{' ' * (attr_lengths[ccount] - len(col))} "
        body.append(f"{rowstr}│")
        body.append(SEP_STR if rcount < CARDINALITY else FLOOR_STR)

    return body


sample_table = [
    (
        randint(1000, 9999),
        "Nandagopal Menon",
        randint(1, 12),
        choice(["A", "B", "C", "D"]),
    )
    for _ in range(10)
]
