FROM python:3.8

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y mc

# Install dependencies:
# TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

RUN pip install structlog pandas numpy matplotlib seaborn sklearn requests tqdm finta ta-lib

# Run the application:
#COPY myapp.py .
#CMD ["python", "myapp.py"]