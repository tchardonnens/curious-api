# Use python 3.11 as base image
FROM python:3.11

# Set working directory
WORKDIR /code

# Copy Pipfile and Pipfile.lock to working directory
COPY Pipfile Pipfile.lock ./

# Install pipenv
RUN pip install pipenv

# Install dependencies
RUN pipenv install --system --deploy --ignore-pipfile

# Copy all files to working directory
COPY . .

# Expose port 8000
EXPOSE 8000

# Run uvicorn with pipenv
CMD ["pipenv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]