#! /bin/bash

docker build -t singularis314/chater-ui:0.4 .
docker push singularis314/chater-ui:0.4
kubectl rollout restart -n chater deployment chater-service