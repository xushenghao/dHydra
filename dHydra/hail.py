import click
from dHydra.console import *
import dHydra.web

@click.command()
@click.argument('what', nargs = -1)
def hail(what = None):
    try:
        if what[0] != "dHydra":
            print("Hail What??")
            exit(0)
        else:
            print("Welcome to dHydra!")
            web = dHydra.web.start_server()
    except Exception as e:
        print("Hail What?")
        print(e)

@click.command()
def workers():
    pass
