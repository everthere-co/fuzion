import requests
import fuzion
import hashlib
import hmac
import time
import base64
from fuzion.exceptions import BadRequestError, UnautorizedError,\
    NotFoundError, PayloadTooLargeError, TooManyRequestsError,\
    InternalServerError, ResourceUnavailableError

class Resource():
    host = "fuzionapi.com/v1/"
    path = ""
    scheme = "https"
    options  = {}
    valid_options = ['params', 'headers']
    object_id_attr_name = None

    def __init__(self, fuzion_event_id, api_key=fuzion.api_key, 
                 api_secret_key=fuzion.api_secret_key, 
                 *args, **kwargs):
        self.fuzion_event_id = fuzion_event_id
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        
        if self.object_id_attr_name in kwargs:
            setattr(self, self.object_id_attr_name, kwargs.get(self.object_id_attr_name))
        
    def _get_object_id_attr(self):
        getattr(self, self.object_id_attr_name, None)
    
    def _extract_object_id(self, values={}):
        if self.object_id_attr_name in values:
            return values.pop(self.object_id_attr_name)
        return self._get_object_id_attr()
        
    def _generate_partner_app_signature(self, 
                                        request_timestamp, 
                                        path, 
                                        http_verb="GET"):
        secret_key = bytes(self.api_secret_key, 'UTF-8')
        method = http_verb
        singature_parts = \
            bytes(f"{self.host}{path}|{method}|"
                  f"{request_timestamp}|{self.api_key}", 'UTF-8')
        
        partner_app_signature = hmac.new(secret_key, 
                                         singature_parts, 
                                         hashlib.sha256).digest()
        return str(base64.standard_b64encode(partner_app_signature), "UTF-8")

    def _get_general_request_header(self, path, http_verb):
        request_timestamp = int(time.time()*1000)
        
        partner_app_signature = self._generate_partner_app_signature(
            request_timestamp, path, http_verb
        )
        
        return {
            "partner_app_key": self.api_key,
            "request_timestamp": str(request_timestamp), 
            "fuzion_event_id": self.fuzion_event_id, 
            "partner_app_signature": partner_app_signature
            }
    
    def _handle_response(self, response):
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
                
            raise error_class(status=status, 
                              reason=response_data["reason"], 
                              message=response_data["message"], 
                              request=response.request, 
                              response=response)
           
        payload = response_data.pop("payload", None)
        return self.new(payload)
        
    def new(self, item):
        if isinstance(item, list):
            return list(dict(rec) for rec in item)
        else:
            return dict(item)

    def extract_options(self, path, http_verb, values):
        options = {k: v for k, v in list(values.items()) \
                    if k in self.valid_options}
        options.update(self.options)

        params  = {k: v for k, v in list(values.items()) \
                    if k not in self.valid_options}
        for k in list(params):
            if isinstance(params[k], list):
                params[k + '[]'] = params.pop(k)

        options.setdefault('params', {}).update(params)
        options.setdefault("headers", {}).update(
            self._get_general_request_header(path, http_verb)
        )

        return options
    
    def _request(self, method, path, values, paging={}):
        http_verb = method.upper()
        
        options = self.extract_options(path, 
                                      http_verb, 
                                      values)
        
        if paging:
            headers = options.get("headers", {})
            headers.update(paging)
            options.setdefault("headers", {}).update(headers)
        
        endpoint = self.scheme + "://" + self.host + path
        
        if method not in ["get", "head", "options"]:
            # Always post as a JSON object
            options['json'] = options.pop('params', {})
            
        response = requests.request(method, endpoint, **options)
        
        if response.status_code == 200:
            return self._handle_response(response)
        
        response.raise_for_status()
