project(watch-movies)

watch_nolan_movies(TITLES "TENET")

if(WE_HAPPY)
    watch_tarantino_movies(TITLES "Pulp Fiction")
else()
    watch_nolan_movies(TITLES "Oppenheimer")
endif()

watch_tarantino_movies(
    TITLES "Inglorious Basterds" "Django Unchained" "Hateful Eight"
)
