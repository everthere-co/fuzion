"""
Python API for Freeman's Fuzion

All Objects inherit from Resource which takes care of making the actual calls.

See the `Resource` object doc-string for more details.

Usage:
-----
from fuzion import Attendee, Exhibitor

# Regular object, having the normal CRUD operations
attendees = Attendee(fuzion_event_id="123").query()
attendee = attendees[0]
updated_attendee = attendee.put(first_name="John", last_name="Doe")
updated_attendee.delete()

# We don't have to fetch the actual data before using update/delete
attendee = Attendee(fuzion_event_id="123", fuzion_attendee_id="A123")
attendee.update(first_name="James")
attendee.delete()

# Objects having nested, fully CRUD operations
exhibitor = Exhibitor(fuzion_event_id="123").get(fuzion_exhibitor_id="A123")
contacts = exhibitor.contacts.query()
new_contact = exhibitor.contacts.post(first_name="John", last_name="Doe")
updated_contact = new_contact.update(first_name="Joe")
updated_contact.delete()

# As with normal objects, before using nested objects we don't have to 
# fetch the parent object from the server
exhibitor = Exhibitor(fuzion_event_id="123", fuzion_exhibitor_id="A123")
contacts = exhibitor.contacts.query()

# Objects having nested "relationships", 
# where a POST is adding an existing object, not creating a new one
# such as exhibitors/{fuzion_exhibitor_id}/booths
exhibitor.booths.add_existing(fuzion_booth_id="B456")
exhibitor.booths.delete_relationship(fuzion_booth_id="B456")

@author: Gabriel Amram, VP R&D @ Everthere.co
"""

import os
from fuzion.registration import Attendee, Option, Survey, Transaction
from fuzion.abstract import (
    Abstract,
    AbstractAffiliation,
    AbstractDisclosure,
    AbstractPoster,
    AbstractResource,
)
from fuzion.exhibitor import Booth, Exhibitor, ExhibitorProduct, ThirdParty
from fuzion.floor_plan import FloorPlan, FloorPlanObject, Plot, PlotCategory, PlotType
from fuzion.resource import Resource


api_key = os.getenv("FUZION_API_KEY", None)
api_secret_key = os.getenv("FUZION_API_SECRET_KEY", None)
