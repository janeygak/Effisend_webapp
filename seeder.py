"""Utility file to seed regions database"""

# from sqlalchemy import func
from model import Country
from model import Company
from model import Rate

from model import connect_to_db, db
from server import app


def load_countries_list():

    print "Countries"

    Country.query.delete()

    for row in open("data_files/country_data.csv"):
        row = row.strip()
        row = row.split(",")

        country_code = row[0]
        name = row[1]
        region = row[2]
        income_group = row[3]

        country = Country(country_code=country_code, name=name, region=region, income_group=income_group)

        db.session.add(country)

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

    for row in open("data_files/rate_data.csv"):
        row = row.strip()
        row = row.split(",")

        country_code = row[0]
        country_name = row[1]
        region = row[2]
        income_group = row[3]
        company = row[4]
        company_type = row[5]
        transaction_type = row[6]
        transaction_time = row[7]
        rate_under_200 = float(row[9])
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

    load_countries_list()
    load_companies_list()
    load_rates()
