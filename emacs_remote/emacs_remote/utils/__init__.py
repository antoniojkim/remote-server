import hashlib


def md5(s: str) -> str:
    """
    Gets md5 hash of the input string in hexadecimal format

    Args:
        s: the input string
    Returns:
        The md5 hash
    """
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()
