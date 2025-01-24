# Use Python 3.13.1 base image
FROM python:3.13-slim


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set the working directory inside the container
WORKDIR /vivaestate

COPY pyproject.toml poetry.lock /vivaestate/

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy project files into the container's working directory
COPY . /vivaestate/

# Expose the application port
EXPOSE 8000

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
