import pytest
from app.models import Client, Parking

# Импортируем фабрики после установки factory-boy
try:
    from tests.factories import ClientFactory, ParkingFactory

    FACTORY_BOY_AVAILABLE = True
except ImportError:
    FACTORY_BOY_AVAILABLE = False


@pytest.mark.skipif(not FACTORY_BOY_AVAILABLE, reason="factory-boy not installed")
class TestFactories:

    def test_create_client_with_factory(self, db_session):
        client = ClientFactory()

        assert client.id is not None
        assert client.name is not None
        assert client.surname is not None
        assert Client.query.count() == 1
        assert client.credit_card is None or isinstance(client.credit_card, str)

    def test_create_parking_with_factory(self, db_session):
        parking = ParkingFactory()

        assert parking.id is not None
        assert parking.address is not None
        assert isinstance(parking.opened, bool)
        assert parking.count_places >= 10
        assert parking.count_available_places == parking.count_places
        assert Parking.query.count() == 1

    def test_create_multiple_clients(self, db_session):
        clients = ClientFactory.create_batch(5)

        assert len(clients) == 5
        assert Client.query.count() == 5

        names = [client.name for client in clients]
        surnames = [client.surname for client in clients]
        assert len(set(names)) > 1 or len(set(surnames)) > 1

    def test_create_multiple_parkings(self, db_session):
        parkings = ParkingFactory.create_batch(3)

        assert len(parkings) == 3
        assert Parking.query.count() == 3

        for parking in parkings:
            assert parking.count_available_places == parking.count_places