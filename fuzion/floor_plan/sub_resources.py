from fuzion.mixins import ListObjectsPaginationMixin
from fuzion.subresource import SubResource, Relationship


class FloorPlanPlot(ListObjectsPaginationMixin, SubResource):
    path = "floorplans/{}/plots"


class PlotCategoryPlot(ListObjectsPaginationMixin, SubResource):
    path = "plot-categories/{}/plots"


class PlotTypePlot(ListObjectsPaginationMixin, SubResource):
    path = "plot-types/{}/plots"


class PlotObject(Relationship):
    path = "plots/{}/objects"
    object_id_attr_name = "fuzion_object_id"
