from progressbar import *

def progress(iterable, maxval=None):
    if maxval is None:
        maxval = len(iterable)

    if maxval == 0:
        return

    pbar = ProgressBar(maxval=maxval, widgets=(
        Percentage(), ' ', Bar(), ' ', ETA()
    )).start()

    for idx, elem in enumerate(iterable):
        yield elem
        pbar.update(idx + 1)

def progress_qs(qs):
    return progress(qs, maxval=qs.count())
