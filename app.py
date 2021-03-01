'''
Check the cost of travelling by car.
Using database and free APIs to get neccessary data.
'''

import json
import http.client
import os
from dotenv import load_dotenv

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_heroku import Heroku

import psycopg2
import requests

load_dotenv()
COLLECT_APIKEY = os.environ['COLLECT_APIKEY']
HERE_APIKEY = os.environ['HERE_APIKEY']

app = Flask(__name__)
app.config.from_object('config.ProdConfig')

heroku = Heroku(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# connection = psycopg2.connect(
#     database=HEROKU_DATABASE,    #cfg.DATABASE
#     user=HEROKU_USER,   #cfg.DATABASE_USERNAME
#     password=HEROKU_PASSWORD,   #cfg.DATABASE_PASSWORD
#     host=HEROKU_HOST,       #cfg.DATABASE_HOST
#     port=HEROKU_PORT)       #cfg.DATABASE_PORT
# cursor = connection.cursor()
# connection = psycopg2.connect(HEROKU_DATABASE_URI, sslmode='require')

conn = http.client.HTTPSConnection('api.collectapi.com')


class Cars(db.Model):
    """ Database class. """
    __tablename__ = 'vehicles_dataset'
    city08 = db.Column(db.Float)
    co2TailpipeGpm = db.Column(db.Float)
    comb08 = db.Column(db.Float)
    displ = db.Column(db.Float)
    drive = db.Column(db.String(50))
    engId = db.Column(db.Float)
    fuelType = db.Column(db.String(50))
    fuelType1 = db.Column(db.String(50))
    highway08 = db.Column(db.Float)
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    mpgData = db.Column(db.String(50))
    trany = db.Column(db.String(50))
    UCity = db.Column(db.String(50))
    UHighway = db.Column(db.Float)
    year = db.Column(db.String(50))
    youSaveSpend = db.Column(db.Float)
    favourite = db.Column(db.Boolean, default=False)
    comb08l100 = db.Column(db.Float)

    def __repr__(self):
        return '<Car %r>' % self.id


def get_fuel_price(fuel_type):
    """
    Gets fuel price in EUR for given fuel_type (lpg, diesel, gasoline).
    GasPrice API.
    """
    # TODO: add price based on location of starting point
    try:
        headers = {
            'content-type': "application/json",
            'authorization': COLLECT_APIKEY
            }
        conn.request("GET", "/gasPrice/europeanCountries", headers=headers)
        result = conn.getresponse()
        response = json.load(result)
    except:
        return 'Could not get the price of the fuel'
    rate = float(response["results"][32][fuel_type].replace(',', '.'))
    return round(rate, 2)


def convert_price_pln(price_in_euro):
    """ Converts given price in EUR to PLN. ExchangeRates API. """
    try:
        r = requests.get('https://api.exchangeratesapi.io/latest?symbols=PLN')
        data = r.json()
    except:
        return 'Could not convert to PLN'
    rate = data['rates']['PLN']
    price = rate * price_in_euro
    return round(price, 2)


def get_place(place):
    """ Gets place details: coords, city, country etc. HERE API. """
    params = {'apikey': HERE_APIKEY, 'q': place}
    url = 'https://discover.search.hereapi.com/v1/geocode'
    try:
        r = requests.get(url=url, params=params)
        data = r.json()
    except:
        return 'Could not get place details'
    return data


def get_place_coord(place):
    """ Gets place coordinates from JSON format to string. """
    coord = place['items'][0]['position']
    return f'{coord["lat"]}, {coord["lng"]}'


def get_trip(search_origin, search_destination):
    """ Details about starting point, ending point and mileage. HERE API. """
    origin = get_place(search_origin)
    destination = get_place(search_destination)
    origin_coord = get_place_coord(origin)
    destination_coord = get_place_coord(destination)
    params = {
        'apikey': HERE_APIKEY,
        'origin': origin_coord,
        'destination': destination_coord,
        'transportMode': 'car',
        'return': 'summary'
        }
    url = 'https://router.hereapi.com/v8/routes'
    try:
        r = requests.get(url=url, params=params)
        data = r.json()
    except:
        return 'Could not get route'
    length = data['routes'][0]['sections'][0]['summary']['length']
    duration = data['routes'][0]['sections'][0]['summary']['baseDuration']
    trip = {
        'origin': origin['items'][0]['title'],
        'destination': destination['items'][0]['title'],
        'mileage': round(length/1000),
        'duration': round(duration/3600, 2)
        }
    return trip


@app.route('/')
def index():
    """ Main site with calculation form. Shows favourite cars. """
    records = Cars.query.filter(Cars.favourite == True)
    return render_template("index.html", records=records)


@app.route('/calculate', methods=['POST', 'GET'])
def calculate():
    """ Pass the infomation needed to calculate cost of the trip. """
    if request.method == 'GET':
        chosen_car_id = request.args.get('chosen_car_id', type=int)
        car = Cars.query.get_or_404(chosen_car_id)

        passengers = request.args.get('passengers', default=0, type=int)

        origin = request.args.get('origin')
        destination = request.args.get('destination')
        trip = get_trip(origin, destination)
        mileage = trip['mileage']
        origin_descr = trip['origin']
        destination_descr = trip['destination']
        duration = trip['duration']

        if 'there_and_back' in request.form:
            mileage = mileage * 2

        fuel_price = get_fuel_price(car.fuelType1)
        price_in_pln = convert_price_pln(fuel_price)
        total_cost = round((car.comb08l100 * mileage * price_in_pln)/100, 2)
        cost_per_user = total_cost/(passengers+1)

        return render_template(
            'results.html',
            origin_descr=origin_descr,
            destination_descr=destination_descr,
            chosen_car_make=car.make,
            chosen_car_model=car.model,
            car_displ=car.displ,
            avg_consumption=car.comb08l100,
            fuel_type=car.fuelType1,
            fuel_price=fuel_price,
            price_in_pln=price_in_pln,
            total_cost=total_cost,
            cost_per_user=cost_per_user,
            mileage=mileage,
            duration=duration
            )
    else:
        return render_template('results.html')


@app.route('/table', methods=['POST', 'GET'])
def table():
    """ Shows database. """
    # TODO: merge with /search
    page = request.args.get('page', default=1, type=int)
    records = Cars.query.order_by(Cars.id).paginate(per_page=10, page=page)
    first_page = url_for('table', page=1)
    next_page = url_for('table', page=records.next_num)
    prev_page = url_for('table', page=records.prev_num)
    last_page = url_for('table', page=records.pages)
    last_page_str = records.pages
    return render_template(
        "table.html",
        records=records.items,
        next_page=next_page,
        prev_page=prev_page,
        last_page=last_page,
        last_page_str=last_page_str,
        first_page=first_page
        )


@app.route('/search', methods=['GET', 'POST'])
def search():
    """ Search database for given car. """
    if request.method == "GET":
        request_make = request.args.get('search_make')
        request_model = request.args.get('search_model')
        records = Cars.query
        filters = {
            'search_by_make': Cars.make.ilike(request_make),
            'search_by_model': Cars.model.ilike(request_model)
            }
        if request_make != '':
            records = records.filter(filters['search_by_make'])
        if request_model != '':
            records = records.filter(filters['search_by_model'])
        records.order_by(Cars.id)
        count = records.count()
        return render_template('table.html', records=records, count=count)


@app.route('/add_new_car', methods=['POST', 'GET'])
def add_new_car():
    """ Adds new car to the databse. """
    # TODO: ADD MESSAGE: ADDED NEW CAR
    if request.method == 'POST':
        car_make = request.form['car_make']
        car_model = request.form['car_model']
        car_displ = request.form['car_displ']
        car_year = request.form['car_year']
        car_fuelType = request.form['car_fuelType']
        car_comb08l100 = request.form['car_comb08l100']
        new_car = Cars(
            make=car_make,
            model=car_model,
            displ=car_displ,
            year=car_year,
            fuelType1=car_fuelType,
            comb08l100=float(car_comb08l100),
            favourite=True
            )
        try:
            db.session.add(new_car)
            db.session.commit()
            return redirect('/table')
        except:
            return 'Error: Could not add a new car'


@app.route('/delete/<int:id>')
def delete(id):
    """ Deletes car from database. """
    car_to_delete = Cars.query.get_or_404(id)
    try:
        db.session.delete(car_to_delete)
        db.session.commit()
        return redirect('/table')
    except:
        return 'There was a problem deleting that car'


@app.route('/add_to_favourite/<int:id>')
def add_to_favourite(id):
    """ Adds car to favourite. """
    car_to_favourite = Cars.query.get_or_404(id)
    car_to_favourite.favourite = True
    try:
        db.session.commit()
        return redirect('/table')
    except:
        return 'There was an issue adding your car to favourite'


@app.route('/remove_from_favourite/<int:id>')
def remove_from_favourite(id):
    """ Removes car from favourite. """
    car_from_favourite = Cars.query.get_or_404(id)
    car_from_favourite.favourite = False
    try:
        db.session.commit()
        return redirect('/table')
    except:
        return 'There was an issue removing your car from favourite'


@app.route('/about')
def about():
    """ About page. """
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=True)
