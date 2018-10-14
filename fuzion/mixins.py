from fuzion.exceptions import ObjectIdMissingError


class RetrieveObjectMixin():
    def get(self, **values):
        object_id = self._extract_object_id(values)
        if object_id is None:
            raise ObjectIdMissingError(f"{self.object_id_attr_name} attribute was not set nor provided")
        
        path = self.path + "/" + object_id
        
        return self._request(method="get", 
                           path=path,
                           values=values
                           )


class ListObjectsMixin():
    def query(self, page_size=500, start=0, **values):
        page_size = page_size or 500
        start = start or 0
        
        return self._request(method="get", 
                           path=self.path, 
                           values=values, 
                           paging={
                               "page_size": str(page_size), 
                               "start": str(start)
                            })


class CreateObjectMixin():
    def post(self, **values):
        return self._request(method="post", 
                           path=self.path, 
                           values=values)


class UpdateObjectMixin():
    def put(self, **values):
        object_id = self._extract_object_id(values)
        if object_id is None:
            raise ObjectIdMissingError(f"{self.object_id_attr_name} attribute was not set nor provided")
        
        path = self.path + "/" + object_id
        
        return self._request(method="put", 
                           path=path, 
                           values=values)


class DestroyObjectMixin():
    def delete(self, **values):
        object_id = self._extract_object_id(values)
        if object_id is None:
            raise ObjectIdMissingError(f"{self.object_id_attr_name} attribute was not set nor provided")
        
        path = self.path + "/" + object_id
        
        return self._request(method="delete", 
                           path=path, 
                           values=values)
        
        
class RetrieveNotSupportedMixin(ListObjectsMixin, 
                                CreateObjectMixin, 
                                UpdateObjectMixin, 
                                DestroyObjectMixin):
    pass


class AllCRUDMixin(ListObjectsMixin, 
                   CreateObjectMixin, 
                   RetrieveObjectMixin, 
                   UpdateObjectMixin, 
                   DestroyObjectMixin):
    pass