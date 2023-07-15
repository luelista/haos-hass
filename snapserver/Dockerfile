ARG BUILD_FROM
FROM $BUILD_FROM

# Add env
ENV LANG C.UTF-8

#Install snapcast
RUN apk add --no-cache snapcast bash python3
#shairport-sync



# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh
# Copy data for add-on
COPY vban.py /
RUN chmod a+x /vban.py

CMD [ "/run.sh" ]
