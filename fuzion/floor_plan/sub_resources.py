from fuzion.mixins import ListObjectsMixin
from fuzion.subresource import SubResource, Relationship


class FloorPlanPlot(ListObjectsMixin, SubResource):
    path = "floorplans/{}/plots"


class PlotCategoryPlot(ListObjectsMixin, SubResource):
    path = "plot-categories/{}/plots"


class PlotTypePlot(ListObjectsMixin, SubResource):
    path = "plot-types/{}/plots"


class PlotObject(Relationship):
    path = "plots/{}/objects"
    object_id_attr_name = "fuzion_object_id"
