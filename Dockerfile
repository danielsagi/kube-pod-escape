FROM danielsagi/hackbox

RUN mkdir /root/exploit
WORKDIR /root/exploit
COPY ./requirements.txt .
COPY ./find_sensitive_files.py .
RUN pip install -r requirements.txt
RUN mkdir -p host_files/tokens
RUN mkdir -p host_files/private_keys

# creating aliases to custom ls-host and cat-host commands
COPY host_fs_wrapper /bin/
RUN chmod +x /bin/host_fs_wrapper
RUN echo 'alias "lsh"="/bin/host_fs_wrapper lsh"' >> /etc/bash.bashrc
RUN echo 'alias "cath"="/bin/host_fs_wrapper cath"' >> /etc/bash.bashrc