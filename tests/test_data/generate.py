import random
import string


def randomString(start: str = "", length: int = 10) -> str:
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return start+''.join(random.choice(letters) for i in range(length-len(start)))


if False:  # Make false to remove running
    with open("window.tsv", "w") as f:
        f.write("lem\tpos\ttok\n")
        for lines in range(200):
            f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                rand1=randomString(start="lem_", length=10),
                rand2=randomString(start="pos_", length=10),
                rand3=randomString(start="tok_", length=10)
            ))

if True:
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
