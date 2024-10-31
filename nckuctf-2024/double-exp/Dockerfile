FROM dockerfiles/centos-lamp 

COPY . /var/www/html/
RUN gcc f.c -o f
RUN gcc pwn_me.c -o pwn_me
RUN rm f.c pwn_me.c
