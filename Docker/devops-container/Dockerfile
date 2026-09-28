# syntax=docker/dockerfile:1
# Stage 1: Builder (fetch secure tools)
FROM ubuntu:24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install oh-my-zsh manually
RUN git clone https://github.com/ohmyzsh/ohmyzsh.git /tmp/ohmyzsh --depth=1 && \
    cp -r /tmp/ohmyzsh/tools/install.sh /tmp/install-ohmyzsh.sh && \
    chmod +x /tmp/install-ohmyzsh.sh && \
    /tmp/install-ohmyzsh.sh --unattended && \
    rm -rf /tmp/ohmyzsh /tmp/install-ohmyzsh.sh

# Install code-server via DEB (latest version)
ARG CODE_SERVER_VERSION=4.107.1
RUN curl -fsSL -o /tmp/code-server.deb https://github.com/coder/code-server/releases/download/v${CODE_SERVER_VERSION}/code-server_${CODE_SERVER_VERSION}_amd64.deb

# Stage 2: Runtime
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

LABEL maintainer="pk" \
      description="Secure Ubuntu dev container with tools" \
      version="1.2"

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    zsh \
    curl \
    wget \
    nano \
    vim \
    git \
    python3 \
    python3-pip \
    jq \
    openssh-server \
    sudo \
    htop \
    net-tools \
    nodejs \
    npm \
    awscli \
    gosu \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /tmp/code-server.deb /tmp/code-server.deb
RUN dpkg -i /tmp/code-server.deb && rm /tmp/code-server.deb

# SSH hardening (require key-based auth for security)
RUN mkdir -p /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

# Non-root user without sudo (principle of least privilege)
RUN useradd -m -s /bin/zsh user && \
    mkdir -p /home/user/.ssh && \
    chown -R user:user /home//home/user/data && \
    chown -R user:user /home/user

WORKDIR /home/user

# Copy configs/scripts (assume originals; update as needed)
COPY config/sshd_config /etc/ssh/sshd_config
COPY config/motd /etc/motd
COPY config/zshrc /home/user/.zshrc
COPY scripts /home/user/scripts

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh /home/user/scripts/*.sh && \
    chmod 700 /home/user/.ssh && \
    chmod 755 /home/user/data && \
    chown -R user:user /home/user
VOLUME ["/home/user/data", "/home/user/.ssh"]

EXPOSE 22 8080

HEALTHCHECK --interval=30s --timeout=10s CMD pgrep sshd || exit 1

ENTRYPOINT ["/entrypoint.sh"]
