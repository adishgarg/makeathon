from flask import Flask, render_template, request, jsonify
from web3 import Web3, HTTPProvider
from eth_account import Account
import json
import os

app = Flask(__name__)

# Replace the infura_url with a Polygon node URL
polygon_url = os.environ.get('POLYGON_URL', 'https://polygon-mainnet.infura.io/v3/6530f65ceacf41639b976ef61182ee5b')
web3 = Web3(HTTPProvider(polygon_url))

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        birth_date = request.form['birth_date']
        ulpin = request.form['ulpin']

        transaction_data = {
            'full_name': full_name,
            'phone_number': phone_number,
            'birth_date': birth_date,
            'ulpin': ulpin,
        }

        transaction_json = json.dumps(transaction_data)
        transaction_hex = transaction_json.encode().hex()

        # Use your private key for the Polygon network
        private_key = 'Your_Private_Key_Goes_Here'
        account = Account.from_key(private_key)
        sender_address = account.address

        nonce = web3.eth.get_transaction_count(sender_address)

        gas_limit = 200000000000000000000

        # Adjust the gas price for the Polygon network
        gas_price_wei = web3.toWei('50', 'gwei')

        tx = {
            'nonce': nonce,
            'to': '0x4dF605965eD98Ff80CDe50469a588B54D753249C',
            'value': 0,
            'gas': gas_limit,
            'gasPrice': gas_price_wei,
            'data': transaction_hex,
        }

        signed_txn = account.sign_transaction(tx)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        if tx_receipt.status:
            return jsonify({'message': 'Transaction successful', 'txhash': tx_hash.hex()}), 201
        else:
            return jsonify({'message': 'Transaction failed'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
