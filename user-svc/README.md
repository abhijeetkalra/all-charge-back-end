# hello world backend API

This docs describes the backend API development and deployment.

## Setup development environment

You can setup development environment in local or using docker-compose

### Local environment

This project require Python 3.7 environment.

For local development, please install dependencies by running
```shell
pip insatll -r src/requirements/dev.txt
```

The API services uses MongoDB, so you need to start MongoDB before starting API backend.

All the configurable parameters are under `src/config/default.py`, you can set parameters for different environment in
`development.py` and `production.py`

After MongoDb is started, please set the following configurations to your MongoDB credentials in `developmemt.py` or environment variables


```python
MONGODB_HOST = "localhost"

MONGODB_PORT = 27017

MONGODB_USERNAME = ""

MONGODB_PASSWORD = ""

MONGODB_DB = "dev"
```

Then start API server by 
```shell
cd src
python server.py
```
Then you can access API service at `http://localhost:8080`

### Using docker-compose dev environment
You can use docker-compose to setup a dev environment with MongoDB

```shell
docker-compose up
```
Then you can access API service at `http://localhost:8080`

### Test

If you setup local environment, you can run unittest and generate coverage report by
```shell
cd src
./run_tests.sh
```

Also, you can run tests in Docker container
```shell
docker build --target testing -t api:test .
docker run api:test
```

## Deployment

### Local deployment
1. Build production image
```
docker build --target prod -t api:prod .
```

2. Run production image by specifying production configuration

It's recommend to pass configuration through environment variables when run docker container
Here is an exampel of env-file
```shell
MONGODB_HOST="mongohost"
MONGODB_PORT=27017
MONGODB_USERNAME = "user"
MONGODB_PASSWORD = "password"
MONGODB_DB = "prod"
```
Run docker image by
```shell
docker run -p 8080:8080 --env-file <env_file> api:prod
```
Then you can access API service at `http://localhost:8080`



## Deployment 

1. Build image
```bash
docker build --target prod -t chargepoint:prod_<version> .
```

2. Push image to repo.

We can use a docker registry on Azure. Run the following command in your local machine.
```bash
docker login infrabase.azurecr.io -u infrabase -p dSjjVh=ReiFnVkypGJGZ75myNGaEf1xZ
```

```bash
docker tag chargepoint:prod_<version> infrabase.azurecr.io/ev/chargepoint:prod_<version>
```
```bash
docker infrabase.azurecr.io/ev/chargepoint:prod_<version>
```

3. Add registry secret to kubernetes

This is already done, you can skip it.

```bash
kubectl -n ev-prod create secret docker-registry infrabase\
 --docker-server infrabase.azurecr.io --docker-username infrabase\
  --docker-password dSjjVh=ReiFnVkypGJGZ75myNGaEf1xZ --docker-email berry.ban@sap.com

```

4. Deploy to kubernetes

```bash
kubectl create -n ev-prod -f deploy/kubernetes/deployment.yaml
```

Then run `kubectl get pods -n ev-prod`, wait until chargepoint pod is running.

5. Deploy ingress

```bash
kubectl create -n ev-prod -f deploy/kubernetes/ingress.yaml
```


## API doc

swagger def: http://ev.funr.xyz/swagger.json

[view online](https://redocly.github.io/redoc/?url=http://ev.funr.xyz/swagger.json)

- get location: http://ev.funr.xyz/api/v1/location/125957
- get station: http://ev.funr.xyz/api/v1/station/225554
- get chargepoint: http://ev.funr.xyz/api/v1/chargepoint/474179

