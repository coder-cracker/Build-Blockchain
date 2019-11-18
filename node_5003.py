import hashlib
import json
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse
import datetime
from abc import ABC, abstractmethod


class Interface(ABC):

    @abstractmethod
    def get_previous_block(self):
        pass

    @abstractmethod
    def create_block(self, proof, previous_hash):
        pass

    @abstractmethod
    def add_transaction(self, sender, receiver, amount):
        pass

    @abstractmethod
    def add_node(self, address):
        pass

    @abstractmethod
    def received_money(self, li):
        pass

    @abstractmethod
    def hash(self, block):
        pass

    @abstractmethod
    def is_chain_valid(self, chain):
        pass

    @abstractmethod
    def total_transaction(self):
        pass

    @abstractmethod
    def change_chain(self):
        pass

    @abstractmethod
    def replace_chain(self):
        pass


# Building a Blockchain

class Blockchain(Interface):

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.balance = 100
        self.nodes = set()
        self.tran_list = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        if amount <= self.balance:
            self.transactions.append({'sender': sender,
                                      'receiver': receiver,
                                      'amount': amount})
            self.balance -= amount
            self.tran_list.append(self.transactions[-1])
            return True
        return False

    def received_money(self, li):
        li_trans = li['transactions']
        for dictionary in li_trans:
            if dictionary['receiver'] == "5003":
                self.balance += dictionary['amount']
                self.tran_list.append(dictionary)

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def total_transaction(self):
        temp_transactions = self.transactions
        network = self.nodes
        for nodes in network:
            response = requests.get(f'http://{nodes}/total_transaction')
            if response.status_code == 200:
                tran_chain = response.json()['transactions']
                temp_transactions = tran_chain + temp_transactions
        self.transactions = list(temp_transactions)

    def change_chain(self):
        network = self.nodes
        flag = 0
        for node in network:
            response = requests.get(f'http://{node}/replace_chain')
            if response.status_code == 200:
                response1 = requests.get(f'http://{node}/get_chain')
                length = response1.json()['length']
                if length == len(self.chain):
                    flag = 1
                else:
                    flag = 3
            else:
                flag = 2
        return flag

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        self.transactions = []
        for nodes in network:
            response = requests.get(f'http://{nodes}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# Mining the Blockchain

# creating a Web app
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()


# Mining a Block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    blockchain.total_transaction()

    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    length = blockchain.change_chain()
    # blockchain.received_money(blockchain.chain[-1])
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions'],
                'length': length}
    return jsonify(response), 200


# Getting the full Blockchain

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# checking if Blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'We have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200


# Adding a new transaction to the Blockchain

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing.', 400
    bool_var = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
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


# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chain so the chain was replaced by longest chain.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    blockchain.received_money(blockchain.chain[-1])
    return jsonify(response), 200


@app.route('/check_balance', methods=['GET'])
def check_balance():
    response = {'transaction-history': blockchain.tran_list,
                'account_balance': blockchain.balance}
    return jsonify(response), 200


@app.route('/total_transaction', methods=['GET'])
def total_transaction():
    response = {'transactions': blockchain.transactions}
    return jsonify(response), 200


app.run(host='0.0.0.0', port=5003)
