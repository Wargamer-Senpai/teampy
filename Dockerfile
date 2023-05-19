FROM alpine:latest

RUN mkdir -p /opt/teampy/configs && \
    mkdir -p /opt/teampy/modules && \
    mkdir -p /opt/teampy/logs && \
    #soon
    mkdir -p /opt/teampy/plugins 


COPY ./main.py /opt/teampy/
COPY ./config.py /opt/teampy/config.py
COPY ./modules/* /opt/teampy/modules

RUN apk add --no-cache python3 && \
    /usr/bin/python3 -m ensurepip && \
    /usr/bin/pip3 --no-input install requests
WORKDIR /opt/teampy/
CMD [ "/usr/bin/python3", "main.py" ]

