class FuzionError(Exception):
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
        
    
class BadRequestError(FuzionError):
    pass


class UnautorizedError(FuzionError):
    pass


class NotFoundError(FuzionError):
    pass


class PayloadTooLargeError(FuzionError):
    pass


class TooManyRequestsError(FuzionError):
    pass


class InternalServerError(FuzionError):
    pass


class ResourceUnavailableError(FuzionError):
    pass


class ObjectIdMissingError(Exception):
    pass


class ImproperlyConfigured(Exception):
    pass
        