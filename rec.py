import random
import copy
import numpy as np
from random import seed, sample, shuffle, randint

# N: total number of recipes, 18000 recipes
def sample_recipes(df, ids):
    # seed random number generator
    # seed(1) -- same results each time
    # generate 10 integers
    indices = []
    for _ in range(10):
        indices.append(randint(0, 17999))
    # 10 recipes to show to user
    sample_recipes = [(df[df.id == ids[idx]].title.iloc[0],
                       df[df.id == ids[idx]].url.iloc[0], idx) for idx in indices]
    return sample_recipes


# use idx of the selected recipes to recommend ten more recipes
# user in webapp can pick up to three recipes they like
# approach, get top 10 recipes similar to the selected ones
# shuffle from the collection if more than 10 total recommended recipes

def get_sim_recs_combined(df, sim_matrix, ids, *choices):
    """
    Input: choices of indices of of recipes selected by the users
    Output: list of 10 tuples (title, url, idx)
    """
    recommend_recipes = []  # tuples (title, url, idx)
    N = 10
    # an array of n sim_matrix_row (n recipes, each has one row in sim matrix)
    sim_matrix_n_recipes = np.empty((0, 18000), int)
    titles, urls, selected_ids, idxs = [], [], [], []
    for i in choices:
        sim_matrix_n_recipes = np.append(
            sim_matrix_n_recipes, np.array([sim_matrix[i]]), axis=0)
    # print(sim_matrix_n_recipes.shape)
    # use aggregate function to add the cosine similarity row for each of the selected recipes
    sim_matrix_agg = sim_matrix_n_recipes.sum(axis=0)  # add element wise
    # print(sim_matrix_agg.shape)
    most_similar_rec = np.argpartition(sim_matrix_agg, -N)[-N:]
    most_similar_ids = [ids[j] for j in most_similar_rec]
    titles.extend(df[df.id.isin(most_similar_ids)].title.values)
    urls.extend(df[df.id.isin(most_similar_ids)].url)
    selected_ids.extend(df[df.id.isin(most_similar_ids)].id)
    # print(ids)
    # get the idx of ids, can be used to get more similar recipes based on the idx
    idxs = [ids.index(i) for i in selected_ids]
    # merge three lists into a list of tuples
    rec_list = list(tuple(zip(titles, urls, idxs)))
    # get 10 random recipes from the rec_list
    random.shuffle(rec_list)
    # return rec_list[:10] # 10 tuples (title, url)
    return rec_list
