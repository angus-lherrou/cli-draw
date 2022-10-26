import enum
import functools
import os

import argparse

import curses
import sys
from typing import Callable, cast, Optional, Iterable
from cli_draw.charsets import *

CHARSET = SingleBox()


class Turn(enum.Enum):
    R = enum.auto()
    L = enum.auto()
    F = enum.auto()
    B = enum.auto()


class Direction(enum.Enum):
    R = (1, 0)
    D = (0, 1)
    L = (-1, 0)
    U = (0, -1)

    def succ(self: "Direction") -> "Direction":
        return Direction(matmul(SUCC, self.value))

    def pred(self: "Direction") -> "Direction":
        return Direction(matmul(PRED, self.value))

    def opp(self: "Direction") -> "Direction":
        return Direction(matmul(OPP, self.value))

    def turn(self: "Direction", turn: Turn) -> "Direction":
        match turn:
            case Turn.R:
                return self.succ()
            case Turn.L:
                return self.pred()
            case Turn.F:
                return self
            case Turn.B:
                return self.opp()

    @property
    def x(self):
        return self.value[0]

    @property
    def y(self):
        return self.value[1]


SUCC = ((0, -1), (1, 0))
PRED = ((0, 1), (-1, 0))
OPP = ((-1, 0), (0, -1))

DIR2VAL = {
    "R": 0b1000,
    "D": 0b0001,
    "L": 0b0010,
    "U": 0b0100,
}


def str2val(coords: str) -> int:
    val = 0
    for coord in coords:
        val |= DIR2VAL[coord]
    return val


def overlay(first: str, second: str) -> str:
    if first not in CHARSET._chars or second not in CHARSET._chars:
        return CHARSET.val2char(15)
    return CHARSET.val2char(CHARSET.char2val(first) | CHARSET.char2val(second))


def matmul(
    mat: tuple[tuple[int, int], tuple[int, int]], vec: tuple[int, int]
) -> tuple[int, int]:
    x = mat[0][0] * vec[0] + mat[0][1] * vec[1]
    y = mat[1][0] * vec[0] + mat[1][1] * vec[1]

    return x, y


def walk(
    initial_dir: Direction, turns: list[Turn]
) -> tuple[tuple[int, int], tuple[int, int]]:
    (x, y) = (min_x, min_y) = (max_x, max_y) = (0, 0)
    this_dir = initial_dir

    def step():
        nonlocal x, y, min_x, min_y, max_x, max_y
        x += this_dir.x
        y += this_dir.y
        min_x, _, max_x = sorted([min_x, max_x, x])
        min_y, _, max_y = sorted([min_y, max_y, y])

    step()
    for turn in turns:
        this_dir = this_dir.turn(turn)
        step()

    return (min_x, min_y), (max_x, max_y)


def _go(
    put_fn: Callable[[int, int, str], None],
    get_fn: Callable[[int, int], str],
    x: int,
    y: int,
    direction: Direction,
    x_step: int,
    y_step: int,
    x_mod: Optional[int] = None,
    y_mod: Optional[int] = None,
) -> tuple[int, int]:
    char_to_put = overlay(get_fn(y, x), CHARSET.val2char(str2val(direction.name)))
    put_fn(y, x, char_to_put)

    x += direction.x
    y += direction.y

    if x_mod is not None:
        x = x % x_mod
    if y_mod is not None:
        y = y % y_mod

    if direction in {Direction.R, Direction.L}:
        step = x_step
    else:
        step = y_step

    for _ in range(step - 1):
        char_to_put = overlay(
            get_fn(y, x),
            CHARSET.val2char(str2val(direction.name + direction.opp().name)),
        )
        put_fn(y, x, char_to_put)

        x += direction.x
        y += direction.y

        if x_mod is not None:
            x = x % x_mod
        if y_mod is not None:
            y = y % y_mod

    char_to_put = overlay(get_fn(y, x), CHARSET.val2char(str2val(direction.opp().name)))
    put_fn(y, x, char_to_put)

    return x, y


def _grid_get_fn(grid, y: int, x: int) -> str:
    return grid[y][x]


def _grid_put_fn(grid, y: int, x: int, char: str) -> None:
    grid[y][x] = char


def go(
    grid: list[list[str]],
    x: int,
    y: int,
    direction: Direction,
    x_step: int,
    y_step: int,
) -> tuple[int, int]:
    put_fn = cast(
        Callable[[int, int, str], None], functools.partial(_grid_put_fn, grid)
    )
    get_fn = cast(Callable[[int, int], str], functools.partial(_grid_get_fn, grid))
    return _go(put_fn, get_fn, x, y, direction, x_step, y_step)


def _curses_put_fn(
    window: curses.window, y_mod: int, x_mod: int, y: int, x: int, char: str
) -> None:
    if y == y_mod - 1 and x == x_mod - 1:
        window.insstr(y, x, char)
    else:
        window.addstr(y, x, char)
    window.move(y, x)


def _curses_get_fn(window: curses.window, y: int, x: int) -> str:
    i = window.inch(y, x)
    window.move(y, x)
    if i > ord("\U0010FFFF"):
        raise RuntimeError("path went out of bounds")
    c = chr(i)
    return c


def go_curses(
    window: curses.window,
    x: int,
    y: int,
    direction: Direction,
    x_step: int,
    y_step: int,
    x_mod: int,
    y_mod: int,
):
    put_fn = cast(
        Callable[[int, int, str], None],
        functools.partial(_curses_put_fn, window, y_mod, x_mod),
    )
    get_fn = cast(Callable[[int, int], str], functools.partial(_curses_get_fn, window))
    return _go(put_fn, get_fn, x, y, direction, x_step, y_step, x_mod, y_mod)


def draw(initial_dir: Direction, turns: list[Turn], x_step, y_step):
    (min_x, min_y), (max_x, max_y) = walk(initial_dir, turns)

    grid = [
        [" " for _x in range((max_x - min_x) * x_step + 1)]
        for _y in range((max_y - min_y) * y_step + 1)
    ]

    this_dir = initial_dir
    x = (-min_x) * x_step
    y = (-min_y) * y_step
    for turn in turns:
        x, y = go(grid, x, y, this_dir, x_step, y_step)
        this_dir = this_dir.turn(turn)
    go(grid, x, y, this_dir, x_step, y_step)

    print("\n".join(["".join(row) for row in grid]))


def draw_curses(
    initial_dir: Direction,
    turns: Iterable[Turn],
    x_step: int,
    y_step: int,
    tick_length: int,
    show_cursor: bool = False,
):
    # Curses setup
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    if not show_cursor:
        old_cursor = curses.curs_set(0)

    try:
        parent_lines, parent_columns = stdscr.getmaxyx()
        parent_lines -= (parent_lines + 2) % y_step
        parent_columns -= (parent_columns + 2) % x_step
        stdscr.resize(parent_lines, parent_columns)

        stdscr.border()
        stdscr.addstr(parent_lines - 1, 1, "Press [q] to exit.")
        stdscr.refresh()

        subwin = stdscr.subwin(parent_lines - 2, parent_columns - 2, 1, 1)

        lines, columns = subwin.getmaxyx()

        this_dir = initial_dir
        x = columns // 2
        y = lines // 2

        subwin.nodelay(True)
        curses.halfdelay(tick_length)

        for turn in turns:
            if subwin.getch() == 113:
                return
            x, y = go_curses(subwin, x, y, this_dir, x_step, y_step, columns, lines)
            this_dir = this_dir.turn(turn)
            subwin.refresh()
        if subwin.getch() == 113:
            return
        go_curses(subwin, x, y, this_dir, x_step, y_step, columns, lines)
        subwin.refresh()
        while True:
            if subwin.getch() != -1:
                break
    except RuntimeError:
        # TODO: deal with this differently
        raise
    finally:
        # Curses teardown
        if not show_cursor:
            curses.curs_set(old_cursor)
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


def main():
    parser = argparse.ArgumentParser(
        description="Draw a path with a sequence of turns.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--curses-mode", "-c", action="store_true")
    parser.add_argument(
        "TURNS",
        type=str,
        default="-",
        help=(
            "The turns the path should take, given as a sequence "
            'of "R" for a right turn, "L" for a left turn, '
            '"F" for a forward face (no turn), and "B" for an '
            "about-face (180-degree turn)"
        ),
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

    parser.add_argument(
        "--initial-direction",
        "-d",
        type=str,
        default="R",
        choices=Direction._member_names_,
        help="The starting direction of travel.",
    )

    args = parser.parse_args()

    initial_direction = Direction[args.initial_direction]

    if args.curses_mode:
        draw_curses(
            initial_direction,
            [Turn[turn] for turn in args.TURNS],
            args.x_step,
            args.y_step,
            args.tick_length,
            args.show_cursor,
        )
    else:
        draw(
            initial_direction,
            [Turn[turn] for turn in args.TURNS],
            args.x_step,
            args.y_step,
        )


if __name__ == "__main__":
    main()
