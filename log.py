import time
import inspect
from pathlib import Path
import traceback

class Enabled:
    info = True
    note = True
    blue = True
    good = True
    warn = False
    error = True
    fatal = True

def getFields(cls):
    return list(filter(lambda x: not x[0].startswith('__'), list(vars(cls).items())))

class Style:
    # Explicit
    NORMAL = 0
    INVERTED = 7
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

def ansi_esc(code, format, nested=False):
    if nested == False:
        return f'\033[{code}m{format}\033[m'
    else:
        return f'\033[{code}m{format}'

# Should only be called from an function in the log.py module
def _printer(style, format, enabled = True):
    if enabled == False: return
    start = time.time()
    t = time.strftime('%H:%M:%S', time.localtime(time.time()))
    frame = None
    try:
        frame = inspect.stack()[2][0]
        info = inspect.getframeinfo(frame)
        function = info.function
        line = info.lineno
        module = Path(info.filename).name.split(sep=".", maxsplit=1)[0]
        print (ansi_esc(style, f'[{inspect.stack()[1].function.upper()}][{t} ({time.time() - start:.3f}s)][{module}.{function}:{line}] {format}'), flush=True)

    except Exception as e:
        print (f'An logging error occured: {str(e)}')
        # traceback.print_exc()

    finally:
        del frame


def info(format, bypass_enabled = False):
    _printer(Style.NORMAL, format, Enabled.info or bypass_enabled)

def note(format, bypass_enabled = False):
    _printer(Style.MAGENTA, format, Enabled.note or bypass_enabled)

def blue(format, bypass_enabled = False):
    _printer(Style.BLUE, format, Enabled.blue or bypass_enabled)

def good(format, bypass_enabled = False):
    _printer(Style.GREEN, format, Enabled.good or bypass_enabled)

def warn(format, bypass_enabled = False):
    _printer(Style.YELLOW, format, Enabled.warn or bypass_enabled)

def error(format, bypass_enabled = False):
    _printer(Style.RED, format, Enabled.error or bypass_enabled)

def fatal(format, bypass_enabled = False):
    _printer(bright(bg(Style.RED)), format, Enabled.fatal or bypass_enabled)


# Internal stuff
def log(format):
    _printer(Style.INVERTED, format, True)

def internal(format):
    _printer(Style.INVERTED, format, True)

def getEnabled(nested = False):
    li = getFields(Enabled)
    out = ""
    for i in range(len (li)):
        val = li[i][1]
        key = li[i][0].upper()
        if val == False:
            out += ansi_esc(bg(Style.RED), f'{key}={val}', nested)
        else:
            out += f'{key}={val}'
        out += " "

    return out

def _test():
    info("This is a info message")
    warn("This is a warning message")
    error("This is a error message")
    fatal("This is a fatal message")

def _styleTest():
    for i in range(40):
        _printer(i, f'Style test {i}')
        _printer(bg(i), f'Style test bg({i})')
        _printer(bright(i), f'Style test bright({i})')
        _printer(bright(bg(i)), f'Style test bright(bg({i}))')

if __name__ == '__main__':
    # _styleTest()
    _test()
else:
    pass

print (f'Enabled log levels: {getEnabled()}')

