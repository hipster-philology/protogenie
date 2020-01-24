import random
import string


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


if False:  # Make false to remove running
    with open("window.tsv", "w") as f:
        f.write("lem\tpos\ttok\n")
        for lines in range(200):
            f.write("{rand1}\t{rand2}\t{rand3}\n".format(
                rand1=randomString(10),
                rand2=randomString(10),
                rand3=randomString(10)
            ))
