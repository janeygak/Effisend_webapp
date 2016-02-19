from jinja2 import StrictUndefined

from flask import Flask, render_template, request, redirect, session
# from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Country, Company, Rate, RicePrice

import math


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return "<html><body>Placeholder for the homepage.</body></html>"


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
    """charts.js"""

    return render_template("stats.html")


@app.route('/best_rate', methods=['GET'])
def best_rate():
    """Given the country return the best rate/company/speed"""

    #assigns the users country and amount to variables
    country = request.args.get('country')
    country_name = Country.query.filter_by(country_code=country).one().name

    #save user's country to their browser session
    session['country'] = country_name

    #set the user's amount to a variable
    amount = int(request.args.get('amount'))

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

    #once rate column is selected, assign the result to a variable
    result = Rate.query.filter_by(country_code=country).order_by(column_to_use)

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

    total_estimate = estimate_fees + amount

    transaction_speed = result.first().transaction_time

    payment_method = result.first().transaction_type

    second_best_rate = result.offset(1).limit(1).all()

    second_best_comp = second_best_rate[0].company

    second_best_fee = second_best_rate[0].rate_under_200

    second_best_estimate_fees = ((float(second_best_fee) * .01) * amount)

    second_best_total = ((float(second_best_fee) * .01) * amount) + amount

    second_best_transaction_speed = second_best_rate[0].transaction_time

    second_best_payment_method = second_best_rate[0].transaction_type

    result_country_rice_price = RicePrice.query.filter_by(country_name=country_name)

    if result_country_rice_price.count() == 0:
        pass
    else:
        amt_of_rice = (amount / country_rice_price.one().rice_price)

        amt_of_rice = (math.ceil(amt_of_rice*100)/100)

        amt_of_rice_whole = int(amt_of_rice)

        days_fed = amt_of_rice / 1.6

        days_fed = int(days_fed)

    return render_template("best_rate.html",
                           best_company=best_company,
                           best_rate=best_rate,
                           estimate_fees=estimate_fees,
                           total_estimate=total_estimate,
                           transaction_speed=transaction_speed,
                           payment_method=payment_method,
                           second_best_comp=second_best_comp,
                           second_best_fee=second_best_fee,
                           second_best_estimate_fees=second_best_estimate_fees,
                           second_best_total=second_best_total,
                           second_best_transaction_speed=second_best_transaction_speed,
                           second_best_payment_method=second_best_payment_method,
                           amt_of_rice_whole=amt_of_rice_whole,
                           amt_of_rice=amt_of_rice,
                           days_fed=days_fed)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()
