Dynamic Model API
=================

The Dynamic Model API is a Django application that allows you to create and manage dynamic database models at runtime. It provides endpoints for creating and updating dynamic models, as well as performing CREATE and GET operations on the data stored in those models.

Getting Started
---------------

To set up the Dynamic Model API using Docker Compose, follow these steps:

1.  Clone the repository: `git clone <repository-url>`
2.  Create a `.env` file based on the `.env.template` file and provide the necessary environment variables.
3.  Run `docker-compose up` to start the services.

The API will be accessible at `http://localhost:8000/`.

API Endpoints
-------------

### Dynamic Models

*   `GET /api/table/`: Retrieve a list of all dynamic models.
*   `POST /api/table/`: Create a new dynamic model.
*   `GET /api/table/{pk}/`: Retrieve details of a specific dynamic model.
*   `PUT /api/table/{pk}/`: Update a dynamic model.

### Dynamic Model Rows

*   `GET /api/table/{pk}/rows/`: Retrieve all rows (objects) of a dynamic model.
*   `POST /api/table/{pk}/row/`: Create a new row (object) in a dynamic model.

Dynamic Model Structure
-----------------------

A dynamic model consists of a name and a list of fields. Each field has a name and a type, which can be one of the following choices: `string`, `number`, or `boolean`.

Example request body for creating a dynamic model:

```json
{
  "name": "Book",
  "fields": [
    {"name": "title", "type": "string"},
    {"name": "author", "type": "string"},
    {"name": "price", "type": "number"},
    {"name": "is_published", "type": "boolean"}
  ]
}
```


Customization
-------------

The Dynamic Model API provides extensibility points for customization. You can modify the `FIELDS_MAP` dictionary in the `DynamicModelService` class to add or modify field types available for dynamic models. The existing field types are `string`, `number`, and `boolean`.

```python
class DynamicModelService:     
    FIELDS_MAP: Dict[str, Type[models.Field]] = {
        'string': models.TextField,
        'number': models.FloatField,
        'boolean': models.BooleanField,
        'date': models.DateField,  # Example custom field type     
    }
```

Docker Compose
--------------

The provided `docker-compose.yml` file defines two services: `database` and `application`. The `database` service runs a PostgreSQL container, and the `application` service runs the Dynamic Model API application.

Ensure that you have Docker and Docker Compose installed on your machine. Then, run `docker-compose up` to start the services.

Environment Variables
---------------------

The `.env` file contains the required environment variables for the application and database services. Customize these variables according to your needs:


```
DEBUG=true 
SECRET_KEY=django-insecure-%2#5xeecm3af=2(3*(jjhc-8v8=*ovmmo3w+13yp5d3sa(7vke  

POSTGRES_DB=api 
POSTGRES_USER=api 
POSTGRES_PASSWORD=api 
POSTGRES_HOST=database 
POSTGRES_PORT=5432
```

Usage
-----

1.  Create a dynamic model by sending a POST request to `/api/table/` with the desired model structure.
2.  Once a dynamic model is created, you can use the `row` action to perform CREATE operations on the model's data, and `rows` for GET operations.

