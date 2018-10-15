from fuzion.resource import Resource
from fuzion.mixins import AllCRUDMixin, RetrieveNotSupportedMixin
from fuzion.exceptions import ImproperlyConfigured, ObjectIdMissingError
from fuzion.exhibitor.sub_resources import (
    ExhibitorContact,
    ExhibitorAddress,
    ExhibitorBooth,
    ExhibitorThirdParty,
    BoothThirdParty,
    BoothExhibitor,
    BoothContact,
    BoothAddress,
    ThirdPartyContact,
    ThirdPartyAddress,
    ThirdPartyExhibitor,
    ThirdPartyBooth,
)
from fuzion.decorators import has_object_id_set


class Exhibitor(AllCRUDMixin, Resource):
    path = "exhibitors"
    object_id_attr_name = "fuzion_exhibitor_id"

    @property
    @has_object_id_set
    def contacts(self):
        return ExhibitorContact(parent_object=self)

    @property
    @has_object_id_set
    def addresses(self):
        return ExhibitorAddress(parent_object=self)

    @property
    @has_object_id_set
    def booths(self):
        return ExhibitorBooth(parent_object=self)

    @property
    @has_object_id_set
    def third_parties(self):
        return ExhibitorThirdParty(parent_object=self)


class Booth(AllCRUDMixin, Resource):
    path = "booths"
    object_id_attr_name = "fuzion_booth_id"

    @property
    @has_object_id_set
    def third_parties(self):
        return BoothThirdParty(parent_object=self)

    @property
    @has_object_id_set
    def exhibitors(self):
        return BoothExhibitor(parent_object=self)

    @property
    @has_object_id_set
    def contacts(self):
        return BoothContact(parent_object=self)

    @property
    @has_object_id_set
    def addresses(self):
        return BoothAddress(parent_object=self)


class ThirdParty(AllCRUDMixin, Resource):
    path = "third-parties"
    object_id_attr_name = "fuzion_third_party_id"

    @property
    @has_object_id_set
    def contacts(self):
        return ThirdPartyContact(parent_object=self)

    @property
    @has_object_id_set
    def addresses(self):
        return ThirdPartyAddress(parent_object=self)

    @property
    @has_object_id_set
    def exhibitors(self):
        return ThirdPartyExhibitor(parent_object=self)

    @property
    @has_object_id_set
    def booths(self):
        return ThirdPartyBooth(parent_object=self)


class ExhibitorProduct(RetrieveNotSupportedMixin, Resource):
    path = "exhibitor-products"
    object_id_attr_name = "fuzion_exhibitor_product_id"
