import time
from datetime import datetime
import inspect
from pathlib import Path
import traceback

log_timer = time.time()
ansi_colors = True

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

def setEnabledLogs(on):
    Enabled.info = on
    Enabled.note = on
    Enabled.blue = on
    Enabled.good = on
    Enabled.warn = on
    Enabled.error = on
    Enabled.fatal = on


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
    global ansi_colors
    if ansi_colors == False: return format
    if nested == False:
        return f'\033[{code}m{format}\033[m'
    else:
        return f'\033[{code}m{format}'


# Should only be called from an function in the log.py module
def _printer(style, format, enabled = True):
    if enabled == False: return
    # start = time.time()
    # t = time.strftime('%H:%M:%S.%f', time.localtime(time.time()))
    # t = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    t = datetime.today().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    frame = None
    try:
        global log_timer
        frame = inspect.stack()[2][0]
        info = inspect.getframeinfo(frame)
        function = info.function
        line = info.lineno
        module = Path(info.filename).name.split(sep=".", maxsplit=1)[0]
        # elapsed = f'{time.time() - start:.3f}s'
        sinceLastLog = f'{time.time() - log_timer:.3f}s'
        print (ansi_esc(style, f'[{inspect.stack()[1].function.upper()}][{t}][{sinceLastLog}][{module}.{function}:{line}] {format}'), flush=True)
        log_timer = time.time()

    except Exception as e:
        print (f'An logging error occured: {str(e)}')
        # traceback.print_exc()

    finally:
        if frame is not None:
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
            out += ansi_esc(Style.YELLOW, f'{key}={val}', nested)
        else:
            out += f'{key}={val}'
        out += " "

    return out

def printEnabled():
    print (f'Enabled log levels: {getEnabled()}')


def _test():
    setEnabledLogs(True)
    info("This is a info message")
    blue("This is a blue message")
    note("This is a note message")
    good("This is a good message")
    internal("This is a internal message")
    warn("This is a warning message")
    error("This is a error message")
    fatal("This is a fatal message")
    setting = Enabled.warn
    Enabled.warn = False
    printEnabled()
    warn("This is a warning message, bypassing enabled", True)
    Enabled.warn = setting



def _styleTest():
    for i in range(40):
        _printer(i, f'Style test {i}')
        _printer(bg(i), f'Style test bg({i})')
        _printer(bright(i), f'Style test bright({i})')
        _printer(bright(bg(i)), f'Style test bright(bg({i}))')

def parseIntArg(arg, index, default):
    try:
        return int(arg[index])
    except:
        return default



if __name__ == '__main__':
    # _styleTest()
    _test()
else:
    pass

printEnabled()
internal(f'Using colors: {ansi_colors}')