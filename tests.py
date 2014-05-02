import unittest
import sys
if sys.version_info >= (3, 3):
    import unittest.mock as mock
    from unittest.mock import patch
else:
    import mock
    from mock import patch

from ishyChat.Utils import Messages, Packer

try:
    from ishyChat.Utils import Encryptor
except ImportError:
    Encryptor = '' # This is just to allow for PyCrypto not being
    # installed.

import ishyChat.Utils.Constants as Const
import ishyChat.Server.BaseServer as BaseServ

class TestPacker(unittest.TestCase):

    def test_packer_can_turn_some_dict_into_string_and_back(self):
        dict_to_pack = {'test': 1,
                        'test1': 2,
                        'test2': 3}
        res = Packer.packUp(dict_to_pack)
        res = Packer.packDown(res)
        self.assertEqual(res, dict_to_pack)

    def test_packer_can_deal_with_packing_and_unpacking_empty_strings(self):
        res = Packer.packDown(Packer.packUp({}))
        self.assertEqual(res, {})
    # Need to add many more tests and more useful
    # tests eg checking if things like pings work
    
    def test_makeDict_returns_valid_dict_when_given_no_args(self):
        res = Packer.makeDict()
        ans = {'message': '', 'name': None, 'metadata': {}, 'type': 'text'}
        self.assertEqual(res, ans)
    
    def test_makeDictAndPack_creates_a_valid_dict(self):
        res = Packer.makeDictAndPack(msg = 'test', metadata = {'test': None}, name = 'client', type = 'text')
        res = Packer.packDown(res)
        self.assertIsInstance(res, dict)

@unittest.skipIf(Encryptor == '',
"PyCrypto probably hasn't been installed.")
class TestEncryptor(unittest.TestCase):
    def setUp(self):
        self.enc = Encryptor.Encryptor('some key')
        self.test_str = 'some random text'
        
    def test_encrypt_and_decrypt_are_inverse_of_each_other(self):
        res = self.enc.encrypt(self.test_str)
        res = self.enc.decrypt(*res)
        self.assertEqual(res, self.test_str)

    def test_encrypt_and_decrypt_work_on_empty_strings(self):
        res = self.enc.encrypt('')
        res = self.enc.decrypt(*res)
        self.assertEqual(res, '')
    
    def test_ECB_encryption_on_normal_string(self):
        res = self.enc.encrypt_ECB(self.test_str)
        res = self.enc.decrypt_ECB(res)
        self.assertEqual(res, self.test_str)
    
    def test_ECB_encryption_on_empty_string(self):
        res = self.enc.encrypt_ECB('')
        res = self.enc.decrypt_ECB(res)
        self.assertEqual(res, '')

class TestBaseServer(unittest.TestCase):
    def test_state_is_initially_getname(self):
        serv = BaseServ.BaseServer(clients = [])
        self.assertEqual(serv.state, Const.STATE_GETNAME)

    @patch.object(BaseServ.BaseServer, 'data_received')
    @patch.object(BaseServ.BaseServer, 'connection_lost')
    @patch.object(BaseServ.BaseServer, 'connection_made')
    def test_camelCase_methods_call_non_camel_case_methods(self, conn_made, conn_lost, data_recv):
        serv = BaseServ.BaseServer(clients = [])

        serv.connectionMade()
        self.assertEqual(conn_made.call_count, 1)

        serv.connectionLost('some_reason')
        self.assertEqual(conn_lost.call_count, 1)

        serv.lineReceived('some line')
        self.assertEqual(data_recv.call_count, 1)

    def test_whether_client_is_deleted_when_connection_is_lost(self):
        clients = {'1': 'test'}
        serv = BaseServ.BaseServer(clients = clients)
        serv.name = '1'
        serv.connection_lost('some reson')
        self.assertEqual(clients, {})

    @patch.object(BaseServ.BaseServer, 'broadcast')
    def test_message_broadcast_when_client_disconnects(self, broadcast):
        serv = BaseServ.BaseServer(clients = {'1': 'test', '2': 'test'})
        serv.name = 't'
        #import pdb; pdb.set_trace()
        serv.connection_lost('some reason')
        self.assertEqual(broadcast.call_count, 1)

    def test_broadcast_can_send_messages_to_all_clients(self):
        clients = {}
        for num in range(10):
            clients[str(num)] = mock.MagicMock()
        serv = BaseServ.BaseServer(clients = clients)
        serv.name = '1'
        to_broadcast = 'msg to broadcast'
        serv.broadcast(to_broadcast)
        
        #The remaining lines in this method are here as python 2.7
        # doesn't have subtests, which would replace all these lines
        # with just three easy-to-read ones...
        res = []
        for mocks in clients.values():
            res.append(mocks.write.call_args[0] == (to_broadcast,))
            res.append(mocks.write.call_count == 1)
        self.assertTrue(all(res))

    def test_broadcast_can_send_messages_to_all_clients_excluding_self(self):
        clients = {}
        for num in range(10):
            clients[str(num)] = mock.MagicMock()
        serv = BaseServ.BaseServer(clients = clients)
        serv.name = '1'
        to_broadcast = 'msg to broadcast'
        serv.broadcast(to_broadcast, also_send_to_self = False)

        self.assertEqual(clients['1'].write.call_count, 0)
        del clients['1']

        #The remaining lines in this method are here as python 2.7
        # doesn't have subtests, which would replace all these lines
        # with just three easy-to-read ones...
        res = []
        for mocks in clients.values():
            res.append(mocks.write.call_args[0] == (to_broadcast,))
            res.append(mocks.write.call_count == 1)
        self.assertTrue(all(res))

    # Still need to make fake packets, and see how they are dealt with.
    # Also need to test corrupt packets to make sure they are handled
    # correctly and dont mess up the program





if __name__ == '__main__':
    unittest.main()
