from fuzion.resource import Resource
from fuzion.mixins import (
    ListObjectsMixin,
    CreateObjectMixin,
    UpdateObjectMixin,
    RetrieveNotSupportedMixin,
)
from fuzion.exceptions import ObjectIdMissingError
from fuzion.floor_plan.sub_resources import (
    FloorPlanPlot,
    PlotObject,
    PlotCategoryPlot,
    PlotTypePlot,
)
from fuzion.decorators import has_object_id_set


class FloorPlan(ListObjectsMixin, CreateObjectMixin, UpdateObjectMixin, Resource):
    path = "floorplans"
    object_id_attr_name = "fuzion_floorplan_id"

    @property
    @has_object_id_set
    def plots(self):
        return FloorPlanPlot(parent_object=self)


class Plot(RetrieveNotSupportedMixin, Resource):
    path = "plots"
    object_id_attr_name = "fuzion_plot_id"

    @property
    @has_object_id_set
    def objects(self):
        return PlotObject(parent_object=self)


class FloorPlanObject(RetrieveNotSupportedMixin, Resource):
    path = "floorplan-objects"
    object_id_attr_name = "fuzion_floorplan_object_id"


class PlotCategory(RetrieveNotSupportedMixin, Resource):
    path = "plot-categories"
    object_id_attr_name = "fuzion_plot_category_id"

    @property
    @has_object_id_set
    def plots(self):
        return PlotCategoryPlot(parent_object=self)


class PlotType(RetrieveNotSupportedMixin, Resource):
    path = "plot-types"
    object_id_attr_name = "fuzion_plot_type_id"

    @property
    @has_object_id_set
    def plots(self):
        return PlotTypePlot(parent_object=self)
