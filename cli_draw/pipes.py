import argparse
import random
from cli_draw import Turn, Direction, draw_curses


def gen_random_turn():
    while True:
        yield random.choice((Turn.L, Turn.R, Turn.F))


def main():
    parser = argparse.ArgumentParser(
        description="Draw a path with a sequence of turns.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--x-step",
        "-x",
        type=int,
        default=2,
        help="The number of columns a single x-axis step takes.",
    )
    parser.add_argument(
        "--y-step",
        "-y",
        type=int,
        default=1,
        help="The number of lines a single y-axis step takes.",
    )
    parser.add_argument(
        "--tick-length",
        "-t",
        type=int,
        default=3,
        help="For --curses-mode only: length of one drawing tick, in tenths of a second.",
    )
    parser.add_argument(
        "--show-cursor",
        "-s",
        action="store_true",
        help="For --curses-mode only: show the cursor as the path is drawn.",
    )

    args = parser.parse_args()
    draw_curses(
        random.choice(list(Direction)),
        gen_random_turn(),
        args.x_step,
        args.y_step,
        args.tick_length,
        args.show_cursor,
    )


if __name__ == "__main__":
    main()
