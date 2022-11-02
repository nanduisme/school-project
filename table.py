sample_table = [[i, chr(ord("a") + i - 1) * i, i / 2, i * 2] for i in range(1, 20)]
attrs = ["ID", "Name", "Float", "FLOATTWICE"]
CARDINALITY = len(sample_table)
DEGREE = len(attrs)

columns = list(zip(*sample_table[::-1]))
maxl = [
    (attrs[n], max(map(lambda x: len(str(x)), col[:]))) for n, col in enumerate(columns)
]

roofstr = ""
sepstr = ""
floorstr = ""

attr_lengths = []
for attr, l in maxl:
    attr_lengths.append(max(len(attr), l))
    roofstr += f"┬{'─' * (attr_lengths[-1] + 2)}"
    sepstr += f"┼{'─' * (attr_lengths[-1] + 2)}"
    floorstr += f"┴{'─' * (attr_lengths[-1] + 2)}"

roofstr = f"╭{roofstr[1:]}╮\n"
sepstr = f"├{sepstr[1:]}┤\n"
floorstr = f"╰{floorstr[1:]}╯\n"

for rcount, row in enumerate([attrs, *sample_table]):
    for n, col in enumerate(row):
        col = str(col)
        roofstr += f"│ {col}{' ' * (attr_lengths[n] - len(col))} "
    roofstr += "│\n"
    roofstr += sepstr if rcount < CARDINALITY else floorstr

print(roofstr)
