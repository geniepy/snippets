from starlette.testclient import TestClient

from main import instance

def main():
    client = TestClient(instance)

    with client.websocket_connect("/ws") as websocket:
        websocket.send_bytes(b"Hello!")

        data = websocket.receive_bytes()

        print(data)

if __name__ == "__main__":
    main()
