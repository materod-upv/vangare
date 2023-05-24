# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

from vangare.cli import main

"""Allow cookiecutter to be executable through `python -m vangare`."""

if __name__ == "__main__":  # pragma: no cover
    main(prog_name="vangare")
