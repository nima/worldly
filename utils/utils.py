"""
Useful utilities for this application.
"""

from typing import Union, Sequence


def sparsify(d: Union[dict, list]) -> Union[dict, list]:
    """
    Recursively remove keys with falsy values from a dictionary or list.
    """
    if isinstance(d, dict):
        return {
            key: sparse for key, value in d.items() if (sparse := sparse_dict(value))
        }

    if isinstance(d, list):
        return [sparse for item in d if (sparse := sparsify(item))]

    return d
