# 🎞 무비피티

상명대학교 졸업 프로젝트를 위한 영화 추천 사이트입니다.


&nbsp;
## 0. 로컬 실행 방법

pip로 프로젝트에 필요한 패키지를 설치합니다.

```bash

> python -m venv venv
> venv\Scripts\activate
> pip install -r requirements.txt
```

migrate를 한 뒤 Django 프로젝트를 실행합니다.

```bash
> python manage.py migrate
> python manage.py loaddata genre_data.json
> python manage.py loaddata movie_data.json
> python manage.py runserver
```




## 1. 사용 기술 및 개발 계획

### 1) 사용 기술

Django 템플릿에서 Vue CDN을 이용해 개발했습니다.

#### Frontend

- Vue : 2.6.10
- Axios : 0.18.0
- Bulma : 0.7.4
- Font Awesome : 5.8.2

#### Backend

- Django : 5.1.1
- Django REST framework : 3.15.2
- Python : 3.11.5

&nbsp;



### 2) 개발 계획

* 진행 기간 : 2024.03.14 - 2024.09.17
* 목표 : 영화 포털 사이트의 기본 기능을 빠르게 구현하자
* 수정한 부분: 영화 추천 탭을 만들어 챗GPT API를 활용한 영화추천 기능을 추가함, 기존에 있던 영화검색 기능 삭제함

&nbsp;







&nbsp;

## 3. 핵심 기능

### 1) 영화 추천

- 메인 화면에서 관람객 수 1위 영화 추천
- 프로필 페이지에서 팔로워들의 최애 영화 추천



### 2) 리뷰 작성

* 로그인한 유저는 :star: 를 조작해 평점과 리뷰 등록
* 내가 남긴 리뷰 수정, 삭제 기능



### 3) 영화 검색

* 메인 화면에서 장르 카드를 눌러 장르별 영화 검색 



### 4) 유저 프로필

* 내가 작성한 평점과 리뷰 확인
* 내 팔로워들의 최애 영화 확인



### 5) UI/UX

- Bulma 프레임워크를 이용해 플랫폼에 최적화된 디자인 구현
- Single Page App으로 페이지 리로드 최소화 (ex. 장르별 영화)






