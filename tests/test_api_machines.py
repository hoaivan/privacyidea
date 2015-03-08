"""
This testcase is used to test the REST API  in api/machines.py
"""
from .base import MyTestCase
import json
from privacyidea.lib.token import init_token, get_tokens
from privacyidea.lib.machine import attach_token

HOSTSFILE = "tests/testdata/hosts"

SSHKEY = "ssh-rsa " \
         "AAAAB3NzaC1yc2EAAAADAQABAAACAQDJy0rLoxqc8SsY8DVAFijMsQyCv" \
         "hBu4K40hdZOacXK4O6OgnacnSKN56MP6pzz2+4svzvDzwvkFsvf34pbsgD" \
         "F67PPSCsimmjEQjf0UfamBKh0cl181CbPYsph3UTBOCgHh3FFDXBduPK4DQz" \
         "EVQpmqe80h+lsvQ81qPYagbRW6fpd0uWn9H7a/qiLQZsiKLL07HGB+NwWue4os" \
         "0r9s4qxeG76K6QM7nZKyC0KRAz7CjAf+0X7YzCOu2pzyxVdj/T+KArFcMmq8V" \
         "dz24mhcFFXTzU3wveas1A9rwamYWB+Spuohh/OrK3wDsrryStKQv7yofgnPMs" \
         "TdaL7XxyQVPCmh2jVl5ro9BPIjTXsre9EUxZYFVr3EIECRDNWy3xEnUHk7Rzs" \
         "734Rp6XxGSzcSLSju8/MBzUVe35iXfXDRcqTcoA0700pIb1ANYrPUO8Up05v4" \
         "EjIyBeU61b4ilJ3PNcEVld6FHwP3Z7F068ef4DXEC/d7pibrp4Up61WYQIXV/" \
         "utDt3NDg/Zf3iqoYcJNM/zIZx2j1kQQwqtnbGqxJMrL6LtClmeWteR4420uZx" \
         "afLE9AtAL4nnMPuubC87L0wJ88un9teza/N02KJMHy01Yz3iJKt3Ou9eV6kqO" \
         "ei3kvLs5dXmriTHp6g9whtnN6/Liv9SzZPJTs8YfThi34Wccrw== " \
         "NetKnights GmbH"


class APIMachinesTestCase(MyTestCase):

    serial2 = "ser1"
    serial3 = "UBOM12345"

    def test_00_create_machine_resolver(self):
        # create a machine resolver
        with self.app.test_request_context('/machineresolver/machineresolver1',
                                           data={'type': 'hosts',
                                                 'filename': HOSTSFILE},
                                           method='POST',
                                           headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertTrue(result["status"] is True, result)
            self.assertTrue(result["value"] == 1, result)

    def test_01_get_machine_list(self):
        with self.app.test_request_context('/machine/',
                                           method='GET',
                                           headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            self.assertEqual(len(result["value"]), 4)
            self.assertTrue("hostname" in result["value"][0].keys())
            self.assertTrue("id" in result["value"][0].keys())
            self.assertTrue("ip" in result["value"][0].keys())
            self.assertTrue("resolver_name" in result["value"][0].keys())

    def test_01_get_machine_list_any(self):
        with self.app.test_request_context('/machine/?any=192',
                                           method='GET',
                                           headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            self.assertEqual(len(result["value"]), 3)
            self.assertTrue("hostname" in result["value"][0].keys())
            self.assertTrue("id" in result["value"][0].keys())
            self.assertTrue("ip" in result["value"][0].keys())
            self.assertTrue("resolver_name" in result["value"][0].keys())

    def test_02_attach_token(self):
        serial = "S1"
        # create token
        init_token({"serial": serial, "type": "spass"})

        with self.app.test_request_context('/machine/token',
                                           method='POST',
                                           data={"hostname": "gandalf",
                                                 "serial": serial,
                                                 "application": "luks",
                                                 "slot": "1"},
                                           headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            self.assertTrue(result["value"] >= 1)

        # check if the options were set.
        token_obj = get_tokens(serial=serial)[0]
        self.assertEqual(token_obj.token.machine_list[0].application, "luks")
        self.assertEqual(token_obj.token.machine_list[0].option_list[0].mt_key,
                         "slot")

    def test_04_set_options(self):
        serial = "S1"
        with self.app.test_request_context('/machine/tokenoption',
                                           method='POST',
                                           data={"hostname": "gandalf",
                                                 "serial": serial,
                                                 "application": "luks",
                                                 "partition": "/dev/sdb1"},
                                           headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            self.assertTrue(result["value"] >= 1)

        # check if the options were set.
        token_obj = get_tokens(serial=serial)[0]
        self.assertEqual(token_obj.token.machine_list[0].application, "luks")
        self.assertEqual(token_obj.token.machine_list[0].option_list[
                             1].mt_value, "/dev/sdb1")

        # delete slot!
        with self.app.test_request_context('/machine/tokenoption',
                                           method='POST',
                                           data={"hostname": "gandalf",
                                                 "serial": serial,
                                                 "application": "luks",
                                                 "slot": ""},
                                           headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            self.assertTrue(result["value"] >= 1)

        # check if the options were set.
        token_obj = get_tokens(serial=serial)[0]
        self.assertEqual(token_obj.token.machine_list[0].application, "luks")
        # As we deleted the slot, the partition now is the only entry in the
        # list
        self.assertEqual(token_obj.token.machine_list[0].option_list[
                             0].mt_value, "/dev/sdb1")

        # Overwrite option
        with self.app.test_request_context('/machine/tokenoption',
                                           method='POST',
                                           data={"hostname": "gandalf",
                                                 "serial": serial,
                                                 "application": "luks",
                                                 "partition": "/dev/sda1"},
                                           headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            self.assertTrue(result["value"] >= 1)

        # check if the options were set.
        token_obj = get_tokens(serial=serial)[0]
        self.assertEqual(token_obj.token.machine_list[0].application, "luks")
        # As we deleted the slot, the partition now is the only entry in the
        # list
        self.assertEqual(token_obj.token.machine_list[0].option_list[
                             0].mt_value, "/dev/sda1")


    def test_05_list_machinetokens(self):
        with self.app.test_request_context('/machine/token?serial=S1',
                                           method='GET',
                                           headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            self.assertEqual(len(result["value"]), 1)
            self.assertTrue(result["value"][0]["application"] == "luks")

        with self.app.test_request_context('/machine/token?hostname=gandalf',
                                           method='GET',
                                           headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            self.assertEqual(len(result["value"]), 1)
            self.assertTrue(result["value"][0]["application"] == "luks")



    def test_99_detach_token(self):
        serial = "S1"
        # create token
        init_token({"serial": serial, "type": "spass"})

        # Gandalf is 192.168.0.1
        with self.app.test_request_context(
                '/machine/token/S1/192.168.0.1/machineresolver1/luks',
                method='DELETE',
                headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            self.assertTrue(result["value"] >= 1)

        # check if the options were set.
        token_obj = get_tokens(serial=serial)[0]
        self.assertEqual(len(token_obj.token.machine_list), 0)


    def test_10_auth_items(self):
        # create an SSH token
        token_obj = init_token({"serial": self.serial2, "type": "sshkey",
                                "sshkey": SSHKEY})
        self.assertEqual(token_obj.type, "sshkey")

        # Attach the token to the machine "gandalf" with the application SSH
        r = attach_token(hostname="gandalf", serial=self.serial2,
                         application="ssh", options={"user": "testuser"})

        self.assertEqual(r.machine_id, "192.168.0.1")

        # fetch the auth_items for application SSH on machine gandalf
        with self.app.test_request_context(
                '/machine/authitem/ssh?hostname=gandalf',
                method='GET',
                headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            self.assertEqual(result["status"], True)
            sshkey = result["value"].get("ssh")[0].get("sshkey")
            self.assertTrue(sshkey.startswith("ssh-rsa"), sshkey)


        # fetch the auth_items on machine gandalf for all applications
        with self.app.test_request_context(
                '/machine/authitem?hostname=gandalf',
                method='GET',
                headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            sshkey = result["value"].get("ssh")[0].get("sshkey")
            self.assertTrue(sshkey.startswith("ssh-rsa"), sshkey)

        token_obj = init_token({"serial": self.serial3, "type": "totp",
                                "otpkey": "12345678"})
        self.assertEqual(token_obj.type, "totp")

        # Attach the token to the machine "gandalf" with the application SSH
        r = attach_token(hostname="gandalf", serial=self.serial3,
                         application="luks", options={"slot": "1",
                                                      "partition": "/dev/sda1"})

        self.assertEqual(r.machine_id, "192.168.0.1")

        # fetch the auth_items on machine gandalf for application luks
        with self.app.test_request_context(
                '/machine/authitem/luks?hostname=gandalf',
                method='GET',
                headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            slot = result["value"].get("luks")[0].get("slot")
            self.assertEqual(slot, "1")

        # fetch the auth_items on machine gandalf for application luks
        with self.app.test_request_context(
                '/machine/authitem/luks?hostname=gandalf&challenge=abcdef',
                method='GET',
                headers={'Authorization': self.at}):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res)
            result = json.loads(res.data).get("result")
            slot = result["value"].get("luks")[0].get("slot")
            self.assertEqual(slot, "1")
            response = result["value"].get("luks")[0].get("response")
            self.assertEqual(response, "93235fc7d1d444d0ec014ea9eafcc44fc65b73eb")