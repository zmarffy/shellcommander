#! /usr/bin/env python3

import asyncio
import os
import sys
import shlex
from colorama import Fore, Style


class ProcessError(Exception):
    def __init__(self, run_output):
        self.run_output = run_output
        super().__init__(
            f"Command \"{run_output.cmd}\" returned a non-zero exit code ({run_output.returncode})")


class RunOutput():
    def __init__(self, cmd, returncode, stdout, stderr):
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "Command \"{}\" with exit code {}".format(self.cmd, self.returncode)


async def _read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line:
            callback(line)
        else:
            break


async def _stream_subprocess(cmd, params={}, stdin=None, quiet=False, print_command=False, safe=True, label_stderr=False, shell=os.environ["SHELL"], check_returncode=True) -> RunOutput:
    if safe:
        params = {param: shlex.quote(value) for param, value in params.items()}
    if label_stderr:
        label = f"{Fore.RED}ERR:{Style.RESET_ALL}"
    else:
        label = ""
    stdin_is_string = isinstance(stdin, str)
    original_cmd = cmd.format(**params)
    platform_settings = {"executable": shell}
    if print_command:
        print(
            f"Running command {Style.BRIGHT}{Fore.GREEN}{original_cmd}{Style.RESET_ALL}")

    if stdin_is_string:
        # Using StringIO would be preferred here, but something converted with that does not have the fileno method :(
        # An alternative to the following is cmd += " <<< " + shlex.quote(stdin)
        cmd = "printf " + shlex.quote(stdin) + " | " + original_cmd
        stdin = None
    p = await asyncio.create_subprocess_shell(cmd, stdin=stdin, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, **platform_settings)
    out = []
    err = []

    def tee(line, sink, pipe, label=""):
        line = line.decode('utf-8').rstrip()
        sink.append(line)
        if not quiet:
            print(label, line, file=pipe)

    await asyncio.wait([
        _read_stream(p.stdout, lambda l: tee(l, out, sys.stdout)),
        _read_stream(p.stderr, lambda l: tee(l, err, sys.stderr, label=label))
    ])

    run_output = RunOutput(original_cmd, await p.wait(), "\n".join(out), "\n".join(err))

    if check_returncode and run_output.returncode != 0:
        raise ProcessError(run_output)

    return run_output


def run(cmd, params={}, stdin=None, quiet=False, print_command=False, label_stderr=False, check_returncode=True) -> RunOutput:
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            _stream_subprocess(cmd, params=params, stdin=stdin, quiet=quiet,
                            print_command=print_command, label_stderr=label_stderr, check_returncode=check_returncode)
        )

        return result
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    # Takes one argument, just the command to run
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    args = parser.parse_args()
    out = run(args.command, quiet=False, label_stderr=False,
              print_command=True, check_returncode=False)
    print(out)
