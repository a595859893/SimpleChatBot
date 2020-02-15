FROM python:3.7
WORKDIR /usr/src/app
ADD ./requirement.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirement.txt
COPY . .
EXPOSE 3001
VOLUME ["/usr/src/app/data"]
CMD ["python","backend.py"]