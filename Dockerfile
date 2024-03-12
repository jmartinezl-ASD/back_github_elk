FROM python:3.9
 
WORKDIR /app
 
COPY . /app

COPY wait-for-es.sh /wait-for-es.sh

ENV TOKEN='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'
ENV GITHUB_API_URL='https://api.github.com'
ENV ORG='Grupo-ASD'

RUN pip install -r requirements.txt

RUN chmod +x /wait-for-es.sh

CMD ["/bin/sh"]