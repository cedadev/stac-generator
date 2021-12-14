# encoding: utf-8
"""
Decorators
-----------

Decorators allow the user to modify the input and out from the processors.

:py:mod:`item_generator.extraction_methods.preprocessors` allow modification of the input arguments.

:py:mod:`item_generator.extraction_methods.postprocessors` modify the output dictionary.

"""
__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

from functools import wraps


def accepts_preprocessors(func):
    """
    Allows preprocessors to work on the input arguments. Uses the key
    ``pre_processors`` from the processor description.

    :param filepath: path to the file
    :param source_media: the source media
    :param pre_processors: list of pre_processors to run
    :param kwargs: additional kwargs passed to the wrapped processor
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        pre_processors = kwargs.get("pre_processors", [])

        # Remove the reference to self
        self = args[0]
        args = args[1:]

        for pprocessor in pre_processors:
            # Modify the input arguments
            args, kwargs = pprocessor.run(*args, **kwargs)

        response = func(self, *args, **kwargs)
        return response

    return wrapper


def accepts_postprocessors(func):
    """
    Allows postprocessors to work on the output from the main
    processor.  Uses the key ``post_processors`` from the processor description.

    :param filepath: Path to the file
    :param source_media: The source media type
    :param source_dict: The output dict from the wrapped processor
    :param post_processors: List of post processors to run
    :param kwargs: Additional kwargs passed to post processor

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the main processor
        response = func(*args, **kwargs)

        post_processors = kwargs.get("post_processors", [])

        # Remove the reference to self from the first processor.
        args = args[1:]

        for pprocessor in post_processors:

            # Modify the response from the main processor
            response = pprocessor.run(*args, source_dict=response, **kwargs)
        return response

    return wrapper
