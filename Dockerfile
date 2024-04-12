FROM python:3.9
 
WORKDIR /app
 
COPY . /app

COPY wait-for-es.sh /wait-for-es.sh

ENV GITHUB_API_URL='https://api.github.com'

ENV ORG='Grupo-ASD'

ENV PYTHONUNBUFFERED=1

RUN pip install -r requirements.txt

RUN chmod +x /wait-for-es.sh

CMD ["/bin/sh"]