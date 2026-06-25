#!/usr/bin/env bash


# this file is AI generated,
# it dose work, but take everything with a grain of salt

#=====================================================================
#
#  Purpose : Build Dockerfile.base and then start the compose stack
#            located in the ./infra directory.
#
#  Options :
#      -t|--tag      <image-tag>   Tag for the built image (default: base:latest)
#      -c|--compose  <file>        Compose file name inside ./infra (default: docker-compose.yml)
#      -p|--project  <name>        Docker‑Compose project name (optional)
#      -d|--detached               Run compose in detached mode (default: foreground)
#      -h|--help                   Show this help and exit
#
#=====================================================================

# ---------------------------  Helper functions  ---------------------------

print_help() {
    grep '^#' "$0" | sed -e 's/^# //;s/^#//'
}

die() {
    echo "ERROR: $*" >&2
    exit 1
}

# ---------------------------  Default values  ---------------------------

IMAGE_TAG="runtime-base:latest"
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME=""          # empty → let compose decide
DETACHED=false

# ---------------------------  Parse arguments  ---------------------------

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--tag)
            [[ -z "$2" ]] && die "Missing argument for $1"
            IMAGE_TAG="$2"
            shift 2
            ;;
        -c|--compose)
            [[ -z "$2" ]] && die "Missing argument for $1"
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -p|--project)
            [[ -z "$2" ]] && die "Missing argument for $1"
            PROJECT_NAME="$2"
            shift 2
            ;;
        -d|--detached)
            DETACHED=true
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            die "Unknown option: $1"
            ;;
    esac
done

# ---------------------------  Preconditions  ---------------------------

# Dockerfile.base must exist in the current directory (or you can adapt the path)
[[ -f "Dockerfile.base" ]] || die "Dockerfile.base not found in $(pwd)"

# Compose file must exist under ./infra
COMPOSE_PATH="./infra/${COMPOSE_FILE}"
[[ -f "$COMPOSE_PATH" ]] || die "Compose file '${COMPOSE_PATH}' not found"

# Verify Docker daemon is reachable
docker info > /dev/null 2>&1 || die "Docker daemon not reachable – is Docker running?"

# Verify docker‑compose command (v2 plugin or legacy binary)
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    die "Neither 'docker-compose' nor 'docker compose' command found"
fi

# ---------------------------  Build the base image  ---------------------------

echo "=== Building Docker image '${IMAGE_TAG}' from Dockerfile.base ==="
docker build -f Dockerfile.base -t "${IMAGE_TAG}" . \
    || die "Docker build failed"

echo "=== Build succeeded ==="

# ---------------------------  Run Docker‑Compose  ---------------------------

# Build the compose command step‑by‑step so we can add optional flags
COMPOSE_RUN="${COMPOSE_CMD} -f \"${COMPOSE_PATH}\""

# If a project name was supplied, add it
if [[ -n "$PROJECT_NAME" ]]; then
    COMPOSE_RUN="${COMPOSE_RUN} -p \"${PROJECT_NAME}\""
fi

# Up command – detached or foreground
if $DETACHED; then
    COMPOSE_RUN="${COMPOSE_RUN} up -d"
else
    COMPOSE_RUN="${COMPOSE_RUN} up"
fi

# Show what we are about to execute (useful for debugging)
echo "=== Executing Docker‑Compose ==="
echo "$COMPOSE_RUN"

# Use eval so that the quoting we built above works correctly
eval $COMPOSE_RUN \
    || die "Docker‑Compose failed"

echo "=== Docker‑Compose stack is now running ==="
echo "Tip:  docker ${COMPOSE_CMD} -f \"${COMPOSE_PATH}\" ps"
echo "Tip:  docker ${COMPOSE_CMD} -f \"${COMPOSE_PATH}\" down   # to stop it"

exit 0
