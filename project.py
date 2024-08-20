import streamlit as st
import pandas as pd
import numpy as np
import requests

st.title("Movie Recommendation System")

import pickle
movie = pickle.load(open('movie.pkl','rb'))
movies_list = movie['title'].values

cosine_similarity = pickle.load(open('cosine_similarity.pkl','rb'))
count = pickle.load(open('count.pkl','rb'))

vote_counts = movie['vote_count'].astype('int')
vote_averages = movie['vote_average'].astype('int')
c = vote_averages.mean()
m = vote_counts.quantile(0.60)

def weighted_rating(x):
    v = x['vote_count']
    R = x['vote_average']
    return (v/(v+m) * R) + (m/(m+v) * c)

def improved_recommendations(title,movies_preprocessed):
    count_matrix = count.fit_transform(movies_preprocessed['soup'])
    cosine_sim = cosine_similarity(count_matrix,count_matrix)
    movies_preprocessed = movies_preprocessed.reset_index()
    titles = movies_preprocessed['title']
    indices = pd.Series(movies_preprocessed.index, index=movies_preprocessed['title'])
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:26]
    movie_indices = [i[0] for i in sim_scores]

    pred = movies_preprocessed.iloc[movie_indices]
    vote_counts = pred['vote_count'].astype('int')
    vote_averages = pred['vote_average'].astype('int')
    c = vote_averages.mean()
    m = vote_counts.quantile(0.40)
    qualified = pred[(pred['vote_count'] >= m)]
    qualified['wr'] = qualified.apply(weighted_rating,axis=1)
    qualified_2 = qualified.sort_values('wr', ascending=False).head(10).title
    return qualified_2



movie_name = st.selectbox(
    "Which movie would you like getting recommendations for?",
    movies_list,
)

id = ((movie[movie['title']==movie_name])['cast']).index[0]
actor = ((movie[movie['title']==movie_name])['cast'])[id]
direct = ((movie[movie['title']==movie_name])['crew'])
crew_list = direct.iloc[0]
crew_string = ', '.join(crew_list)

pref = st.selectbox(
    "Is there a lead star/director in that movie whom you love and want to see a bit more of???",
    ("Nah...just suggest similar movies","Oh...I love that actor/actress","More films by director pls")
)
if (pref=="Oh...I love that actor/actress") :
    actor_choice = st.selectbox(
        "Which one of these???",
        actor
    )
    def add_actor(row):
        if actor_choice in row['cast']:
            row['soup'] = row['soup'] + 2 * (' ' + actor_choice)
        return row['soup']

    movie['soup'] = movie.apply(add_actor, axis=1)

if (pref=="More films by director pls") :
    def add_director(row):
        if crew_string in row['crew']:
            row['soup'] = row['soup'] + 2 * (' ' + crew_string)
        return row['soup']

    movie['soup'] = movie.apply(add_director, axis=1)




option = st.selectbox(
    "Interested in getting recommendations from any specific year or decade?",
    ("None (suggest all year)", "decade", "year"),
)
if option=='year':
    number = st.number_input("Select the year (max - 2016)")
    st.write("Suggesting movies from year : ", number)
    
if option=='decade':
    number = st.number_input("Select the decade(ex: 1970 for 1970s, max - 2010)")
    st.write("Suggesting movies from decade : ", number)
    

if st.button("Recommend"):
    if option=='None (suggest all year)':
        recom = improved_recommendations(movie_name,movie)
        for i in recom:
            st.write(i)
    elif option=='decade':
        movie_2=movie[movie['decade']==number]
        a=movie[movie['title']==movie_name].index[0]
        b = movie_2.index
        if (a not in b):
            movie_2.loc[a]=movie.loc[a]
        movie_2= movie_2.reset_index()
        movie_2.drop(columns='index',inplace=True)
        recom = improved_recommendations(movie_name,movie_2)
        for i in recom:
            st.write(i)
    elif option=='year':
        movie_2=movie[movie['year']==number]
        a=movie[movie['title']==movie_name].index[0]
        b = movie_2.index
        if (a not in b):
            movie_2.loc[a]=movie.loc[a]
        movie_2= movie_2.reset_index()
        movie_2.drop(columns='index',inplace=True)
        recom = improved_recommendations(movie_name,movie_2)
        for i in recom:
            st.write(i)

