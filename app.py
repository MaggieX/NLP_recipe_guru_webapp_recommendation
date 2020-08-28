import rec
import os
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_assets import Environment, Bundle
from flask import send_from_directory
# from flask_sqlalchemy import SQLAlchemy

import pickle
import numpy as np
from datetime import timedelta #set session time 
from scipy import sparse
from scipy.sparse import coo_matrix

# from sqlalchemy.ext.automap import automap_base
# import flask_whooshalchemy as wa
# from sqlalchemy import Column, Integer, String

############## Load Models & data ################
# similarity matrix from bag of words
with open("model/top10_BoW_similarity.pickle", 'rb') as f:
  bow_sim = pickle.load(f)

# sim matrix from doc2vec
# with open("model/doc2vec_similarity_mat.pickle", 'rb') as f:
with open("model/top10_d2v_similarity.pickle", 'rb') as f:
  d2v_sim = pickle.load(f)

# cleaned recipe dataframe with 18000 entries
with open("model/bow_recipes.pickle", 'rb') as file:
  df_bow = pickle.load(file)

with open("model/d2v_recipes.pickle", 'rb') as file:
  df_d2v = pickle.load(file)

############## Load Cosine Similarities #################
sim_matrix_bow = np.squeeze(np.asarray(bow_sim['cosine_similarities'].todense()))
ids_bow = bow_sim['ids']

sim_matrix_d2v = np.squeeze(np.asarray(d2v_sim['cosine_similarities'].todense()))
ids_d2v = d2v_sim['ids']

################### sqlalchemy ####################

# This creates a base we can inheret from
# Base = declarative_base()

##################### Flask ######################                

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

app.config['SECRET_KEY'] = 'the random string'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['DEBUG'] = True
app.config['WHOODH_BASE'] = 'whoosh'

# instantiate sqlalchemy
# db = SQLAlchemy(app)

"""
class Recipes(db.Model):
    #__tablename__ = "recipes“
    __searchable__ = ['title', 'id', 'ingredients', 'instructions']

    # sqlalchemy uses these names as the column namess
    url = db.Column(db.String)
    title = db.Column(db.String)
    id = db.Column(db.String, primary_key=True)
    ingredients = db.Column(db.String)
    instructions = db.Column(db.String)
wa.whoosh_index(app, Recipes)


# for flash, use cookies, need secret cookie that cookie is encrypted
app.secret_key = 'shhhhh'
app.permanent_session_lifetime = timedelta(minutes = 1)

## Approach 1: create recipes object with Reflect
# recipes = db.Table('RECIPES', db.metadata, autoload=True, autoload_with=db.engine)

# Approach 2:
#Base = automap_base()
## similar to reflecting the tables
# Base.prepare(db.engine, reflect=True)
# Recipes = Base.classes.RECIPES

# work with exisiting database
@app.route('/search')
def get_recipe():
    myRecipes = Recipes.query.whoosh_search(Recipes).all()
    for r in myRecipes:
      print(r)
    return render_template('search.html', myRecipes = myRecipes)
"""

@app.route('/')
def index():
    return redirect('/main')

@app.route('/main')
def main():
    return render_template("main.html")


@app.route("/login", methods=["POST", "GET"])
def login():
  if request.method == "POST":
    session.permanent = True  # if set the session permanent, turn on True flag
    user = request.form["nm"]  # use "nm" as dictionary key to get the name
    # store info in the session, session data deleted from the server once the browser is closed
    session["user"] = user
    return redirect(url_for("user"))
  else:
    if "user" in session:
      return redirect(url_for("user"))
    return render_template("login.html")


@app.route("/user")
def user():
  # check if any info in the session
  if "user" in session:
      user = session["user"]
      return f"<h1>{user}</h1>"
  else:
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
  session.pop("user", None)  # remove data
  return redirect(url_for("login"))


@app.route("/rec",  methods=['GET'])
def rec_get():
    if request.method == 'GET':
      # show 10 recommended recipes based on choices in the random 10 recipes
      # get the data of 10 random recipes
      sample_recipes_ten = rec.sample_recipes(df = df_bow, ids = ids_bow)
      return render_template('rec.html', sample_recipes=sample_recipes_ten)

@app.route("/rec",  methods=['POST'])
def recommend():
    # Save user's choices among the already recommended recipes, to continue recommending.
    if request.form.getlist('recipe_checkbox'): 
      checked_recipes_list = request.form.getlist('recipe_checkbox')
      checked_recipes = map(int, checked_recipes_list)
      top_10_recommend_new = rec.get_sim_recs_combined(df_bow, sim_matrix_bow, ids_bow, *checked_recipes)
      # save the new 10 recommendations to be shown once the "recommend more based on selections here" is clicked.
      # session["recs"] = top_10_recommend_new
      # return render_template("recommend_rec.html", rec = session["recs"])
      return render_template("recommend_rec.html", rec = top_10_recommend_new)
    # if user wants to get further recommendations but did not select any selections    
    else:
      flash("Oops, looks like you did not select any recipes. Here are more choices.")
      return redirect(url_for("rec_get"))
      # return redirect(url_for("rec_get"))
      # return render_template("rec.html")


@app.route("/rec2",  methods=['GET'])
def rec_get2():
    if request.method == 'GET':
      # show 10 recommended recipes based on choices in the random 10 recipes
      # get the data of 10 random recipes
      sample_recipes_ten = rec.sample_recipes(df=df_d2v, ids=ids_d2v)
      return render_template('rec.html', sample_recipes=sample_recipes_ten)


@app.route("/rec2",  methods=['POST'])
def recommend2():
    # Save user's choices among the already recommended recipes, to continue recommending.
    if request.form.getlist('recipe_checkbox'):
      checked_recipes_list = request.form.getlist('recipe_checkbox')
      checked_recipes = map(int, checked_recipes_list)
      top_10_recommend_new = rec.get_sim_recs_combined(
          df_d2v, sim_matrix_d2v, ids_d2v, *checked_recipes)
      # save the new 10 recommendations to be shown once the "recommend more based on selections here" is clicked.
      #session["recs"] = top_10_recommend_new
      #return render_template("recommend_rec.html", rec = session["recs"])
      return render_template("recommend_rec.html", rec=top_10_recommend_new)
    # if user wants to get further recommendations but did not select any selections
    else:
      flash("Oops, looks like you did not select any recipes. Here are more choices.")
      return redirect(url_for("rec_get2"))
      # return redirect(url_for("rec_get"))
      #return render_template("rec.html")

@app.route('/explore')
def pca():
    return render_template('explore.html')

@app.route('/rec_sample')
def rec_sample():
    return render_template('rec_sample.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/custom')
def custom():
  return render_template('custom.html')


@app.route('/main_original')
def main_original():
  return render_template('main_original.html')

#@app.errorhandler(404)
#def page_not_found(e):
#  return render_template('404.html'), 404

if __name__ == '__main__':
  app.run(port=33507)
  # app.debug = True
  # app.run()
