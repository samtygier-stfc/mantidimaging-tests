# Copyright (C) 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
from logging import getLogger
import os

logger = getLogger(__name__)

filter_names = [
    'Crop Coordinates', 'Flat-fielding', 'Remove Outliers', 'ROI Normalisation', 'Arithmetic', 'Circular Mask',
    'Clip Values', 'Divide', 'Gaussian', 'Median', 'Monitor Normalisation', 'NaN Removal', 'Rebin', 'Rescale',
    'Ring Removal', 'Rotate Stack', 'Remove all stripes', 'Remove dead stripes', 'Remove large stripes',
    'Stripe Removal', 'Remove stripes with filtering', 'Remove stripes with sorting and fitting'
]

filter_names = list(map(lambda x: "-".join(x.split()).lower(), filter_names))


def _valid_operation(operation: str):
    """
    Checks if a given operation exists in Mantid Imaging.
    :param operation: The name of the operation.
    :return: True if it is a valid operation, False otherwise.
    """
    return operation.lower() in filter_names


def _log_and_exit(msg: str):
    """
    Log an error message and exit.
    :param msg: The log message.
    """
    logger.error(msg)
    exit()


class CommandLineArguments:
    _instance = None
    images_path = ""
    init_operation = ""
    show_recon = False

    def __new__(cls, path: str = "", operation: str = "", show_recon: bool = False):
        """
        Creates a singleton for storing the command line arguments.
        """
        if cls._instance is None:
            cls._instance = super(CommandLineArguments, cls).__new__(cls)
            if path:
                if not os.path.exists(path):
                    _log_and_exit(f"Path {path} doesn't exist. Exiting.")
                else:
                    cls.images_path = path
            if operation:
                if not cls.images_path:
                    _log_and_exit("No path given for initial operation. Exiting.")
                elif not _valid_operation(operation):
                    _log_and_exit(f"{operation} is not a known operation. Exiting.")
                else:
                    cls.init_operation = operation
            if show_recon and not path:
                _log_and_exit("No path given for reconstruction. Exiting.")
            else:
                cls.show_recon = show_recon

        return cls._instance

    @classmethod
    def path(cls) -> str:
        """
        Returns the command line images path.
        """
        return cls.images_path

    @classmethod
    def operation(cls) -> str:
        """
        Returns the initial operation.
        """
        return cls.init_operation

    @classmethod
    def recon(cls) -> bool:
        """
        Returns whether or not the recon window should be started.
        """
        return cls.show_recon
