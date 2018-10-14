from fuzion.resource import Resource
from fuzion.mixins import ListObjectsMixin, CreateObjectMixin,\
    UpdateObjectMixin, RetrieveNotSupportedMixin
from fuzion.exceptions import ObjectIdMissingError
from fuzion.floor_plan.sub_resources import FloorPlanPlot, PlotObject,\
    PlotCategoryPlot, PlotTypePlot

class FloorPlan(ListObjectsMixin, CreateObjectMixin, 
                UpdateObjectMixin, Resource):
    path = "floorplans"
    object_id_attr_name = "floorplan_id"
    
    @property
    def plots(self):
        if self.floorplan_id:
            return FloorPlanPlot(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    
    
class Plot(RetrieveNotSupportedMixin, Resource):
    path = "plots"
    object_id_attr_name = "plot_id"
    
    @property
    def objects(self):
        if self.plot_id:
            return PlotObject(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
        

class FloorPlanObject(RetrieveNotSupportedMixin, Resource):
    path = "floorplan-objects"
    object_id_attr_name = "floorplan_object_id"
    
    
class PlotCategory(RetrieveNotSupportedMixin, Resource):
    path = "plot-categories"
    object_id_attr_name = "plot_category_id"
    
    @property
    def plots(self):
        if self.plot_category_id:
            return PlotCategoryPlot(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")
    

class PlotType(RetrieveNotSupportedMixin, Resource):
    path = "plot-types"
    object_id_attr_name = "plot_type_id"
    
    @property
    def plots(self):
        if self.plot_type_id:
            return PlotTypePlot(parent_object=self)
        raise ObjectIdMissingError(f"`{self.object_id_attr_name}` attribute is not set")