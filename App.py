from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_pymongo import PyMongo
from web3 import Web3, HTTPProvider
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['MONGO_URI'] = 'mongodb+srv://gargadi456:adishgarg@cluster0.efzbcpd.mongodb.net/'
mongo = PyMongo(app)

infura_url = 'https://mainnet.infura.io/v3/6530f65ceacf41639b976ef61182ee5b'

# Create a web3.py instance
web3 = Web3(HTTPProvider(infura_url))

latest_block_number = web3.eth.block_number
print("Latest block number:", latest_block_number)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        user = mongo.db.users.find_one({'username': username})
        if user and pwd == user['password']:
            session['username'] = user['username']
            return redirect(url_for('login'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/form')
def form():
    if 'username' in session:
        return render_template('form.html')
    else:
        return redirect(url_for('login'))

@app.route('/properties', methods=['GET'])
def get_properties():
    if 'username' in session:
        properties = mongo.db.properties.find()
        result = []
        for prop in properties:
            result.append({
                'id': str(prop['_id']),
                'address': prop['address'],
                'owner_name': prop['owner_name'],
                'owner_contact': prop['owner_contact'],
                # Add more fields as needed
            })
        return jsonify(result)
    else:
        return redirect(url_for('login'))

@app.route('/properties', methods=['POST'])
def create_property():
    if 'username' in session:
        data = request.get_json()
        new_property = {
            'address': data['address'],
            'owner_name': data['owner_name'],
            'owner_contact': data['owner_contact']
            # Add more fields as needed
        }
        mongo.db.properties.insert_one(new_property)
        return jsonify({'message': 'Property created successfully'}), 201
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
