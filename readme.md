# IMDB Movie Database System

A robust system for managing and querying movie data using FastAPI, PostgreSQL, and Celery.

## System Architecture

### Database
The system uses PostgreSQL as the primary database due to its:
- Native support for JSON and array data types
- Robust SQL features and reliability 
- Existing setup convenience (MongoDB could be an alternative)

### API Framework
FastAPI was chosen as the REST framework because:
- ASGI support for better performance
- Built-in OpenAPI/Swagger documentation
- Type hints and automatic validation
- Alternative frameworks like Flask or Django could also be used

### CSV Upload Processing
The system supports two methods for handling large CSV file uploads:

1. **Celery Workers**
   - Uses Redis as message broker
   - Provides better flow control through worker concurrency settings
   - Task persistence in Redis queues
   - Recovery capability after service interruptions
   - Recommended for production use

2. **FastAPI Background Tasks**
   - Simpler setup for development
   - No additional infrastructure required
   - Default option when Celery is not enabled

## CSV Validation
The system assumes incoming CSV files are pre-validated. For production environments where validation is needed:
- Pandas can be used for schema validation and data type checking
- Great Expectations or Pandera provide more robust validation frameworks
- Custom validators can be implemented using Python's CSV module

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/LarflleezeGonzo/dailyrounds_imdb.git
cd dailyrounds_imdb
```

2. Start the services using Docker Compose:
```bash
docker-compose up --build -d
```

This will initialize:
- PostgreSQL database
- Redis broker
- API server (Uvicorn)
- Celery worker

## API Endpoints
The API server will be available at `http://0.0.0.0:8000`

### Available Endpoints:

1. **Health Check**
   - Endpoint: `/api/v1/ping`
   - Method: GET
   - Purpose: System health verification

2. **CSV Upload**
   - Endpoint: `/api/v1/upload`
   - Method: POST
   - Query Parameters:
     - `use_celery` (boolean, default: false)
       - `true`: Process using Celery workers
       - `false`: Process using background tasks

3. **Movie Listing**
   - Endpoint: `/api/v1/movies`
   - Method: GET
   - Purpose: Retrieve movies imported from CSV

### API Documentation
Access the OpenAPI/Swagger documentation at:
```
http://0.0.0.0:8000/docs
```

## Testing & Integration

### Postman Collection
The repository includes a Postman collection for testing:
```
IMDB Upload.postman_collection.json
```

Integration testing can be performed via:

1. **Postman**
   - Import the provided collection
   - All endpoints, parameters, and example payloads are pre-configured

2. **Swagger Documentation**
   - Interactive testing through OpenAPI interface
   - Available at `/docs` endpoint
   - Supports all API operations with example requests

## Notes
- The system is containerized using Docker Compose for easy deployment
- Services communicate over a Docker network
- Celery is recommended for production use due to better task management
- Background tasks are suitable for development or smaller workloads
- CSV validation should be implemented based on specific requirements
- Integration tests can be automated using either Postman or the Swagger interface
- Currently, the system does not provide task status notifications (e.g., email notifications when CSV processing completes)

