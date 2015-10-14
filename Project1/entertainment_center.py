import media
import fresh_tomatoes

# Create a list of movies - the movies have title, movie image, youtube URL, and lead actor
movies = [];
movies.append(media.Movie("District 9", 
"http://resizing.flixster.com/lHqsM1_l_WK9eQWy_edrYPUUSH0=/180x270/dkpu1ddg7pbsk.cloudfront.net/movie/11/17/33/11173366_ori.jpg", 
"https://www.youtube.com/watch?v=DyLUwOcR5pk",
"Sharlto Copley"))
movies.append(media.Movie("The Departed",
"http://resizing.flixster.com/MFejqwGdgaMC3ormFhAnKfYsoQY=/180x270/dkpu1ddg7pbsk.cloudfront.net/movie/11/16/67/11166721_ori.jpg",
"https://www.youtube.com/watch?v=SGWvwjZ0eDc",
"Leonardo DiCaprio"))
movies.append(media.Movie("This Is The End",
"http://resizing.flixster.com/sPdtswW9AgAi6DLRotRlv3X3yU4=/180x270/dkpu1ddg7pbsk.cloudfront.net/movie/11/17/36/11173666_ori.jpg",
"https://www.youtube.com/watch?v=ILnE7dEhCcc",
"James Franco"))

# Create web page with movies
fresh_tomatoes.open_movies_page(movies)