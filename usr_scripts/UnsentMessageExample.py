#! /bin/python

from IrohaUtils import *
from IrohaHashCustodian import Custodian
import logging
import grpc
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
        custodian = Custodian()
        break
    except grpc._channel._InactiveRpcError:
        logging.info("Network unreachable, retrying")
        sleep(2)
logging.info("Create user Jack")
user_a = custodian.new_hashing_user("jack")
logging.info("Create user Jill")
user_b = custodian.new_hashing_user("jill")
logging.info("Create user Victoria")
user_c = custodian.new_hashing_user("victoria")


wait_point("Jack sends message1 to Jill, logging the hash")
message1_hash = custodian.get_file_hash("messages/message1.secret")
logging.info(f"{message1_hash=}")
logging.info("Storing on chain...")
status = custodian.store_hash_on_chain(user_a, message1_hash)
assert status[0] == "COMMITTED"
logging.info("Jack successfully stored message1 hash")

wait_point("Jill replies to Jack and also logs the hash")
message2_hash = custodian.get_file_hash("messages/message2.secret")
logging.info(f"{message2_hash=}")
logging.info("Storing on chain...")
status = custodian.store_hash_on_chain(user_b, message2_hash)
assert status[0] == "COMMITTED"
logging.info("Jill successfully stored message2 hash")

wait_point("Jack, receiving Jill's reply, creates reply message3 but does not send it")

print("\n\n")

wait_point("Some time later, Victoria is called in to verify the communications have occurred")
logging.info("Victoria gets the chain hashes")
domain_hashes = custodian.get_domain_hashes()
logging.info(json.dumps(domain_hashes, indent=2))

wait_point("Victoria gets message1 and checks if the hash exists on the chain")
file_hash = custodian.get_file_hash("messages/message1.secret")
logging.info(f"Searching for hash {file_hash}...")
assert custodian.find_hash_on_chain(user_c, file_hash)
logging.info("Victoria found message1 hash on chain")

wait_point("Victoria gets message2 and checks if the hash exists on the chain")
file_hash = custodian.get_file_hash("messages/message2.secret")
logging.info(f"Searching for hash {file_hash}...")
assert custodian.find_hash_on_chain(user_c, file_hash)
logging.info("Victoria found message2 hash on chain")

wait_point("Victoria is asked to verify if message3 is on chain\nJack claims he sent message3 but actually did not")
file_hash = custodian.get_file_hash("messages/message3.secret")
logging.info(f"Searching for hash {file_hash}...")
assert not custodian.find_hash_on_chain(user_c, file_hash)
logging.info("Victoria did not find message3 hash on chain, verifies that message3 was not sent")

wait_point("Valid communications are verified, unsent messages are identified!")

log_all_blocks("node1.log")