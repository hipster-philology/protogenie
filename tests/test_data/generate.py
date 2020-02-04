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

if False:
    with open("disambiguation.tsv", "w") as f:
        for lines in range(150):
            f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                rand1=randomString(start="lem_", length=10)+str(random.randint(0, 10)),
                rand2=randomString(start="pos_", length=10)+str(random.randint(0, 10)),
                rand3=randomString(start="tok_", length=10)+str(random.randint(0, 10))
            ))

if False:
    at_least_one_zero = False
    at_least_one_one = False
    with open("replacement.tsv", "w") as f:
        for lines in range(140):
            if lines % 7 == 0:
                if not at_least_one_one:
                    rndint = 1
                    at_least_one_one = True
                elif at_least_one_zero:
                    rndint = 0
                    at_least_one_zero = True
                else:
                    rndint = random.randint(0, 10)
                f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                    rand1=rndint,
                    rand2=rndint,  # Keeping it in POS to keep track of the original value in tests
                    rand3=rndint
                ))
            else:
                f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                    rand1=randomString(start="lem_", length=10),
                    rand2=randomString(start="pos_", length=10),
                    rand3=randomString(start="tok_", length=10)
                ))

if True:
    at_least_one_zero = False
    at_least_one_one = False
    with open("skip.tsv", "w") as f:
        for lines in range(200):
            if (lines + 1) % 10 == 0:
                f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                    rand1="removed_by_pos",
                    rand2="PUNfrt",
                    rand3="lala"
                ))
            elif (lines + 1) % 5 == 0:
                f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                    rand1=".",
                    rand2="removed_by_token",
                    rand3="."
                ))
            else:
                f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                    rand1=randomString(start="lem_", length=10),
                    rand2=randomString(start="pos_", length=10),
                    rand3=randomString(start="tok_", length=10)
                ))

            if (lines + 1) % 20 == 0:
                f.write("\n")
