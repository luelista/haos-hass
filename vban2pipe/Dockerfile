ARG BUILD_FROM
FROM $BUILD_FROM

# Add env
ENV LANG C.UTF-8

WORKDIR /app
RUN apk add gcc git make musl-dev
RUN git clone https://github.com/004helix/vban2pipe.git
RUN cd /app/vban2pipe && make

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
