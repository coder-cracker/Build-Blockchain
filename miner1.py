import hashlib
import json
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse
import datetime 

class Miner:
    def __init__(self):
        self.transactions = [] 
        self.nodes = ["http://127.0.0.1:5001","http://127.0.0.1:5002","http://127.0.0.1:5003"] 
        self.amount = 0 
        self.chain = []
        self.create_block(proof=1, previous_hash='0')
    
    def get_transactions(self):
        network =  self.nodes 
        flag = 0
        for nodes in network:
            response = requests.get(f'http://{nodes}/total_transactions')
            if response.status_code ==200:
                temp_trans = response.json()['transactions']
                self.transactions = self.transactions+ temp_trans
                self.transactions = list(set(self.transactions))
            else:
                return False
        return True

    def change_chain(self):
        block = self.chain[-1]
        network = self.nodes
        data = {'block':self.chain[-1]}
        for nodes in network:
            response = requests.post(f'http://{nodes}/change_chain',data)
            if response.status_code !=201:
                return False 
        return True
            
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
    

app = Flask(__name__)

block_miner = Miner()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    block_miner.get_transactions()
    previous_block = block_miner.get_previous_block()
    previous_proof = previous_block['proof']
    proof = block_miner.proof_of_work(previous_proof)
    previous_hash = block_miner.hash(previous_block)
    block = block_miner.create_block(proof, previous_hash)
    length = block_miner.change_chain()
    response = {'message': 'Congratulations, you just mined a block! and you also got 10 Hadcoins for successfully mining a block...',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions'],
                'length': length}
    block_miner.change_chain()
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = block_miner.is_chain_valid(block_miner.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'We have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200


app.run(host='0.0.0.0', port=1001)