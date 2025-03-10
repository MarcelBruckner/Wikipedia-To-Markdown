FROM python:3.13-slim

WORKDIR /app

ADD requirements.txt /app 
ADD wiki-to-md.py /app

RUN pip install -r requirements.txt

CMD ["--output", "/output"]
ENTRYPOINT ["python", "-u", "./wiki-to-md.py"] 

