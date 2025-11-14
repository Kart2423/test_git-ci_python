import pytest
import json
from app.models import Client, Parking, ClientParking


class TestAPI:

    @pytest.mark.parametrize('url,expected_status', [
        ('/clients', 200),
        ('/clients/1', 200),
    ])
    def test_get_methods_status_code(self, client, sample_client, url, expected_status):
        response = client.get(url)
        assert response.status_code == expected_status

    def test_create_client(self, client, db_session):
        data = {
            'name': 'Alice',
            'surname': 'Smith',
            'credit_card': '1111222233334444',
            'car_number': 'B456CD'
        }

        response = client.post('/clients',
                               data=json.dumps(data),
                               content_type='application/json')

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['name'] == 'Alice'
        assert response_data['surname'] == 'Smith'
        assert Client.query.count() == 1

    def test_create_parking(self, client, db_session):
        data = {
            'address': 'New Parking Address',
            'opened': True,
            'count_places': 100,
            'count_available_places': 100
        }

        response = client.post('/parkings',
                               data=json.dumps(data),
                               content_type='application/json')

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['address'] == 'New Parking Address'
        assert response_data['count_places'] == 100
        assert Parking.query.count() == 1

    @pytest.mark.parking
    def test_enter_parking(self, client, sample_client, sample_parking):
        data = {
            'client_id': sample_client.id,
            'parking_id': sample_parking.id
        }

        response = client.post('/client_parkings',
                               data=json.dumps(data),
                               content_type='application/json')

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['client_id'] == sample_client.id
        assert response_data['parking_id'] == sample_parking.id

        # Проверяем, что количество свободных мест уменьшилось
        updated_parking = Parking.query.get(sample_parking.id)
        assert updated_parking.count_available_places == sample_parking.count_available_places - 1

    @pytest.mark.parking
    def test_exit_parking(self, client, sample_client_parking):
        data = {
            'client_id': sample_client_parking.client_id,
            'parking_id': sample_client_parking.parking_id
        }

        response = client.delete('/client_parkings',
                                 data=json.dumps(data),
                                 content_type='application/json')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['payment_processed'] == True
        assert 'time_out' in response_data

        # Проверяем, что количество свободных мест увеличилось
        parking = Parking.query.get(sample_client_parking.parking_id)
        assert parking.count_available_places == 50  # Изначальное значение

    def test_enter_closed_parking(self, client, sample_client, db_session):
        closed_parking = Parking(
            address='Closed Parking',
            opened=False,
            count_places=10,
            count_available_places=10
        )
        db_session.session.add(closed_parking)
        db_session.session.commit()

        data = {
            'client_id': sample_client.id,
            'parking_id': closed_parking.id
        }

        response = client.post('/client_parkings',
                               data=json.dumps(data),
                               content_type='application/json')

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Parking is closed' in response_data['error']

    def test_enter_parking_no_places(self, client, sample_client, db_session):
        full_parking = Parking(
            address='Full Parking',
            opened=True,
            count_places=10,
            count_available_places=0
        )
        db_session.session.add(full_parking)
        db_session.session.commit()

        data = {
            'client_id': sample_client.id,
            'parking_id': full_parking.id
        }

        response = client.post('/client_parkings',
                               data=json.dumps(data),
                               content_type='application/json')

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'No available places' in response_data['error']

    def test_exit_parking_no_credit_card(self, client, db_session):
        client_no_card = Client(
            name='NoCard',
            surname='Client',
            credit_card=None,
            car_number='C789DE'
        )
        parking = Parking(
            address='Test Parking',
            opened=True,
            count_places=50,
            count_available_places=49
        )
        client_parking = ClientParking(
            client_id=client_no_card.id,
            parking_id=parking.id,
            time_in=datetime.utcnow() - timedelta(hours=1)
        )

        db_session.session.add_all([client_no_card, parking, client_parking])
        db_session.session.commit()

        data = {
            'client_id': client_no_card.id,
            'parking_id': parking.id
        }

        response = client.delete('/client_parkings',
                                 data=json.dumps(data),
                                 content_type='application/json')

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'No credit card' in response_data['error']