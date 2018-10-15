import functools
from fuzion.exceptions import ObjectIdMissingError


def has_object_id_set(func):
    """
    A decorator that makes sure the `internal_object_id` was set on the instance
    before requesting a sub-object
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        instance = args[0]
        if instance.internal_object_id is None:
            raise ObjectIdMissingError(
                "`{}` attribute is not set".format(instance.object_id_attr_name)
            )
        return func(*args, **kwargs)

    return wrapper
