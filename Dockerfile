FROM python:3.10-slim-bullseye
# install source
RUN mkdir -p /app/thorikos
ADD . /app/thorikos
WORKDIR /app/thorikos
# install dependencies
RUN pip3 install -r requirements_min.txt
# install waitress
RUN pip3 install gunicorn
# copy docker config
COPY config.docker.py config.py
# copy entrypoint
COPY ./entrypoint /entrypoint
RUN ["chmod", "+x", "/entrypoint"]
# set entrypoint script
CMD ["/entrypoint"]