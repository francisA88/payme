# Webhook handler for Flutterwave charge.completed events

import logging
import uuid
import os
import pathlib, dotenv
import smtplib

import requests
import flask
from flask import request, jsonify, redirect

from db import *
from authmanager import AuthManager, env_path

authmanager = AuthManager()

print("CLIENT ID FROM APP: ", 	os.environ["FLW_CLIENT_ID"])
FLUTTERWAVE_BASE_URL = 'https://api.flutterwave.cloud/f4bexperience'


app = flask.Flask(__name__, static_folder='static', static_url_path='/static', template_folder="templates")


# Webhook handler for Flutterwave charge.completed events
@app.route('/webhook', methods=['POST'])
def flutterwave_webhook():
	event = request.get_json()
	signature = request.headers.get('flutterwave-signature')
	if signature != authmanager.credentials["hash"]:
		logging.warning("Invalid webhook signature")
		return jsonify({'status': 'error', 'message': 'Invalid signature'}), 400
	
	logging.info(f"Received webhook: {event}")
	if event.get('type') == 'charge.completed':
		data = event.get('data', {})
		charge_id = data.get('id')
		headers = {
			"Authorization": f"Bearer {authmanager.get_access_token()}",
			"Accept": "application/json"
		}
		# Verify payment using Flutterwave charges endpoint
		try:
			resp = requests.get(f"{FLUTTERWAVE_BASE_URL}/charges/{charge_id}", headers=headers, timeout=10)
			resp.raise_for_status()
			result = resp.json()
			charge = result.get('data', {})
			# Verification checks
			if (
				charge.get('status') == 'succeeded' and
				charge.get('amount') == data.get('amount') and
				charge.get('currency') == data.get('currency') and
				charge.get('customer_id') == data.get('customer', {}).get('id') and
				charge.get('reference') == data.get('reference')
			):
				logging.info(f"Payment verified for reference: {charge.get('reference')}")
				# TODO: Update payment status in your database here
				# TODO: Send email notification
				return jsonify({'status': 'success', 'verified': True}), 200
			else:
				logging.warning(f"Payment verification failed for charge: {charge_id}")
				return jsonify({'status': 'error', 'verified': False}), 400
		except requests.RequestException as e:
			logging.error(f"Verification request failed: {str(e)}")
			return jsonify({'status': 'error', 'message': str(e)}), 500
	return jsonify({'status': 'ignored'}), 200


@app.route('/static/<path:filename>')
def serve_static(filename):
	return flask.send_from_directory('static', filename)

# Index route to serve index.html
@app.route('/')
def index():
	return flask.render_template('index.html')

@app.route('/success/<path:reference>')
def success(reference):
	data = fetch_virtual_account_by_reference(reference)
	if not data:
		return flask.abort(404)
	return flask.render_template('success.html', **data)

@app.route('/payment/<path:reference>')
def payment(reference):
	data = fetch_virtual_account_by_reference(reference)
	if not data:
		return flask.abort(404)
	print(data)
	return flask.render_template('payment.html', **data)

# Helper: Validate customer input
def validate_customer_data(data):
	required_fields = ['first_name', 'last_name', 'phone', 'email']
	for field in required_fields:
		if field not in data or not data[field]:
			return False, f"Missing field: {field}"
	return True, None


# Endpoint: Create customer as well as virtual account
@app.route('/api/create_customer', methods=['POST'])
def create_customer():
	print("go here")
	data = request.form
	valid, error = validate_customer_data(data)
	if not valid:
		return jsonify({'status': 'error', 'message': error}), 400

	# Prepare payload for Flutterwave
	payload = {
		"name": {
			"first": data['first_name'],
			"last": data['last_name']
		},
		"email": data['email'],
		"meta": {
			"phone_number": data['phone']
	    }
	}

	headers = {
		"Content-Type": "application/json",
		"accept": "application/json",
		"Authorization": f"Bearer {authmanager.get_access_token()}",
		"X-Idempotency-Key": str(uuid.uuid4())
	}

	try:
		customer_result = create_flutterwave_customer(payload, headers)
		if customer_result.get('status') == 'success':
			cus_data = customer_result['data']
			if isinstance(cus_data, list): customer_id = customer_result['data'][0]['id']
			else: customer_id = customer_result['data']['id']
			# Generate the virtual account here
			va_result = create_flutterwave_virtual_account(customer_id)
			if va_result.get('status') == 'success':
				va_data = va_result['data']
				# Store in sqlite3
				store_virtual_account_in_db(customer_id, data, va_data)
				return redirect(f'/payment/{va_data.get("reference")}')
			else:
				return jsonify({'status': 'error', 'message': va_result.get('message', 'Virtual account creation failed')}), 400
		else:
			return jsonify({'status': 'error', 'message': customer_result.get('message', 'Unknown error')}), 400
	except Exception as e:
		print("Got herer?")
		return jsonify({'status': 'error', 'message': str(e)}), 500


# --- Helper functions ---
def create_flutterwave_customer(payload, headers):
	resp = requests.post(f"{FLUTTERWAVE_BASE_URL}/customers", json=payload, headers=headers, timeout=10)
	if resp.status_code == 201:
		return resp.json()
	elif resp.status_code == 409:
		resp = requests.get(f"{FLUTTERWAVE_BASE_URL}/customers", params={"email": payload['email']}, headers=headers, timeout=10)
		if resp.status_code != 200:
			resp.raise_for_status()
		return resp.json()
	
	resp.raise_for_status()
	return resp.json()

def create_flutterwave_virtual_account(customer_id):# data):
	# print(data)
	print("cusssid: ", customer_id)
	expiry_seconds = 1800  # 30 minutes
	reference = str(uuid.uuid4())
	va_payload = {
		"reference": reference,
		"customer_id": customer_id,
		"expiry": expiry_seconds,
		"amount": 100,
		"currency": "NGN",
		"account_type": "dynamic",
		"narration": "Sapa Reduction Scheme",
	}
	va_headers = {
		"Authorization": f"Bearer {authmanager.get_access_token()}",
		"X-Idempotency-Key": str(uuid.uuid4()),
		"Content-Type": "application/json",
	}
	# print(va_headers)
	# print(va_payload)
	va_resp = requests.post(f"{FLUTTERWAVE_BASE_URL}/virtual-accounts", json=va_payload, headers=va_headers, timeout=10)
	va_resp.raise_for_status()
	return va_resp.json()

