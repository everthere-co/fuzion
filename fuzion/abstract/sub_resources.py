from fuzion.mixins import RetrieveNotSupportedMixin
from fuzion.subresource import SubResource

class AbstractContact(RetrieveNotSupportedMixin, SubResource):
    object_id_attr_name = "contact_id"
    
    def _set_path(self):
        self.path = f"abstracts/{self.parent_object.abstract_id}/contacts"