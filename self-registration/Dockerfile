FROM python:3.12@sha256:05855f5bf06f5a004b0c1a8aaac73a9d9ea54390fc289d3e80ef52c4f90d5585

WORKDIR /app

COPY ./requirements.txt /tmp/requirements.txt

# need to pre-install cython < 3 to avoid pyyaml >= 5.4.1 incompatibility: https://github.com/yaml/pyyaml/issues/601
RUN echo "cython<3" > /tmp/constraint.txt

RUN PIP_CONSTRAINT=/tmp/constraint.txt pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

COPY ./app /app

# Run web app as non-root
RUN useradd -m www
USER www

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
