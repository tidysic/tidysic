from rich import print


def log(message, prefix="", color="blue"):

    if len(prefix) > 0:
        prefix = f"[{color}]\[tidysic] [italic]{prefix}[/italic][/{color}]: "
    else:
        prefix = f"[{color}]\[tidysic][/{color}]: "

    if isinstance(message, str):
        print(prefix + message)
    else:
        print(prefix)
        for line in message:
            print("\t" + line)
