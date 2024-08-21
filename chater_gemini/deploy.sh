#! /bin/bash

docker build -t singularis314/chater-gemini:0.1 .
docker push singularis314/chater-gemini:0.1
kubectl rollout restart -n chater-gemini deployment chater-gemini