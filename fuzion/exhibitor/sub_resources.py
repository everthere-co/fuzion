from fuzion.mixins import RetrieveNotSupportedMixin, ListObjectsPaginationMixin
from fuzion.subresource import SubResource, Relationship


class ExhibitorContact(RetrieveNotSupportedMixin, SubResource):
    path = "exhibitors/{}/contacts"
    object_id_attr_name = "fuzion_contact_id"


class ExhibitorAddress(RetrieveNotSupportedMixin, SubResource):
    path = "exhibitors/{}/addresses"
    object_id_attr_name = "fuzion_address_id"


class ExhibitorBooth(ListObjectsPaginationMixin, Relationship):
    path = "exhibitors/{}/booths"
    object_id_attr_name = "fuzion_booth_id"


class ExhibitorThirdParty(ListObjectsPaginationMixin, Relationship):
    path = "exhibitors/{}/third-parties"
    object_id_attr_name = "fuzion_third_party_id"


class BoothThirdParty(ListObjectsPaginationMixin, SubResource):
    path = "booths/{}/third-parties"


class BoothExhibitor(ListObjectsPaginationMixin, SubResource):
    path = "booths/{}/exhibitors"


class BoothContact(RetrieveNotSupportedMixin, SubResource):
    path = "booths/{}/contacts"
    object_id_attr_name = "fuzion_contact_id"


class BoothAddress(RetrieveNotSupportedMixin, SubResource):
    path = "booths/{}/addresses"
    object_id_attr_name = "fuzion_address_id"


class ThirdPartyContact(RetrieveNotSupportedMixin, SubResource):
    path = "third-parties/{}/contacts"
    object_id_attr_name = "fuzion_contact_id"


class ThirdPartyAddress(RetrieveNotSupportedMixin, SubResource):
    path = "third-parties/{}/addresses"
    object_id_attr_name = "fuzion_address_id"


class ThirdPartyExhibitor(ListObjectsPaginationMixin, SubResource):
    path = "third-parties/{}/exhibitors"


class ThirdPartyBooth(ListObjectsPaginationMixin, Relationship):
    path = "third-parties/{}/booths"
    object_id_attr_name = "fuzion_booth_id"
