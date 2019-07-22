FROM danielsagi/hackbox

COPY ./requirements.txt requirements.txt
COPY ./exploit.py exploit.py
RUN mkdir -p downloads/tokens
RUN mkdir -p downloads/private_keys
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "exploit.py" ]