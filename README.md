# fuzion
Python package as API for Freeman's Fuzion


## Basic Usage:
```
import fuzion

# Defaults to os environment variables FUZION_API_KEY and FUZION_API_SECRET_KEY respectively
fuzion.api_key = "1234567890"
fuzion.api_secret_key = "1234567890"

from fuzion import Attendee
data = Attendee(fuzion_event_id=123).query() # "data" is now a python list of dicts

attendee = Attendee(fuzion_event_id=123).get(attendee_id=123) # "data" is not a python dict with the attendee data

# credentials can also be set per-object
attendee = Attendee(fuzion_event_id=123, api_key="1234567890", api_secret_key="1234567890").post(registration_number="1234")


# Objects with sub-resources, such as contacts:
from fuzion import Exhibitor
exhibitor = Exhibitor(fuzion_event_id=123).get(exhibitor_id=123)
contacts = exhibitor.contacts.query()


# Objects with relationships, such as exhibitors booth where one normally adds
# an existing object, updates the relationship attributes or deletes the relationship:
from fuzion import Exhibitor
exhibitor = Exhibitor(fuzion_event_id=123).get(exhibitor_id=123)

# add existing booth to exhibitor
exhibitor.booths.add_existing(booth_id=456)

# update relationship
exhibitor.booths.update_relationship(booth_id=456, relationship_type_flag=1, relationship_confirmation_status_flag=2)

# delete relationship
exhibitor.booths.delete_relationship(booth_id=456)


# You don't have to fetch the whole data from the server before accessing sub-resources/relationships
exhibitor = Exhibitor(fuzion_event_id=123, exhibitor_id=123)
exhibitor.third_parties.query()
```


## The working pieces:
### Resource
Everything starts with the `Resource` class which every other resource derives from.
This class takes care of building the requests themselves, setting the partner request signature etc.

#### Attributes:
`path` : the api path the resource calls (i.e. "attendees")
`host` : "fuzionapi.com"
`scheme` : "https"
`object_id_attr_name` : the resource-specific name for the object idenfitied (i.e. "attendee_id")

#### Notable Methods:
`__init__` : Requires at least the `fuzion_event_id`
             One can also set the `api_key` and `api_secret_key` attributes here for each resource.
             Accepts the corresponding `object_id_attr_name` to set the instance to (i.e. "attendee_id" kwarg will set the instance's `attendee_id` attribute accordingly)
`_request` : Makes the request according to the path, method and payload. Generates the signatures accordingly.

### SubResource
A SubResource builds its `path` dynamically according to a `parent_object`. 
Inheriting classes are aware of the `parent_object` passed and can use it to build the `path` accordingly

### Relationship
A SubResource that exposes `add_existing`, `update_relationship` and `delete_relationship`.
It is special because it cannot use the normal "POST" method as `add_existing` passes an object id in the path

### RetrieveObjectMixin
Exposes the `get` method (to retrieve an object with a specific id) 

### ListObjectsMixin
Exposes the `query` method, used to retrieve a list of objects.
Provides paging by accepting the `page_size` and `start` parameters:

```
Attendee(fuzion_event_id=123).query(page_size=250, start=2)
```

If these paramters are ommited they default to `page_size=500` and `start=0`

### CreateObjectMixin
Exposes the `post` method, used to create a new object
Attributes to be used as the request body are sent as kwargs, such as:

```
Poster(fuzion_event_id=123).post(fuzion_abstract_id=123456, name="New poster", description="The poster's description")
```

Nested attributes should be dicts:

```
Attendee(fuzion_event_id=123).post(registration_number=1234567890, contact={"first_name": "John", "last_name": "Doe"})
```

### UpdateObjectMixin
Exposes the `put` method, used to update an existing object.
Expects the resource specific object id attribute to be either set on class level or supplied in this call:

```
Exhibitor(fuzion_event_id=123).put(exhibitor_id=456, exhibitor_name="The new name")

# or 

Exhibitor(fuzion_event_id=123, exhibitor_id=456).put(exhibitor_name="The new name")
``` 

### DestroyObjectMixin
Exposes the `delete` method, used to delete an existing object
As the `update` method also expect the object id attribute to be set or sent

### RetrieveNotSupportedMixin
A convenience mixin that groups `ListObjectsMixin`, `CreateObjectMixin`, `UpdateObjectMixin`, `DestroyObjectMixin`
together. All BUT the `RetrieveObjectMixin`

### AllCRUDMixin
A convenience mixin that groups `ListObjectsMixin`, `CreateObjectMixin`, `UpdateObjectMixin`, `DestroyObjectMixin`
WITH `RetrieveObjectMixin`



## When things go wrong...
### Exceptions
HTTP errors will be raised accordingly as `RequestException` (such as `ConnectionError`)

If the request itself is a valid HTTP request and Fuzion are the one returning the error
a `FuzionError` is raised, one of:
- `BadRequestError`
- `UnauthorizedError`
- `NotFoundError`
- `PayloadTooLargeError`
- `TooManyRequestsError`
- `InternalServerError`
- `ResourceUnavailableError`

All these exception classes provide the `status`, `reason`, `message` (as provided by Fuzion)
and the original `request` and `response` objects

If a certain call required the object id to be set (such as `update`) a `ObjectIdMissingError` will be thrown

