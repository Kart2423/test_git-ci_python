import factory
from factory.alchemy import SQLAlchemyModelFactory
from app import db
from app.models import Client, Parking
import random


class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    credit_card = factory.LazyAttribute(lambda x: random.choice([
        None,
        factory.Faker('credit_card_number').generate({})
    ]))
    car_number = factory.Faker('license_plate')


class ParkingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    address = factory.Faker('address')
    opened = factory.Faker('boolean')
    count_places = factory.Faker('random_int', min=10, max=200)
    count_available_places = factory.LazyAttribute(lambda o: o.count_places)