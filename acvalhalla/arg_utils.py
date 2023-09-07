from argparse import ArgumentParser


def read_args():
    parser = ArgumentParser()
    parser.add_argument("-p", "--preset", dest="preset",
                        help="graphics preset", metavar="preset", required=False)
    args = parser.parse_args()
    return args
