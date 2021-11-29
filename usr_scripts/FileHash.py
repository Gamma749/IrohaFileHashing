#! /bin/python

from IrohaUtils import *
from iroha import primitive_pb2
import logging
import hashlib

# INFO gives descriptions of steps
# DEBUG gives information on transactions and queries too
logging.basicConfig(level=logging.INFO)

@trace
def md5_hash(filename):
    """
    Generate and return the MD5 hex digest of the contents of a file
    While it would be nice to use a different, more secure algorithm we are constrained
    The output of this hash will be the name of an Iroha asset, which can have max length of 32

    Args:
        filename (String): The name of the file to hash

    Returns:
        String: The hex digest of the contents of the file described by filename
    """
    with open(filename, "rb") as f:
        b = f.read()
        h = hashlib.md5(b)
    logging.debug(h.hexdigest())
    return h.hexdigest()

@trace
def store_hash_on_chain(user, h, connection=net_1):
    """
    Take the hex digest of a message and store this on the blockchain as the name of an asset

    Args:
        user (Dictionary): The user dictionary of the user sending this hash
        h (String): The hash of a message
        connection (IrohaGrpc, optional): The connection to send this hash over. Defaults to net_1.

    Return:
        IrohaStatus: The status of the transaction to put this hash to the chain
    """

    commands = [
        user["iroha"].command('CreateAsset', asset_name=h,
                      domain_id=user["domain"], precision=0)
    ]
    tx = IrohaCrypto.sign_transaction(
        user["iroha"].transaction(commands), user["private_key"])
    logging.debug(tx)
    status = send_transaction(tx, net_1)
    logging.debug(status)
    return status

@trace
def find_hash_on_chain(user, h, connection=net_1):
    """
    Given the hex digest of a message, attempt to find this hash on the blockchain

    Args:
        user (Dictionary): The user dictionary of the user querying this hash
        h (String): The hash of a message
        connection (IrohaGrpc, optional): The connection to send this hash over. Defaults to net_1.

    Return:
        IrohaStatus: The status of this query. True if the hash exists on the blockchain, False otherwise.
    """
    
    query = user["iroha"].query("GetAssetInfo", asset_id=f"{h}#{user['domain']}")
    query = IrohaCrypto.sign_query(query, user["private_key"])
    logging.debug(query)
    response = connection.send_query(query)
    logging.debug(response)
    #Check if response has an asset id matching the hash we are after
    return response.asset_response.asset.asset_id==h+f"#{user['domain']}"

# The iroha domain that document hashes are stored in
DOMAIN_NAME = "document"

# Create the users
user_a = new_user("user_a", DOMAIN_NAME)
user_b = new_user("user_b", DOMAIN_NAME)
user_c = new_user("user_c", DOMAIN_NAME)

logging.info("Create new role \'document_creator\'\n\tand new domain \'document\'")
commands = [
    # Create a new role that can only create assets (i.e. create hashes) and read assets (to see if they exist)
    iroha_admin.command("CreateRole", role_name="document_creator", permissions=[
            primitive_pb2.can_create_asset,
            primitive_pb2.can_read_assets
        ]),
    # Create a new domain that has document_creator as role
    iroha_admin.command("CreateDomain", domain_id=DOMAIN_NAME, default_role="document_creator")
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
    iroha_admin.command('CreateAccount', account_name=user_a["name"], domain_id=DOMAIN_NAME,
                        public_key=user_a["public_key"]),
    iroha_admin.command('CreateAccount', account_name=user_b["name"], domain_id=DOMAIN_NAME,
                        public_key=user_b["public_key"]),
    iroha_admin.command('CreateAccount', account_name=user_c["name"], domain_id=DOMAIN_NAME,
                        public_key=user_c["public_key"])
]
tx = IrohaCrypto.sign_transaction(
        iroha_admin.transaction(commands), ADMIN_PRIVATE_KEY)
logging.debug(tx)
status = send_transaction(tx, net_1)
logging.debug(status)
assert status[0] == "COMMITTED"
logging.info("Users added")


logging.info("User A sends message1 to User B")
logging.info("Log hash of message1 on blockchain")
file_hash = md5_hash("message1.secret")
status = store_hash_on_chain(user_a, file_hash)
assert status[0] == "COMMITTED"
logging.info("User A successfully stored message1 hash")

logging.info("User B replies to User A and also logs the hash")
file_hash = md5_hash("message2.secret")
status = store_hash_on_chain(user_b, file_hash)
assert status[0] == "COMMITTED"
logging.info("User B successfully stored message2 hash")

logging.info("Some time later, User C is called in to verify the communications have occurred")
logging.info("User C gets message1 and checks if the hash exists on the chain")
file_hash = md5_hash("message1.secret")
assert find_hash_on_chain(user_c, file_hash)
logging.info("User C found message1 hash on chain")

logging.info("User C is asked to verify if message3 (unsent) is on chain")
file_hash = md5_hash("message3.secret")
assert not find_hash_on_chain(user_c, file_hash)
logging.info("User C did not find message3 hash on chain, verifies that message3 was not sent")

log_all_blocks(net_1, f"node1.log")