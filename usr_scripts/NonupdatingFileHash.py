#! /bin/python

from IrohaUtils import *
from IrohaHashCustodian import Custodian
from iroha import primitive_pb2
import logging


# INFO gives descriptions of steps
# DEBUG gives information on transactions and queries too
logging.basicConfig(level=logging.INFO)
logging.info("Create hash custodian")
custodian = Custodian()
logging.info("Create user A")
user_a = custodian.new_hashing_user("user_a")
logging.info("Create user B")
user_b = custodian.new_hashing_user("user_b")
logging.info("Create user C")
user_c = custodian.new_hashing_user("user_c")


logging.info("User A sends message1 to User B")
logging.info("Log hash of message1 on blockchain")
file_hash = custodian.get_file_hash("message1.secret")
status = custodian.store_hash_on_chain(user_a, file_hash)
assert status[0] == "COMMITTED"
logging.info("User A successfully stored message1 hash")

logging.info("User B replies to User A and also logs the hash")
file_hash = custodian.get_file_hash("message2.secret")
status = custodian.store_hash_on_chain(user_b, file_hash)
assert status[0] == "COMMITTED"
logging.info("User B successfully stored message2 hash")

logging.info("Some time later, User C is called in to verify the communications have occurred")
logging.info("User C gets message1 and checks if the hash exists on the chain")
file_hash = custodian.get_file_hash("message1.secret")
assert custodian.find_hash_on_chain(user_c, file_hash)
logging.info("User C found message1 hash on chain")

logging.info("User C is asked to verify if message3 (unsent) is on chain")
file_hash = custodian.get_file_hash("message3.secret")
assert not custodian.find_hash_on_chain(user_c, file_hash)
logging.info("User C did not find message3 hash on chain, verifies that message3 was not sent")

log_all_blocks("node1.log")