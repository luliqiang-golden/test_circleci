# seed-to-sale-api

## Installation
Setting up the api and database can be done through Docker.

1. First, install docker and docker-compose.
1. Git clone this repository.
1. Copy `.env.sample` to `.env` and edit the necessary fields.
1. Copy `.dockerenv.sample` to `.dockerenv`.
1. Startup the API and DB with `docker-compose up`.

You can find addicional information on Confluence: [Setup on Docker](https://wilcompute.atlassian.net/wiki/spaces/SEED/pages/271450115/Setup+with+Docker).

## Branches
- Development: all features branch off and are merged back here
- Test: for internal and client QA
- Master: for production code

## VSCode Tasks
Run tasks in the .vscode folder to start your back end server for local development
`CTRL+SHIFT+P > Run Task`

## Postman
A postman collection (`S2S API.postman_collection.json`) is included in this repository. It is updated as endpoints are added with examples and utilties for interacting with the API. In the collection settings are two base urls: cloud and local. You can change between them by setting the base_url variable to point to either base_url_cloud or base_url_local

### First step: create an environment
There are scripts in the Postman collection that will automatically update the access_token required to access API resources. You must create an environment and add a "token" variable (it can be empty). You must then select that environment to be active before following the second step below. 

### Second step: send the Get Auth0 Access Token request
This request will log you in through Auth0 and save the access_token to the `token` environment variable. This token will then be available to any requests that need it. You can see how to use the variable by looking at the authorization information in the API request examples.

## Testing

You can use `pytest` to run all the tests at once, or instead run them individually like `python tests/test_api_roles.py`. The tests rely on having a `seed-to-sale-test` database that is created empty. To create all tables and objects necessary to run the tests, it is necessary to run the command `pipenv run setup-db-test` to create the structure for the first time. After that, run this command again just to update the structure with new migrations if necessary. Otherwise, execute the tests normally, how explained before.

To see this configuration in more details, visit [this page](https://wilcompute.atlassian.net/wiki/spaces/SEED/pages/2407366675/Setup+test+database+in+local+environment) in our confluence.

A test coverage report can be generated with this command: `py.test --cov=python_scripts tests/`

## Deployment

We use Google Cloud app engine for the deployment. You will need `gcloud` on your machine or your CI server.
Deployment configuration files are kept in the python_secrets folder and named `app-dev.yaml`, `app-prod.yaml`, and `.env`. The `.env` file is not kept in the repository. Note that this `.env` file is separate from the .env file that may be in the root of the repository for local development.

Within our App Engine, we have a 'default' service (for the api). All requests to `*.groweriq.ca` that are not matched to a specific service and or version will go to the default service and be split among all versions receiving requests.

Within our 'default' service, we have our latest version and our dev version. The deploy commands are below, they must be run inside the python_scripts folder:

### Dev Deployment
This is best handled by the Bitbucket Pipeline service!
```
gcloud app deploy app-dev.yaml --version dev --no-promote
```

It is not necessary to run the dev deployment all the time. You can start and stop it with these commands:
```
gcloud app versions stop dev
gcloud app versions start dev
```

### Custom Deployment
If you want to test a feature in development, you can do so by running the following command. Replace `test` with a description of the work you're doing. Be sure to stop and delete your version when you're done.

```
gcloud app deploy app-dev.yaml --version test --no-promote
```

### Production Deployment
(Make sure the .env file has been created in python_scripts.)
```
gcloud app deploy app-prod.yaml --no-stop-previous-version
```

Once the production deployment succeeds, it will take over traffic from the old version, which will be stopped
