from fuzion.mixins import CreateObjectMixin, DestroyObjectMixin,\
    ListObjectsMixin
from fuzion.resource import Resource

class ErrorWebhook(ListObjectsMixin, CreateObjectMixin, DestroyObjectMixin, Resource):
    path = "errors-webhooks"
    object_id_attr_name = "fuzion_webhook_id"