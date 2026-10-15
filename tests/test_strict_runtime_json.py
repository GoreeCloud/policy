import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from goreecloud_policy.runtime import Handler, parse_json_payload


class StrictRuntimeJsonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def post(self, payload):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            connection.request("POST", "/v1/evaluate", body=payload, headers={"Content-Type": "application/json"})
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def request_with_headers(self, method, path, payload, headers):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            connection.request(method, path, body=payload, headers=headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_json_response_has_privacy_headers(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            connection.request("GET", "/healthz")
            response = connection.getresponse()
            self.assertEqual(200, response.status)
            self.assertEqual("no-store", response.getheader("Cache-Control"))
            self.assertEqual("nosniff", response.getheader("X-Content-Type-Options"))
            self.assertEqual("application/json", response.getheader("Content-Type"))
            response.read()
        finally:
            connection.close()

    def test_valid_local_request_still_evaluates(self):
        payload = {
            "request": {
                "policy_id": "development-check", "policy_version": "1",
                "authority": "privacy-shield", "subject": "service:tester",
                "resource": "resource:synthetic", "action": "read",
                "context": {"purpose": "unit-test"},
            },
            "rules": [{
                "rule_id": "explicit", "policy_id": "development-check",
                "policy_version": "1", "authority": "privacy-shield",
                "when": {"purpose": "unit-test"}, "decision": "allow",
            }],
        }
        status, body = self.post(json.dumps(payload).encode("utf-8"))
        self.assertEqual(200, status)
        self.assertEqual("allow", body["decision"])
        self.assertEqual(["explicit"], body["matched_rule_ids"])
        self.assertIs(body["production_accepted"], False)
        self.assertEqual("development-reference-runtime", body["scope"])

    def test_nonlocal_host_is_rejected(self):
        for host in ("example.invalid", "localhost.example.invalid", "127.0.0.1@evil.invalid"):
            with self.subTest(host=host):
                status, response = self.request_with_headers("GET", "/healthz", None, {"Host": host})
                self.assertEqual(403, status)
                self.assertEqual("untrusted_host", response["error"])

    def test_non_json_post_media_types_are_rejected(self):
        for content_type in ("text/plain", "application/x-www-form-urlencoded"):
            with self.subTest(content_type=content_type):
                status, response = self.request_with_headers(
                    "POST", "/v1/evaluate", b"{}", {"Content-Type": content_type},
                )
                self.assertEqual(415, status)
                self.assertEqual("unsupported_media_type", response["error"])

    def test_browser_origin_post_is_rejected(self):
        status, response = self.request_with_headers(
            "POST", "/v1/evaluate", b"{}", {
                "Content-Type": "application/json", "Origin": "https://example.invalid",
            },
        )
        self.assertEqual(403, status)
        self.assertEqual("browser_origin_not_supported", response["error"])

    def raw_post(self, extra_headers):
        """Send deliberate HTTP header duplicates without client normalization."""
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            connection.putrequest("POST", "/v1/evaluate", skip_host=True)
            connection.putheader("Host", "127.0.0.1")
            connection.putheader("Content-Type", "application/json")
            for key, value in extra_headers:
                connection.putheader(key, value)
            connection.endheaders(b"{}")
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_ambiguous_http_headers_are_rejected(self):
        cases = [
            ([("Host", "example.invalid"), ("Content-Length", "2")], 403, "untrusted_host"),
            ([("Content-Length", "2"), ("Content-Length", "2")], 400, "invalid_request_framing"),
            ([("Content-Length", "2"), ("Transfer-Encoding", "chunked")], 400, "invalid_request_framing"),
            ([("Content-Length", "+2")], 400, "invalid_request_framing"),
            ([("Content-Length", "2"), ("Sec-Fetch-Site", "cross-site")], 403, "browser_origin_not_supported"),
            ([("Content-Length", "2"), ("Origin", "")], 403, "browser_origin_not_supported"),
        ]
        for headers, expected_status, expected_error in cases:
            with self.subTest(headers=headers):
                status, response = self.raw_post(headers)
                self.assertEqual(expected_status, status)
                self.assertEqual(expected_error, response["error"])

    def test_valid_nested_json_is_accepted_by_parser(self):
        self.assertEqual({"subject": {"action": "read"}}, parse_json_payload(b'{"subject":{"action":"read"}}'))

    def test_excessively_nested_json_is_rejected_over_http(self):
        # A bounded HTTP body can still exceed the JSON decoder's recursion limit.
        payload = b"[" * 10000 + b"0" + b"]" * 10000
        status, response = self.post(payload)
        self.assertEqual(400, status)
        self.assertEqual("error", response["decision"])

    def test_top_level_duplicate_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            parse_json_payload(b'{"authority":"one","authority":"other"}')

    def test_nested_duplicate_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            parse_json_payload(b'{"context":{"role":"viewer","role":"admin"}}')

    def test_non_finite_numbers_rejected(self):
        for value in (b"NaN", b"Infinity", b"-Infinity"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "non-finite"):
                    parse_json_payload(b'{"metric":' + value + b'}')

    def test_numeric_exponent_overflow_is_rejected(self):
        for value in (b"1e309", b"-1e309"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "non-finite"):
                    parse_json_payload(b'{"metric":' + value + b'}')

    def test_finite_json_float_is_preserved(self):
        self.assertEqual({"metric": 1.25}, parse_json_payload(b'{"metric":1.25}'))

    def test_numeric_exponent_overflow_is_rejected_over_http(self):
        status, response = self.post(b'{"metric":1e309}')
        self.assertEqual(400, status)
        self.assertEqual("error", response.get("decision"))

    def test_omitted_when_is_rejected_over_http(self):
        request = {"policy_id": "p", "policy_version": "1", "authority": "a",
                   "subject": "s", "resource": "r", "action": "read"}
        rule = {"rule_id": "x", "policy_id": "p", "policy_version": "1",
                "authority": "a", "decision": "allow"}
        code, body = self.post(json.dumps({"request": request, "rules": [rule]}).encode())
        self.assertEqual(400, code)
        self.assertEqual("error", body["decision"])

    def test_duplicate_input_is_rejected_over_http(self):
        status, response = self.post(b'{"request":{},"request":{}}')
        self.assertEqual(400, status)
        self.assertEqual("error", response.get("decision"))

    def test_non_finite_input_is_rejected_over_http(self):
        status, response = self.post(b'{"data":NaN}')
        self.assertEqual(400, status)
        self.assertEqual("error", response.get("decision"))


if __name__ == "__main__":
    unittest.main()
