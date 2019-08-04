#!/bin/bash

docker-compose -f secret_sawtooth.yaml down &&
docker-compose -f secret_sawtooth.yaml up

