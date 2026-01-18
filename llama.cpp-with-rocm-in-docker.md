---
layout: post
tags: [ "post" ]
title: "llama.cpp in Docker"
date: 2025-12-13
description: build llama.cpp inside a Docker container with AMD ROCm support
---

Github Gist - [Docker files](https://gist.github.com/bijumon/fe538885b530b7fa00f01225d0f1ce82)

Lets build llama.cpp inside a Docker container with AMD ROCm + HIP toolchain installed. The result is a container image that can compile optimized HIP binaries for our AMD GPU and run GGUF models with full GPU acceleration.

## Ubuntu container image with ROCm/HIP

ROCm is very sensitive to ABI mismatches between the kernel driver, HIP runtime, and system libraries, which can cause subtle runtime failures even when builds succeed. AMD recommends [Ubuntu](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/install-overview.html) because ROCm is built and validated against specific Ubuntu releases, keeping these ABIs aligned and predictable.

I used the docker image [rocm/dev-ubuntu-24.04](https://hub.docker.com/r/rocm/dev-ubuntu-24.04/tags) because ROCm HIP support and developer tooling (hipcc, hipconfig, runtime libs) are preinstalled. Using this image avoids the hunt for missing system packages and subtle ABI mismatches inside the container.

## Preparing the Container for GPU Access

We want run the build using a Dockerfile, but let's reproduce the steps manually first.

Set these shell variables:

- `LLAMACPP_ROCM_ARCH` — the AMD GPU architecture to target for optimized binaries, `gfx1101` or `gfx1102` for some RDNA3 cards

- `HIP_VISIBLE_DEVICES` — which GPU(s) the ROCm runtime should expose to the process inside the container. It takes a comma-separated list of GPU indices.

  - `HIP_VISIBLE_DEVICES=0` → expose only GPU 0
  - `HIP_VISIBLE_DEVICES=0,1` → expose GPUs 0 and 1

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
  rocm/dev-ubuntu-24.04:latest
```

lets walk through it line by line, focusing on why each flag

- `docker run -it` runs a new container and attaches our terminal to it. We get an interactive prompt inside the container.

  - `-i` keeps STDIN open.
  - `-t` allocates a pseudo-TTY so you get a normal shell.

- `--name=llamacpp_build_01` gives the container a usable name, instead of having to use a container-id like 36569e4cb3cd.

`docker start -ai llamacpp_build_01` attach and run interactive shell inside container

`docker exec -it llamacpp_build_01 bash` - start a shell inside an already running container

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

i.e. launch a privileged, GPU enabled, interactive ROCm development container with access to our AMD GPU and local model files, optimized for building and running large LLM workloads with `llama.cpp`.

## Update and build llama.cpp

1. Install build dependencies

```bash
apt update && apt install -y nano libcurl4-openssl-dev cmake git
```

2. get llama.cpp source

```bash
mkdir -p /workspace && cd /workspace
git clone https://github.com/ggml-org/llama.cpp.git
```

3. Set the target GPU architecture and build using CMake with HIP enabled

```bash
export LLAMACPP_ROCM_ARCH=gfx1101,gfx1102
HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)"

cmake -S . -B build -DGGML_HIP=ON \
-DAMDGPU_TARGETS=$LLAMACPP_ROCM_ARCH \
-DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=ON

cmake --build build --config Release -j$(nproc)
```

## Dockerfile: Building llama.cpp with ROCm

``` dockerfile
FROM rocm/dev-ubuntu-24.04:latest

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

## Making the Container Usable

`entrypoint.sh` is a wrapper that turns the container into a friendly CLI. It interprets `--run`, `--serve` and `--help` and dispatches to llama-cli or llama-server. We can use the container like a command-line tool instead of manually invoking binaries.

``` shell
#!/usr/bin/env bash
set -euo pipefail

LLAMA_BIN="/workspace/llama.cpp/build/bin/llama-cli"
SERVER_BIN="/workspace/llama.cpp/build/bin/llama-server"

usage() {
  cat <<EOF
llama.cpp ROCm container

Usage:
  --run     Run llama-cli (default)
  --serve   Run llama-serverx`
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

## Docker Compose: Running the ROCm Container

``` yaml
version: "3.9"

services:
  llamacpp-rocm:
    container_name: llamacpp_build_01
    image: rocm/dev-ubuntu-24.04:latest
    tty: true
    stdin_open: true

    privileged: true
    network_mode: host

    devices:
      - /dev/kfd
      - /dev/dri

    group_add:
      - video

    cap_add:
      - SYS_PTRACE

    security_opt:
      - seccomp=unconfined

    ipc: host
    shm_size: 16g

    volumes:
      - /home/bj/LLM_MODELS:/data
```

## Run the cli

``` shell
docker compose run --rm llamacpp-rocm \
  --run -m /data/model.gguf -p "Hello"
```

## Run the server

``` shell
docker compose run --rm llamacpp \
  --serve -m /data/model.gguf --port 8080
```

Here are **concise, technical “Notes / Caveats”** you can drop in without expanding the scope of the article:

## Caveats

- ROCm is sensitive to ABI mismatches, host kernel driver, ROCm version and Ubuntu image must remain aligned.
- `LLAMACPP_ROCM_ARCH` must match the GPU architecture, or else HIP kernels may compile but fail or underperform.
- `HIP_VISIBLE_DEVICES` only controls GPU visibility inside the process. it does not replace proper device mounts.
- Large models place heavy pressure on shared memory. If /dev/shm is too small, inference may fail silently or run with severe and confusing performance degradation.
- `--privileged` simplifies ROCm usage but broadens the security surface, avoid on untrusted hosts.
