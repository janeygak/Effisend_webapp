"""Utility file to seed regions database"""

# from sqlalchemy import func
from model import Country
from model import Company
from model import Rate
from model import CountryInflow
from model import RicePrice
from model import CountryCode

from model import connect_to_db, db
from server import app
import csv


def load_rice_prices():

    print "World rice prices"

    RicePrice.query.delete()

    for row in csv.reader(open("data_files/worldwide_1kg_rice_prices.csv")):
        country_name = row[0]
        rice_price = float(row[1])

        rice_data = RicePrice(country_name=country_name, rice_price=rice_price)

        db.session.add(rice_data)

    db.session.commit()


def load_inflows():

    print "Remittance inflows"

    CountryInflow.query.delete()

    for row in csv.reader(open("data_files/world_inflows.csv")):
        country_name = row[0]

        amt_2014 = row[45].strip(",")

        if row[45] == "..":
            amt_2014 = None
        else:
            amt_2014 = float(amt_2014)

        share_gdp_2014 = row[48].strip("%")

        if row[48] == "..":
            share_gdp_2014 = None
        else:
            share_gdp_2014 = share_gdp_2014

        inflow = CountryInflow(country_name=country_name, amt_2014=amt_2014, share_gdp_2014=share_gdp_2014)

        db.session.add(inflow)

    db.session.commit()


def load_countries_list():

    print "Countries"

    Country.query.delete()

    for row in csv.reader(open("data_files/country_data.csv")):
        country_code = row[0]
        name = row[1]
        region = row[2]
        income_group = row[3]

        country = Country(country_code=country_code, name=name, region=region, income_group=income_group)

        db.session.add(country)

    db.session.commit()


def load_country_codes():

    print "Country Codes"

    CountryCode.query.delete()

    for row in csv.reader(open("data_files/full_country_codes.csv")):
        name = row[1]
        currency = row[4]
        country_code_iso2 = row[6]
        country_code_iso3 = row[7]

        country_code = CountryCode(country_code_iso2=country_code_iso2, country_code_iso3=country_code_iso3, name=name, currency=currency)

        db.session.add(country_code)

    db.session.commit()


def load_companies_list():

    print "Companies"

    Company.query.delete()

    for row in open("data_files/companies.csv"):
        row = row.strip()
        row = row.split(",")

        name = row[0]
        code = row[1]
        URL = row[2]

        company = Company(name=name, URL=URL, code=code)

        db.session.add(company)

    db.session.commit()


def load_rates():

    print "Rates"

    Rate.query.delete()

    for row in csv.reader(open("data_files/rate_data.csv")):
        country_code = row[0]
        country_name = row[1]
        region = row[2]
        income_group = row[3]
        company = row[4]
        company_type = row[5]
        transaction_type = row[6]
        transaction_time = row[7]
        rate_under_200 = float(row[9])

        if row[11] == "":
            rate_over_200 = rate_under_200
        else:
            rate_over_200 = float(row[11])

        rate_date = row[13]

        rate = Rate(country_code=country_code,
                    country_name=country_name,
                    region=region,
                    income_group=income_group,
                    company=company,
                    company_type=company_type,
                    transaction_type=transaction_type,
                    transaction_time=transaction_time,
                    rate_under_200=rate_under_200,
                    rate_over_200=rate_over_200,
                    rate_date=rate_date
                    )

        db.session.add(rate)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data

    load_country_codes()
    load_rice_prices()
    load_inflows()
    load_countries_list()
    load_companies_list()
    load_rates()
