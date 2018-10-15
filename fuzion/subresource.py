from fuzion.resource import Resource
from fuzion.exceptions import ImproperlyConfigured, ObjectIdMissingError
from fuzion.mixins import UpdateObjectMixin, DestroyObjectMixin


class SubResource(Resource):
    """
    A special case of `Resource`.
    When a certain Resource has nested objects it instantiate an instance of this class
    by providing the `parent_object` that will be used, with its object id attribute to
    perform requests.
    
    The path attribute must be in the format of: 
    `path = "parent_object_endpoint/{}/child_object_endpoint"` (i.e. "exhibitors/{}/booths")
    This allows the path to be dynamically constructed with the `parent_object.internal_object_id`
    so:
    `Exhibitor(fuzion_event_id="123", fuzion_exhibitor_id="E123").booth`
    
    generates a path of `exhibitors/E123/booths`
    """

    path = None
    parent_object = None

    def __init__(self, *args, **kwargs):
        self.parent_object = kwargs.pop("parent_object", None)
        if self.parent_object is None:
            raise ImproperlyConfigured(
                "parent_object is expected but missing in __init__ method of {}".format(
                    self.__class__.__name__
                )
            )

        if self.parent_object.fuzion_event_id not in args:
            kwargs.setdefault("fuzion_event_id", self.parent_object.fuzion_event_id)
        Resource.__init__(self, *args, **kwargs)

        self.path = self.path.format(self.parent_object.internal_object_id)

    def process_payload(self, payload):
        """ 
        Special case, we need to use the parent_object as well to construct the new instance/s
        """
        return self.__class__.new(
            self.fuzion_event_id, payload, parent_object=self.parent_object
        )


class Relationship(UpdateObjectMixin, DestroyObjectMixin, SubResource):
    """
    Special case of SubResource where the `post` endpoint needs to use an existing
    sub-object id.
    
    provides `add_existing`, `update_relationship`, `delete_relationship` as a minimum
    """

    def add_existing(self, **values):
        # "create" becomes "add existing", which is a POST call
        # with the object id already provided
        object_id = self._extract_object_id(values)
        if object_id is None:
            raise ObjectIdMissingError(
                "{} attribute was not set nor provided".format(self.object_id_attr_name)
            )

        path = self.path + "/" + object_id

        return self._request(method="post", path=path, values=values)

    def update_relationship(self, **values):
        return self.put(**values)

    def delete_relationship(self, **values):
        return self.delete(**values)
