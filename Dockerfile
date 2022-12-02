# Base image
FROM python:3.7

# Install pipenv
RUN pip install pipenv

# Set working directory
WORKDIR /api/

# Copy Pipfile and Pipfile.lock to container
COPY Pipfile /api/
COPY Pipfile.lock /api/

RUN apt-get update && apt-get install -y \
    python-dev libxml2-dev libxslt1-dev antiword poppler-utils \
    python3-pip zlib1g-dev
RUN pipenv install --dev

# Expose port for api
EXPOSE 5000

# Add flask app entrypoint to ENV
ENV FLASK_APP=python_scripts/api.py

# Default command
CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]
