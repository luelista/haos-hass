ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
WORKDIR /forwarder

RUN apk add go
RUN GOPATH=/forwarder/go go install github.com/luelista/ftp-http-forwarder@9c3654783083f60aaecb13c454566d243cd45d48

COPY run.sh /forwarder
RUN chmod a+x /forwarder/run.sh

CMD [ "/forwarder/run.sh" ]
