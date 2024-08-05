#! /bin/bash

docker build -t singularis314/chater-ui:0.2 .
docker push singularis314/chater-ui:0.2
kubectl rollout restart -n chater-ui deployment chater-ui