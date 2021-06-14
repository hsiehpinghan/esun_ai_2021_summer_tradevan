FROM python:3.7.10-stretch
ENV FLASK_APP=/app.py
ENV FLASK_ENV=production
ENV CAPTAIN_EMAIL=allenwu9453@gmail.com
ENV SALT=my_salt
ENV MODEL_DIR=/model
ADD ./src/esun /esun
ADD ./src/app.py /app.py
ADD ./src/cache.py /cache.py
ADD ./setup.py /
RUN pip install -e /
ADD ./model /model
CMD flask run --host=0.0.0.0 >> /log/esun_ai_2021_summer_tradevan.log 2>&1