FROM alpine:latest

# signal the script that it is a container
ENV CONTAINER_BOOL="True"

RUN mkdir -p /opt/teampy/configs && \
    mkdir -p /opt/teampy/modules && \
    mkdir -p /opt/teampy/logs && \
    mkdir -p /opt/teampy/plugins 


COPY ./main.py /opt/teampy/
COPY ./config.py /opt/teampy/config.py
COPY ./modules/* /opt/teampy/modules
COPY ./plugins/ /opt/teampy/plugins
COPY ./watchdog.sh /opt/teampy/

RUN apk add --no-cache python3 && \
    /usr/bin/python3 -m ensurepip && \
    /usr/bin/pip3 --no-input install requests  && \
    apk add iputils && \
    apk add bash

WORKDIR /opt/teampy/
CMD [ "/bin/bash", "watchdog.sh" ]

