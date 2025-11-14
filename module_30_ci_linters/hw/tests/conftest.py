import pytest
from app import create_app, db
from app.models import Client, Parking, ClientParking
from datetime import datetime, timedelta


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db
        db.session.rollback()


@pytest.fixture
def sample_client(db_session):
    client = Client(
        name='John',
        surname='Doe',
        credit_card='1234567890123456',
        car_number='A123BC'
    )
    db_session.session.add(client)
    db_session.session.commit()
    return client


@pytest.fixture
def sample_parking(db_session):
    parking = Parking(
        address='Test Street 123',
        opened=True,
        count_places=50,
        count_available_places=50
    )
    db_session.session.add(parking)
    db_session.session.commit()
    return parking


@pytest.fixture
def sample_client_parking(db_session, sample_client, sample_parking):
    client_parking = ClientParking(
        client_id=sample_client.id,
        parking_id=sample_parking.id,
        time_in=datetime.utcnow() - timedelta(hours=2)
    )
    db_session.session.add(client_parking)
    sample_parking.count_available_places -= 1
    db_session.session.commit()
    return client_parking