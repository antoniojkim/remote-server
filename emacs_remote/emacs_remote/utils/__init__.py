import hashlib


def md5(s) -> str:
    """
    Gets md5 hash of the input string in hexadecimal format

    Args:
        s: the input to be hashed
    Returns:
        The md5 hash
    """
    m = hashlib.md5()

    def recurse(arg):
        if isinstance(arg, str):
            m.update(arg.encode("utf-8"))
        elif isinstance(arg, int):
            m.update(arg)
        elif isinstance(arg, (list, tuple)):
            list(map(recurse, arg))
        else:
            raise TypeError(f"Invalid arg type for hash: {type(arg)}")

    recurse(s)
    return m.hexdigest()
