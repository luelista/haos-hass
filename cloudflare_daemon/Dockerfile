ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
WORKDIR /cloudflare

RUN wget -O /cloudflare/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && \
    chmod +x /cloudflare/cloudflared


# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
