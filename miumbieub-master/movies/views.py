from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Genre, Movie, Rating
from .serializers import GenreSerializer, MovieSerializer, RatingSerializer
import json
import os
import openai
import requests

@login_required(login_url='/accounts/login/')  # 로그인이 필요한 경우, 로그인 페이지로 리다이렉트
def movie_recommend_view(request):
    # 영화 추천 페이지(movie_recommend.html)를 렌더링하는 뷰
    return render(request, 'movies/movie_recommend.html')

def index(request):
    movie_of_week = Movie.max_audience()
    return render(request, 'movies/home.html', {'movie': movie_of_week})


def movies_view(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'movies/detail.html', {'movie': movie})


def genres_view(request):
    genre = get_object_or_404(Genre, type=request.GET.get('type'))
    return render(request, 'movies/genre.html', {'genre': genre})

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")  # 환경변수에서 OpenAI API 키를 가져옵니다.
)

@api_view(['GET'])
def movie_recommend_api(request):
    movie_name = request.GET.get('movie_title', '')  # 쿼리 파라미터에서 영화 제목을 가져옵니다.

    try:
        # GPT-4o 모델에 ChatCompletion API 요청을 보냅니다.
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "당신은 영화 추천 전문가입니다."  # 시스템 역할로 영화 추천 전문가 설정
                },
                {
                    "role": "user",
                    "content": f"'{movie_name}'이/라는 영화 제목과 비슷한 주제나 장르의 영화를 6개 추천하세요. "
                               "추천할 때는 '영화 영어 제목 [개봉년도] : 한글 설명' 형식으로만 응답하세요."
                               # 사용자가 입력한 영화 제목을 바탕으로 영화 추천 요청
                }
            ],
            model="gpt-4o"  # GPT-4o 모델 사용
        )

        # GPT-4o의 응답에서 추천된 영화 제목과 설명을 가져옵니다.
        recommended_movies = response.choices[0].message.content.strip().split('\n')

        # '영화 제목: 영화 설명' 형식으로 결과를 포맷합니다.
        formatted_movies = [movie.strip() for movie in recommended_movies]

        return Response({'results': formatted_movies})  # 포맷된 결과를 응답으로 반환

    except Exception as e:
        # API 호출 실패 시 오류 응답을 반환
        return Response({'error': f'OpenAI API 오류: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)



@api_view(["GET"])
def genres_list(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def genres_detail(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    serializer = GenreSerializer(genre)
    return Response(serializer.data)

@api_view(["GET"])
def movies_search_tmdb(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return Response({"error": "검색어를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    
    tmdb_api_key = os.environ.get('TMDB_API_KEY')
    if not tmdb_api_key:
        return Response({"error": "TMDB API 키가 설정되지 않았습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 항상 영어 결과를 요청하되, 쿼리는 그대로 사용
    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={query}&language=en-US"
    
    try:
        response = requests.get(tmdb_url)
        response.raise_for_status()
        data = response.json()
        
        if not data['results']:
            return Response({"error": "TMDB 검색 결과 없는 영화입니다!"}, status=status.HTTP_404_NOT_FOUND)
        
        movie = data['results'][0]
        
        return Response({
            'title': movie['title'],
            'original_title': movie['original_title'],
            'english_title': movie['title']
        })
    
    except requests.RequestException as e:
        return Response({"error": f"TMDB API 요청 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def movies_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)


@api_view(["GET", "POST"])
def ratings_list(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "GET":
        ratings = movie.ratings.all()
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)
    else:
        if request.user.is_authenticated:
            request.data["movie"] = movie.id
            request.data["user"] = request.user.id
            serializer = RatingSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET", "DELETE", "PUT"])
def ratings_detail(request, pk):
    rating = get_object_or_404(Rating, pk=pk)
    if request.method == 'GET':
        serializer = RatingSerializer(rating)
        return Response(serializer.data)
    else:
        if request.user == rating.user:
            request.data["movie"] = rating.movie.id
            request.data["user"] = request.user.id
            if request.method == 'PUT':
                serializer = RatingSerializer(rating, data=request.data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            elif request.method == 'DELETE':
                rating.delete()
                return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


def load(request):
    data = []
    json_data = os.path.join(settings.BASE_DIR, 'static', "data/data.json")
    with open(json_data, encoding='UTF-8') as f:
        data = json.load(f)
    for rec in data:
        # 'genre': rec['genre'].split('/'),
        context = {
            'id': rec['id'],
            'title': rec['title'],
            'title_eng': rec['title_eng'],
            'title_org': rec['title_org'],
            'audience': rec['audience'],
            'release': rec['release'],
            'thumb_url': rec['thumb_url'],
            'poster_url': rec['poster_url'],
            'running_time': rec['running_time'],
            'director': rec['director'],
            'film_rating': rec['film_rating'],
            'actor1': rec['actor1'],
            'actor2': rec['actor2'],
            'actor3': rec['actor3'],
        }
        movie = Movie.objects.create(**context)
        for genre_name in rec['genre'].split('/'):
            obj, created = Genre.objects.get_or_create(type=genre_name)
            movie.genres.add(obj)
        movie.save()
