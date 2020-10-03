# `shellcommander`

`shellcommander` is a POC that you literally can't run subprocesses in Python and both capture their output **and** print it normally.

## What

The code is based on [this StackOverflow answer](https://stackoverflow.com/a/59041913/6131504). The code looks good in some spots and weird in others (how about that piping a `printf`'d string lol) and it handles non-interactive processes well... usually. Interactive ones though? Definitely not so much.

## See what I mean

| Command | Result |
| --- | --- |
| `./shellcommander.py 'bash'` | No prompt but works |
| `./shellcommander.py 'bash -i'` | Prompt only appears after a command is run. You also can't see commands you're typing in |
| `./shellcommander.py 'python3'` | `>>>` appears after you run a command (lolwut) |
| `./shellcommander.py 'nano'` | Nothing displays on the screen; can't use Ctrl key |
| `./shellcommander.py 'python3 test.py'` | `stderr` prints first |

## Give up

Yeah. It seems it can't be done. Prove me wrong.
