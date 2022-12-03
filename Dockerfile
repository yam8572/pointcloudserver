# FROM：基底映像檔
FROM python:3.8

# WORKDI：建立 working directory
WORKDIR /app

# ADD：將檔案加到 images 內
ADD . /app

# http://www.open3d.org/docs/release/docker.html
# Install Open3D system dependencies and pip
RUN apt-get update && apt-get install --install-recommends -y \
    gcc \
    libgl1 \
    libgomp1 \
    libusb-1.0-0 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

# Install Open3D from the PyPI repositories
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade open3d

# 只有build 時使用，會執行此命令
RUN pip install -r requirements.txt

# run container 時要執行的命令
CMD python main.py