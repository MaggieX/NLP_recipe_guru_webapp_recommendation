from python:3.6.1-alpine
COPY . /recipe_guru
WORKDIR /recipe_guru
Add . /recipe_guru
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ] 
CMD ["app.py"]

