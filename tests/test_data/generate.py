import random
import string


def randomString(start: str = "", length: int = 10) -> str:
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return start+''.join(random.choice(letters) for i in range(length-len(start)))

# I am using different numbers of sequence size to be sure tests are not being right on another corpus

if False:  # Make false to remove running
    with open("window.tsv", "w") as f:
        f.write("lem\tpos\ttok\n")
        for lines in range(200):
            f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                rand1=randomString(start="lem_", length=10),
                rand2=randomString(start="pos_", length=10),
                rand3=randomString(start="tok_", length=10)
            ))

if False:
    with open("sentence.tsv", "w") as f:
        f.write("lem\tpos\ttok\n")
        for lines in range(190):
            if (lines + 1) % 19 == 0:
                f.write(".\tPONfor\t.\n")
            else:
                f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                    rand1=randomString(start="lem_", length=10),
                    rand2=randomString(start="pos_", length=10),
                    rand3=randomString(start="tok_", length=10)
                ))

if False:
    with open("empty_line.tsv", "w") as f:
        f.write("lem\tpos\ttok\n")
        for lines in range(180):
            f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                rand1=randomString(start="lem_", length=10),
                rand2=randomString(start="pos_", length=10),
                rand3=randomString(start="tok_", length=10)
            ))
            if (lines + 1) % 18 == 0:
                f.write("\n")

if False:
    with open("file.tsv", "w") as f:
        f.write("lem\tpos\ttok\n")
        for lines in range(170):
            f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                rand1=randomString(start="lem_", length=10),
                rand2=randomString(start="pos_", length=10),
                rand3=randomString(start="tok_", length=10)
            ))

if False:
    with open("implicit.tsv", "w") as f:
        for lines in range(160):
            f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                rand1=randomString(start="lem_", length=10),
                rand2=randomString(start="pos_", length=10),
                rand3=randomString(start="tok_", length=10)
            ))

if True:
    with open("disambiguation.tsv", "w") as f:
        for lines in range(150):
            f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                rand1=randomString(start="lem_", length=10)+str(random.randint(0, 10)),
                rand2=randomString(start="pos_", length=10)+str(random.randint(0, 10)),
                rand3=randomString(start="tok_", length=10)+str(random.randint(0, 10))
            ))
