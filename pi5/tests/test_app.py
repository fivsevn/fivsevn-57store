import json
import socket
import tempfile
import time
import unittest
from pathlib import Path

import app


class MirrorStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp.name)
        self.store = app.MirrorStore(self.data_dir / "mirror.db")
        self.store.initialize()

    def tearDown(self):
        self.temp.cleanup()

    def test_state_and_events_survive_new_connection(self):
        self.store.set_state("start_count", 3)
        event = self.store.add_event("DISPLAY LINKED", "notice", "test")
        reopened = app.MirrorStore(self.data_dir / "mirror.db")
        self.assertEqual(reopened.get_state("start_count"), 3)
        self.assertEqual(reopened.last_event()["id"], event["id"])
        self.assertEqual(reopened.last_event()["message"], "DISPLAY LINKED")

    def test_event_validation(self):
        with self.assertRaises(ValueError):
            self.store.add_event("")
        with self.assertRaises(ValueError):
            self.store.add_event("BAD LEVEL", "unknown")

    def test_authorization(self):
        self.assertTrue(app.is_event_authorized("127.0.0.1", "", "secret"))
        self.assertTrue(app.is_event_authorized("192.168.0.2", "secret", "secret"))
        self.assertFalse(app.is_event_authorized("192.168.0.2", "wrong", "secret"))


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp.name)
        self.static_dir = Path(__file__).resolve().parents[1] / "static"
        self.store = app.MirrorStore(self.data_dir / "mirror.db")
        self.store.initialize()
        self.started_at = app.utc_now()
        handler = app.configured_handler(
            self.store,
            self.data_dir,
            time.monotonic(),
            self.started_at,
            "test-secret",
            self.static_dir,
        )
        self.handler = handler
        self.server = type("TestServer", (), {"server_name": "57store", "server_port": 5757})()

    def tearDown(self):
        self.temp.cleanup()

    def request(self, method, path, body=None):
        encoded = json.dumps(body).encode() if body is not None else b""
        headers = [
            f"{method} {path} HTTP/1.0",
            "Host: 57store.local",
            f"Content-Length: {len(encoded)}",
        ]
        if body is not None:
            headers.append("Content-Type: application/json")
        raw_request = ("\r\n".join(headers) + "\r\n\r\n").encode() + encoded

        server_socket, client_socket = socket.socketpair()
        try:
            client_socket.sendall(raw_request)
            client_socket.shutdown(socket.SHUT_WR)
            self.handler(server_socket, ("127.0.0.1", 54321), self.server)
            server_socket.close()
            chunks = []
            while True:
                chunk = client_socket.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
        finally:
            server_socket.close()
            client_socket.close()

        header_data, response_body = b"".join(chunks).split(b"\r\n\r\n", 1)
        status = int(header_data.split(b"\r\n", 1)[0].split()[1])
        return status, response_body

    def request_json(self, method, path, body=None):
        status, response_body = self.request(method, path, body)
        return status, json.loads(response_body)

    def test_status_and_snapshot(self):
        status_code, payload = self.request_json("GET", "/api/status")
        self.assertEqual(status_code, 200)
        self.assertTrue(payload["online"])
        self.assertIn("disk", payload)
        self.assertTrue((self.data_dir / "status.json").exists())

    def test_local_event_post_and_read(self):
        status_code, payload = self.request_json(
            "POST",
            "/api/events",
            {"message": "TEST SIGNAL", "level": "info", "source": "test"},
        )
        self.assertEqual(status_code, 201)
        self.assertEqual(payload["event"]["message"], "TEST SIGNAL")
        status_code, payload = self.request_json("GET", "/api/events?limit=8")
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["events"][0]["message"], "TEST SIGNAL")

    def test_front_page(self):
        status, response_body = self.request("GET", "/")
        body = response_body.decode()
        self.assertEqual(status, 200)
        self.assertIn("PHYSICAL MIRROR NODE", body)


if __name__ == "__main__":
    unittest.main()
