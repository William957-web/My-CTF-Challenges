FROM python:3.11.6

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -qy xinetd && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m chal
RUN chown -R root:root /home/chal

COPY shared /home/chal/shared
COPY verifier/chal.py /home/chal/chal.py
COPY verifier/run.sh /home/chal/run.sh
RUN chmod 755 /home/chal/run.sh /home/chal/chal.py

COPY verifier/xinetd /etc/xinetd.d/chal
RUN chmod 700 /etc/xinetd.d/chal

COPY verifier/startup.sh /home/startup.sh
RUN chmod 700 /home/startup.sh

CMD ["/home/startup.sh"]

EXPOSE 10000
