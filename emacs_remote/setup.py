#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="emacs-remote",
    version="0.1",
    description="Emacs Remote Client/Server",
    author="Antonio Kim",
    author_email="antoniok@antoniojkim.com",
    url="https://github.com/antoniojkim/emacs-remote/tree/main/emacs_remote",
    package_dir={"": "emacs_remote"},
    packages=find_packages(where="emacs_remote"),
    entry_points={
        "console_scripts": [
            "emacs-remote-client = client.main:main",
            "emacs-remote-server = server.main:main",
        ]
    },
)
