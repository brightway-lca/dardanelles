# dardanelles

## Table of Contents

- [Background](#background)
- [Installation](#installation)
- [Client](#client)
- [Server](#server)
- [Contributing](#contributing)
- [Maintainers](#maintainers)
- [License](#license)

## Background

## Concepts

## Installation

## Client

## Server

`dardanelles` is also a web service for LCI data exchange. The default URL is [lci.brightway.dev](https://lci.brightway.dev), but you can run your own server. The server uses [flask](https://flask.palletsprojects.com/en/2.2.x/).

### Running the web service

Run the ``flask`` application any way you want. For example, to run the test server (not in production!), do:

.. code-block:: bash

    export FLASK_APP=/path/to/dardanelles/__init__.py
    flask run

### API endpoints

The following API endpoints are supported:

#### `/`

Ping the server. Returns something like ``dardanelles life cycle inventory web data exchange, version (0, 1)``.

HTTP method: **GET**

#### `/catalog`

Get the list of datasets available

HTTP method: **GET**

*Response*

* 200: Return a JSON payload of the form:

```javascript

    [
        ('file name', 'database name', 'hex-encoded sha256 hash of file'),
    ]
```

#### /upload

Upload a datapackage.

HTTP method: **POST**

*Parameters*

Post the following required form data:

* ``name``: File name
* ``sha256``: SHA 256 hash of file

The file should be in the field ``file``.

*Responses*

* 201: The file was uploaded and registered. Returns a JSON payload:

```javascript

    {
        'filename': 'some file name',
        'database name': 'reported name of the database',
        'sha256': 'hex-encoded sha256 hash of file contents'
    }
```

* 400: The request form was missing a required field
* 406: The input data was invalid (either the hash wasn't correct or the file isn't readable)
* 409: File already exists
* 413: The uploaded file was too large (current limit is 250 MB)

#### /download

Request the download of the file.

HTTP method: **POST**

*Parameters*

Post the following form data:

* ``hash``: SHA 256 hash of the file

*Responses*

* 200: The requested file will be returned
* 400: The request form was missing a required field
* 404: A file for this hash was not found

## Contributing

Your contribution is welcome! Please follow the [pull request workflow](https://guides.github.com/introduction/flow/), even for minor changes.

When contributing to this repository with a major change, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository.

Please note we have a [code of conduct](https://github.com/brightway-lca/dardanelles/blob/master/CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

### Documentation and coding standards

* [Black formatting](https://black.readthedocs.io/en/stable/)
* [isort formatting](https://pycqa.github.io/isort/)
* [Semantic versioning](http://semver.org/)

## Maintainers

* [Chris Mutel](https://github.com/cmutel/)

## License

[BSD-3-Clause](https://github.com/brightway-lca/dardanelles/blob/master/LICENSE).




