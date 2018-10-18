import requests
import fuzion
import hashlib
import hmac
import time
import base64
from fuzion.exceptions import (
    BadRequestError,
    UnautorizedError,
    NotFoundError,
    PayloadTooLargeError,
    TooManyRequestsError,
    InternalServerError,
    ResourceUnavailableError,
)


class Resource(dict):
    host = ""
    path = ""  # The object's path in fuzion's API
    scheme = "https"
    options = {}
    valid_options = ["params", "headers"]
    object_id_attr_name = None  # The object's id ('attendee_id' for Attendee, etc..)

    def __init__(
        self, fuzion_event_id, api_key=None, api_secret_key=None, host=None, *args, **kwargs
    ):
        self.fuzion_event_id = fuzion_event_id
        self.api_key = api_key or fuzion.api_key
        self.api_secret_key = api_secret_key or fuzion.api_secret_key
        self.host = host or fuzion.host

        # If the object's id attibute was sent, set it for this instance
        if self.object_id_attr_name in kwargs:
            setattr(
                self, self.object_id_attr_name, kwargs.get(self.object_id_attr_name)
            )

        dict.__init__(self, *args, **kwargs)

    @property
    def internal_object_id(self):
        return getattr(self, self.object_id_attr_name, None)

    def _extract_object_id(self, values={}):
        """ 
        Extracts the instance object id, either from the values supploed
        or from the instance itself
        """
        if self.object_id_attr_name in values:
            return values.pop(self.object_id_attr_name)
        return self.internal_object_id

    def _generate_partner_app_signature(self, request_timestamp, path, http_verb="GET"):
        """
        Generate the required base64 encoded signature for the request.
        See "Constructing the App Signature" section in Fuzion's documentation
        """
        secret_key = bytes(self.api_secret_key, "UTF-8")
        method = http_verb
        singature_parts = bytes(
            "{0}{1}|{2}|{3}|{4}".format(
                self.host, path, method, request_timestamp, self.api_key
            ),
            "UTF-8",
        )

        partner_app_signature = hmac.new(
            secret_key, singature_parts, hashlib.sha256
        ).digest()
        return str(base64.standard_b64encode(partner_app_signature), "UTF-8")

    def _get_general_request_header(self, path, http_verb):
        """
        Returns the general header required for all requests, including the partner app signature
        """
        request_timestamp = int(time.time() * 1000)

        partner_app_signature = self._generate_partner_app_signature(
            request_timestamp, path, http_verb
        )

        return {
            "partner_app_key": self.api_key,
            "request_timestamp": str(request_timestamp),
            "fuzion_event_id": self.fuzion_event_id,
            "partner_app_signature": partner_app_signature,
        }

    def process_response(self, response):
        """
        Handles erroneous responses
        Raises specific error according to response status received from the server
        
        Returns the payload of the response (without the meta-data part)
        """
        response_data = response.json()

        if response_data["error"]:
            status = response_data["status"]

            if status == 400:
                error_class = BadRequestError
            elif status == 401:
                error_class = UnautorizedError
            elif status == 404:
                error_class = NotFoundError
            elif status == 413:
                error_class = PayloadTooLargeError
            elif status == 429:
                error_class = TooManyRequestsError
            elif status == 500:
                error_class = InternalServerError
            elif status == 503:
                error_class = ResourceUnavailableError

            raise error_class(
                status=status,
                reason=response_data["reason"],
                message=response_data["message"],
                request=response.request,
                response=response,
            )

        payload = response_data.get("payload", None)
        return payload

    def process_payload(self, payload):
        return self.__class__.new(self.fuzion_event_id,
                                  payload, 
                                  api_key=self.api_key, 
                                  api_secret_key=self.api_secret_key, 
                                  host=self.host)

    @classmethod
    def new(cls, fuzion_event_id, item, *args, **kwargs):
        """
        Creates a new instance of the underlying class
        
        If the payload is a list, creates a list of instances
        """
        if isinstance(item, list):
            return list(
                cls(fuzion_event_id, *args, **{**rec, **kwargs}) for rec in item
            )
        else:
            return cls(fuzion_event_id, *args, **{**item, **kwargs})

    def extract_options(self, path, http_verb, values):
        """
        Builds the options (params, json, headers) that will be sent along with the request.
        
        `valid_options` will be treated as-is
        keys not in `valid_options` are added to the `params` option
        
        handles params as list if necessary
        
        adds the general request header to the supplied header, if any
        """
        options = {k: v for k, v in list(values.items()) if k in self.valid_options}
        options.update(self.options)

        params = {k: v for k, v in list(values.items()) if k not in self.valid_options}
        for k in list(params):
            if isinstance(params[k], list):
                params[k + "[]"] = params.pop(k)

        options.setdefault("params", {}).update(params)
        options.setdefault("headers", {}).update(
            self._get_general_request_header(path, http_verb)
        )

        return options

    def _request(self, method, path, values, paging={}):
        """
        Performs the actual request.
        
        if `paging` is supplied, adds it as a header option
        """
        http_verb = method.upper()

        options = self.extract_options(path, http_verb, values)

        if paging:
            headers = options.get("headers", {})
            headers.update(paging)
            options.setdefault("headers", {}).update(headers)

        endpoint = self.scheme + "://" + self.host + path

        if method not in ["get", "head", "options"]:
            # Always post as a JSON object
            options["json"] = options.pop("params", {})

        response = requests.request(method, endpoint, **options)

        if response.status_code == 200:
            payload = self.process_response(response)
            return self.process_payload(payload)

        response.raise_for_status()
