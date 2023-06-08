# Use an official Python runtime as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install system dependencies for python-ldap
RUN apt-get update && \
    apt-get install -y \
    xmlsec1

# Set the working directory in the container
WORKDIR /code

# Install project dependencies from requirements.txt
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt