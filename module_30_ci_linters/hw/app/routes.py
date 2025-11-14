from flask import jsonify, request
from app import db
from app.models import Client, Parking, ClientParking  # Исправленный импорт
from datetime import datetime


def init_routes(app):
    @app.route('/clients', methods=['GET'])
    def get_clients():
        clients = Client.query.all()
        return jsonify([{
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        } for client in clients])

    @app.route('/clients/<int:client_id>', methods=['GET'])
    def get_client(client_id):
        client = Client.query.get_or_404(client_id)
        return jsonify({
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        })

    @app.route('/clients', methods=['POST'])
    def create_client():
        data = request.get_json()

        client = Client(
            name=data['name'],
            surname=data['surname'],
            credit_card=data.get('credit_card'),
            car_number=data.get('car_number')
        )

        db.session.add(client)
        db.session.commit()

        return jsonify({
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        }), 201

    @app.route('/parkings', methods=['POST'])
    def create_parking():
        data = request.get_json()

        parking = Parking(
            address=data['address'],
            opened=data.get('opened', True),
            count_places=data['count_places'],
            count_available_places=data['count_available_places']
        )

        db.session.add(parking)
        db.session.commit()

        return jsonify({
            'id': parking.id,
            'address': parking.address,
            'opened': parking.opened,
            'count_places': parking.count_places,
            'count_available_places': parking.count_available_places
        }), 201

    @app.route('/client_parkings', methods=['POST'])
    def enter_parking():
        data = request.get_json()
        client_id = data['client_id']
        parking_id = data['parking_id']

        client = Client.query.get_or_404(client_id)
        parking = Parking.query.get_or_404(parking_id)

        if not parking.opened:
            return jsonify({'error': 'Parking is closed'}), 400

        if parking.count_available_places <= 0:
            return jsonify({'error': 'No available places'}), 400

        existing_parking = ClientParking.query.filter_by(
            client_id=client_id,
            parking_id=parking_id,
            time_out=None
        ).first()

        if existing_parking:
            return jsonify({'error': 'Client is already on this parking'}), 400

        client_parking = ClientParking(
            client_id=client_id,
            parking_id=parking_id,
            time_in=datetime.utcnow()
        )

        parking.count_available_places -= 1

        db.session.add(client_parking)
        db.session.commit()

        return jsonify({
            'id': client_parking.id,
            'client_id': client_parking.client_id,
            'parking_id': client_parking.parking_id,
            'time_in': client_parking.time_in.isoformat()
        }), 201

    @app.route('/client_parkings', methods=['DELETE'])
    def exit_parking():
        data = request.get_json()
        client_id = data['client_id']
        parking_id = data['parking_id']

        client_parking = ClientParking.query.filter_by(
            client_id=client_id,
            parking_id=parking_id,
            time_out=None
        ).first_or_404()

        client = Client.query.get_or_404(client_id)
        parking = Parking.query.get_or_404(parking_id)

        if not client.credit_card:
            return jsonify({'error': 'No credit card attached to client'}), 400

        parking.count_available_places += 1
        client_parking.time_out = datetime.utcnow()

        parking_time = client_parking.time_out - client_parking.time_in
        hours = parking_time.total_seconds() / 3600

        db.session.commit()

        return jsonify({
            'id': client_parking.id,
            'client_id': client_parking.client_id,
            'parking_id': client_parking.parking_id,
            'time_in': client_parking.time_in.isoformat(),
            'time_out': client_parking.time_out.isoformat(),
            'parking_hours': round(hours, 2),
            'payment_processed': True
        })