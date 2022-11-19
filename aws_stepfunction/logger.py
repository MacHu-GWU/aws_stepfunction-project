# -*- coding: utf-8 -*-

"""
Logging utilities.
"""

import typing as T
import logging
import functools
import contextlib

DEFAULT_STREAM_FORMAT = "%(message)s"


def set_stream_handler(
    logger,
    stream_level,
    stream_format,
):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(stream_level)
    stream_handler.setFormatter(logging.Formatter(stream_format))
    logger.addHandler(stream_handler)


def decohints(decorator: T.Callable) -> T.Callable:
    return decorator


class BaseLogger(object):
    """
    A base class for logger constructor.
    """

    def __init__(self, name=None, **kwargs):
        self.logger = logging.getLogger(name)
        self.tab = " " * 4
        self.enable = True
        self._handler_cache = list()

    def _indent(self, msg, indent):
        return "%s%s" % (self.tab * indent, msg)

    def debug(self, msg, indent=0, **kwargs):
        return self.logger.debug(self._indent(msg, indent), **kwargs)

    def info(self, msg, indent=0, **kwargs):
        return self.logger.info(self._indent(msg, indent), **kwargs)

    def warning(self, msg, indent=0, **kwargs):
        return self.logger.warning(self._indent(msg, indent), **kwargs)

    def error(self, msg, indent=0, **kwargs):
        return self.logger.error(self._indent(msg, indent), **kwargs)

    def critical(self, msg, indent=0, **kwargs):
        return self.logger.critical(self._indent(msg, indent), **kwargs)

    def remove_all_handler(self):
        """
        Unlink the file handler association.
        """
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            self._handler_cache.append(handler)

    def recover_all_handler(self):
        """
        Relink the file handler association you just removed.
        """
        for handler in self._handler_cache:
            self.logger.addHandler(handler)
        self._handler_cache = list()

    @contextlib.contextmanager
    def temp_disable(self, disable=True, *args, **kwargs):
        if disable is True:
            self.remove_all_handler()
        try:
            yield self
        finally:
            if disable is True:
                self.recover_all_handler()

    @decohints
    def decorator(self, func):
        """
        A decorator that allow you to use ``verbose`` parameter to temporarily
        disable logging in the given function. (default is enabled)

        Example::

            @logger.decorator
            def my_func(name):
                logger.info(f"hello {name}!")

            my_func("alice") # this will print "hello alice"
            my_func("alice", verbose=False) # this will print nothing
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if "verbose" in kwargs:
                verbose = kwargs.pop("verbose")
            else:
                verbose = True
            with self.temp_disable(disable=not verbose):
                return func(*args, **kwargs)

        return wrapper


class StreamOnlyLogger(BaseLogger):
    """
    This logger only print message to console, and not write log to file.

    :param stream_level: level above this will be streamed.
    :param stream_format: log information format.
    """

    def __init__(
        self,
        name=None,
        stream_level=logging.INFO,
        stream_format=DEFAULT_STREAM_FORMAT,
    ):
        super(StreamOnlyLogger, self).__init__(name)

        # Set Logging Level
        self.logger.setLevel(logging.DEBUG)

        # Set Stream Handler
        set_stream_handler(self.logger, stream_level, stream_format)


logger = StreamOnlyLogger(name="aws_stepfunction")
