import time
from pathlib import Path

from emacs_remote.utils.stcp_socket import SecureTCPSocket

for i in range(5):
    with SecureTCPSocket() as s:
        s.connect("localhost", 9130)

        start = time.time()
        s.sendall("Get projectile.index")
        end = time.time()
        print("Send Elapsed time: ", (end - start))
        start = time.time()
        response = s.recvall()
        end = time.time()
        print("Receive Elapsed time: ", (end - start))
        time.sleep(2)
