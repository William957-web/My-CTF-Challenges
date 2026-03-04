FROM python:3.11.6

RUN apt-get update && \
    DEBAIN_FRONTEND=noninteractive apt-get install -qy xinetd

RUN useradd -m chal
RUN chown -R root:root /home/chal

COPY ./share /home/chal
RUN chmod -R 755 /home/chal

COPY ./xinetd /etc/xinetd.d/chal
RUN chmod 700 /etc/xinetd.d/chal

COPY ./startup.sh /home/startup.sh
RUN chmod 700 /home/startup.sh

CMD ["/home/startup.sh"]

EXPOSE 10000
