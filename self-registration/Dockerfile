FROM python:3.12

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
