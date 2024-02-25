const express = require('express');
const { Web3 } = require('web3');
const { Account } = require('eth-lib');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

module.exports = generateUniqueId;

function uuidToBytes32(uuid) {
    const cleanedUuid = uuid.replace(/-/g, '').toLowerCase();

    const paddedUuid = cleanedUuid.padEnd(64, '0');

    const bytes32Value = '0x' + paddedUuid;

    return bytes32Value;
}


const app = express();
const port = process.env.PORT || 3000;

app.use(express.static('public'));

function generateUniqueId() {
    return uuidv4();
}

const contractABI =[
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "sender",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "message",
				"type": "string"
			}
		],
		"name": "TransactionFailed",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "sender",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "txhash",
				"type": "uint256"
			}
		],
		"name": "TransactionSuccessful",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "_uuid",
				"type": "bytes32"
			}
		],
		"name": "getTransactionData",
		"outputs": [
			{
				"components": [
					{
						"internalType": "string",
						"name": "full_name",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "phone_number",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "birth_date",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "ulpin",
						"type": "string"
					}
				],
				"internalType": "struct FormSubmission.Transaction",
				"name": "",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_admin",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "_status",
				"type": "bool"
			}
		],
		"name": "setAdmin",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_full_name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_phone_number",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_birth_date",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_ulpin",
				"type": "string"
			},
			{
				"internalType": "bytes32",
				"name": "_uuid",
				"type": "bytes32"
			}
		],
		"name": "submitForm",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
];

const contractAddress = "0x358AA13c52544ECCEF6B0ADD0f801012ADAD5eE3";

const polygonURL = 'https://polygon-mumbai.infura.io/v3/6530f65ceacf41639b976ef61182ee5b';
const web3 = new Web3(new Web3.providers.HttpProvider(polygonURL));

app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/form.html');
});

app.post('/submit_form', async (req, res) => {
    try {
        const { full_name, phone_number, birth_date, ulpin } = req.body;

        const uniqueId = generateUniqueId();
        const uniqueIdBytes32 = uuidToBytes32(uniqueId);



        const contract = new web3.eth.Contract(contractABI, contractAddress);

        const encodedData = contract.methods.submitForm(
            full_name,
            phone_number,
            birth_date,
            ulpin,
            uniqueIdBytes32  
        ).encodeABI();

        const privateKey = "0x286db74e965ab5ac570ae3ac0097833df5c3aaf65058255672caf794672571c2";
        const account = web3.eth.accounts.privateKeyToAccount(privateKey);
        const senderAddress = account.address;

        const nonce = await web3.eth.getTransactionCount(senderAddress);
        const estimatedGas = await contract.methods.submitForm(
            full_name,
            phone_number,
            birth_date,
            ulpin,
            uniqueIdBytes32
        ).estimateGas();
        
        const txObject = {
            nonce: web3.utils.toHex(nonce),
            gasLimit: web3.utils.toHex(estimatedGas),
            gasPrice: web3.utils.toHex(web3.utils.toWei('0.00001', 'gwei')),
            to: contractAddress,
            data: encodedData
        };
        
        const signedTx = await account.signTransaction(txObject);
        const tx = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);

        console.log('Transaction hash:', tx.transactionHash);
        console.log('Generated Unique ID:', uniqueId);

        res.json({ message: 'Transaction successful', transactionHash: tx.transactionHash, uniqueId: uniqueId });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/transaction_data/:uuid', async (req, res) => {
    try {
        const { uuid } = req.params;

        const contract = new web3.eth.Contract(contractABI, contractAddress);

        const transactionData = await contract.methods.getTransactionData(web3.utils.fromAscii(uuid)).call();

        console.log('Transaction Data for UUID:', uuid);
        console.log('Full Name:', transactionData.full_name);
        console.log('Phone Number:', transactionData.phone_number);
        console.log('Birth Date:', transactionData.birth_date);
        console.log('ULPIN:', transactionData.ulpin);

        res.json(transactionData);
        res.send('POST request to /transaction_data/:uuid endpoint');
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/verification', (req, res) => {
    res.redirect('/verify.html');
  });
  

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
