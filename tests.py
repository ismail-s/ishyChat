import unittest

from ishyChat.Utils import Messages, Packer, Encryptor

class TestPacker(unittest.TestCase):
    def setUp(self):
        self.dict_to_pack = {'test': 1,
                             'test1': 2,
                             'test2': 3}

    def test_packer_can_turn_some_dict_into_string_and_back(self):
        res = Packer.packUp(self.dict_to_pack)
        res = Packer.packDown(res)
        self.assertEqual(res, self.dict_to_pack)

    def test_packer_can_deal_with_packing_and_unpacking_empty_strings(self):
        res = Packer.packDown(Packer.packUp({}))
        self.assertEqual(res, {})
    # Need to add many more tests and more useful
    # tests eg checking if things like pings work


if __name__ == '__main__':
    unittest.main()
