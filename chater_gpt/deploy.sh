#! /bin/bash

docker build -t singularis314/chater-gpt:0.1 .
docker push singularis314/chater-gpt:0.1
kubectl rollout restart -n chater-gpt deployment chater-gpt