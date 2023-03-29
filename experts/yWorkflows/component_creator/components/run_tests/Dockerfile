# Start with a base Python image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container
COPY ./workflows/component_creator/components/GenerateTechnicalInfo/requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn
# Copy the Python code into the container
COPY ./workflows/component_creator/components/GenerateTechnicalInfo .

# replace it with installable yeager python library
COPY ./core ./core

# Expose port 80 for the FastAPI application
EXPOSE 5000

# Start the FastAPI application when the container is run
CMD ["uvicorn", "GenerateTechnicalInfo:gen_tech_info_app", "--host", "0.0.0.0", "--port", "5000"]