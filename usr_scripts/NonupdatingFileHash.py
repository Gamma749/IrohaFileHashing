#! /bin/python

from IrohaUtils import *
from iroha import primitive_pb2
import logging


# INFO gives descriptions of steps
# DEBUG gives information on transactions and queries too
logging.basicConfig(level=logging.INFO)



# The iroha domain that document hashes are stored in
DEFAULT_DOMAIN_NAME = "document"

# Create the users
user_a = new_user("user_a", DEFAULT_DOMAIN_NAME)
user_b = new_user("user_b", DEFAULT_DOMAIN_NAME)
user_c = new_user("user_c", DEFAULT_DOMAIN_NAME)

logging.info("Create new role \'document_creator\'\n\tand new domain \'document\'")
commands = [
    # Create a new role that can only create assets (i.e. create hashes) and read assets (to see if they exist)
    iroha_admin.command("CreateRole", role_name="document_creator", permissions=[
            primitive_pb2.can_create_asset,
            primitive_pb2.can_read_assets
        ]),
    # Create a new role that can do NOTHING
    iroha_admin.command("CreateRole", role_name="null_role", permissions=[
        
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
                        public_key=user_b["public_key"]),
    iroha_admin.command('CreateAccount', account_name=user_c["name"], domain_id=DEFAULT_DOMAIN_NAME,
                        public_key=user_c["public_key"])
]
tx = IrohaCrypto.sign_transaction(
        iroha_admin.transaction(commands), ADMIN_PRIVATE_KEY)
logging.debug(tx)
status = send_transaction(tx, net_1)
logging.debug(status)
assert status[0] == "COMMITTED"
logging.info("Users added")

custodian = IrohaHashCustodian()


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

log_all_blocks(net_1, f"node1.log")