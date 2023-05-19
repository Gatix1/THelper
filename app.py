import datetime

from flask import Flask, request, redirect, url_for
from flask import render_template
import parse
import os
import sqlite3
import parse
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
start = datetime.datetime.now()

def loadPhones(sort_col="title", search_text=None):
    db = sqlite3.connect("products.db")
    cursor = db.cursor()
    phones = []
    if search_text != None:
        print("SEARCH")
        phones = cursor.execute(f"""SELECT * FROM phones WHERE title LIKE '%{search_text}%' ORDER BY {sort_col}""").fetchall()
    else:
        phones = cursor.execute(
            f"""SELECT * FROM phones ORDER BY {sort_col}""").fetchall()
    db.commit()
    return phones


@app.route("/howlong")
def main():
    return str((datetime.datetime.now() - start).seconds / 60)


def loadLaptops(sort_col="title", search_text=None):
    db = sqlite3.connect("products.db")
    cursor = db.cursor()
    laptops = []
    if search_text != None:
        print("SEARCH")
        laptops = cursor.execute(
            f"""SELECT * FROM laptops WHERE title LIKE '%{search_text}%' ORDER BY {sort_col}""").fetchall()
    else:
        laptops = cursor.execute(
            f"""SELECT * FROM laptops ORDER BY {sort_col}""").fetchall()
    db.commit()
    return laptops


def init_app():
    print("Hi")


@app.route("/home")
def home_page():
    return render_template('home.html', title="THelper")

@app.route("/about")
def about_page():
    return render_template('about.html', title="About Page")

@app.route("/phones", methods=["GET", "POST"])
def phones_page():
    if request.method == 'POST':
        states = {}
        if 'title_sort' in request.form:
            phones = loadPhones("title")
            states['title'] = 'btn-secondary'
            states['price'] = 'btn-dark'
            states['ram'] = 'btn-dark'
            states['memory'] = 'btn-dark'
        elif 'price_sort' in request.form:
            phones = loadPhones("price")
            states['title'] = 'btn-dark'
            states['price'] = 'btn-secondary'
            states['ram'] = 'btn-dark'
            states['memory'] = 'btn-dark'
        elif 'ram_sort' in request.form:
            phones = loadPhones("ram")
            states['title'] = 'btn-dark'
            states['price'] = 'btn-dark'
            states['ram'] = 'btn-secondary'
            states['memory'] = 'btn-dark'
        elif 'memory_sort' in request.form:
            phones = loadPhones("memory")
            states['title'] = 'btn-dark'
            states['price'] = 'btn-dark'
            states['ram'] = 'btn-dark'
            states['memory'] = 'btn-secondary'
        return render_template('phones.html', title="Smartphones", phones=phones, state=states)

    else:
        states = {}
        states['title'] = 'btn-secondary'
        states['price'] = 'btn-dark'
        states['ram'] = 'btn-dark'
        states['memory'] = 'btn-dark'
        phones = loadPhones()
        return render_template('phones.html', title="Smartphones", state=states, phones=phones)

@app.route("/laptops", methods=["GET", "POST"])
def laptops_page():
    if request.method == 'POST':
        states = {}
        if 'title_sort' in request.form:
            laptops = loadLaptops("title")
            states['title'] = 'btn-secondary'
            states['price'] = 'btn-dark'
            states['ram'] = 'btn-dark'
            states['memory'] = 'btn-dark'
        elif 'price_sort' in request.form:
            laptops = loadLaptops("price")
            states['title'] = 'btn-dark'
            states['price'] = 'btn-secondary'
            states['ram'] = 'btn-dark'
            states['memory'] = 'btn-dark'
        elif 'ram_sort' in request.form:
            laptops = loadLaptops("ram")
            states['title'] = 'btn-dark'
            states['price'] = 'btn-dark'
            states['ram'] = 'btn-secondary'
            states['memory'] = 'btn-dark'
        elif 'memory_sort' in request.form:
            laptops = loadLaptops("memory")
            states['title'] = 'btn-dark'
            states['price'] = 'btn-dark'
            states['ram'] = 'btn-dark'
            states['memory'] = 'btn-secondary'
        return render_template('laptops.html', title="Smartphones", laptops=laptops, state=states)

    else:
        states = {}
        states['title'] = 'btn-secondary'
        states['price'] = 'btn-dark'
        states['ram'] = 'btn-dark'
        states['memory'] = 'btn-dark'
        laptops = loadLaptops()
        return render_template('laptops.html', title="Smartphones", state=states, laptops=laptops)


@app.route('/')
def redirect_home():
    return redirect("home")


@app.route('/search')  # 'GET' is the default method, you don't need to mention it explicitly
def search():

    # query = request.args['search']
    search_input = request.args['search_input']  # try this instead
    phones = loadPhones(search_text=search_input, sort_col='price')
    laptops = loadLaptops(search_text=search_input, sort_col='price')
    print(phones)
    print(laptops)
    return render_template('search.html', sort_product_type="Telefoane", phones=phones, laptops=laptops)


def reload_bd():
    parse.get_laptops()
    parse.get_phones()
    pass

def main():
    auto_reload_bd_scheduler = BackgroundScheduler()
    auto_reload_bd_scheduler.add_job(func=reload_bd, trigger="interval", seconds=86400)
    auto_reload_bd_scheduler.start()
    app.run(debug=True)
    atexit.register(lambda: auto_reload_bd_scheduler.shutdown())


main()