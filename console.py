from app.admintools import console
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--command", "-c", nargs="*", help="Execute a command")
args = parser.parse_args()

if args.command:
    try:
        fullcommand = ""
        for command in args.command:
            fullcommand += f"{command} "
        console.execute_command(fullcommand)
        exit(0)
    except Exception as e:
        exit(1)

while True:
    console.interpreter()