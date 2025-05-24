#! /bin/bash

docker build -t singularis314/chater-ui:0.5 .
docker push singularis314/chater-ui:0.5
kubectl rollout restart -n chater-ui deployment chater-ui