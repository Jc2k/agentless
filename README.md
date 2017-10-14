# AGENTLESS

A simple microservice that allows:

 * an SSH key to be shared but without comprising it
 * all use of an SSH key to be audit logged

Access to the private key can be revoked by blocking access to this service.

**WARNING**: Don't use this when multiple user accounts with multiple SSH keys is more appropriate - which is most of the time!!


# How

agentless works by providing an API for generating SSH private keys and the same API that an SSH Agent would provide. It is effectively an SSH Agent on the network, but where the user of the SSH key has no access to the underlying private key.


# Background

In [Touchdown](https://github.com/yaybu/touchdown) 0.2.0 back in 2015 we added a simple SSH Agent. This ultimately served two goals:

 * The `touchdown ssh` wrapper CLI could launch the full SSH client and use private key credentials that were protected through touchdowns secret infrastructure without them touching disk.
 * Those secrets could also be forwarded to EC2 instances through paramiko SSH agent forwarding. This meant you could use a bastion host without exposing private key material on the bastion host, and again these secrets were protected through touchdowns secret infrastructure. They are not exposed unencrypted locally, either.

Touchdown could use a mixture of GPG encryption and Amazon KMS - and these could be stacked.

However ultimately the secrets did exist in an unprotected form. If a user was able to run Touchdown then they could extract the secrets and abuse them outside of any Touchdown controls.
