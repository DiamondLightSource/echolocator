from importlib.metadata import version

__version__ = version("echolocator")
del version

__all__ = ["__version__"]
