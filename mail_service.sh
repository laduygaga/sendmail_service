#!/bin/bash

run() {
	celery -A app.celery worker & > /dev/null 2>&1
	python3 app.py & > /dev/null 2>&1
	echo "Server is running"
}

function stop() {
	sudo killall python3
}

$1
