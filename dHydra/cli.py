# -*- coding: utf-8 -*-
import click

@click.command()
@click.argument('what', nargs = -1)
def hail(what = None):
    if what != "dHydra":
        print("Hail What?")
