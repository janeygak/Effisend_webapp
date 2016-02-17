from jinja2 import StrictUndefined

from flask import Flask, render_template, request, redirect
# from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Country, Company, Rate


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


@app.route('/search')
def search():
    """Show the landing page which allows users to select the country"""

    country = request.args.get('country')
    return render_template('search.html', country=country)




@app.route('/rates')
def movie_list():
    """Show list of rates."""

    rates = Rate.query.all()
    return render_template("rates_list.html", rates=rates)


@app.route('/best_rate', methods=['GET'])
def best_rate():
    """Given the country return the best rate/company/speed"""

    country = request.args.get('country')
    amount = int(request.args.get('amount'))

    if amount <= 200:
        column_to_use = 'rate_under_200'
        use_under_200 = True
    elif amount < 3000:
        column_to_use = 'rate_over_200'
        use_under_200 = False
    else:
        # forward to error
        return "error! too much money. :("

    result = Rate.query.filter_by(country_code=country).order_by(column_to_use)

    if result.count() == 0:
        return "No service data for that country :("
    else:
        best_company = str(result.first().company)

    if use_under_200:
        best_rate = str(Rate.query.filter_by(country_code=country).order_by(column_to_use).first().rate_under_200)
    else:
        best_rate = str(Rate.query.filter_by(country_code=country).order_by(column_to_use).first().rate_over_200)

    estimate_fees = ((float(best_rate) * .01) * amount)

    total_estimate = estimate_fees + amount

    transaction_speed = result.first().transaction_time

    payment_method = result.first().transaction_type

    other_rates = result.offset(1).limit(1).all()

    other_comp = other_rates[0].company

    other_fee = other_rates[0].rate_under_200

    other_estimate_fees = ((float(other_fee) * .01) * amount)

    other_total = ((float(other_fee) * .01) * amount) + amount

    return render_template("best_rate.html",
                            best_company=best_company,
                            best_rate=best_rate,
                            estimate_fees=estimate_fees,
                            total_estimate=total_estimate,
                            transaction_speed=transaction_speed,
                            payment_method=payment_method,
                            other_rates=other_rates,
                            other_comp=other_comp,
                            other_fee=other_fee,
                            other_estimate_fees=other_estimate_fees,
                            other_total=other_total)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()
