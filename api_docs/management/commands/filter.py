#!/usr/bin/env python

from panflute import *


def action(elem, doc):
    # Remove links without urls
    if isinstance(elem, Link) and not elem.url:
        return []


def main(doc=None):
    return run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
