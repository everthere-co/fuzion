from fuzion.mixins import CreateObjectMixin, DestroyObjectMixin,\
    ListObjectsMixin
from fuzion.resource import Resource

class NotificationWebhook(ListObjectsMixin, CreateObjectMixin, DestroyObjectMixin, Resource):
    path = "notification-webhooks"
    object_id_attr_name = "fuzion_webhook_id"