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
    """Given the country, find the region, and show the best rate for that region"""

    country = request.args.get('country')
    region = Country.query.filter_by(country_code=country).one().region
    best_company = str(Rate.query.filter_by(region=region).order_by('fee').first().company.name)
    best_rate = str(Rate.query.filter_by(region=region).order_by('fee').first().fee)
    return render_template("best_rate.html", best_company=best_company, best_rate=best_rate)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()
