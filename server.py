from jinja2 import StrictUndefined

from flask import Flask, flash, render_template, request, redirect, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Country, Rate, RicePrice, CountryCode, USOutflow, WaterPrice, Company

import math

from datetime import datetime, timedelta
from pytz import country_timezones
from delorean import Delorean
import os
from twilio.rest import TwilioRestClient


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
# app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

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
    """datamaps"""
    outflow = db.engine.execute("SELECT country_code_iso3, amount FROM us_outflows JOIN country_codes ON us_outflows.receiving_country = country_codes.name order by amount")

    outflow2 = dict((str(y), str(x)) for y, x in outflow)

    dictlist = []

    for key, value in outflow2.iteritems():
        temp = [key, value]
        if value is None:
            value = 'None'
        dictlist.append(temp)

    jsonify(outflow2=outflow2)

    return render_template("stats.html", outflow=outflow2)


@app.route('/sms', methods=['GET', 'POST'])
def send_sms():
    """Send an sms to a phone number"""

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


# app.jinja_env.globals.update(send_sms=send_sms)

@app.route('/best_rate', methods=['GET'])
def best_rate():
    """Given the country return the best rate/company/speed"""

    #assigns the users country and amount to variables
    country = request.args.get('country')
    country_name = Country.query.filter_by(country_code=country).one().name

    currency = CountryCode.query.filter_by(country_code_iso3=country).one().currency
    #save user's country to their browser session for use later
    session['country'] = country_name

    #because there are two different kinds of country codes, each used by different libraries/data, this saves the 2-digit format of the country code
    country_code_iso2 = CountryCode.query.filter_by(country_code_iso3=country).one().country_code_iso2
    session['country_code'] = country_code_iso2

    #set the user's amount to a variable
    amount = int(request.args.get('amount'))

    global amount
    #save user's amount to their browser session for use later
    session['amount'] = amount
    #get the user's speed preference
    speed = request.args.get('speed')
    #get the user's preferred payment method (if any)
    payment_method = request.args.get('payment_method')
    #determine the receiver's timezone
    receivers_timezone = (country_timezones(country_code_iso2)[0])
    global receivers_timezone
    #decide which rate to use depending on input amount
    if amount <= 200:
        column_to_use = 'rate_under_200'
        use_under_200 = True
    elif amount < 3000:
        column_to_use = 'rate_over_200'
        use_under_200 = False
    else:
        # forward to error if amount greater than 3000
        return "error! too much money. :("

    if payment_method != "any" and speed == 'quickly':
        result = Rate.query.filter(Rate.country_code == country, Rate.transaction_time == 'Less than one hour', Rate.transaction_type.like('%'+payment_method+'%')).order_by(column_to_use)
    elif payment_method == "any" and speed == 'quickly':
        result = Rate.query.filter(Rate.country_code == country, Rate.transaction_time == 'Less than one hour').order_by(column_to_use)
    elif payment_method != "any" and speed != 'quickly':
        result = Rate.query.filter(Rate.country_code == country, Rate.transaction_type.like('%'+payment_method+'%')).order_by(column_to_use)
    else:
    #once rate column is selected, assign the result to a variable
        result = Rate.query.filter_by(country_code=country).order_by(column_to_use)

    global result
    #check if inputed country is not in database and redirect to sorry page
    if result.count() == 0:

        return redirect('/sorry')
    #if country in database, continue query
    else:
        best_company = str(result.first().company)
    #assigns what the rate is based on the amount
    if use_under_200:
        best_rate = str(result.first().rate_under_200)
    else:
        best_rate = str(result.first().rate_over_200)

    estimate_fees = ((float(best_rate) * .01) * amount)

    estimate_fees = round(estimate_fees, 2)

    total_estimate = estimate_fees + amount

    best_URL = Company.query.filter(Company.company_name == best_company).one().link

    if best_URL is None:

        best_URL = "http://" + best_company.replace(" ", "") + ".com"

    transaction_speed = result.first().transaction_time

    current_time_in_utc = Delorean()

    if transaction_speed == 'Less than one hour':
        current_time_in_utc += timedelta(hours=1)
    elif transaction_speed == '2 days':
        current_time_in_utc += timedelta(days=2)
    elif transaction_speed == '3-5 days':
        current_time_in_utc += timedelta(days=5)
    elif transaction_speed == 'Same day':
        current_time_in_utc += timedelta(hours=2)
    elif transaction_speed == 'Next day':
        current_time_in_utc += timedelta(hours=24)
    elif transaction_speed == '6 days or more':
        current_time_in_utc += timedelta(days=6)

    estimated_receive_date_time = (current_time_in_utc.shift(receivers_timezone))
    estimated_receive_date_time = estimated_receive_date_time.format_datetime(locale='en_US')

    payment_method = result.first().transaction_type

    result_country_water_price = WaterPrice.query.filter_by(country_name=country_name)

    if result_country_water_price.count() > 0:

        num_of_bottles = (amount / result_country_water_price.one().water_price)

        num_of_bottles = int(num_of_bottles)

        water_needed = num_of_bottles / 2

        water_needed = int(water_needed)

    result_country_rice_price = RicePrice.query.filter_by(country_name=country_name)

    if result_country_rice_price.count() > 0:

        amt_of_rice = (amount / result_country_rice_price.one().rice_price)

        amt_of_rice = (math.ceil(amt_of_rice*100)/100)

        amt_of_rice_whole = int(amt_of_rice)

        days_fed = amt_of_rice / 1.6

        days_fed = int(days_fed)

    second_best_rate = result.offset(1).limit(1).all()

    second_best_comp = second_best_rate[0].company

    if second_best_comp == result[0].company:

        second_best_rate = result.offset(2).limit(1).all()

    second_best_fee = second_best_rate[0].rate_under_200

    second_best_estimate_fees = ((float(second_best_fee) * .01) * amount)

    second_best_estimate_fees = round(second_best_estimate_fees, 2)

    second_best_total = ((float(second_best_fee) * .01) * amount) + amount

    second_best_total = round(second_best_total, 2)

    second_best_transaction_speed = second_best_rate[0].transaction_time

    second_best_payment_method = second_best_rate[0].transaction_type

    second_current_time_in_utc = Delorean()

    if second_best_transaction_speed == 'Less than one hour':
        second_current_time_in_utc += timedelta(hours=1)
    elif second_best_transaction_speed == '2 days':
        second_current_time_in_utc += timedelta(days=2)
    elif second_best_transaction_speed == '3-5 days':
        second_current_time_in_utc += timedelta(days=5)
    elif second_best_transaction_speed == 'Same day':
        second_current_time_in_utc += timedelta(hours=2)
    elif second_best_transaction_speed == 'Next day':
        second_current_time_in_utc += timedelta(hours=24)
    elif second_best_transaction_speed == '6 days or more':
        second_current_time_in_utc += timedelta(days=6)

    second_estimated_receive_date_time = (second_current_time_in_utc.shift(receivers_timezone))
    second_estimated_receive_date_time = second_estimated_receive_date_time.format_datetime(locale='en_US')

    return render_template("best_rate.html",
                           amount=amount,
                           best_company=best_company,
                           best_rate=best_rate,
                           estimate_fees=estimate_fees,
                           total_estimate=total_estimate,
                           best_URL=best_URL,
                           transaction_speed=transaction_speed,
                           estimated_receive_date_time=estimated_receive_date_time,
                           payment_method=payment_method,
                           num_of_bottles=num_of_bottles,
                           water_needed=water_needed,
                           amt_of_rice_whole=amt_of_rice_whole,
                           amt_of_rice=amt_of_rice,
                           days_fed=days_fed,
                           second_best_comp=second_best_comp,
                           second_best_fee=second_best_fee,
                           second_best_estimate_fees=second_best_estimate_fees,
                           second_best_total=second_best_total,
                           second_best_transaction_speed=second_best_transaction_speed,
                           second_best_payment_method=second_best_payment_method,
                           second_estimated_receive_date_time=second_estimated_receive_date_time,
                           currency=currency)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run()
