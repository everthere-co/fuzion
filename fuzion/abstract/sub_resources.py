from fuzion.mixins import RetrieveNotSupportedMixin
from fuzion.subresource import SubResource


class AbstractContact(RetrieveNotSupportedMixin, SubResource):
    path = "abstracts/{}/contacts"
    object_id_attr_name = "fuzion_contact_id"
