Flask implementation of the ff6worldscollide.com balance-and-ruin API (ref: https://github.com/kielbasiago/ultima/tree/main/apps/balance-and-ruin/api)

Tested with python 3.9.6

Running requires several environment variables in a .env file. This includes these values:
```
PATCH_BUCKET='<your S3 bucket used to store patches>'
RECAPTCHA_SECRET='<recaptcha secret>'
PUBLIC_URL='<where you're hosting the ff6worldscollide frontend, for example https://dev.ff6worldscollide.com>'
FF3_INPUT_ROM='ff3.smc'
HELLO_TEXT='<whatever you want to show up at base URL>'
ENV='<DEV or PROD -- appended to Datastore names>'
GOOGLE_APPLICATION_CREDENTIALS='<JSON file with google credentials>'
```

To run locally:
```
pip install -r requirements.txt
flask run
```



Docker:
build with  `docker build --tag=narshe .`
run locally with `docker run --rm -p5000:5000 -e PORT=5000 narshe:latest`
deploy with `gcloud run deploy --source .`
-- may need to set CLOUDSDK_PYTHON env
also useful: `docker run --rm -it --entrypoint bash narshe:latest`