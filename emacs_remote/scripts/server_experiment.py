from pathlib import Path

from emacs_remote.utils.stcp_socket import SecureTCPSocket

with SecureTCPSocket() as s:
    s.bind("localhost", 9131)

    s.listen()
    conn, addr = s.accept()

    with conn:
        request = conn.recvall(timeout=60)
        if not request:
            raise ValueError("No request received")

        print(f"Request: {request}")

        data = Path(
            "/Users/antoniokim/Documents/Cerebras/projectile.index"
        ).read_bytes()
        conn.sendall([data])
