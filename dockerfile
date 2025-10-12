ARG WEB_VNC=true
ARG EMULATOR_DEVICE="Nexus 4"
FROM budtmo/docker-android:emulator_12.0

ENV DEBIAN_FRONTEND=noninteractive
USER root
# RUN adduser --disabled-password --gecos '' --uid 1012 appuser
# 更新软件包列表并安装 Python 3.10
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.11 python3.11-distutils python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 创建符号链接，让 'python' 和 'pip' 指向 3.10
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# 验证安装
RUN python --version
RUN echo "root:x:0:0:root:/root:/bin/bash" >> /etc/passwd

#
WORKDIR /AppDev-Bench
COPY . ./AppDev-Bench/


ENV GRADLE_USER_HOME "/opt/gradle"
ENV GRADLE_HOME "/opt/gradle"
ENV PATH "$PATH:$GRADLE_HOME/bin"
ENV GRADLE_VERSION=7.2
ENV GRADLE_HOME=/opt/gradle
ENV PATH=$PATH:$GRADLE_HOME/bin

RUN pip install --no-deps -r /AppDev-Bench/AppDev-Bench/appdev_req.txt --break-system-packages

WORKDIR /AppDev-Bench/AppDev-Bench/compiler/
# RUN ./gradlew build
RUN python build.py --android-sdk-path="/opt/android"  --templates-dir="./templates" --generated-files="output.json" --output="./debug" --project-name="debug" --json_content_directly
RUN python3 -m uiautomator2 init