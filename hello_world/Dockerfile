ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 py3-pyserial
    
WORKDIR /ptouch

# Copy data for add-on
COPY run.sh /ptouch/
COPY *.py /ptouch/
COPY ui /ptouch/ui/
COPY hubarcode /ptouch/hubarcode/
RUN chmod a+x /ptouch/run.sh

CMD [ "/ptouch/run.sh" ]
