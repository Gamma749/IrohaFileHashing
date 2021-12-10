# Hyperledger Iroha File Hash Example

## Prerequisites
Ensure that your machine runs docker and docker-compose.

## Network Setup
From the multinode-network directory, run

`./manage-network up`

to start the iroha containers. Run

`./manage-network down`

to destroy those containers when finished.

Run

`./manage-network (pause|unpause)`

to pause or unpause the network respectively.

## Running the examples

In the `usr_scripts` directory, run `python3 <filename>.py`. 

The logging will describe what steps are being taken, and will require you to hit "enter" to proceed at some points so you can inspect the outputs.


## Example explanation

### UnsentMessageExample.py
In this example, we will see two users (Jack and Jill) exchange messages (the exchange itself is outside of this example, you can imagine email, telegram, carrier pigeon...). Both users hash these messages and store the hashes on the blockchain, as proof that they have sent the message at a specific time. Importantly, the message content is *not* on the blockchain and hence is *not* public.

At some later time, Victoria is asked to verify that the messages were sent. Victoria, gathering those messages, can recalculate the hashes and search for them on the blockchain. By checking if those hashes are present in a block, Victoria can verify if a message was sent or not (more accurately, Victoria can verify if the message was *logged* as sent by this method)

Over time the events are:
- Jack sends message1.secret to Jill. logging the hash
- Jill replies to Jack with message2.secret, logging the hash
- Jack composes but does not send message3.secret
- Victoria gets message1.secret, computes the hash, and determines the hash *is* on chain
    - Verifies that message1.secret was sent
- Victoria gets message2.secret, computes the hash, and determines the hash *is* on chain
    - Verifies that message2.secret was sent
- Victoria gets message3.secret, computes the hash, and determines the hash is *not* on chain
    - Verifies that message3.secret was *not* sent

### DifferingMessageExample.py
In this example, Alice sends a message to Bob and logs the hash on chain. Bob can verify that the message he receives has the same hash as he sees on chain, verifying the message. Alice can update the message, send it to Bob, and log the hash again. Bob can once again check the message and see it has updated.

A new user, Mallory, enters the picture and wants to trick Alice and Bob. Mallory creates a new message claiming Bob owes Mallory some money. Mallory logs this hash and sends it to Alice *only* (Bob does not see this message). Alice can see this hash and verify it, so she believes Bob owes Mallory. Mallory updates the message and sends the now non-dubious message to Bob.

Mallory now has two choices:
1. Do not log the new message hash on chain. Bob can check the chain and see his message hash is not the same as the one on chain, and knows he is being tricked
2. Log the new message hash on chain. Bob can check the chain and verify the hash (although the previous hash from Alice should raise suspicion).
Alice and Bob meet and Alice states Bob owes Mallory, citing her message hash. Bob disputes this and provides his message hash. Alice and Bob can now check the chain again, and Alice can see her message is outdated, so she will stop believing Bob owes Mallory.

## Some thoughts
- This example, as with much of blockchain and cryptography, relies on there being absolutely no hash collisions. If a hash collision occurs, it would be possible to trick the auditor User C.
    - Because the hashes are public, a malicious user could *theoretically* attempt to find messages that would fool an auditor by finding alternative messages that fit the same hash (a preimage attack). The message would *probably* be gibberish, and would *probably* take far too long to compute, but is still worth considering
- In this example, we have used MD5 hashing. This is a bad idea (see above) and should *not* be used for anything important! We have been constrained to this because Iroha assets can have a maximum name length of 32 characters, which MD5 outputs. This example is a hack to get file hashes stored on Iroha, and is meant as an example only!!
