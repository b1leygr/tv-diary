# TV Diary
## Overview
TV Diary is a viewing activity tracking application for television. Users can create an account and log watched TV shows, and view information about current and upcoming episodes. The application uses [TMDB](https://www.themoviedb.org/) for programming metadata.

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
2. Start the Vite development server
    ```
    cd frontend
    pnpm dev
    ```

You can also start the application with: ```cd backend && ./run.sh app```
  

Interactive API documentation using [Swagger UI](https://swagger.io/open-source/swagger-ui/) can be accessed at [localhost:8000/docs](http://localhost:8000/docs).

## Preview
Preview images of the Activity, Episode, Season, Show, and Search pages.

#### Activity
<img width="100%" alt="Activity" src="https://github.com/user-attachments/assets/5c9dd35b-7087-43dc-8218-dd802ead9a32" />

#### Episode
<img width="100%" alt="Episode" src="https://github.com/user-attachments/assets/e94661d2-5134-4345-b580-e0b17e5b627d" />

#### Season
<img width="100%" alt="Season" src="https://github.com/user-attachments/assets/ccbeab7e-bfed-4d27-abfd-134c462e3dd5" />


#### Show
<img width="100%" alt="Show" src="https://github.com/user-attachments/assets/bcc2f48c-4ae6-4c30-8d53-d188a84a75e4" />

#### Search
<img width="100%" alt="Search" src="https://github.com/user-attachments/assets/c207d8f7-d387-4f2b-8b38-7c8f4d57c063" />
