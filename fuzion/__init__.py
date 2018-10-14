import os
from fuzion.registration import Attendee, Option, Survey, Transaction
from fuzion.abstract import Abstract, AbstractAffiliation, AbstractDisclosure, AbstractPoster, AbstractResource
from fuzion.exhibitor import Booth, Exhibitor, ExhibitorProduct, ThirdParty
from fuzion.floor_plan import FloorPlan, FloorPlanObject, Plot, PlotCategory, PlotType 
 

api_key = os.getenv("FUZION_API_KEY", None)
api_secret_key = os.getenv("FUZION_SECRET_API_KEY", None)