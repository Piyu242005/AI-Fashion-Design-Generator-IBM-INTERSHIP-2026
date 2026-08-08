#!/usr/bin/env bash
# ============================================================
#  docker-run.sh
#  Piyu AI Clothing Fashion Design Generator — Docker Helper
#  Linux / macOS launcher
# ============================================================
set -euo pipefail

IMAGE="piyu-fashion:latest"
CONTAINER_GPU="piyu-fashion-gpu"
CONTAINER_CPU="piyu-fashion-cpu"
APP_URL="http://localhost:8501"

# ── Colors ────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()  { echo -e " ${GREEN}[✓]${RESET} $*"; }
warn()  { echo -e " ${YELLOW}[!]${RESET} $*"; }
error() { echo -e " ${RED}[✗]${RESET} $*"; }
title() { echo -e "\n${CYAN}${BOLD}$*${RESET}"; }

# ── Banner ────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD} ╔══════════════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD} ║   Piyu AI Clothing Fashion Design Generator          ║${RESET}"
echo -e "${CYAN}${BOLD} ║   Docker Launcher                                    ║${RESET}"
echo -e "${CYAN}${BOLD} ╚══════════════════════════════════════════════════════╝${RESET}"
echo ""

# ── Pre-flight checks ─────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    error "Docker is not installed."
    echo "        Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &>/dev/null; then
    error "Docker daemon is not running. Start Docker and retry."
    exit 1
fi
info "Docker is running."

# ── .env setup ───────────────────────────────────────────────────────────
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        warn ".env not found — copying from .env.example"
        cp ".env.example" ".env"
        info ".env created."
        warn "IMPORTANT: Edit .env and set your HF_TOKEN"
        echo "           Get your token: https://huggingface.co/settings/tokens"
        read -rp "  Press Enter to continue after editing .env, or Ctrl+C to abort..."
    else
        error ".env.example not found."
        exit 1
    fi
fi

# ── Streamlit secrets ────────────────────────────────────────────────────
if [[ ! -f ".streamlit/secrets.toml" && -f ".streamlit/secrets.toml.example" ]]; then
    cp ".streamlit/secrets.toml.example" ".streamlit/secrets.toml"
    info ".streamlit/secrets.toml created from example."
fi

# ── Output directories ───────────────────────────────────────────────────
mkdir -p results reference_images
info "Output directories ready."

# ── GPU detection ────────────────────────────────────────────────────────
USE_GPU=0
if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
    USE_GPU=1
    info "NVIDIA GPU detected — GPU mode enabled."
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 || echo "Unknown")
    echo "         GPU: $GPU_NAME"
else
    warn "No NVIDIA GPU detected — CPU-only mode (slower inference)."
fi

# ── Action menu ───────────────────────────────────────────────────────────
echo ""
echo -e " ${BOLD}Select an action:${RESET}"
echo "   1. Build image only"
echo "   2. Build and run  (recommended first time)"
echo "   3. Run existing image  (skip build)"
echo "   4. Stop running container"
echo "   5. View logs"
echo "   6. Shell into container"
echo "   7. Remove everything (image + volumes)"
echo "   8. Exit"
echo ""
read -rp "  Enter choice [1-8]: " CHOICE

build_image() {
    title "Building Docker image…"
    docker build -t "$IMAGE" .
    info "Image built: $IMAGE"
}

run_container() {
    # Stop existing
    docker stop "$CONTAINER_GPU" &>/dev/null || true
    docker stop "$CONTAINER_CPU" &>/dev/null || true
    docker rm   "$CONTAINER_GPU" &>/dev/null || true
    docker rm   "$CONTAINER_CPU" &>/dev/null || true

    if [[ $USE_GPU -eq 1 ]]; then
        title "Starting GPU container…"
        docker compose --profile gpu up -d
        RUNNING_CONTAINER="$CONTAINER_GPU"
    else
        title "Starting CPU container…"
        docker compose --profile cpu up -d
        RUNNING_CONTAINER="$CONTAINER_CPU"
    fi

    info "Container started: $RUNNING_CONTAINER"
    echo ""
    echo -e " ${CYAN}┌─────────────────────────────────────────────────────┐${RESET}"
    echo -e " ${CYAN}│${RESET}  App URL : ${BOLD}${APP_URL}${RESET}                          ${CYAN}│${RESET}"
    echo -e " ${CYAN}│${RESET}  Logs    : docker logs -f $RUNNING_CONTAINER  ${CYAN}│${RESET}"
    echo -e " ${CYAN}│${RESET}  Stop    : docker stop $RUNNING_CONTAINER      ${CYAN}│${RESET}"
    echo -e " ${CYAN}└─────────────────────────────────────────────────────┘${RESET}"
    echo ""
    warn "App will be available in ~60-120 seconds while models load."

    # Open browser (Linux / macOS)
    sleep 5
    if command -v xdg-open &>/dev/null; then
        xdg-open "$APP_URL" &>/dev/null &
    elif command -v open &>/dev/null; then
        open "$APP_URL"
    fi
}

case "$CHOICE" in
    1)
        build_image
        ;;
    2)
        build_image
        run_container
        ;;
    3)
        if ! docker image inspect "$IMAGE" &>/dev/null; then
            error "Image $IMAGE not found. Run option 2 first."
            exit 1
        fi
        run_container
        ;;
    4)
        title "Stopping containers…"
        docker stop "$CONTAINER_GPU" "$CONTAINER_CPU" &>/dev/null || true
        docker rm   "$CONTAINER_GPU" "$CONTAINER_CPU" &>/dev/null || true
        info "Containers stopped."
        ;;
    5)
        title "Showing logs (Ctrl+C to exit)…"
        docker logs -f "$CONTAINER_GPU" 2>/dev/null || \
        docker logs -f "$CONTAINER_CPU" 2>/dev/null || \
        error "No running container found."
        ;;
    6)
        title "Opening shell…"
        docker exec -it "$CONTAINER_GPU" /bin/bash 2>/dev/null || \
        docker exec -it "$CONTAINER_CPU" /bin/bash 2>/dev/null || \
        error "No running container found. Start the container first."
        ;;
    7)
        echo ""
        warn "This will remove the image AND all model weight volumes (~40 GB)."
        read -rp "  Type YES to confirm: " CONFIRM
        if [[ "$CONFIRM" != "YES" ]]; then
            echo "  Cancelled."
            exit 0
        fi
        docker stop  "$CONTAINER_GPU" "$CONTAINER_CPU" &>/dev/null || true
        docker rm    "$CONTAINER_GPU" "$CONTAINER_CPU" &>/dev/null || true
        docker rmi   "$IMAGE"         &>/dev/null || true
        docker volume rm piyu_fashion_model_weights piyu_fashion_hf_cache &>/dev/null || true
        info "Cleanup complete."
        ;;
    8)
        echo "  Bye!"
        exit 0
        ;;
    *)
        error "Invalid choice: $CHOICE"
        exit 1
        ;;
esac
