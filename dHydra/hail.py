import click

@click.command()
@click.argument('what', nargs = -1)
def hail(what = None):
    try:
        if what[0] != "dHydra":
            print("Hail What??")
            exit(0)
        else:
            print("Welcome to dHydra!")
            import dHydra.web
    except Exception as e:
        print("Hail What?")

@click.command()
def workers():
    pass
