# TV Diary
## Overview
TV Diary is a viewing activity tracking application for television. Users can create an account and log watched TV shows, and view information about current and upcoming episodes. The application uses data fetched from [TMDB](https://www.themoviedb.org/) for programming metadata.

## Technology Stack
- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the backend API.
  - [SQLAlchemy](https://www.sqlalchemy.org/) for SQL database interactions (ORM).
  - [Pydantic](https://docs.pydantic.dev) for data validation and settings management.
  - [PostgreSQL](https://www.postgresql.org) for the SQL database.
- 🚀 [**React**](https://react.dev) for the frontend.
  - [TailwindCSS](https://tailwindcss.com) and [Mantine](https://mantine.dev/) for frontend components.
  - [Tanstack Query](https://tanstack.com/query/latest) for server-state management.
  - [TanStack Router](https://tanstack.com/router/latest) for routing.
  - [Hey API](https://heyapi.dev/) for client generation.
- 🐋 [Docker Compose](https://www.docker.com) for local services.

## Running the application locally
### 1. Configure environment variables.
Configure .env using the .env.example template.
### 2. Run
1. Start the FastAPI server
    ```
    docker compose up --build
    ```
3. Start the Vite development server
    ```
    cd frontend
    pnpm dev
    ```
  Interactive API documentation using [Swagger UI](https://swagger.io/open-source/swagger-ui/) can be accessed at [localhost:8000/docs](http://localhost:8000/docs).