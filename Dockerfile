FROM alpine:latest

# signal the script that it is inside a container
ENV CONTAINER_BOOL="True"

RUN mkdir -p /opt/teampy/data && \
    mkdir -p /opt/teampy/modules && \
    mkdir -p /opt/teampy/logs && \
    mkdir -p /opt/teampy/plugins && \
    apk add --no-cache python3 py3-requests py3-setuptools py3-pip py3-yaml iputils bash vim && \
    pip3 install --break-system-packages --no-cache-dir ping3


COPY ./main.py /opt/teampy/
COPY ./config.py.example /opt/teampy/config.py
COPY ./modules/* /opt/teampy/modules
COPY ./plugins/ /opt/teampy/plugins
COPY ./watchdog.sh /opt/teampy/


WORKDIR /opt/teampy/
CMD [ "/bin/bash", "watchdog.sh" ]

