# `cli-draw`: Draw a path with a sequence of turns

`cli-draw` is a tool for drawing a path given a sequence of turns.
It can draw over time in a `curses` window or all at once into 
standard output.

## Installation
`cli-draw` requires Python 3.10 or higher. For personal projects, I
like to use the newest language features; if you want to backport
this to an earlier version of Python, it shouldn't be too hard, but I
will not be doing that.

If you have a virtual environment set up, you can just install it:

```sh
$ git clone git@github.com:angus-lherrou/cli-draw.git
$ cd cli-draw
$ # conda activate venv, source venv/bin/activate, etc
$ pip install .
```

If you want to install the `cli-draw` terminal command for your user:

```sh
$ git clone git@github.com:angus-lherrou/cli-draw.git
$ cd cli-draw
$ python3.10 -m pip install --user .
$ # make sure the install location is in PATH 
$ # (pip should warn you about this)
```

Help for `cli-draw`:
```sh
$ cli-draw --help
usage: cli-draw [-h] [--curses-mode] [--x-step X_STEP]
                [--y-step Y_STEP] [--tick-length TICK_LENGTH]
                [--show-cursor] [--initial-direction {R,D,L,U}]
                TURNS

Draw a path with a sequence of turns.

positional arguments:
  TURNS                 The turns the path should take, given as a
                        sequence of "R" for a right turn, "L" for a
                        left turn, "F" for a forward face (no turn),
                        and "B" for an about-face (180-degree turn)

options:
  -h, --help            show this help message and exit
  --curses-mode, -c
  --x-step X_STEP, -x X_STEP
                        The number of columns a single x-axis step
                        takes. (default: 2)
  --y-step Y_STEP, -y Y_STEP
                        The number of lines a single y-axis step
                        takes. (default: 1)
  --tick-length TICK_LENGTH, -t TICK_LENGTH
                        For --curses-mode only: length of one drawing
                        tick, in tenths of a second. (default: 3)
  --show-cursor, -s     For --curses-mode only: show the cursor as the
                        path is drawn. (default: False)
  --initial-direction {R,D,L,U}, -d {R,D,L,U}
                        The starting direction of travel. (default: R)

```

## `cli-pipes`

This package also installs a script called `cli-pipes`. This will
start up a `curses` window and randomly walk around the screen, similar
to the "pipes" screensaver of yesteryear. Options are the same as for
`cli-draw` except it takes no positional argument, `--curses-mode` is 
implicitly true and can't be deactivated, and `--initial-direction` is 
random and can't be set explicitly.
