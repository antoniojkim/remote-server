from threading import Lock


class AtomicInt:
    def __init__(self, init_val: int = 0):
        self.val = init_val
        self.lock = Lock()

    @property
    def value(self):
        with self.lock:
            return self.val

    @value.setter
    def value(self, val):
        with self.lock:
            self.val = val

    def __eq__(self, other: int):
        with self.lock:
            return self.val == other

    def __gt__(self, other: int):
        with self.lock:
            return self.val > other

    def __lt__(self, other: int):
        with self.lock:
            return self.val < other

    def __ge__(self, other: int):
        with self.lock:
            return self.val >= other

    def __le__(self, other: int):
        with self.lock:
            return self.val <= other

    def __iadd__(self, inc):
        with self.lock:
            self.val += inc

    def __isub__(self, inc):
        with self.lock:
            self.val -= inc

    def __enter__(self):
        with self.lock:
            self.val += 1

        return self

    def __exit__(self, *args):
        with self.lock:
            self.val -= 1

    def __bool__(self):
        with self.lock:
            return self.val > 0
