import time
import inspect
from pathlib import Path

class Style:
    # Explicit
    NORMAL = 0
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

def bright(fg_code):
    return fg_code + 60

def bg(fg_code):
    return fg_code + 10

def ansi_esc(code, format):
    return f'\033[{code}m{format}\033[m'

def _printer(style, format):
    start = time.time()
    t = time.strftime('%H:%M:%S', time.localtime(time.time()))
    try:
        frame = inspect.stack()[2][0]
        info = inspect.getframeinfo(frame)
        function = info.function
        line = info.lineno
        module = Path(info.filename).name.split(sep=".", maxsplit=1)[0]

    finally:
        del frame

    print (ansi_esc(style, f'[{inspect.stack()[1].function.upper()}][{t}({time.time() - start:.3f})][{module}.{function}:{line}] {format}') )

def info(format):
    _printer(Style.NORMAL, format)

def good(format):
    _printer(Style.GREEN, format)

def warn(format):
    _printer(Style.YELLOW, format)

def error(format):
    _printer(Style.RED, format)

def fatal(format):
    _printer(bright(bg(Style.RED)), format)

def _test():
    info("This is a info message")
    warn("This is a warning message")
    error("This is a error message")
    fatal("This is a fatal message")


if __name__ == '__main__':
    _test()
