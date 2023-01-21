import json
import datetime
import math

# This method calculates the relevance score of the particular movie using movie genres and the a user preferences with genre preference score.
def cal_movie_genre_relevance(movie_genres, user_pref):
    movie_genre_score = 0
    for genre in movie_genres:
        for uprec in user_pref:
            if (uprec['genre'] == genre):
                movie_genre_score += uprec['preference_score']
    return movie_genre_score

# This method will process all the movies list and calculates the relevance score for any given user.
def movie_recommendations(user, userprefs_data, related_user_data):
    movie_scores = dict()
    user_pref = None
    for userrec in userprefs_data:
        if(userrec['user_id'] == user):
            user_pref = userrec['preference']
            break

    user_network = related_user_data[str(user)]
    # Checking user preferences again for Null check as few user's doesn't have any preferences records.  
    if (user_pref) != None:
        with open("movie_data.json", "r") as moviedata:
            mdata = json.load(moviedata)
            for movie in mdata:
                # Used Gaussian decay function to retrieve relevance based on the release date.
                tdelta = ((datetime.datetime.now() - datetime.datetime.strptime(movie['release_date'], '%m/%d/%Y')).days)
                time_delta_score = math.exp(-0.5 * math.pow((tdelta / 1800),2))
                # Multiplying the time delta score with 20 to normalize with the genre score.
                movie_timedelta_score = round(time_delta_score,8) * 20
                #print(movie['movie_name'], movie_timedelta_score)

                # Scoring the relevance based on the user preferences
                movie_genres = list(movie['genres'])
                movie_genre_score = cal_movie_genre_relevance(movie_genres, user_pref)
                #print(movie['movie_name'], movie_genre_score)

                # Scoring the relevance based on the users preferences that are related to this user.
                movie_genre_score_network = 0
                for record in user_network:
                    temp_user_pref = list(filter(lambda x: x['user_id'] == record['user_id'], userprefs_data))
                    if (len(temp_user_pref) > 0):
                        movie_genre_score_network += cal_movie_genre_relevance(movie_genres, temp_user_pref[0]['preference'])
                if (movie_genre_score_network != 0 and len(user_network) > 0):
                    movie_genre_score_network = movie_genre_score_network / len(user_network)
                #print(movie['movie_name'], movie_genre_score_network)

                movie_scores[movie['movie_name']] = movie_genre_score_network + movie_genre_score + movie_timedelta_score

    movie_scores = sorted(movie_scores.items(), key=lambda item: item[1], reverse=True)
    return movie_scores[:10]

if __name__ == "__main__":
    userprefs_data = None
    with open("user_preference.json", "r") as userprefs:
        userprefs_data = json.load(userprefs)

    related_user_data = None
    with open("related_users.json", "r") as relatedusers:
        related_user_data = json.load(relatedusers)

    with open("user_data.json", "r") as userdata:
        data = json.load(userdata)
        userid=115
        movies = movie_recommendations(userid, userprefs_data, related_user_data)
        print(movies)
        # for item in data:
        #     movies = movie_recommendations(item['user_id'], userprefs_data, related_user_data)
        #     print(movies)
        #     #using break just to process only first record alone, if we want a particular user to be used for calculating the movie score,
        #     # directly pass that user id to the method movie_recommendations.
        #     break