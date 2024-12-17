#! /bin/bash

docker build -t singularis314/eater-init:0.1 .
docker push singularis314/eater-init:0.1
kubectl rollout restart -n eater deployment eater

# Generate a new semantic version dynamically
# current_version=$(docker images --format '{{.Tag}}' singularis314/eater-init | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -n 1)

# if [[ -z "$current_version" ]]; then
#   new_version="0.1.0"
# else
#   IFS='.' read -r major minor patch <<< "$current_version"
#   patch=$((patch + 1))
#   new_version="$major.$minor.$patch"
# fi

# echo "Building new version: $new_version"

# docker build -t singularis314/eater-init:$new_version .
# docker push singularis314/eater-init:$new_version
# kubectl set image -n eater deployment eater eater=singularis314/eater-init:$new_version
# kubectl rollout restart -n eater deployment eater
