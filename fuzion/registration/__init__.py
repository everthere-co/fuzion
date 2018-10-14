from fuzion.resource import Resource
from fuzion.mixins import RetrieveNotSupportedMixin

class Attendee(RetrieveNotSupportedMixin, Resource):
    path = 'attendees'
    object_id_attr_name = "attendee_id"
    

class Option(RetrieveNotSupportedMixin, Resource):
    path = 'attendee-option'
    object_id_attr_name = "attendee_option_id"
    

class Survey(RetrieveNotSupportedMixin, Resource):
    path = "attendee-surveys"
    object_id_attr_name = "attendee_survey_id"
    

class Transaction(RetrieveNotSupportedMixin, Resource):
    path = "attendee-transactions"
    object_id_attr_name = "attendee_transaction_id"