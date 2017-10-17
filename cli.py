import os
import socketserver
import struct
import threading


SSH_AGENT_FAILURE = 5
SSH_AGENT_SUCCESS = 6
SSH2_AGENT_IDENTITIES_ANSWER = 12
SSH2_AGENT_SIGN_RESPONSE = 14


def _write_byte(data):
    if len(data) > 1:
        raise ValueError("Data larger than expected")
    return data


def _write_int(data):
    return struct.pack(">I", data)


def _write_string(data):
    return _write_int(len(data)) + data


def _read_byte(data):
    return data[0], data[1:]


def _read_int(data):
    if len(data) < 4:
        raise ValueError("Data smaller than exepected - minimum 4 bytes")
    value, = struct.unpack('>I', data[:4])
    return value, data[4:]


def _read_string(data):
    if len(data) < 4:
        raise ValueError("Data smaller than exepected - minimum 4 bytes")
    length, = struct.unpack('>I', data[:4])
    if len(data) < length + 4:
        raise ValueError("Data smaller than expected")
    return data[4:4 + length], data[4 + length:]



class ConnectionError(Exception):
    pass


class AgentHandler(socketserver.BaseRequestHandler):

    def handler_11(self, msg):
        # SSH2_AGENTC_REQUEST_IDENTITIES = 11
        message = []
        message.append(_write_string(byte_chr(SSH2_AGENT_IDENTITIES_ANSWER)))
        message.append(_write_int(len(self.server.identities)))
        for pkey, comment in self.server.identities.values():
            message.append(_write_string(pkey.asbytes())
            message.append(_write_string(comment)
        return b''.join(message)

    def handler_13(self, msg):
        # SSH2_AGENTC_SIGN_REQUEST = 13
        identity, msg = _read_string(msg)
        data, msg = _read_string(msg)
        someint, msg = _read_int(msg)

        pkey, comment = self.server.identities.get(identity, (None, None))

        if not pkey:
            return _write_byte(byte_chr(SSH_AGENT_FAILURE))

        return b''.join((
            _write_byte(byte_chr(SSH2_AGENT_SIGN_RESPONSE)),
            _write_string(pkey.sign_ssh_data(data).asbytes())
        ))

    def _read(self, wanted):
        result = b''
        while len(result) < wanted:
            buf = self.request.recv(wanted - len(result))
            if not buf:
                raise ConnectionError()
            result += buf
        return result

    def read_message(self):
        size = _read_int(self._read(4))
        msg = self._read(size)
        msgtype, msg = _read_byte(msg)
        return ord(msgtype), msg

    def handle(self):
        while True:
            try:
                mtype, msg = self.read_message()
            except ConnectionError:
                return

            handler = getattr(self, 'handler_{}'.format(mtype))
            if not handler:
                continue

            self.request.sendall(_write_string(handler(msg)))


class PosixAgentServer(socketserver.ThreadingUnixStreamServer):

    def __init__(self, socket_file):
        socketserver.ThreadingUnixStreamServer.__init__(self, socket_file, PosixAgentHandler)
        self.identities = {}

    def add(self, pkey, comment):
        self.identities[pkey.asbytes()] = (pkey, comment)

    def serve_while_pid(self, pid):
        self.listen_start()
        while os.waitpid(pid, 0)[0] != pid:
            pass
        self.listen_stop()

    def listen_start(self):
        self.listen_thread = threading.Thread(target=self.serve_forever)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def listen_stop(self):
        if self.listen_thread:
            self.listen_thread = None
        self.shutdown()
        self.server_close()


def run():
    environ = os.environ.copy()

    socket_dir = tempfile.mkdtemp(prefix='ssh-')
    socket_file = os.path.join(socket_dir, 'agent.{}'.format(os.getpid()))

    environ['SSH_AUTH_SOCK'] = socket_file
    del environ['SHELL']

    child_pid = os.fork()
    if child_pid:
        a = PosixAgentServer(socket_file)

        # a.add(identity_bytes, comment)

        try:
            a.serve_while_pid(child_pid)
        finally:
            shutil.rmtree(socket_dir)
            return

    while not os.path.exists(socket_file):
        time.sleep(0.5)

    os.execvpe(cmd[0], cmd, environ)
