from fuzion.mixins import ListObjectsMixin
from fuzion.subresource import SubResource, Relationship

class FloorPlanPlot(ListObjectsMixin, SubResource):    
    def _set_path(self):
        self.path = f"floorplans/{self.parent_object.floorplan_id}/plots"
        
        
class PlotCategoryPlot(ListObjectsMixin, SubResource):
    def _set_path(self):
        self.path = f"plot-categories/{self.parent_object.plot_category_id}/plots"
        

class PlotTypePlot(ListObjectsMixin, SubResource):
    def _set_path(self):
        self.path = f"plot-types/{self.parent_object.plot_type_id}/plots"
        

class PlotObject(Relationship):
    object_id_attr_name = "object_id"
    
    def _set_path(self):
        self.path = f"plots/{self.parent_object.plot_id}/objects"
    