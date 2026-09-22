#!/bin/bash
set -e

## Starts the development environment.
dev() {
    trap 'docker compose down -v --remove-orphans; echo "Development database stopped."' EXIT

    echo "Starting development database..."
    echo "Waiting for development database to be ready..."
    docker compose up -d --wait db
    echo "Development database is ready."
    
    echo "Running database migrations..."
    uv run alembic upgrade head
    echo "Database migrations completed."

    echo "Starting development server..."
    uv run fastapi dev
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
    dev|help)
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