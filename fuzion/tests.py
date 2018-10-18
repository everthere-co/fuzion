import unittest

from unittest.mock import patch

import fuzion
from fuzion import *
from fuzion.exceptions import *

fuzion.api_key = "key"
fuzion.api_secret_key = "secret_key"


class MockResource:
    """
    We cannot rely on Resource to sign the request, as timestamp depends on the time of the request
    which makes it hard to test. So we override its ability to sign and use the same signature
    (apart from the `test_generate_partner_app_signature` where we test that exactly)
    """

    mock_general_headers = {
        "partner_app_key": "key",
        "request_timestamp": 1539596918424,
        "fuzion_event_id": "123",
        "partner_app_signature": "signature",
    }

    @classmethod
    def new(cls, instance):
        """
        Returns the required Resource instance with general mock headers so they don't get
        generated while during the actual request
        """
        instance._get_general_request_header = (
            lambda path, http_verb: cls.mock_general_headers
        )
        return instance


class Response:
    def __init__(self, payload):
        self.payload = payload
        self.request = {}

    def json(self):
        """
        Mocks requests.Response by providing this method
        """
        return self.payload


class TestResource(unittest.TestCase):
    def test_generate_partner_app_signature(self):
        request_timestamp = "1539596918424"
        signature = Resource(fuzion_event_id="123")._generate_partner_app_signature(
            request_timestamp=request_timestamp, path="attendees", http_verb="GET"
        )
        self.assertEqual(
            signature,
            "622r1BPOffqxIieVXH8Laq7gZIek1srUlmztGxngXLw=",
            "signatures not equal",
        )
    
    @patch("fuzion.resource.requests")
    def test_stage_env(self, requests):
        MockResource.new(Attendee(fuzion_event_id="123", host="stage.fuzionapi.com/v1/")).query()
        requests.request.assert_called_with(
            "get",
            "https://stage.fuzionapi.com/v1/attendees",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )
    
    @patch("fuzion.resource.requests")
    def test_subresouce_gets_params_of_father(self, requests):
        exhibitor = MockResource.new(Exhibitor(fuzion_event_id="123",
                                               api_key="subresource123", 
                                               api_secret_key="subresource123",  
                                               host="stage.fuzionapi.com/v1/", 
                                               fuzion_exhibitor_id="123"))
        contacts_resource = exhibitor.contacts
        
        self.assertTrue(contacts_resource.host == "stage.fuzionapi.com/v1/")
        self.assertTrue(contacts_resource.api_key == "subresource123")
        self.assertTrue(contacts_resource.api_secret_key == "subresource123")
        self.assertTrue(contacts_resource.fuzion_event_id == "123")
        
    def test_error_payload(self):
        func = Resource(fuzion_event_id="123").process_response

        response = Response(
            {
                "type": "json",
                "build": "0.1.8",
                "status": 400,
                "reason": "001",
                "message": "some error",
                "error": True,
                "date": "2018-01-15 14:30:32.123 EST",
                "page_size": 250,
                "start": 0,
                "total_count": 0,
                "payload": [],
            }
        )

        self.assertRaises(BadRequestError, func, response)

        response.payload["status"] = 401
        self.assertRaises(UnautorizedError, func, response)

        response.payload["status"] = 404
        self.assertRaises(NotFoundError, func, response)

        response.payload["status"] = 413
        self.assertRaises(PayloadTooLargeError, func, response)

        response.payload["status"] = 429
        self.assertRaises(TooManyRequestsError, func, response)

        response.payload["status"] = 500
        self.assertRaises(InternalServerError, func, response)

        response.payload["status"] = 503
        self.assertRaises(ResourceUnavailableError, func, response)

    def test_successful_payload(self):
        func = Resource(fuzion_event_id="123").process_response

        response = Response(
            {
                "type": "json",
                "build": "0.1.8",
                "status": 200,
                "reason": 0,
                "message": "Request was successful",
                "error": False,
                "date": "2018-01-15 14:30:32.123 EST",
                "page_size": 250,
                "start": 0,
                "total_count": 0,
                "payload": {
                    "fuzion_exhibitor_booth_id": "5555D95146B83C38ABDD4F9C20CA5555",
                    "fuzion_plot_id": "4444D95146B83C38ABDD4F9C20CA4444",
                    "booth_name": "Print A Lot",
                    "booth_number": 2222,
                    "booth_description": "copies and prints everywhere",
                    "assigned_area": "EntryArea",
                    "assigned_sub_area": "OnsiteRegistration",
                    "gps_location": "GPS coordinates",
                    "unit_of_measure_flag": 1,
                    "booth_width": 15,
                    "booth_depth": 10,
                    "booth_area": 150,
                    "signage_text": "ABC Printing Is Number One",
                    "target_start_timestamp": "2018-01-20 00:00:00.000",
                    "target_end_timestamp": "2018-01-22 23:00:00.000",
                    "custom_attributes": '{"booth_theme":"OverTheRainbow"}',
                    "relationship_type_flag": 0,
                    "relationship_confirmation_status_flag": 1,
                    "last_mod_timestamp": "2017-01-06T16:43:12.000Z",
                    "create_timestamp": "2017-01-06T16:43:12.000Z",
                },
            }
        )

        payload = func(response)
        self.assertEqual(payload, response.payload["payload"])

    def test_returns_new_instance(self):
        success_payload = {
            "fuzion_exhibitor_booth_id": "5555D95146B83C38ABDD4F9C20CA5555",
            "fuzion_plot_id": "4444D95146B83C38ABDD4F9C20CA4444",
            "booth_name": "Print A Lot",
            "booth_number": 2222,
            "booth_description": "copies and prints everywhere",
            "assigned_area": "EntryArea",
            "assigned_sub_area": "OnsiteRegistration",
            "gps_location": "GPS coordinates",
            "unit_of_measure_flag": 1,
            "booth_width": 15,
            "booth_depth": 10,
            "booth_area": 150,
            "signage_text": "ABC Printing Is Number One",
            "target_start_timestamp": "2018-01-20 00:00:00.000",
            "target_end_timestamp": "2018-01-22 23:00:00.000",
            "custom_attributes": '{"booth_theme":"OverTheRainbow"}',
            "relationship_type_flag": 0,
            "relationship_confirmation_status_flag": 1,
            "last_mod_timestamp": "2017-01-06T16:43:12.000Z",
            "create_timestamp": "2017-01-06T16:43:12.000Z",
        }

        resource = Resource(fuzion_event_id="123").process_payload(success_payload)

        self.assertEqual(resource.fuzion_event_id, "123")
        self.assertEqual(resource["fuzion_plot_id"], "4444D95146B83C38ABDD4F9C20CA4444")


class TestAbstract(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.abstract = MockResource.new(Abstract(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.abstract.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/abstracts",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.abstract.post(title="the title", category="category")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/abstracts",
            headers={**MockResource.mock_general_headers},
            json={"title": "the title", "category": "category"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.abstract.put(
            fuzion_abstract_id="456", title="new title", category="category"
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/abstracts/456",
            headers=MockResource.mock_general_headers,
            json={"title": "new title", "category": "category"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.abstract.delete(fuzion_abstract_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/abstracts/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestAbstractContact(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.abstract = MockResource.new(
            Abstract(fuzion_event_id="123", fuzion_abstract_id="123")
        )
        self.abstract_contact = MockResource.new(self.abstract.contacts)

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.abstract_contact.post(role_type_code="123")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/abstracts/123/contacts",
            headers=MockResource.mock_general_headers,
            json={"role_type_code": "123"},
        )

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.abstract_contact.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/abstracts/123/contacts",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_update(self, requests):
        self.abstract_contact.put(fuzion_contact_id="456", role_type_code="000")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/abstracts/123/contacts/456",
            headers=MockResource.mock_general_headers,
            json={"role_type_code": "000"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.abstract_contact.delete(fuzion_contact_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/abstracts/123/contacts/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestAbstractDisclosure(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.abstract_disclosure = MockResource.new(
            AbstractDisclosure(fuzion_event_id="123")
        )

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.abstract_disclosure.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/abstract-disclosures",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.abstract_disclosure.post(
            fuzion_abstract_id="123",
            fuzion_contact_id="456",
            name="A name",
            disclosure_text="Text",
            type="AAA",
        )
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/abstract-disclosures",
            headers={**MockResource.mock_general_headers},
            json={
                "fuzion_abstract_id": "123",
                "fuzion_contact_id": "456",
                "name": "A name",
                "disclosure_text": "Text",
                "type": "AAA",
            },
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.abstract_disclosure.put(
            fuzion_abstract_disclosure_id="456", name="new name"
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/abstract-disclosures/456",
            headers=MockResource.mock_general_headers,
            json={"name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.abstract_disclosure.delete(fuzion_abstract_disclosure_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/abstract-disclosures/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestAbstractAffiliation(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.abstract_affiliation = MockResource.new(
            AbstractAffiliation(fuzion_event_id="123")
        )

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.abstract_affiliation.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/abstract-affiliations",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.abstract_affiliation.post(
            fuzion_abstract_id="123",
            fuzion_contact_id="456",
            name="A name",
            description="description",
        )
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/abstract-affiliations",
            headers={**MockResource.mock_general_headers},
            json={
                "fuzion_abstract_id": "123",
                "fuzion_contact_id": "456",
                "name": "A name",
                "description": "description",
            },
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.abstract_affiliation.put(
            fuzion_abstract_affiliation_id="456", name="new name"
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/abstract-affiliations/456",
            headers=MockResource.mock_general_headers,
            json={"name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.abstract_affiliation.delete(fuzion_abstract_affiliation_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/abstract-affiliations/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestAbstractResource(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.abstract_resource = MockResource.new(
            AbstractResource(fuzion_event_id="123")
        )

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.abstract_resource.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/abstract-resources",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.abstract_resource.post(
            fuzion_abstract_id="123", resource_type_flag="1", name="A name"
        )
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/abstract-resources",
            headers={**MockResource.mock_general_headers},
            json={
                "fuzion_abstract_id": "123",
                "resource_type_flag": "1",
                "name": "A name",
            },
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.abstract_resource.put(fuzion_abstract_resource_id="456", name="new name")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/abstract-resources/456",
            headers=MockResource.mock_general_headers,
            json={"name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.abstract_resource.delete(fuzion_abstract_resource_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/abstract-resources/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestAbstractPoster(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.abstract_poster = MockResource.new(AbstractPoster(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.abstract_poster.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/abstract-posters",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.abstract_poster.post(fuzion_abstract_id="123", name="A name")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/abstract-posters",
            headers={**MockResource.mock_general_headers},
            json={"fuzion_abstract_id": "123", "name": "A name"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.abstract_poster.put(fuzion_abstract_poster_id="456", name="new name")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/abstract-posters/456",
            headers=MockResource.mock_general_headers,
            json={"name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.abstract_poster.delete(fuzion_abstract_poster_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/abstract-posters/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestExhibitor(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.exhibitor = MockResource.new(Exhibitor(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.exhibitor.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/exhibitors",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_get(self, requests):
        self.exhibitor.get(fuzion_exhibitor_id="456")
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/exhibitors/456",
            headers=MockResource.mock_general_headers,
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.exhibitor.post(exhibitor_name="name")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/exhibitors",
            headers={**MockResource.mock_general_headers},
            json={"exhibitor_name": "name"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.exhibitor.put(fuzion_exhibitor_id="456", exhibitor_name="new name")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/exhibitors/456",
            headers=MockResource.mock_general_headers,
            json={"exhibitor_name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.exhibitor.delete(fuzion_exhibitor_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/exhibitors/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestExhibitorContact(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.exhibitor = MockResource.new(
            Exhibitor(fuzion_event_id="123", fuzion_exhibitor_id="456")
        )
        self.exhibitor_contact = MockResource.new(self.exhibitor.contacts)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.exhibitor_contact.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/exhibitors/456/contacts",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.exhibitor_contact.post(first_name="name")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/exhibitors/456/contacts",
            headers={**MockResource.mock_general_headers},
            json={"first_name": "name"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.exhibitor_contact.put(fuzion_contact_id="789", first_name="new name")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/exhibitors/456/contacts/789",
            headers=MockResource.mock_general_headers,
            json={"first_name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.exhibitor_contact.delete(fuzion_contact_id="789")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/exhibitors/456/contacts/789",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestExhibitorAddress(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.exhibitor = MockResource.new(
            Exhibitor(fuzion_event_id="123", fuzion_exhibitor_id="456")
        )
        self.exhibitor_address = MockResource.new(self.exhibitor.addresses)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.exhibitor_address.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/exhibitors/456/addresses",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.exhibitor_address.post(country="israel")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/exhibitors/456/addresses",
            headers={**MockResource.mock_general_headers},
            json={"country": "israel"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.exhibitor_address.put(fuzion_address_id="789", country="usa")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/exhibitors/456/addresses/789",
            headers=MockResource.mock_general_headers,
            json={"country": "usa"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.exhibitor_address.delete(fuzion_address_id="789")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/exhibitors/456/addresses/789",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestExhibitorBooth(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.exhibitor = MockResource.new(
            Exhibitor(fuzion_event_id="123", fuzion_exhibitor_id="456")
        )
        self.exhibitor_booth = MockResource.new(self.exhibitor.booths)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.exhibitor_booth.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/exhibitors/456/booths",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.exhibitor_booth.add_existing(fuzion_booth_id="000")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/exhibitors/456/booths/000",
            headers={**MockResource.mock_general_headers},
            json={},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.exhibitor_booth.update_relationship(
            fuzion_booth_id="000", relationship_type_flag=1
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/exhibitors/456/booths/000",
            headers=MockResource.mock_general_headers,
            json={"relationship_type_flag": 1},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.exhibitor_booth.delete_relationship(fuzion_booth_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/exhibitors/456/booths/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestExhibitorThirdParties(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.exhibitor = MockResource.new(
            Exhibitor(fuzion_event_id="123", fuzion_exhibitor_id="456")
        )
        self.exhibitor_tp = MockResource.new(self.exhibitor.third_parties)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.exhibitor_tp.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/exhibitors/456/third-parties",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.exhibitor_tp.add_existing(fuzion_third_party_id="000")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/exhibitors/456/third-parties/000",
            headers={**MockResource.mock_general_headers},
            json={},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.exhibitor_tp.update_relationship(
            fuzion_third_party_id="000", relationship_type_flag=1
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/exhibitors/456/third-parties/000",
            headers=MockResource.mock_general_headers,
            json={"relationship_type_flag": 1},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.exhibitor_tp.delete_relationship(fuzion_third_party_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/exhibitors/456/third-parties/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestBooth(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.booth = MockResource.new(Booth(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.booth.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/booths",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_get(self, requests):
        self.booth.get(fuzion_booth_id="456")
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/booths/456",
            headers=MockResource.mock_general_headers,
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.booth.post(booth_name="name")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/booths",
            headers={**MockResource.mock_general_headers},
            json={"booth_name": "name"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.booth.put(fuzion_booth_id="456", booth_name="new name")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/booths/456",
            headers=MockResource.mock_general_headers,
            json={"booth_name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.booth.delete(fuzion_booth_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/booths/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestBoothContact(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.booth = MockResource.new(
            Booth(fuzion_event_id="123", fuzion_booth_id="456")
        )
        self.booth_contact = MockResource.new(self.booth.contacts)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.booth_contact.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/booths/456/contacts",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.booth_contact.post(first_name="name")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/booths/456/contacts",
            headers={**MockResource.mock_general_headers},
            json={"first_name": "name"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.booth_contact.put(fuzion_contact_id="789", first_name="new name")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/booths/456/contacts/789",
            headers=MockResource.mock_general_headers,
            json={"first_name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.booth_contact.delete(fuzion_contact_id="789")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/booths/456/contacts/789",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestBoothAddress(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.booth = MockResource.new(
            Booth(fuzion_event_id="123", fuzion_booth_id="456")
        )
        self.booth_address = MockResource.new(self.booth.addresses)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.booth_address.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/booths/456/addresses",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.booth_address.post(country="israel")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/booths/456/addresses",
            headers={**MockResource.mock_general_headers},
            json={"country": "israel"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.booth_address.put(fuzion_address_id="789", country="usa")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/booths/456/addresses/789",
            headers=MockResource.mock_general_headers,
            json={"country": "usa"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.booth_address.delete(fuzion_address_id="789")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/booths/456/addresses/789",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestBoothExhibitor(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.booth = MockResource.new(
            Booth(fuzion_event_id="123", fuzion_booth_id="456")
        )
        self.both_exhibitor = MockResource.new(self.booth.exhibitors)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.both_exhibitor.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/booths/456/exhibitors",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )


class TestBoothThirdParty(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.booth = MockResource.new(
            Booth(fuzion_event_id="123", fuzion_booth_id="456")
        )
        self.booth_tp = MockResource.new(self.booth.third_parties)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.booth_tp.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/booths/456/third-parties",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )


class TestThirdParty(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.tp = MockResource.new(ThirdParty(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.tp.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/third-parties",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_get(self, requests):
        self.tp.get(fuzion_third_party_id="456")
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/third-parties/456",
            headers=MockResource.mock_general_headers,
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.tp.post(third_party_name="name")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/third-parties",
            headers={**MockResource.mock_general_headers},
            json={"third_party_name": "name"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.tp.put(fuzion_third_party_id="456", third_party_name="new name")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/third-parties/456",
            headers=MockResource.mock_general_headers,
            json={"third_party_name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.tp.delete(fuzion_third_party_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/third-parties/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestThirdPartyContact(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.tp = MockResource.new(
            ThirdParty(fuzion_event_id="123", fuzion_third_party_id="456")
        )
        self.tp_contact = MockResource.new(self.tp.contacts)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.tp_contact.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/third-parties/456/contacts",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.tp_contact.post(first_name="name")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/third-parties/456/contacts",
            headers={**MockResource.mock_general_headers},
            json={"first_name": "name"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.tp_contact.put(fuzion_contact_id="789", first_name="new name")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/third-parties/456/contacts/789",
            headers=MockResource.mock_general_headers,
            json={"first_name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.tp_contact.delete(fuzion_contact_id="789")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/third-parties/456/contacts/789",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestThirdPartyAddress(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.tp = MockResource.new(
            ThirdParty(fuzion_event_id="123", fuzion_third_party_id="456")
        )
        self.tp_address = MockResource.new(self.tp.addresses)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.tp_address.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/third-parties/456/addresses",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.tp_address.post(country="israel")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/third-parties/456/addresses",
            headers={**MockResource.mock_general_headers},
            json={"country": "israel"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.tp_address.put(fuzion_address_id="789", country="usa")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/third-parties/456/addresses/789",
            headers=MockResource.mock_general_headers,
            json={"country": "usa"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.tp_address.delete(fuzion_address_id="789")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/third-parties/456/addresses/789",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestThirdPartyExhibitor(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.tp = MockResource.new(
            ThirdParty(fuzion_event_id="123", fuzion_third_party_id="456")
        )
        self.tp_exhibitor = MockResource.new(self.tp.exhibitors)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.tp_exhibitor.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/third-parties/456/exhibitors",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )


class TestThirdPartyBooth(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.tp = MockResource.new(
            ThirdParty(fuzion_event_id="123", fuzion_third_party_id="456")
        )
        self.tp_booth = MockResource.new(self.tp.booths)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.tp_booth.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/third-parties/456/booths",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_add_existing(self, requests):
        self.tp_booth.add_existing(fuzion_booth_id="000")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/third-parties/456/booths/000",
            headers={**MockResource.mock_general_headers},
            json={},
        )

    @patch("fuzion.resource.requests")
    def test_update_relationship(self, requests):
        self.tp_booth.update_relationship(
            fuzion_booth_id="000", relationship_confirmation_status_flag=1
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/third-parties/456/booths/000",
            headers=MockResource.mock_general_headers,
            json={"relationship_confirmation_status_flag": 1},
        )

    @patch("fuzion.resource.requests")
    def test_delete_relationship(self, requests):
        self.tp_booth.delete(fuzion_booth_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/third-parties/456/booths/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestExhibitorProduct(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.exhibitor_product = MockResource.new(
            ExhibitorProduct(fuzion_event_id="123")
        )

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.exhibitor_product.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/exhibitor-products",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.exhibitor_product.post(product_name="name", category="category")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/exhibitor-products",
            headers={**MockResource.mock_general_headers},
            json={"product_name": "name", "category": "category"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.exhibitor_product.put(
            fuzion_exhibitor_product_id="456", product_name="new name"
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/exhibitor-products/456",
            headers=MockResource.mock_general_headers,
            json={"product_name": "new name"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.exhibitor_product.delete(fuzion_exhibitor_product_id="456")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/exhibitor-products/456",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestFloorPlan(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.floorplan = MockResource.new(FloorPlan(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.floorplan.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/floorplans",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.floorplan.post(name="name")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/floorplans",
            headers={**MockResource.mock_general_headers},
            json={"name": "name"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.floorplan.put(fuzion_floorplan_id="456", name="new name")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/floorplans/456",
            headers=MockResource.mock_general_headers,
            json={"name": "new name"},
        )


class TestFloorPlanPlot(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.floorplan = MockResource.new(
            FloorPlan(fuzion_event_id="123", fuzion_floorplan_id="456")
        )
        self.floorplan_plots = MockResource.new(self.floorplan.plots)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.floorplan_plots.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/floorplans/456/plots",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )


class TestPlot(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.plot = MockResource.new(Plot(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.plot.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/plots",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.plot.post(fuzion_floorplan_id="123", fuzion_plot_type_id="123")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/plots",
            headers={**MockResource.mock_general_headers},
            json={"fuzion_floorplan_id": "123", "fuzion_plot_type_id": "123"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.plot.put(
            fuzion_plot_id="000", fuzion_floorplan_id="456", fuzion_plot_type_id="123"
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/plots/000",
            headers=MockResource.mock_general_headers,
            json={"fuzion_floorplan_id": "456", "fuzion_plot_type_id": "123"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.plot.delete(fuzion_plot_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/plots/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestPlotObject(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.plot = MockResource.new(Plot(fuzion_event_id="123", fuzion_plot_id="456"))
        self.object = MockResource.new(self.plot.objects)

    @patch("fuzion.resource.requests")
    def test_add_existing(self, requests):
        self.object.add_existing(fuzion_object_id="123")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/plots/456/objects/123",
            headers={**MockResource.mock_general_headers},
            json={},
        )

    @patch("fuzion.resource.requests")
    def test_update_relationship(self, requests):
        self.object.update_relationship(fuzion_object_id="123")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/plots/456/objects/123",
            headers=MockResource.mock_general_headers,
            json={},
        )

    @patch("fuzion.resource.requests")
    def test_delete_relationship(self, requests):
        self.object.delete_relationship(fuzion_object_id="123")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/plots/456/objects/123",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestFloorPlanObject(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.fp_obj = MockResource.new(FloorPlanObject(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.fp_obj.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/floorplan-objects",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.fp_obj.post(fuzion_floorplan_id="123", object_type_code="Floor")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/floorplan-objects",
            headers={**MockResource.mock_general_headers},
            json={"fuzion_floorplan_id": "123", "object_type_code": "Floor"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.fp_obj.put(
            fuzion_floorplan_object_id="000",
            fuzion_floorplan_id="456",
            object_type_code="Wall",
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/floorplan-objects/000",
            headers=MockResource.mock_general_headers,
            json={"fuzion_floorplan_id": "456", "object_type_code": "Wall"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.fp_obj.delete(fuzion_floorplan_object_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/floorplan-objects/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestPlotCategory(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.plot_cat = MockResource.new(PlotCategory(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.plot_cat.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/plot-categories",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.plot_cat.post(fuzion_floorplan_id="123", name="Floor")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/plot-categories",
            headers={**MockResource.mock_general_headers},
            json={"fuzion_floorplan_id": "123", "name": "Floor"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.plot_cat.put(
            fuzion_plot_category_id="000", fuzion_floorplan_id="456", name="Wall"
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/plot-categories/000",
            headers=MockResource.mock_general_headers,
            json={"fuzion_floorplan_id": "456", "name": "Wall"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.plot_cat.delete(fuzion_plot_category_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/plot-categories/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestPlotCategoryPlot(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.plot_cat = MockResource.new(
            PlotCategory(fuzion_event_id="123", fuzion_plot_category_id="123")
        )
        self.plot = MockResource.new(self.plot_cat.plots)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.plot.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/plot-categories/123/plots",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )


class TestPlotType(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.plot_type = MockResource.new(PlotType(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.plot_type.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/plot-types",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.plot_type.post(fuzion_floorplan_id="123", name="Floor")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/plot-types",
            headers={**MockResource.mock_general_headers},
            json={"fuzion_floorplan_id": "123", "name": "Floor"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.plot_type.put(
            fuzion_plot_type_id="000", fuzion_floorplan_id="456", name="Wall"
        )
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/plot-types/000",
            headers=MockResource.mock_general_headers,
            json={"fuzion_floorplan_id": "456", "name": "Wall"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.plot_type.delete(fuzion_plot_type_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/plot-types/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestPlotTypePlot(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.plot_type = MockResource.new(
            PlotType(fuzion_event_id="123", fuzion_plot_type_id="123")
        )
        self.plot = MockResource.new(self.plot_type.plots)

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.plot.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/plot-types/123/plots",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )


class TestAttendee(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.attendee = MockResource.new(Attendee(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.attendee.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/attendees",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.attendee.post(registration_number="123")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/attendees",
            headers={**MockResource.mock_general_headers},
            json={"registration_number": "123"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.attendee.put(fuzion_attendee_id="000", registration_number="456")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/attendees/000",
            headers=MockResource.mock_general_headers,
            json={"registration_number": "456"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.attendee.delete(fuzion_attendee_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/attendees/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestOption(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.option = MockResource.new(Option(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.option.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/attendee-options",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.option.post(option_code="123")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/attendee-options",
            headers={**MockResource.mock_general_headers},
            json={"option_code": "123"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.option.put(fuzion_option_id="000", option_code="456")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/attendee-options/000",
            headers=MockResource.mock_general_headers,
            json={"option_code": "456"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.option.delete(fuzion_option_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/attendee-options/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestSurvey(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.survey = MockResource.new(Survey(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.survey.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/attendee-surveys",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.survey.post(question_id="123")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/attendee-surveys",
            headers={**MockResource.mock_general_headers},
            json={"question_id": "123"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.survey.put(fuzion_survey_id="000", question_id="456")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/attendee-surveys/000",
            headers=MockResource.mock_general_headers,
            json={"question_id": "456"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.survey.delete(fuzion_survey_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/attendee-surveys/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestTransaction(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.transaction = MockResource.new(Transaction(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.transaction.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/attendee-transactions",
            headers={
                **MockResource.mock_general_headers,
                **{"page_size": "500", "start": "0"},
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.transaction.post(option_code="123")
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/attendee-transactions",
            headers={**MockResource.mock_general_headers},
            json={"option_code": "123"},
        )

    @patch("fuzion.resource.requests")
    def test_put(self, requests):
        self.transaction.put(fuzion_transaction_id="000", option_code="456")
        requests.request.assert_called_with(
            "put",
            "https://fuzionapi.com/v1/attendee-transactions/000",
            headers=MockResource.mock_general_headers,
            json={"option_code": "456"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.transaction.delete(fuzion_transaction_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/attendee-transactions/000",
            headers=MockResource.mock_general_headers,
            json={},
        )
        

class TestNotificationWebhook(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.notification_wh = MockResource.new(NotificationWebhook(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.notification_wh.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/notification-webhooks",
            headers={
                **MockResource.mock_general_headers,
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.notification_wh.post(callback_url="https://mycallback.com/fuzion/", 
                                  entity_type="attendee", 
                                  entity_operation="insert")
        
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/notification-webhooks",
            headers={**MockResource.mock_general_headers},
            json={"callback_url": "https://mycallback.com/fuzion/", 
                  "entity_type": "attendee", 
                  "entity_operation": "insert"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.notification_wh.delete(fuzion_webhook_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/notification-webhooks/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


class TestErrorWebhook(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.error_wh = MockResource.new(ErrorWebhook(fuzion_event_id="123"))

    @patch("fuzion.resource.requests")
    def test_query(self, requests):
        self.error_wh.query()
        requests.request.assert_called_with(
            "get",
            "https://fuzionapi.com/v1/errors-webhooks",
            headers={
                **MockResource.mock_general_headers,
            },
            params={},
        )

    @patch("fuzion.resource.requests")
    def test_post(self, requests):
        self.error_wh.post(callback_url="https://mycallback.com/fuzion/")
        
        requests.request.assert_called_with(
            "post",
            "https://fuzionapi.com/v1/errors-webhooks",
            headers={**MockResource.mock_general_headers},
            json={"callback_url": "https://mycallback.com/fuzion/"},
        )

    @patch("fuzion.resource.requests")
    def test_delete(self, requests):
        self.error_wh.delete(fuzion_webhook_id="000")
        requests.request.assert_called_with(
            "delete",
            "https://fuzionapi.com/v1/errors-webhooks/000",
            headers=MockResource.mock_general_headers,
            json={},
        )


if __name__ == "__main__":
    unittest.main()
