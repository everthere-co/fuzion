from fuzion.exceptions import ObjectIdMissingError


class RetrieveObjectMixin:
    """
    Provides retrieving a single-object with GET
    """

    def get(self, **values):
        object_id = self._extract_object_id(values)
        if object_id is None:
            raise ObjectIdMissingError(
                "{} attribute was not set nor provided".format(self.object_id_attr_name)
            )

        path = self.path + "/" + object_id

        return self._request(method="get", path=path, values=values)


class ListObjectsMixin:
    """
    Provides retrieving multiple objects with GET
    """

    def query(self, **values):
        return self._request(
            method="get",
            path=self.path,
            values=values,
            paging={},
        )


class ListObjectsPaginationMixin:
    """
    Provides retrieving multiple objects with GET with pagination enabled
    """
    
    def query(self, page_size=500, start=0, **values):
        page_size = page_size or 500
        start = start or 0

        return self._request(
            method="get",
            path=self.path,
            values=values,
            paging={"page_size": str(page_size), "start": str(start)},
        )


class CreateObjectMixin:
    """
    Provides creating a new object with POST
    """

    def post(self, **values):
        return self._request(method="post", path=self.path, values=values)


class UpdateObjectMixin:
    """
    Provides updating an existing object with PUT
    """

    def put(self, **values):
        object_id = self._extract_object_id(values)
        if object_id is None:
            raise ObjectIdMissingError(
                "{} attribute was not set nor provided".format(self.object_id_attr_name)
            )

        path = self.path + "/" + object_id

        return self._request(method="put", path=path, values=values)


class DestroyObjectMixin:
    """
    Provides deleting an existing object with DELETE
    """

    def delete(self, **values):
        object_id = self._extract_object_id(values)
        if object_id is None:
            raise ObjectIdMissingError(
                "{} attribute was not set nor provided".format(self.object_id_attr_name)
            )

        path = self.path + "/" + object_id

        return self._request(method="delete", path=path, values=values)


class RetrieveNotSupportedMixin(
    ListObjectsPaginationMixin, CreateObjectMixin, UpdateObjectMixin, DestroyObjectMixin
):
    """
    Convenienve mixin that groups all but the retrieving a single object option
    """

    pass


class AllCRUDMixin(
    ListObjectsPaginationMixin,
    CreateObjectMixin,
    RetrieveObjectMixin,
    UpdateObjectMixin,
    DestroyObjectMixin,
):
    """
    Convenienve mixin that groups all actions
    """

    pass
