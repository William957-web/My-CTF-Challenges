FROM alpine:latest

RUN echo "lottery" > /etc/hostname
RUN adduser -D cat
COPY . /home/cat/
WORKDIR /home/cat
RUN chown -R cat:cat /home/cat
USER cat
ENTRYPOINT ["/home/cat/lottery"]
