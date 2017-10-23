# AGENTLESS

This codebase implements ssh-agent as a bare bones microservice. This simple codebase allows the use of an SSH key without an end user possessing its private key. This might be useful if:

 * You want to reduce the number of machines that hold a copy of your private key material

 * You don't want a compromised desktop developer machine to compromise private key material

 * You want to perform additional or non-standard authentication of a user before allowing a key to be used - for example you can require a valid TOTP code. This effectively gives you 2FA without having to install extra PAM modules on your entire fleet of machines and without needed to do LDAP 2FA.

 * You have devops / CD deployment tooling and don't really want to commit private keys alongside the configuration for them. (Good doggo).

 * You want to capture an audit event every time a private key is used

 * You want to store private keys for some systems in a more secure environment (different physical security, use of HSM or other hardware crypto, etc) and provide restricted access to them.

 * You want to reduce the likelihood of criticial private key material from been exfiltrated.

 * You have shared cloud infrastructure where each user doesn't have their own account

You will probably have to customize it for your environment - a lot of these ideas are left to the reader (for now).

**WARNING**: Don't use this when multiple user accounts with multiple SSH keys is more appropriate. It's not a replacement for a good LDAP deployment.


## Dev Environment

You can get a simple dev environment with Docker and docker-compose. Dev happens on macOS with Docker for Mac:

```
$ docker-compose -f dev.yml build
$ docker-compose -f dev.yml up
```

This will automatically run any migrations.

You can run tests with:

```
$ docker-compose -f dev.yml run --rm flask py.test agentless/
```

And run flake8 with:

```
$ docker-compose -f dev.yml run --rm flask flake8 agentless/
```

You can generate a private key and get the public key with curl:

```
$ curl -X POST -H "applicaton/json" -d '{"name": "example"}' https://localhost:8000/api/v1/keys
```

You can use it with your normal SSH client with the `cli.py` wrapper:

```
./cli.py myuser@myserver.org
```

This will:

 * Start an SSH agent running locally
 * Update the environment so that subprocesses can see that agent
 * Start SSH
 * Wait for SSH to finish
 * Ensure the SSH agent is cleaned up


## How

The ssh-agent protocol is simply an API that allows listing the public keys that are available to participate in authentication and an API for signing challenge payloads. By signing a payload from the host with the private portion of a key it knows about (in `~/.ssh/authorized_keys`) it knows you are who you say you are.

But there is no reason why this has to happen on your machine. If you are suitably authenticated by other means then it's actually nicer to be physically seperated from the private key material.

With agentless, the user installs a client which implements the ssh agent protocol. This client listens on a unix socket and forwards any authentication challenges to agentless via the `/api/v1/keys/1/sign` endpoint. This means the local ssh agent client has no access to the secret material.


## Background

In [Touchdown](https://github.com/yaybu/touchdown) 0.2.0 back in 2015 we added a simple SSH Agent. This ultimately served two goals:

 * The `touchdown ssh` wrapper CLI could launch the full SSH client and use private key credentials that were protected through touchdowns secret infrastructure without them touching disk.
 * Those secrets could also be forwarded to EC2 instances through paramiko SSH agent forwarding. This meant you could use a bastion host without exposing private key material on the bastion host, and again these secrets were protected through touchdowns secret infrastructure. They are not exposed unencrypted locally, either.

Touchdown could use a mixture of GPG encryption and Amazon KMS - and these could be stacked.

However ultimately the secrets did exist in an unprotected form. If a user was able to run Touchdown then they could extract the secrets and abuse them outside of any Touchdown controls.
