from fuzion.mixins import RetrieveNotSupportedMixin
from fuzion.resource import Resource
from fuzion.abstract.sub_resources import AbstractContact
from fuzion.exceptions import ObjectIdMissingError

class Abstract(RetrieveNotSupportedMixin, Resource):
    path = "abstracts"
    object_id_attr_name = "abstract_id"
    
    @property
    def contacts(self):
        if self.abstract_id:
            return AbstractContact(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    
class AbstractDisclosure(RetrieveNotSupportedMixin, Resource):
    path = "abstract-disclosures"
    object_id_attr_name = "abstract_disclosure_id"
    
    
class AbstractAffiliation(RetrieveNotSupportedMixin, Resource):
    path = "abstract-affiliations"
    object_id_attr_name = "abstract_affiliation_id"
    
    
class AbstractResource(RetrieveNotSupportedMixin, Resource):
    path = "abstract-resources"
    object_id_attr_name = "abstract_resource_id"
    

class AbstractPoster(RetrieveNotSupportedMixin, Resource):
    path = "abstract-posters"
    object_id_attr_name = "abstract_poster_id"
    