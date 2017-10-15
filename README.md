# AGENTLESS

This codebase implements ssh-agent as a microservice. This simple codebase allows the use of an SSH key without an end user possessing its private key. This might be useful if:

 * You have devops / CD deployment tooling and don't really want to commit private keys alongside the configuration for them.

 * You want to capture an audit event every time a private key is used

 * You want to store private keys for some systems in a more secure environment (different physical security, use of HSM or other hardware crypto, etc) and provide restricted access to them.

 * You have shared cloud infrastructure where each user doesn't have their own account

**WARNING**: Don't use this when multiple user accounts with multiple SSH keys is more appropriate - which is most of the time!!


# How

The user installs a client which implements the ssh agent protocol. This client listens on a unix socket and forwards any authentication challenges to agentless via the `/api/v1/keys/1/sign` endpoint. The local ssh agent client has no access to the secret material.


# Background

In [Touchdown](https://github.com/yaybu/touchdown) 0.2.0 back in 2015 we added a simple SSH Agent. This ultimately served two goals:

 * The `touchdown ssh` wrapper CLI could launch the full SSH client and use private key credentials that were protected through touchdowns secret infrastructure without them touching disk.
 * Those secrets could also be forwarded to EC2 instances through paramiko SSH agent forwarding. This meant you could use a bastion host without exposing private key material on the bastion host, and again these secrets were protected through touchdowns secret infrastructure. They are not exposed unencrypted locally, either.

Touchdown could use a mixture of GPG encryption and Amazon KMS - and these could be stacked.

However ultimately the secrets did exist in an unprotected form. If a user was able to run Touchdown then they could extract the secrets and abuse them outside of any Touchdown controls.
