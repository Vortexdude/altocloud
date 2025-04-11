from functools import wraps


class Logger:
    LEVELS = {
        "debug": (10, "chartreuse2"),
        "info": (10, "magenta"),
        "warn": (10, "gold1"),
        "error": (10, "deep_pink2"),
        "fatal": (10, "red1")
    }

    def __init__(self, level):
        try:
            from rich.console import Console
            console = Console()
            self.stdout = console.print
        except ImportError:
            def pp(msg, style=None):
                print(msg)

            self.stdout = pp

        self.current_level = None
        self.set_level(level)

    @classmethod
    def get_logger(cls, level="warn"):
        return cls(level)

    @staticmethod
    def color(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self._log(func.__name__, *args, **kwargs)
            func(self, *args, **kwargs)

        return wrapper

    def set_level(self, level):
        if not level in self.LEVELS:
            raise Exception(f"Given log level {level} not in predefined")
        self.current_level = self.LEVELS[level.lower()][0]

    def _log(self, level, message):
        level = level.lower()
        scoped_level_value, style = self.LEVELS[level]
        if scoped_level_value >= self.current_level:
            self.stdout(f"[{level.upper()}] {message}", style=style)

    @color
    def debug(self, message):
        pass

    @color
    def info(self, message):
        pass

    @color
    def warn(self, message):
        pass

    @color
    def error(self, message):
        pass

    @color
    def fatal(self, message):
        pass
