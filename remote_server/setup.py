from setuptools import find_packages, setup

setup(
    name="emacs-remote",
    version="0.1",
    description="Emacs Remote Client/Server",
    author="Antonio Kim",
    author_email="antoniok@antoniojkim.com",
    url="https://github.com/antoniojkim/emacs-remote/tree/main/emacs_remote",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "emacs-remote-client = emacs_remote.client.main:main",
            "emacs-remote-server = emacs_remote.server.main:main",
        ]
    },
    data_files=[("emacs_remote_scripts", ["scripts/server.sh"])],
)
