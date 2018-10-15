class FuzionError(Exception):
    """
    This package base exception
    
    Adds fuzion's response `status`, `reason` and `message` attributes, 
    along with adding the original `requests.PreparedRequest` and `requests.Response` objects
    """

    status = None
    reason = None
    message = None
    request = None
    response = None

    def __init__(self, status, reason, message, request, response, *args, **kwargs):
        self.status = status
        self.reason = reason
        self.message = message
        self.request = request
        self.response = response

        Exception.__init__(self, *args, **kwargs)

    def __str__(self):
        return self.message


class BadRequestError(FuzionError):
    """
    For status 400 - Bad request
    """

    pass


class UnautorizedError(FuzionError):
    """
    For status 401 - Unauthorized
    """

    pass


class NotFoundError(FuzionError):
    """
    For status 404 - Not found
    """

    pass


class PayloadTooLargeError(FuzionError):
    """
    For status 413 - Payload too large
    """

    pass


class TooManyRequestsError(FuzionError):
    """
    For status 429 - Too many requests
    """

    pass


class InternalServerError(FuzionError):
    """
    For status 500 - Internal server error
    """

    pass


class ResourceUnavailableError(FuzionError):
    """
    For status 503 - Service unavailable
    """

    pass


class ObjectIdMissingError(Exception):
    """
    General error where object id is needed to process the request
    but it wasn't previously set or provided to the specific call
    """

    pass


class ImproperlyConfigured(Exception):
    """
    General error where something is malconfigured
    """

    pass
