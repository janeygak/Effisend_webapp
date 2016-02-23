from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class RicePrice(db.Model):
    """Average price of one kilo of white rice in country for year 2015"""

    __tablename__ = "rice_prices"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    country_name = db.Column(db.String(200), nullable=False)
    rice_price = db.Column(db.Float, nullable=False)


class Country(db.Model):
    """Every country in the world, the region they belong to, and their income group, according to World Bank"""

    __tablename__ = "countries"

    country_code = db.Column(db.String(25), primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    income_group = db.Column(db.String(100), nullable=False)

    def __repr__(self):

        return "<%s - %s\n - %s - %s>" % (self.country_code, self.name, self.region, self.income_group)


class CountryCode(db.Model):
    """Because some data utilizes ISO-2 country codes while others use ISO-3- this contains both for records."""

    __tablename__ = "country_codes"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    country_code_iso2 = db.Column(db.String(25), nullable=False)
    country_code_iso3 = db.Column(db.String(25), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    currency = db.Column(db.String(100), nullable=False)


class Company(db.Model):
    """Money Transfer Companies, their id, and their URL. This table is currently unused."""

    __tablename__ = "companies"

    # company_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    code = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    URL = db.Column(db.String(500), nullable=True)

    def __repr__(self):

        return "<%s - %s \n %s \n %s>" % (self.code, self.name, self.URL)


class Rate(db.Model):
    """The rates associated with each country, company, and amount"""

    __tablename__ = "rates"

    rate_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    country_code = db.Column(db.String(20), nullable=False)
    country_name = db.Column(db.String(100), nullable=False)
    income_group = db.Column(db.String(100))
    region = db.Column(db.String(300), nullable=False)
    company = db.Column(db.String(300), nullable=False)
    company_type = db.Column(db.String(200))
    transaction_type = db.Column(db.String(200))
    transaction_time = db.Column(db.String(200))
    rate_under_200 = db.Column(db.Float)
    rate_over_200 = db.Column(db.Float)
    rate_date = db.Column(db.String(20))

    # code = db.Column(db.String(5), db.ForeignKey('companies.code'))
    # company = db.relationship("Company", backref=db.backref("rates", order_by=rate_id))

    # def __repr__(self):

    #     return "<%s - %s - %s>" % (self.code, self.region, self.fee)


class CountryInflow(db.Model):

    __tablename__ = "worldinflows"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    country_name = db.Column(db.String(100))
    amt_2014 = db.Column(db.Float, nullable=True)
    share_gdp_2014 = db.Column(db.String(100), nullable=True)


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///money_transfers'
#    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    db.create_all()
    print "Connected to DB."
