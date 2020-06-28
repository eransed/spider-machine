import time
import inspect
from pathlib import Path
import traceback

class Enabled:
    info = True
    blue = True
    good = True
    warn = False
    error = True
    fatal = True

def getFields(cls):
    return list(filter(lambda x: not x[0].startswith('__'), list(vars(cls).items())))

# def getClassFields(cls):
#     return [attr for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith("__")]

# def classFields (cls):
#     # return [attr for attr in vars(cls).items() if not callable(getattr(cls, attr)) and not attr.startswith("__")]
#     return vars(cls).items()

# def cf(cls):
#     fields = list()
#     for attr, value in cls.:
#         fields.append(f'{attr}={value}')

#     return fields

# def clsFlds (cls):
#     return vars(cls.__class__).items()

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

def ansi_esc(code, format):
    return f'\033[{code}m{format}\033[m'

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



def info(format):
    _printer(Style.NORMAL, format, Enabled.info)

def blue(format):
    _printer(Style.BLUE, format, Enabled.blue)

def good(format):
    _printer(Style.GREEN, format, Enabled.good)

def warn(format):
    _printer(Style.YELLOW, format, Enabled.warn)

def error(format):
    _printer(Style.RED, format, Enabled.error)

def fatal(format):
    _printer(bright(bg(Style.RED)), format, Enabled.fatal)



# Internal stuff
def log(format):
    _printer(Style.INVERTED, format, True)

def internal(format):
    _printer(Style.INVERTED, format, True)

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
    _styleTest()
    _test()
else:
    internal (f'Enabled log levels: {getFields(Enabled)}')


