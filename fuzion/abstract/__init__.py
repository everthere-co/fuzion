from fuzion.mixins import RetrieveNotSupportedMixin
from fuzion.resource import Resource
from fuzion.abstract.sub_resources import AbstractContact
from fuzion.exceptions import ObjectIdMissingError
from fuzion.decorators import has_object_id_set


class Abstract(RetrieveNotSupportedMixin, Resource):
    path = "abstracts"
    object_id_attr_name = "fuzion_abstract_id"

    @property
    @has_object_id_set
    def contacts(self):
        return AbstractContact(parent_object=self)


class AbstractDisclosure(RetrieveNotSupportedMixin, Resource):
    path = "abstract-disclosures"
    object_id_attr_name = "fuzion_abstract_disclosure_id"


class AbstractAffiliation(RetrieveNotSupportedMixin, Resource):
    path = "abstract-affiliations"
    object_id_attr_name = "fuzion_abstract_affiliation_id"


class AbstractResource(RetrieveNotSupportedMixin, Resource):
    path = "abstract-resources"
    object_id_attr_name = "fuzion_abstract_resource_id"


class AbstractPoster(RetrieveNotSupportedMixin, Resource):
    path = "abstract-posters"
    object_id_attr_name = "fuzion_abstract_poster_id"
