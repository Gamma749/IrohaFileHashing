#! /bin/python

from IrohaUtils import *
from IrohaHashCustodian import Custodian
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

logging.info("User A creates a message and logs it in a new domain")
message = "Hello, World!"
logging.info(f"Message: {message}")
message_hash = custodian.get_hash(message)
logging.debug(message_hash)
custodian.store_hash_on_chain(user_a, message_hash, domain_name="message")
logging.info("Message successfully logged in new domain")

logging.info("User A changes the message slightly, and stores new hash")
message+="---Foobar---"
logging.info(f"Message: {message}")
message_hash = custodian.get_hash(message)
custodian.store_hash_on_chain(user_a, message_hash, domain_name="message")
logging.info("Message successfully updated")

logging.info("User B, having received the message from A, wants to verify it")
message_hash = custodian.get_hash(message)
assets = custodian.get_domain_hashes(user_b, domain_name="message")
logging.info("User B, having got the assets from the domain, checks the most recent against their message")
assert message_hash==assets[-1]["hash"]
logging.info("User B verifies that their message is the most recent on chain")

log_all_blocks("node1.log")