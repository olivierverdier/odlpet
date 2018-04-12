import stir

class StirVerbosity(object):

    """Context manager setting STIR verbosity to a fixed level."""

    def __init__(self, verbosity):
        self.verbosity = verbosity
        self.old_verbosity = None

    def __enter__(self):
        self.old_verbosity = stir.Verbosity.get()
        stir.Verbosity.set(self.verbosity)

    def __exit__(self, *_):
        stir.Verbosity.set(self.old_verbosity)

