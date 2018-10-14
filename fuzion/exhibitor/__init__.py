from fuzion.resource import Resource
from fuzion.mixins import AllCRUDMixin, RetrieveNotSupportedMixin
from fuzion.exceptions import ImproperlyConfigured, ObjectIdMissingError
from fuzion.exhibitor.sub_resources import ExhibitorContact, ExhibitorAddress,\
    ExhibitorBooth, ExhibitorThirdParty, BoothThirdParty, BoothExhibitor,\
    BoothContact, BoothAddress, ThirdPartyContact, ThirdPartyAddress,\
    ThirdPartyExhibitor, ThirdPartyBooth


class Exhibitor(AllCRUDMixin, Resource):
    path = "exhibitors"
    object_id_attr_name = "exhibitor_id"
            
    @property
    def contacts(self):
        if self.exhibitor_id:
            return ExhibitorContact(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    @property
    def addresses(self):
        if self.exhibitor_id:
            return ExhibitorAddress(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    @property
    def booths(self):
        if self.exhibitor_id:
            return ExhibitorBooth(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    @property
    def third_parties(self):
        if self.exhibitor_id:
            return ExhibitorThirdParty(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
        
        
class Booth(AllCRUDMixin, Resource):
    path = "booths"
    object_id_attr_name = "booth_id"
    
    @property
    def third_parties(self):
        if self.booth_id:
            return BoothThirdParty(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    @property
    def exhibitors(self):
        if self.booth_id:
            return BoothExhibitor(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    @property
    def contacts(self):
        if self.booth_id:
            return BoothContact(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    @property
    def addresses(self):
        if self.booth_id:
            return BoothAddress(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
        
        
class ThirdParty(AllCRUDMixin, Resource):
    path = "third-parties"
    object_id_attr_name = "third_party_id"
    
    @property
    def contacts(self):
        if self.third_party_id:
            return ThirdPartyContact(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    @property
    def addresses(self):
        if self.third_party_id:
            return ThirdPartyAddress(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    @property
    def exhibitors(self):
        if self.third_party_id:
            return ThirdPartyExhibitor(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    @property
    def booths(self):
        if self.third_party_id:
            return ThirdPartyBooth(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    
class ExhibitorProduct(RetrieveNotSupportedMixin, Resource):
    path = "exhibitor-products"
    object_id_attr_name = "exhibitor_product_id"
