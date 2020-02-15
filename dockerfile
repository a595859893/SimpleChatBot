FROM python:3.7
WORKDIR /usr/src/app
ADD ./requirement.txt .
RUN pip install -r requirement.txt

COPY . .
EXPOSE 3001
CMD ["python","backend.py"]