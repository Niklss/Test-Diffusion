## How to run
1. To run the needed infrastructure you firstly need to have MinIO, 
Kafka broker, Zookeeper and Nginx
```
docker-compose up -d -f docker-compose-infra.yaml
```
2. Then you need to go to the MinIO web interface to create a system 
account to use API with boto3. Credentials placed in the top level .env file 
3. Having MinIO secrets add credentials to the apps.env file of api and 
diffusion services. 
4. You also might need to check the dif-Dockerfile to meet your runtime and 
torch requirements
5. From now on you can start services using docker-compose up -d  

Of course you may start api and diffusion services locally, but you firstly
need to set up the environment variables

## How it works
On 8000 port sets up swagger (http://localhost:8000/docs). 
There is single endpoint for Img2Img generation (/api/diffusion).
This endpoint receives model_name, prompt, priority query params and 
image as a form data.
The method returns an access link for the future generated image.

When the request is sent, service produce message to kafka topic 
by model name and writes file to MinIO. Having running consumers, 
they poll the new message according to the model name, download the image
from MinIO, perform Img2Img, and save file to MinIO back.

When the process is finished, it is possible to download a new image 
by provided access link in the first place.

It is also possible to perform img2img having local folder 'images' 
using __local_img2img.py__. It simply calls the HTTP API and prints
out access links.

## General idea
Having task description I firstly wanted to simply load a models
and perform Img2Img, but then I saw the scalability requirement.

To make scalable solution capable of processing thousands RPS
I decided to apply producer-consumer approach with the help of
MinIO (Distributed object storage) and Kafka (Distributed message broker).  

In my current approach I have a producer (FastAPI service) 
which receives requests with image files and places it into the 
Kafka topic according to the model name, provided in request.  
Another service called diffusion creates a bunch of consumer processes, 
which listen to the topic according to the model name. 
The amount of processes defined by the model_names.txt file 
(one model name, one process).

The final idea behind this project is to have a central service, 
which scales or deploys new consumer container per topic 
(instead of all in one) according to different queue loading. 
And of course, it stops the unused one.

In common/benchmark defined an async decorator which writes 
time and memory consumption into local file in the table format 
with __;__ delimiter. The columns are model name, time, memory in MiB.

## Future improvements
1. To make this service actually be useful, as I mentioned earlier, we 
need to add a central service for managing consumers according to 
loading, or simply use autoscaling provided by AWS for example.
2. It is possible to create a sort of priority queue. Simply add 
more topic for each model and add in consumer reading from more
prioritized topics first.
3. To accurately handling the end of the processing we need to add 
webhooks or another consumer service to notify on finish
4. To handle multiple users more accurately we need to add databases.
Redis for caching and storing user data if user data is not so important 
or any SQL-like DB for storing user data.
5. Deploy Grafana and Prometheus to visualise performance results.


## P.S
I didn't run the diffusion service to test it out, but it should work =)