from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_pymongo import PyMongo
from web3 import Web3, HTTPProvider
import secrets
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['MONGO_URI'] = 'mongodb+srv://gargadi456:adishgarg@cluster0.efzbcpd.mongodb.net/'
mongo = PyMongo(app)

infura_url = 'https://mainnet.infura.io/v3/6530f65ceacf41639b976ef61182ee5b'

# Create a web3.py instance
web3 = Web3(HTTPProvider(infura_url))

latest_block_number = web3.eth.block_number
print("Latest block number:", latest_block_number)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'adishgarg'
app.config['MYSQL_DB'] = 'login_registers'
mysql = MySQL(app)

@app.route('/')
def home():
    if 'username' in session:
        return render_template('login.html', username=session['username'])
    else:
        return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method =='POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute(f"select username, password from information where username = '{username}'")
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[1]:
            session['username'] = user[0]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error = 'invalid username or password')
    
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
