#! /bin/bash

docker build -t singularis314/chater-ui:0.1 .
docker push singularis314/chater-ui:0.1
kubectl rollout restart -n chater-ui deployment chater-ui