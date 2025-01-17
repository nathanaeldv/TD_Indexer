# main.py
from web3 import Web3
import os
import sqlite3  # Import nécessaire pour la partie Flask qui interroge la BDD
from dotenv import load_dotenv
from time import sleep

load_dotenv()

# Import Flask et les fonctions nécessaires
from flask import Flask, jsonify, request, render_template
# Import de toutes les fonctions utiles depuis db.py (dont get_all_events)
from db import init_db, save_event, get_all_events
import threading

#  listen http://127.0.0.1:5000/front or http://localhost:5000/front 

# Connexion au nœud Ethereum
ETH_NODE_URL ="https://eth-mainnet.g.alchemy.com/v2/Wr6Tvk0lVFSbJfE9ex7adjiVSfsLOMy7"
w3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))

# Adresse du contrat et signature de l'événement
CONTRACT_ADDRESS = "0x0000000071727de22e5e9d8baf0edac6f37da032"
EVENT_ABI = [{"inputs":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"ret","type":"bytes"}],"name":"DelegateAndRevert","type":"error"},{"inputs":[{"internalType":"uint256","name":"opIndex","type":"uint256"},{"internalType":"string","name":"reason","type":"string"}],"name":"FailedOp","type":"error"},{"inputs":[{"internalType":"uint256","name":"opIndex","type":"uint256"},{"internalType":"string","name":"reason","type":"string"},{"internalType":"bytes","name":"inner","type":"bytes"}],"name":"FailedOpWithRevert","type":"error"},{"inputs":[{"internalType":"bytes","name":"returnData","type":"bytes"}],"name":"PostOpReverted","type":"error"},{"inputs":[],"name":"ReentrancyGuardReentrantCall","type":"error"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"SenderAddressResult","type":"error"},{"inputs":[{"internalType":"address","name":"aggregator","type":"address"}],"name":"SignatureValidationFailed","type":"error"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"bytes32","name":"userOpHash","type":"bytes32"},{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":False,"internalType":"address","name":"factory","type":"address"},{"indexed":False,"internalType":"address","name":"paymaster","type":"address"}],"name":"AccountDeployed","type":"event"},{"anonymous":False,"inputs":[],"name":"BeforeExecution","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"},{"indexed":False,"internalType":"uint256","name":"totalDeposit","type":"uint256"}],"name":"Deposited","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"bytes32","name":"userOpHash","type":"bytes32"},{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":False,"internalType":"uint256","name":"nonce","type":"uint256"},{"indexed":False,"internalType":"bytes","name":"revertReason","type":"bytes"}],"name":"PostOpRevertReason","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"aggregator","type":"address"}],"name":"SignatureAggregatorChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"},{"indexed":False,"internalType":"uint256","name":"totalStaked","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"unstakeDelaySec","type":"uint256"}],"name":"StakeLocked","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"},{"indexed":False,"internalType":"uint256","name":"withdrawTime","type":"uint256"}],"name":"StakeUnlocked","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"},{"indexed":False,"internalType":"address","name":"withdrawAddress","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"StakeWithdrawn","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"bytes32","name":"userOpHash","type":"bytes32"},{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":True,"internalType":"address","name":"paymaster","type":"address"},{"indexed":False,"internalType":"uint256","name":"nonce","type":"uint256"},{"indexed":False,"internalType":"bool","name":"success","type":"bool"},{"indexed":False,"internalType":"uint256","name":"actualGasCost","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"actualGasUsed","type":"uint256"}],"name":"UserOperationEvent","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"bytes32","name":"userOpHash","type":"bytes32"},{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":False,"internalType":"uint256","name":"nonce","type":"uint256"}],"name":"UserOperationPrefundTooLow","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"bytes32","name":"userOpHash","type":"bytes32"},{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":False,"internalType":"uint256","name":"nonce","type":"uint256"},{"indexed":False,"internalType":"bytes","name":"revertReason","type":"bytes"}],"name":"UserOperationRevertReason","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"},{"indexed":False,"internalType":"address","name":"withdrawAddress","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdrawn","type":"event"},{"inputs":[{"internalType":"uint32","name":"unstakeDelaySec","type":"uint32"}],"name":"addStake","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"delegateAndRevert","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"depositTo","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"deposits","outputs":[{"internalType":"uint256","name":"deposit","type":"uint256"},{"internalType":"bool","name":"staked","type":"bool"},{"internalType":"uint112","name":"stake","type":"uint112"},{"internalType":"uint32","name":"unstakeDelaySec","type":"uint32"},{"internalType":"uint48","name":"withdrawTime","type":"uint48"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"getDepositInfo","outputs":[{"components":[{"internalType":"uint256","name":"deposit","type":"uint256"},{"internalType":"bool","name":"staked","type":"bool"},{"internalType":"uint112","name":"stake","type":"uint112"},{"internalType":"uint32","name":"unstakeDelaySec","type":"uint32"},{"internalType":"uint48","name":"withdrawTime","type":"uint48"}],"internalType":"struct IStakeManager.DepositInfo","name":"info","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"uint192","name":"key","type":"uint192"}],"name":"getNonce","outputs":[{"internalType":"uint256","name":"nonce","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes","name":"initCode","type":"bytes"}],"name":"getSenderAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"bytes","name":"initCode","type":"bytes"},{"internalType":"bytes","name":"callData","type":"bytes"},{"internalType":"bytes32","name":"accountGasLimits","type":"bytes32"},{"internalType":"uint256","name":"preVerificationGas","type":"uint256"},{"internalType":"bytes32","name":"gasFees","type":"bytes32"},{"internalType":"bytes","name":"paymasterAndData","type":"bytes"},{"internalType":"bytes","name":"signature","type":"bytes"}],"internalType":"struct PackedUserOperation","name":"userOp","type":"tuple"}],"name":"getUserOpHash","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"bytes","name":"initCode","type":"bytes"},{"internalType":"bytes","name":"callData","type":"bytes"},{"internalType":"bytes32","name":"accountGasLimits","type":"bytes32"},{"internalType":"uint256","name":"preVerificationGas","type":"uint256"},{"internalType":"bytes32","name":"gasFees","type":"bytes32"},{"internalType":"bytes","name":"paymasterAndData","type":"bytes"},{"internalType":"bytes","name":"signature","type":"bytes"}],"internalType":"struct PackedUserOperation[]","name":"userOps","type":"tuple[]"},{"internalType":"contract IAggregator","name":"aggregator","type":"address"},{"internalType":"bytes","name":"signature","type":"bytes"}],"internalType":"struct IEntryPoint.UserOpsPerAggregator[]","name":"opsPerAggregator","type":"tuple[]"},{"internalType":"address payable","name":"beneficiary","type":"address"}],"name":"handleAggregatedOps","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"bytes","name":"initCode","type":"bytes"},{"internalType":"bytes","name":"callData","type":"bytes"},{"internalType":"bytes32","name":"accountGasLimits","type":"bytes32"},{"internalType":"uint256","name":"preVerificationGas","type":"uint256"},{"internalType":"bytes32","name":"gasFees","type":"bytes32"},{"internalType":"bytes","name":"paymasterAndData","type":"bytes"},{"internalType":"bytes","name":"signature","type":"bytes"}],"internalType":"struct PackedUserOperation[]","name":"ops","type":"tuple[]"},{"internalType":"address payable","name":"beneficiary","type":"address"}],"name":"handleOps","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint192","name":"key","type":"uint192"}],"name":"incrementNonce","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"callData","type":"bytes"},{"components":[{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"verificationGasLimit","type":"uint256"},{"internalType":"uint256","name":"callGasLimit","type":"uint256"},{"internalType":"uint256","name":"paymasterVerificationGasLimit","type":"uint256"},{"internalType":"uint256","name":"paymasterPostOpGasLimit","type":"uint256"},{"internalType":"uint256","name":"preVerificationGas","type":"uint256"},{"internalType":"address","name":"paymaster","type":"address"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"uint256","name":"maxPriorityFeePerGas","type":"uint256"}],"internalType":"struct EntryPoint.MemoryUserOp","name":"mUserOp","type":"tuple"},{"internalType":"bytes32","name":"userOpHash","type":"bytes32"},{"internalType":"uint256","name":"prefund","type":"uint256"},{"internalType":"uint256","name":"contextOffset","type":"uint256"},{"internalType":"uint256","name":"preOpGas","type":"uint256"}],"internalType":"struct EntryPoint.UserOpInfo","name":"opInfo","type":"tuple"},{"internalType":"bytes","name":"context","type":"bytes"}],"name":"innerHandleOp","outputs":[{"internalType":"uint256","name":"actualGasCost","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint192","name":"","type":"uint192"}],"name":"nonceSequenceNumber","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"unlockStake","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"withdrawAddress","type":"address"}],"name":"withdrawStake","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"withdrawAddress","type":"address"},{"internalType":"uint256","name":"withdrawAmount","type":"uint256"}],"name":"withdrawTo","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=EVENT_ABI
)

if not w3.is_connected():
    print("Erreur : Impossible de se connecter au nœud Ethereum")
else:
    print("Connexion réussie !")
    
def listen_to_events(w3, contract):
    from_block = 21629245
    to_block = 21629250
    for block in range(from_block, to_block):
        try:
            events = contract.events.UserOperationEvent().get_logs(from_block=block, to_block=block)
            for event in events:
                processed_event = {
                    "userOpHash": event.args.userOpHash.hex(),
                    "sender": event.args.sender,
                    "paymaster": event.args.paymaster,
                    "nonce": str(event.args.nonce),
                    "success": event.args.success,
                    "actualGasCost": event.args.actualGasCost,
                    "actualGasUsed": event.args.actualGasUsed,
                    "blockNumber": event.blockNumber,
                }
                print(f"Nouvel événement : {processed_event}")
                save_event(processed_event)
            latest_block = w3.eth.block_number + 1
        except Exception as e:
            print(f"Erreur : {e}")
            continue
        finally:
            sleep(1)
        


from flask import Flask, jsonify, request
from db import init_db, save_event
import threading

app = Flask(__name__)

@app.route("/events", methods=["GET"])
def get_events():
    conn = sqlite3.connect("user_operations.db")
    cursor = conn.cursor()
    query = "SELECT * FROM user_operations WHERE 1=1"
    params = []

    if "sender" in request.args:
        query += " AND sender = ?"
        params.append(request.args["sender"])

    if "paymaster" in request.args:
        query += " AND paymaster = ?"
        params.append(request.args["paymaster"])

    cursor.execute(query, params)
    events = cursor.fetchall()
    conn.close()
    return jsonify(events)

# Nouvelle route pour afficher la page HTML
@app.route("/front", methods=["GET"])
def front():
    """Affiche un tableau HTML listant tous les événements."""
    events = get_all_events()  # Lecture de tous les enregistrements de la BDD
    return render_template("events_front.html", events=events)

# Initialiser la base de données
init_db()

# Lancer l'écoute des événements dans un thread séparé
listener_thread = threading.Thread(target=listen_to_events, args=(w3, contract), daemon=True)
listener_thread.start()

# Lancer le serveur Flask
app.run(debug=True)
listen_to_events(w3, contract)
