FROM python:3.7
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirement.txt
EXPOSE 3001
CMD ["python","backend.py","-p","3001"]