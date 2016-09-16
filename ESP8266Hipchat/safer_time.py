from time import *

def sleep(duration):
    import time
    if float(duration) > 2.0:
        return "Woah, that is way too long"
    time.sleep(duration)

def sleep_ms(duration):
    import time
    if float(duration) > 2000.0:
        return "Woah, that is way too long, even in milliseconds"
    time.sleep_ms(duration)