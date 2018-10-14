from fuzion.mixins import RetrieveNotSupportedMixin, ListObjectsMixin
from fuzion.subresource import SubResource, Relationship

class ExhibitorContact(RetrieveNotSupportedMixin, SubResource):
    object_id_attr_name = "contact_id"
    
    def _set_path(self):
        self.path = f"exhibitors/{self.parent_object.exhibitor_id}/contacts"
        

class ExhibitorAddress(RetrieveNotSupportedMixin, SubResource):
    object_id_attr_name = "contact_id"
    
    def _set_path(self):
        self.path = f"exhibitors/{self.parent_object.exhibitor_id}/addresses"    


class ExhibitorBooth(Relationship):
    object_id_attr_name = "booth_id"
    
    def _set_path(self):
        self.path = f"exhibitors/{self.parent_object.exhibitor_id}/booths"


class ExhibitorThirdParty(Relationship):
    object_id_attr_name = "third_party_id"
    
    def _set_path(self):
        self.path = f"exhibitors/{self.parent_object.exhibitor_id}/third-parties"
        
        
class BoothThirdParty(ListObjectsMixin, SubResource):
    def _set_path(self):
        self.path = f"exhibitors/{self.parent_object.booth_id}/third-parties"
        

class BoothExhibitor(ListObjectsMixin, SubResource):
    def _set_path(self):
        self.path = f"exhibitors/{self.parent_object.booth_id}/exhibitors"
    

class BoothContact(RetrieveNotSupportedMixin, SubResource):
    object_id_attr_name = "booth_contact_id"
    parent_object_id_attr_name = "booth_id"
    
    def _set_path(self):
        self.path = f"booths/{self.booth_id}/contacts"
    
        
class BoothAddress(RetrieveNotSupportedMixin, SubResource):
    object_id_attr_name = "booth_address_id"
    
    def _set_path(self):
        self.path = f"booths/{self.parent_object.booth_id}/addresses"
        
        
class ThirdPartyContact(RetrieveNotSupportedMixin, SubResource):
    object_id_attr_name = "contact_id"
    
    def _set_path(self):
        self.path = f"third-parties/{self.parent_object.third_party_id}/contacts"
        

class ThirdPartyAddress(RetrieveNotSupportedMixin, SubResource):
    object_id_attr_name = "address_id"
    
    def _set_path(self):
        self.path = f"third-parties/{self.parent_object.third_party_id}/addresses"
        

class ThirdPartyExhibitor(ListObjectsMixin, SubResource):
    def _set_path(self):
        self.path = f"third-parties/{self.parent_object.third_party_id}/exhibitors"
        

class ThirdPartyBooth(ListObjectsMixin, Relationship):
    object_id_attr_name = "booth_id"
    
    def _set_path(self):
        self.path = f"third-parties/{self.parent_object.third_party_id}/booths"
