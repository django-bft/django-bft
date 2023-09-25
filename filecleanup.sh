#!/bin/sh

docker exec -it django sh -c "/code/manage.py deleteuploads"
docker exec -it django sh -c "/code/manage.py deletetempfiles"
