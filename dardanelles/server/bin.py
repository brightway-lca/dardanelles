#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dardanelles web server.

Usage:
  dardanelles [--port=<port>] [--localhost]
  dardanelles -h | --help
  dardanelles --version

Options:
  --localhost   Only allow connections from this computer.
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
from pandarus_remote import pr_app


def webapp():
    args = docopt(__doc__, version="Dardanelles web service 0.1")
    port = int(args.get("--port", False) or 5000)
    host = "localhost" if args.get("--localhost", False) else "0.0.0.0"

    print("dardanelles started on {}:{}".format(host, port))

    pr_app.run(host=host, port=port, debug=False)
