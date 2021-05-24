FROM python:3.6.9-stretch

ADD ./src/esun /esun
ADD ./src/app.py /app.py
ADD ./model /model
ADD ./setup.py /
RUN pip install -e /
ENV FLASK_APP=/app.py
ENV FLASK_ENV=production
ENV CAPTAIN_EMAIL=allenwu9453@gmail.com
ENV SALT=my_salt
ENV MODEL_DIR=/model
CMD flask run --host=0.0.0.0 >> /tmp/esun_ai_2021_summer_tradevan.log 2>&1
