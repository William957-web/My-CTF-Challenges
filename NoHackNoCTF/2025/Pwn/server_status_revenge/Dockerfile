# Use Ubuntu as base
FROM ubuntu:22.04

# Install dependencies: SSH server, build tools, xxd for random hex
RUN apt-get update \
    && apt-get install -y openssh-server gcc xxd \
    && rm -rf /var/lib/apt/lists/*

# Prepare SSHD runtime directory
RUN mkdir /var/run/sshd

# Create hacker user with default password
RUN useradd -m -s /bin/bash hacker \
    && echo 'hacker:hacker' | chpasswd

# Generate random hex and write flag
RUN hex=$(xxd -l 16 -p /dev/urandom) \
    && echo "NHNC{just_sharing_every_every_thing_around_world_${hex}}" > /flag \
    && chmod 600 /flag

COPY Dockerfile /Dockerfile

COPY server_status.c /home/hacker/
WORKDIR /home/hacker
RUN gcc -O3 -s server_status.c -o server_status \
    && rm -f server_status.c \
    && chmod +s server_status

# Remove the Dockerfile from the container
RUN rm -f /Dockerfile

# Configure SSH to listen on port 2222 and allow password login
RUN sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config \
    && sed -i 's/PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 2222

# Launch SSH daemon
CMD ["/usr/sbin/sshd", "-D"]
