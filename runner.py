def _exec(task):
    a, b, h = task
    r = a + b
    if h:
        h(r)
    return r


def _each(val):
    print "each: %s" % val


def _complete(val):
    print  "updated: %s" % val


if __name__ == '__main__':
    print "done__"
