#! /bin/python

import grpc
from IrohaUtils import *
from IrohaHashCustodian import Custodian
import logging
import json
from time import sleep


def wait_point(msg):
    input(f"{bcolors.OKGREEN}===> {msg}{bcolors.ENDC}")


# INFO gives descriptions of steps
# DEBUG gives information on transactions and queries too
logging.basicConfig(level=logging.INFO)

logging.info("Create hash custodian")
while True:
    try:
        custodian = Custodian(blockstore_threading=True)
        break
    except grpc._channel._InactiveRpcError:
        logging.info("Network unreachable, retrying")
        sleep(2)

logging.info("Create user Alice")
user_a = custodian.new_hashing_user("alice")
logging.info("Create user Bob")
user_b = custodian.new_hashing_user("bob")

domain_name = custodian._parse_domain_name("message")

wait_point("Alice creates a message, and sends this to Bob")
message = "Hello, World!"
logging.info(f"Message:\n{message}")
wait_point("Alice also hashes the message and stores the hash on chain")
message_hash = custodian.get_hash(message)
logging.info(f"{message_hash=}")
logging.info("Storing hash...")
status = custodian.store_hash_on_chain(user_a, message_hash, domain_name=domain_name)
assert status[0] == "COMMITTED"
logging.info(f"Message hash successfully logged in new domain {domain_name}")

wait_point("Bob, having received the message from Alice, wants to verify it")
received_hash = custodian.get_hash(message)
chain_asset = custodian.get_domain_hashes(domain_name=domain_name)[-1]
logging.info(f"Received Hash {received_hash}")
logging.info(f"Blockchain Info:\n{json.dumps(chain_asset, indent=2)}")
wait_point("Bob can see the two hashes are the same, and trusts the message")

print("\n\n")

wait_point("Alice changes the message slightly, sending Bob the new message")
message+="\n---Foobar---"
logging.info(f"Message: \n{message}")
wait_point("Alice again hashes and stores the hash in the same domain")
new_message_hash = custodian.get_hash(message)
logging.info(f"{new_message_hash=}")
logging.info("Storing hash...")
status = custodian.store_hash_on_chain(user_a, new_message_hash, domain_name=domain_name)
assert status[0] == "COMMITTED"
logging.info(f"Message hash successfully updated in {domain_name}")

wait_point("Bob, with a new message from Alice, wants to verify it")
received_hash = custodian.get_hash(message)
chain_asset = custodian.get_domain_hashes(domain_name=domain_name)[-1]
logging.info(f"Received Hash {received_hash}")
logging.info(f"Blockchain Info:\n{json.dumps(chain_asset, indent=2)}")
wait_point("Bob can see the two hashes are the same, and again trusts the message")

print("\n\n")

wait_point("A new user Mallory joins")
logging.info("Create user Mallory")
user_m = custodian.new_hashing_user("mal")

domain_name = custodian._parse_domain_name("mal-message")

wait_point("Mallory claims Bob owes her a small sum of money")
mal_message = "Bob owes Mallory $1,000,000"
logging.info(f"{mal_message=}")
wait_point("Mallory sends this message only to Alice, leaving Bob out")
mal_message_hash = custodian.get_hash(mal_message)
logging.info(f"{mal_message_hash=}")
logging.info("Storing hash...")
status = custodian.store_hash_on_chain(user_m, mal_message_hash, domain_name=domain_name)
assert status[0] == "COMMITTED"
logging.info(f"Message hash successfully stored in {domain_name}")

wait_point("Alice checks the received hash against the blockchain")
alice_received_hash = custodian.get_hash(mal_message)
logging.info(f"Received hash {alice_received_hash}")
chain_asset = custodian.get_domain_hashes(domain_name=domain_name)
logging.info(f"Blockchain info:\n{json.dumps(chain_asset, indent=2)}")
wait_point("Alice sees the hashes are the same, and believes Bob owes Mallory")

wait_point("Mallory changes the message and sends this to Bob instead")
mal_message = "Hello, Bob!"
logging.info(f"{mal_message=}")
wait_point("Mallory has two options:\n\t1) Do not store the new hash on chain")
logging.info("Bob checks received message against chain information")
bob_received_hash = custodian.get_hash(mal_message)
chain_asset = custodian.get_domain_hashes(domain_name=domain_name)
logging.info(f"Received hash {bob_received_hash}")
logging.info(f"Blockchain info:\n{json.dumps(chain_asset, indent=2)}")
logging.info("The hashes are different, so Bob knows he is being tricked")

wait_point("\t2) Do store the new hash on chain")
mal_message_hash = custodian.get_hash(mal_message)
logging.info(f"{mal_message_hash=}")
logging.info("Storing hash...")
status = custodian.store_hash_on_chain(user_m, mal_message_hash, domain_name=domain_name)
assert status[0] == "COMMITTED"
logging.info(f"Message hash successfully stored in {domain_name}")
logging.info("Bob checks received message against chain information")
bob_received_hash = custodian.get_hash(mal_message)
chain_asset = custodian.get_domain_hashes(domain_name=domain_name)
logging.info(f"Bob received hash {bob_received_hash}")
logging.info(f"Blockchain info:\n{json.dumps(chain_asset, indent=2)}")
wait_point("Bob sees the most recent hash matches, so trusts the message\n(But may be suspicious because of the earlier hash he did not receive)")

wait_point("Alice and Bob now convene, and Alice states Bob owes Mallory, which Bob disputes")
logging.info("Alice and Bob exchange their received hashes")
logging.info(f"Alice received hash {alice_received_hash}")
logging.info(f"Bob received hash {bob_received_hash}")
logging.info("Alice and Bob see their hashes (and hence messages) are not the same")
wait_point("Because Alice and Bob both verified their received messages, they check the chain again")
logging.info(f"Alice received hash {alice_received_hash}")
logging.info(f"Bob received hash {bob_received_hash}")
logging.info(f"Blockchain info:\n{json.dumps(chain_asset, indent=2)}")
wait_point("Alice can see she now has an outdated message, so she stops believing the debt\n(or at least would require further proof since Bob denies it)")

wait_point("Mallory cannot trick Alice or Bob!")




log_all_blocks("node1.log")