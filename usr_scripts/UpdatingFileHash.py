#! /bin/python

from google.protobuf import message
from IrohaUtils import *
from iroha import primitive_pb2
import logging
import time


# INFO gives descriptions of steps
# DEBUG gives information on transactions and queries too
logging.basicConfig(level=logging.INFO)



# The iroha domain that document hashes are stored in
DEFAULT_DOMAIN_NAME = "hashing"

# Create the users
user_a = new_user("user_a", DEFAULT_DOMAIN_NAME)
user_b = new_user("user_b", DEFAULT_DOMAIN_NAME)

logging.info(f"Create new roles \'document_creator\', \'null_role\'\n\tand new domain \'{DEFAULT_DOMAIN_NAME}\'")
commands = [
    # Create a new role that can only create assets (i.e. create hashes) and read assets (to see if they exist)
    iroha_admin.command("CreateRole", role_name="document_creator", permissions=[
            primitive_pb2.can_create_asset,
            primitive_pb2.can_read_assets,
        ]),
    # Create a new domain that has document_creator as role
    iroha_admin.command("CreateDomain", domain_id=DEFAULT_DOMAIN_NAME, default_role="document_creator")
]
# Sign and send set up block
tx = IrohaCrypto.sign_transaction(
        iroha_admin.transaction(commands), ADMIN_PRIVATE_KEY)
logging.debug(tx)
status = send_transaction(tx, net_1)
logging.debug(status)
assert status[0] == "COMMITTED"
logging.info("Domain created")

logging.info("Create new users in domain")
commands = [
    iroha_admin.command('CreateAccount', account_name=user_a["name"], domain_id=DEFAULT_DOMAIN_NAME,
                        public_key=user_a["public_key"]),
    iroha_admin.command('CreateAccount', account_name=user_b["name"], domain_id=DEFAULT_DOMAIN_NAME,
                        public_key=user_b["public_key"])
]
tx = IrohaCrypto.sign_transaction(
        iroha_admin.transaction(commands), ADMIN_PRIVATE_KEY)
logging.debug(tx)
status = send_transaction(tx, net_1)
logging.debug(status)
assert status[0] == "COMMITTED"
logging.info("Users added")

custodian = IrohaHashCustodian()

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

log_all_blocks(net_1, f"node1.log")