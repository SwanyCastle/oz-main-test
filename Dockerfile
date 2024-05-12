# 파이썬 3.12를 기반 이미지로 사용
FROM python:3.12

# 환경 변수 설정
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# pip 업그레이드 및 poetry 설치
RUN pip install --upgrade pip \
  && pip install poetry

# 작업 디렉터리 설정
WORKDIR /app

# Python 의존성 파일 복사
COPY pyproject.toml poetry.lock* ./

# poetry를 사용하여 의존성 설치
# 가상 환경 생성 비활성화
# poetry 설정 변경
RUN poetry config virtualenvs.create false

# dependencies 설치 명령 수정
RUN poetry install --only main --no-interaction --no-ansi

# 현재 디렉터리의 모든 파일을 컨테이너의 /app 디렉터리로 복사
COPY . .

# .env 파일 및 entrypoint.sh 스크립트 복사
COPY ./.env /app/.env
COPY ./entrypoint.sh /app/entrypoint.sh

# entrypoint.sh 실행 권한 부여
RUN chmod -R +x ./entrypoint.sh

# 컨테이너 실행 시 entrypoint.sh 스크립트 실행
ENTRYPOINT [ "/app/entrypoint.sh" ]
