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

## Example explanation
In this (admittedly barren) example, we will see two users (User A and User B) exchange messages (the exchange itself is outside of this example, you can imagine email, telegram, carrier pigeon...). Both users hash these messages and store this hash on the blockchain, as proof that they have sent the message at a specific time. Importantly, the message content is *not* on the blockchain and hence is *not* public.

At some later time, User C is asked to verify that the messages were sent. User C, gathering those messages, can recalculate the hashes and search for them on the blockchain. By checking if those hashes are present in a block, User C can verify if a message was sent or not (more accurately, User C can verify if the message was *logged* as sent by this method)

Over time the events are:
- User A sends message1.secret to User B. logging the hash
- User B replies to User A with message2.secret, logging the hash
- User A composes but does not send message3.secret
- User C gets message1.secret, computes the hash, and determines the hash *is* on chain
    - Verifies that message1.secret was sent
- User C gets message3.secret, computes the hash, and determines the hash is *not* on chain
    - Verifies that message3.secret was not sent

## Running this example
Ensure the Iroha network is up by running `./manage-network up` from the root directory

In the `usr_scripts` directory, run `python3 FileHash.py`. The logging will describe what steps are being taken. When convinced that this program runs without error, checkout the `FileHash.py` code to see how the above example is implemented.

## Some thoughts
- This example, as with much of blockchain and cryptography, relies on there being absolutely no hash collisions. If a hash collision occurs, it would be possible to trick the auditor User C.
    - Because the hashes are public, a malicious user could *theoretically* attempt to find messages that would fool an auditor by finding alternative messages that fit the same hash (a preimage attack). The message would *probably* be gibberish, and would *probably* take far too long to compute, but is still worth considering
- In this example, we have used MD5 hashing. This is a bad idea (see above) and should *not* be used for anything important! We have been constrained to this because Iroha assets can have a maximum name length of 32 characters, which MD5 outputs. This example is a hack to get file hashes stored on Iroha, and is meant as an example only!!
