from fuzion.resource import Resource
from fuzion.exceptions import ImproperlyConfigured, ObjectIdMissingError
from fuzion.mixins import UpdateObjectMixin,\
    DestroyObjectMixin

class SubResource(Resource):
    path = None
    parent_object = None
    
    def _set_path(self):
        raise NotImplementedError()
        
    def __init__(self, *args, **kwargs):
        self.parent_object = kwargs.pop("parent_object", None)
        if self.parent_object is None:
            raise ImproperlyConfigured(f"parent_object is expected but missing in __init__ method of {self.__class__.__name__}")
        
        kwargs.setdefault("fuzion_event_id", self.parent_object.fuzion_event_id)
        Resource.__init__(self, *args, **kwargs)
        
        self._set_path()
        
        
class Relationship(UpdateObjectMixin, 
                   DestroyObjectMixin, SubResource):
    def add_existing(self, **values):
        # "create" becomes "add existing", which is a POST call
        # with the object id already provided 
        object_id = self._extract_object_id(values)
        if object_id is None:
            raise ObjectIdMissingError(f"{self.object_id_attr_name} attribute was not set nor provided")
        
        path = self.path + "/" + object_id
        
        return self._request(method="post", 
                           path=path, 
                           values=values)
    
    def update_relationship(self, **values):
        return self.put(**values)
    
    def delete_relationship(self, **values):
        return self.delete(**values)