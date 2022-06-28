from argparse import *
import sys


def parse_args(parser, subparsers):
    # divide argv by commands
    split_argv = [[]]
    for c in sys.argv[1:]:
        if c in subparsers.choices:
            split_argv.append([c])
        else:
            split_argv[-1].append(c)
    # initialize namespace
    args = Namespace()
    for c in subparsers.choices:
        setattr(args, c, None)
    # parse each command
    parser.parse_args(split_argv[0], namespace=args)  # Without command
    for argv in split_argv[1:]:  # Commands
        n = Namespace()
        setattr(args, argv[0], n)
        parser.parse_args(argv, namespace=n)
    # return args
    return args
