FROM python:3.9

ADD loan_api.py .
ADD loan.db .

RUN pip install flask flask_sqlalchemy PyJWT pytz uuid datetime

EXPOSE 5000

CMD [ "python","./loan_api.py" ]




