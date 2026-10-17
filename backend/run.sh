#!/bin/bash
set -euo pipefail

## Starts the development environment.
dev() {
    cleanup() {
        echo "Stopping development environment..."
        docker compose down -v --remove-orphans
        echo "Development environment stopped."
        trap - INT TERM
        exit 0
    }
    
    trap cleanup INT TERM

    echo "Starting development database..."
    if docker compose up -d --wait db; then
        echo "Development database is ready."
    else
        echo "Failed to start development database."
        cleanup
        exit 1
    fi

    echo "Running database migrations..."
    if uv run alembic upgrade head; then
        echo "Database migrations completed."
    else
        echo "Failed to run database migrations."
        cleanup
        exit 1
    fi

    echo "Starting development server..."
    uv run fastapi dev
}

## Starts the development environment in a Docker container.
dev-docker() {
    cleanup() {
        echo -e "\nStopping development container..."
        docker compose down -v --remove-orphans
        echo "Development container stopped."
        trap - INT TERM
        exit 0
    }

    trap cleanup INT TERM

    echo "Starting development container..."
    if docker compose up --wait backend; then
        echo "Development container is ready."
        echo "You can now access the application at http://localhost:8000"
        echo "Press Ctrl+C to stop the development container."
        echo "--------------------------------------------------------------"

        docker compose logs -f backend
    else
        echo "Failed to start development containers."
        cleanup
        exit 1
    fi
}

## Starts the application with backend and frontend components.
app() {
    cleanup() {
        echo -e "\nStopping application..."
        docker compose down -v --remove-orphans
        echo "Backend containers stopped."
        echo "Application stopped."
        trap - INT TERM
        exit 0
    }

    trap cleanup INT TERM

    echo "Starting application..."
    echo "Starting backend Docker containers..."
    if docker compose up -d --wait backend; then
        echo "Backend containers are ready."
        echo "Starting frontend development server..."
        (cd ../frontend && pnpm run dev)
    else
        echo "Failed to start application."
        cleanup
        exit 1
    fi
}

## Runs integration tests against a containerised test database.
test() {
    trap 'echo "Tests completed."' EXIT

    echo "Running integration tests..."
    uv run pytest tests/integration "$@"
}

help() {
    echo "Usage: ./run.sh <command> [args...]"
    echo ""
    echo "Available commands:"
    awk '
    /^## / { 
        desc = $0 
        sub(/^## /, "", desc) 
        next 
    } 
    /^[a-zA-Z_-][a-zA-Z0-9_-]*\(\)/ { 
        if (desc != "") { 
            name = $0 
            sub(/\(\).*/, "", name)
            if (name != "help") { 
                printf " %-12s - %s\n", name, desc 
            } 
            desc = "" 
        } 
    }
    ' "$0"
}

COMMAND="$1"
shift

case "$COMMAND" in
    dev|dev-docker|app|test|help)
        # Execute the function matching the command name
        "$COMMAND" "$@"
        ;;
    -h|--help)
        help
        exit 0
        ;;
    "")
        echo "Error: No command specified." >&2
        echo "Use './run.sh help | -h | --help' to see available commands." >&2
        exit 2
        ;;
    *)
        echo "Error: Unknown command '$COMMAND'." >&2
        echo "Use './run.sh help | -h | --help' to see available commands." >&2
        exit 2
        ;;
esac