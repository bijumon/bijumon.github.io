---
layout: post
tags: [ "post" ]
title: "llama.cpp in Docker"
date: 2025-12-13
description: build llama.cpp inside a Docker container with AMD ROCm support
---
![](/images/llamacpp-docker-rocm.png)

Running llama.cpp on AMD GPUs inside Docker with ROCm is fragile by default. Small mismatches between the host driver, ROCm runtime, Ubuntu base image, or HIP toolchain often lead to build failures, missing devices, or binaries that compile but fail at runtime. Docker’s default security model blocks several GPU-related syscalls, so even a “successful” build may fail to detect the GPU or run.

Lets build llama.cpp inside a ROCm-enabled Docker container in a way that is repeatable and predictable. The result is a container image that can compile optimized HIP binaries for our AMD GPU, run GGUF models with full GPU acceleration, and behave like a simple command-line tool (--run, --serve, --help) instead of a fragile development environment.

Ive built [llama.cpp]() inside a ROCm enabled container. I used the docker image [rocm/dev-ubuntu-24.04:7.0-complete]() because ROCm HIP support and developer tooling (hipcc, hipconfig, runtime libs) are preinstalled on a matching Ubuntu base. Using this image avoids chasing missing system packages or ABI mismatches inside the container.

We need to set these shell variables:

- `LLAMACPP_ROCM_ARCH` — the AMD GPU architecture to target for optimized binaries, `gfx1101` or `gfx1102` for some RDNA3 cards
- `HIP_VISIBLE_DEVICES` — which GPU(s) the ROCm runtime should expose to the process inside the container

We want run the build inside a Dockerfile (below), but let's reproduce the steps manually first.

```bash
docker run -it \
  --name=llamacpp_build_01 \
  --privileged \
  --network=host \
  --device=/dev/kfd \
  --device=/dev/dri \
  --group-add video \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --shm-size 16G \
  -v /home/bj/LLM_MODELS:/data \
  rocm/dev-ubuntu-24.04:7.0-complete
```

lets walk through it line by line, focusing on why each flag

- `docker run -it` runs a new container and attaches our terminal to it. We get an interactive prompt inside the container.

  - `-i` keeps STDIN open.
  - `-t` allocates a pseudo-TTY so you get a normal shell.

- `--name=llamacpp_build_01` gives the container a usable name, instead of having to use a container-id like 36569e4cb3cd.

```bash
docker start -ai llamacpp_build_01 # attach and run interactive shell inside container
docker exec -it llamacpp_build_01 bash 
```

- `--privileged` gives container access to the host GPU and other devices

- `--network=host` shares the host’s network stack, for port forwarding etc

- `--device=/dev/kfd` pass the **Kernel Fusion Driver** device into the container, which lets HIP/OpenCL programs communicate with the GPU.

- `--device=/dev/dri` pass the **Direct Rendering Infrastructure** devices, used for GPU enumeration, memory mapping etc.

- `--group-add video` add the container user to the `video` group, since `/dev/dri/*` devices owned by `video` group.

- `--cap-add=SYS_PTRACE` allows the container to trace processes, used by llama.cpp and rocm runtime tools (helpful for testing).

- `--security-opt seccomp=unconfined` disables Docker’s default security profile thats blocks some syscalls needed by GPU tools

- `--ipc=host` shares host’s IPC namespace, improves performance for GPU runtimes that rely on shared memory segments

- `--shm-size 16G` increases `/dev/shm` size inside the container, for large model inference, tensor buffers etc

- `-v $HOME/LLM_MODELS:/data` mounts our model directory into the container

In short, lets launch a privileged, GPU enabled, interactive ROCm development container with access to our AMD GPU and local model files, optimized for building and running large LLM workloads with `llama.cpp` ;D

Once inside the container, we clone `ggml-org/llama.cpp`, enabled HIP and built `llama.cpp` with **-DGGML_HIP=ON**

```bash
# inside the running container
# 
export LLAMACPP_ROCM_ARCH=gfx1101,gfx1102

apt update && apt install -y nano libcurl4-openssl-dev cmake git

mkdir -p /workspace && cd /workspace
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp

HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
cmake -S . -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=$LLAMACPP_ROCM_ARCH -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=ON
cmake --build build --config Release -j$(nproc)
```

Here is a single-stage Dockerfile that installs deps, sets build args and envs, builds llama.cpp.

``` dockerfile
FROM rocm/dev-ubuntu-24.04:7.0-complete

ARG LLAMACPP_ROCM_ARCH=gfx1101
ARG HIP_VISIBLE_DEVICES=0

ENV LLAMACPP_ROCM_ARCH=${LLAMACPP_ROCM_ARCH}
ENV HIP_VISIBLE_DEVICES=${HIP_VISIBLE_DEVICES}

RUN apt update && apt install -y \
    nano \
    libcurl4-openssl-dev \
    cmake \
    git \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
RUN git clone https://github.com/ggml-org/llama.cpp.git

WORKDIR /workspace/llama.cpp
RUN HIPCXX="$(/opt/rocm/bin/hipconfig -l)/clang" \
    HIP_PATH="$(/opt/rocm/bin/hipconfig -R)" \
    cmake -S . -B build \
      -DGGML_HIP=ON \
      -DAMDGPU_TARGETS=${LLAMACPP_ROCM_ARCH} \
      -DCMAKE_BUILD_TYPE=Release \
      -DLLAMA_CURL=ON \
 && cmake --build build --config Release -j$(nproc)

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["help"]
```

`entrypoint.sh` is a wrapper that turns the container into a friendly CLI. It interprets `--run`, `--serve` and `--help` and dispatches to llama-cli or llama-server. We can use the container like a command-line tool instead of manually invoking binaries.

``` bash
#!/usr/bin/env bash
set -euo pipefail

LLAMA_BIN="/workspace/llama.cpp/build/bin/llama-cli"
SERVER_BIN="/workspace/llama.cpp/build/bin/llama-server"

usage() {
  cat <<EOF
llama.cpp ROCm container

Usage:
  --run     Run llama-cli (default)
  --serve   Run llama-server
  --help    Show this help

Examples:
  docker run IMAGE --run   -m /data/model.gguf -p "Hello"
  docker run IMAGE --serve -m /data/model.gguf --port 8080
  docker run IMAGE --help
EOF
}

die() {
  echo "error: $*" >&2
  exit 1
}

check_bin() {
  [ -x "$1" ] || die "binary not found or not executable: $1"
}

run_llama() {
  check_bin "$LLAMA_BIN"
  exec "$LLAMA_BIN" "$@"
}

run_server() {
  check_bin "$SERVER_BIN"
  exec "$SERVER_BIN" "$@"
}

if [ $# -eq 0 ]; then
  usage
  exit 0
fi

case "$1" in
  --run)
    shift
    run_llama "$@"
    ;;
  --serve)
    shift
    run_server "$@"
    ;;
  --help|-h)
    usage
    exit 0
    ;;
  *)
    # Default mode: treat args as llama-cli flags
    run_llama "$@"
    ;;
esac
```

## Running llama.cpp binaries

We can run the container image directly, using the `--run` argument specified in `entrypoint.sh` and passing to it, llama.cpp arguments like path to GGUF model file.

```bash
docker run -it --privileged --network=host --device=/dev/kfd --device=/dev/dri --group-add video --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --ipc=host --shm-size 16G -v "$MODEL_PATH:/data" llamacpp-rocm-dev --run -n 512 --n-gpu-layers 999 -m /data/deepseek-r1.gguf
```

We can override runtime envs at `docker run` time:

```bash
docker run -e HIP_VISIBLE_DEVICES=1 ... llamacpp-rocm-dev ...
```

Usually, we want a named container that can be started again, from a script like `run-llamacpp.sh`

{% raw %}

```bash
#!/usr/bin/env bash
set -e

IMAGE="llamacpp-rocm-dev"
CONTAINER_NAME="llamacpp-rocm-dev_01"
MODEL_PATH="${MODEL_PATH:-$HOME/LLM_MODELS}"

DOCKER_ARGS=(
  --privileged
  --network=host
  --device=/dev/kfd
  --device=/dev/dri
  --group-add video
  --cap-add=SYS_PTRACE
  --security-opt seccomp=unconfined
  --ipc=host
  --shm-size 16G
  -v "$MODEL_PATH:/data"
)

LLAMACPP_ARGS=(
  -n 512
  --n-gpu-layers 999
)

usage() {
  cat <<EOF
Usage:
  $0 run   [llama.cpp args...]
  $0 serve [llama.cpp args...]

Examples:
  $0 run   -m /data/model.gguf -p "Hello"
  $0 serve -m /data/model.gguf --port 8080

Defaults:
  llama.cpp args: ${LLAMACPP_ARGS[*]}
EOF
}

MODE="${1:-help}"

case "$MODE" in
  run|serve)
    shift
    ;;
  help|--help|-h|"")
    usage
    exit 0
    ;;
  *)
    echo "error: first argument must be 'run' or 'serve'"
    usage
    exit 1
    ;;
esac

FINAL_LLAMA_ARGS=(
  "${LLAMACPP_ARGS[@]}"
  "$@"
)

if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  echo "Starting existing container: $CONTAINER_NAME"
  docker start -ai "$CONTAINER_NAME"
else
  echo "Creating and running container: $CONTAINER_NAME"
  docker run -it \
    --name "$CONTAINER_NAME" \
    "${DOCKER_ARGS[@]}" \
    "$IMAGE" \
    --"$MODE" \
    "${FINAL_LLAMA_ARGS[@]}"
fi
```

{% endraw %}

Run it:

```bash
chmod +x run-llamacpp.sh
./run-llamacpp.sh run -m /data/deepseek-r1.gguf -p "Explain ROCm, briefly"
./run-llamacpp.sh run -m /data/deepseek-r1.gguf --ctx-size 4096 --batch-size 512
./run-llamacpp.sh serve -m /data/tinyllama.gguf --host 0.0.0.0 --port 8080
```
