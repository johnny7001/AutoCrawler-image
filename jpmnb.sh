#!/bin/bash
clear
date
docker rm jbmnb_crawler
docker rmi jbmnb_crawler
docker build -t jbmnb_crawler .
docker run --name jbmnb_crawler jbmnb_crawler
