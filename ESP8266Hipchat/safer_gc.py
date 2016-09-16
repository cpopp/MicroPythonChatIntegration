from gc import collect, enable, isenabled, mem_free, mem_alloc

# implement to avoid the threshold from being set
def threshold():
    import gc
    return gc.threshold()