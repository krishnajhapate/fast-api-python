FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
copy ./app /code/app
copy ./main.py /code
copy ./index.html /code
copy ./login.html /code
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","80"]
