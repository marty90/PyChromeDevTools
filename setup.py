
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="PyChromeDevTools",
    description="PyChromeDevTools : Interact with Google Chrome using the Chrome DevTools Protocol.",
    license="Apache License 2.0",
    version="0.1",
    author="Martino Trevisan",
    author_email="martino.trevisan@polito.it",
    maintainer="Martino Trevisan",
    maintainer_email="martino.trevisan@polito.it",
    url="https://github.com/marty90/PyChromeDevTools",
    download_url = 'https://github.com/marty90/PyChromeDevTools/tarball/1.0.1',
    packages=['PyChromeDevTools'],
    install_requires=['requests', 'websocket-client']
)
