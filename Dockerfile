ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
    apk add gfortran \
        python3 \
        py3-pip

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install requests colorlog bottle

WORKDIR /

# Copy data for add-on
COPY rootfs /
ARG BUILD_ARCH
COPY wgrib2/${BUILD_ARCH}/wgrib2 /usr/bin/gfsweatherforecast

RUN chmod a+x /usr/bin/gfsweatherforecast/wgrib2
RUN chmod a+x /etc/services.d/gfsweatherforecast_api/run /etc/services.d/gfsweatherforecast_api/finish 
RUN chmod a+x /etc/services.d/gfsweatherforecast_web/run /etc/services.d/gfsweatherforecast_web/finish 
RUN chmod a+x /etc/services.d/gfsweatherforecast/run /etc/services.d/gfsweatherforecast/finish
