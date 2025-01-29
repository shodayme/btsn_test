FROM python:3.10.12-slim


#### Installing Microsoft ODBC Driver for SQL Server on Linux ####
# Set the noninteractive mode to avoid prompts

#ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
COPY ./data_processor/requirements.txt .
RUN pip install -r requirements.txt
COPY ./logger/logger_factory.py ./logger/
COPY ./data_processor/data_processor.py .


# Download the Microsoft repo package
RUN apt-get update && apt-get install -y curl apt-transport-https ca-certificates && \
    curl -sSL -O https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb

# Install the ODBC Driver, SQLCMD, and development headers
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 unixodbc-dev

# Add SQLCMD tools to the PATH
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc

# Apply the PATH changes for all future sessions
SHELL ["/bin/bash", "-c", "source ~/.bashrc"]

# Set default working directory

ENTRYPOINT ["python", "data_processor.py"]
 # "data_processor.py"]