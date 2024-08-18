FROM dylanmei/zeppelin

RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y vim

COPY master /usr/spark-2.2.0/conf/master
COPY slaves /usr/spark-2.2.0/conf/slaves
COPY hosts .

EXPOSE 4040 6066 7077 8080 18080 8081

RUN cat hosts >> /etc/hosts
