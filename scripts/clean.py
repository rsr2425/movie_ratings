# NOTE: needs to be run from the scripts folder

import pandas as pd
import numpy as np

PATH = "..//data//ml-20m//"
movies = pd.read_csv(PATH + "movies.csv")
movies = movies.set_index('movieId')

links = pd.read_csv(PATH + "links.csv")
tags = pd.read_csv(PATH + "tags.csv")
ratings = pd.read_csv(PATH + "ratings.csv")

avg_ratings = pd.pivot_table(ratings, values='rating'
             , index=['movieId']
             , aggfunc=lambda x: int(2*np.mean(x))+1)

title = dict(zip(movies.index, movies['title']))
id = dict(zip(movies['title'], movies.index))
movie_ratings = pd.concat([movies[['title']], avg_ratings]
                          , axis=1)
avg_rating_from_id = dict(zip(movie_ratings.index
                      , movie_ratings['rating']))

np.save('id.npy', id)
np.save('avg_rating_from_id.npy', avg_rating_from_id)
avg_rating_from_title = dict(zip(movie_ratings['title']
                      , movie_ratings['rating']))
np.save('avg_rating_from_title.npy', avg_rating_from_title)
