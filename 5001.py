import hashlib
import json
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse

# Building a Blockchain

class Blockchain():
    def __init__(self):
        self.chain = []
        self.balance = 100
        self.nodes = set()
        self.tran_list = []
        self.transactions= []

    def add_transaction(self, receiver, amount):
        if amount <= self.balance:
            self.transactions.append({'receiver': receiver,
                                      'amount': amount})
            self.balance -= amount
            self.tran_list.append(self.transactions[-1])
            return True
        return False

    def received_money(self, li):
        li_trans = li['transactions']
        for dictionary in li_trans:
            if dictionary['receiver'] == "5001":
                self.balance += dictionary['amount']
                self.tran_list.append(dictionary)

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    
# creating a Web app
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Adding a new transaction to the Blockchain

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing.', 400
    bool_var = blockchain.add_transaction(json['receiver'],json['amount'])
    if bool_var:
        response = {'message': f'This transactions will be added to block {len(blockchain.chain) + 1}'}
        return jsonify(response), 201
    else:
        response = {
            'message': f'transaction is failed due to insufficient balance... and Your current balance is {blockchain.balance}'}
        return jsonify(response), 400


# Part 3- Decentralizing our Blockchain

# Connecting new nodes

@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No Node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Hadcoin Blockchain now contains the following node :',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


@app.route('/check_balance', methods=['GET'])
def check_balance():
    response = {'transaction-history': blockchain.tran_list,
                'account_balance': blockchain.balance}
    return jsonify(response), 200


@app.route('/total_transaction', methods=['GET'])
def total_transaction():
    response = {'transactions': blockchain.transactions}
    return jsonify(response), 200


@app.route('/change_chain',methods = ['POST'])
def change_chain():
    json = request.get_json()
    block = json.get('block')
    blockchain.chain.append(block) 
    response = {'message': 'Block is successfully mined....'}
    blockchain.received_money(block)
    blockchain.transactions = []
    return jsonify(response), 201

app.run(host='0.0.0.0', port=5001)

