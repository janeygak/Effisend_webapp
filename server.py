# from jinja2 import StrictUndefined

from flask import Flask, flash, render_template, request, redirect, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Country, Rate, RicePrice, CountryCode, WaterPrice, Company
import math
from datetime import timedelta
from pytz import country_timezones
from delorean import Delorean
import os
from twilio.rest import TwilioRestClient


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# app.jinja_env.undefined = StrictUndefined
JS_TESTING_MODE = False


@app.before_request
def add_tests():
    g.jasmine_tests = JS_TESTING_MODE


@app.route('/')
def index():
    """Redirects to the search page."""

    return redirect('/search')


@app.route('/sorry')
def sorry():
    """Placeholder for countries with no data. User can opt to receive email when country is available"""

    return render_template('sorry.html')


@app.route('/search')
def search():
    """Show the landing page which allows users to select the country and amount they want to send"""

    country = request.args.get('country')
    return render_template('search.html', country=country)


@app.route('/stats')
def world_wide_stats():
    """Page with displays amount of money sent from the US and Cost of Living around the world."""

    #Due to the many, many ways country names are written, a SQLAlchemy join is not possible so using native SQL
    outflow = db.engine.execute("SELECT country_code_iso3, amount FROM us_outflows JOIN country_codes ON us_outflows.receiving_country = country_codes.name order by amount")
    #pass the data into a dictionary
    outflow2 = dict((str(y), str(x)) for y, x in outflow)

    # dictlist = []

    # for key, value in outflow2.iteritems():
    #     temp = [key, value]
    #     if value is None:
    #         value = 'None'
    #     dictlist.append(temp)

    jsonify(outflow2=outflow2)
    #set the cost of living function to be called so both maps can be displayed on one page
    col = show_cost_of_living_map()

    return render_template("stats.html", outflow=outflow2, col=col)


def show_cost_of_living_map():
    """code that queries the cost of living database and returns data for d3 map"""

    wwcol = db.engine.execute("SELECT country_code_iso3, col FROM world_coli JOIN country_codes ON world_coli.country_name = country_codes.name order by col")

    wwcol2 = dict((str(y), str(x)) for y, x in wwcol)

    jsonify(wwcol2=wwcol2)

    return wwcol2


@app.route('/sms', methods=['GET', 'POST'])
def send_sms():
    """Twiio API call to send an sms to a phone number"""

    account_sid = os.environ['TWILIO_SID']
    auth_token = os.environ['TWILIO_TOKEN']

    client = TwilioRestClient(account_sid, auth_token)

    input_number = request.form.get('input_number')

    amount = session['amount']

    time = request.form.get('time')

    company = request.form.get('company')

    message = client.messages.create(to=input_number, from_="+14242420403",
                                     body="Hi! I am sending you $%s via %s. It should be available at %s" % (amount, company, time))

    return "Your SMS has been sent!"


@app.route('/best_rate', methods=['GET'])
def get_user_inputs():
    """Get user inputs and determine how to calculate their best rates"""

    #assigns the users country and amount to variables
    country = request.args.get('country')
    country_name = Country.query.filter_by(country_code=country).one().name
    #query another table to get the currency code for the receiver's country
    currency = CountryCode.query.filter_by(country_code_iso3=country).one().currency
    #save user's country to their browser session for use later
    session['country'] = country_name

    #because there are two different kinds of country codes, each used by different libraries/data, this saves the 2-digit format of the country code
    country_code_iso2 = CountryCode.query.filter_by(country_code_iso3=country).one().country_code_iso2
    session['country_code'] = country_code_iso2

    #set the user's amount to a variable
    amount = int(request.args.get('amount'))

    #save user's amount to their browser session for use later
    session['amount'] = amount
    #get the user's speed preference
    speed = request.args.get('speed')
    #get the user's preferred payment method (if any)
    payment_method = request.args.get('payment_method')
    #determine the receiver's timezone
    receivers_timezone = (country_timezones(country_code_iso2)[0])

    #determine which rate to use depending on input amount
    if amount <= 200:
        column_to_use = 'rate_under_200'
        use_under_200 = True
    elif amount < 3000:
        column_to_use = 'rate_over_200'
        use_under_200 = False
    else:
        # forward to error if amount greater than 3000
        return "error! too much money. :("

    #code for querying the database based on user speed and payment type parameters
    if payment_method != "any" and speed == 'quickly':
        results = Rate.query.filter(Rate.country_code == country, Rate.transaction_time == 'Less than one hour', Rate.transaction_type.like('%'+payment_method+'%')).order_by(column_to_use)
    elif payment_method == "any" and speed == 'quickly':
        results = Rate.query.filter(Rate.country_code == country, Rate.transaction_time == 'Less than one hour').order_by(column_to_use)
    elif payment_method != "any" and speed != 'quickly':
        results = Rate.query.filter(Rate.country_code == country, Rate.transaction_type.like('%'+payment_method+'%')).order_by(column_to_use)
    else:
        results = Rate.query.filter_by(country_code=country).order_by(column_to_use)

    best_data = get_best_rate(results, amount, use_under_200, receivers_timezone)

    amt_of_rice, days_fed = calculate_rice_price(country_name, amount)

    second_best_data = get_second_best_rate(results, amount, receivers_timezone)

    num_of_bottles, water_needed = calculate_water_price(country_name, amount)

    return render_template("best_rate.html",
                           amount=amount,
                           best_data=best_data,
                           num_of_bottles=num_of_bottles,
                           water_needed=water_needed,
                           amt_of_rice=amt_of_rice,
                           days_fed=days_fed,
                           second_best_data=second_best_data,
                           currency=currency)


def get_best_rate(results, amount, use_under_200, receivers_timezone):

    #if inputed country is not in database then redirect to sorry page
    if results.count() == 0:

        return redirect('/sorry')
    #if country in database, continue query for best company
    else:
        best_company = str(results.first().company)
    #assigns what the best rate is based on the given amount
    if use_under_200:
        best_rate = str(results.first().rate_under_200)
    else:
        best_rate = str(results.first().rate_over_200)

    #calculate fees using the rate and user's inputted amount
    estimate_fees = ((float(best_rate) * .01) * amount)
    #and round it to the cents
    estimate_fees = round(estimate_fees, 2)
    #calculate total amount the transaction will cost the sender
    total_estimate = estimate_fees + amount
    #query the database for the link to the transfer company website
    best_URL = Company.query.filter(Company.company_name == best_company).one().link
    #if the company is not in the database, create a link using the company name
    if best_URL == '':

        best_URL = "http://" + best_company.replace(" ", "") + ".com"

    #set the queried rate payment method to a variable
    payment_method = results.first().transaction_type

    #query how long the method will take
    transaction_speed = results.first().transaction_time

    receive_date_time = calculate_receive_time(transaction_speed, receivers_timezone)

    return {'best_company': best_company,
            'best_rate': best_rate,
            'estimate_fees': estimate_fees,
            'total_estimate': total_estimate,
            'best_URL': best_URL,
            'payment_method': payment_method,
            'transaction_speed': transaction_speed,
            'receive_date_time': receive_date_time,
            }


def calculate_water_price(country_name, amount):
    """Calculate the price of water in receiver's country"""

    #if receiver's country water price is in table, query the table
    country_water_price = WaterPrice.query.filter_by(country_name=country_name)

    if country_water_price.count() > 0:

        num_of_bottles = (amount / country_water_price.one().water_price)

        num_of_bottles = int(num_of_bottles)
        #calculate how much water the user's amount will buy and last for one person
        water_needed = num_of_bottles / 2

        water_needed = int(water_needed)

    return num_of_bottles, water_needed


def calculate_rice_price(country_name, amount):
    """Given the sending amount and receiver's country, calculate the price
    of rice there and number of days it could feed a family, using data from freerice.com"""

    #query the price of rice table using the receiver's country
    country_rice_price = RicePrice.query.filter_by(country_name=country_name)

    """if the receiver's country's rice price is in the table, calculate how much rice the sender's
    amount will buy and how many days it will feed a family of four"""

    if country_rice_price.count() > 0:

        amt_of_rice = (amount / country_rice_price.one().rice_price)

        amt_of_rice = (math.ceil(amt_of_rice*100)/100)

        amt_of_rice = int(amt_of_rice)

        days_fed = amt_of_rice / 1.6

        days_fed = int(days_fed)

    return amt_of_rice, days_fed


def get_second_best_rate(results, amount, receivers_timezone):
    """Given user's preferences, return the second best option"""
    second_best_rate = results.offset(1).limit(1).all()

    company = second_best_rate[0].company

    if company == results[0].company:
        second_best_rate = results.offset(2).limit(1).all()

    fee = second_best_rate[0].rate_under_200

    estimate_fees = ((float(fee) * .01) * amount)

    estimate_fees = round(estimate_fees, 2)

    total = ((float(fee) * .01) * amount) + amount

    total = round(total, 2)

    transaction_speed = second_best_rate[0].transaction_time

    payment_method = second_best_rate[0].transaction_type

    URL = Company.query.filter(Company.company_name == company).one().link

    if URL == '':
        URL = "http://" + company.replace(" ", "") + ".com"

    receive_date_time = calculate_receive_time(transaction_speed, receivers_timezone)

    return {'second_best_comp': company,
            'second_best_fee': fee,
            'second_best_estimate_fees': estimate_fees,
            'second_best_total': total,
            'second_best_transaction_speed': transaction_speed,
            'second_best_payment_method': payment_method,
            'receive_date_time': receive_date_time,
            'second_best_URL': URL,
            }


def calculate_receive_time(transaction_speed, receivers_timezone):
    """Given a rate, calculate the receive time"""
    time_in_utc = Delorean()

    if transaction_speed == 'Less than one hour':
        time_in_utc += timedelta(hours=1)
    elif transaction_speed == '2 days':
        time_in_utc += timedelta(days=2)
    elif transaction_speed == '3-5 days':
        time_in_utc += timedelta(days=5)
    elif transaction_speed == 'Same day':
        time_in_utc += timedelta(hours=2)
    elif transaction_speed == 'Next day':
        time_in_utc += timedelta(hours=24)
    elif transaction_speed == '6 days or more':
        time_in_utc += timedelta(days=6)

    receive_date_time = (time_in_utc.shift(receivers_timezone))
    receive_date_time = receive_date_time.format_datetime(locale='en_US')

    return receive_date_time


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    # app.run()

    import sys
    if sys.argv[-1] == "jstest":
        JS_TESTING_MODE = True

    app.run(debug=True)
