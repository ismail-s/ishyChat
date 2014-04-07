#This is for timing pings.
import time

#import message packer/unpacker
import ishyChat.Utils.Packer as Pk

#import ishyChat.Utils.Encryptor as Encryptor
#These are messages to display to the user
import ishyChat.Utils.Messages as Messages

class BaseConnection(object):
    """This is a base class that implements functionality
    
    common to other networking ClientConnection classes."""
    def __init__(self, factory, application, *args, **kwargs):
        self.factory = factory
        self.app = application
        #Set up the encryption-getting rid of this
        #self.encryptor = Encryptor.Encryptor(key)

    def connection_made(self):
        self.data_received(Messages.start_message)
        self.factory.state = "CONNECTED"

    def lineReceived(self, line):
        return self.data_received(line)

    def data_received(self, line):
        if not line: return  # If we haven't been given anything, then we don't do anything.
        dict_obj = Pk.packDown(line)
        name, msg, metadata = dict_obj['name'], dict_obj['message'], dict_obj['metadata']
        name_tag = ''
        if 'server' == name:
            if 'getname' in metadata:
                self.factory.state = "GET NAME"
            elif 'gotname' in metadata:
                self.factory.state = "CONNECTED"
                self.getUsers()
                self.app.addClient(self.name)
            elif 'pong' in metadata:
                msg = 'ping time: ' + str(time.clock() - self.ping_start)
            elif 'newclient' in metadata:
                new_name = msg[:msg.find(' ')]
                self.app.addClient(new_name)
            elif 'lostclient' in metadata:
                name_to_remove = msg[:msg.find(' ')]
                self.app.removeClient(name_to_remove)
            elif 'gotusers' in metadata:
                list_of_users = metadata['gotusers']
                self.app.addClients(*list_of_users)
                msg = 'Users in chatroom: ' + ' '.join(list_of_users)
        
        elif 'client' != name:
            name_tag = name
        self.app.addString(msg, name_tag)

    def sendLine(self, line):
        return self.send_data(line)

    def send_data(self, line):
        """Sends line, but only after checking to see
        
        if anything special need to be done (this is
        what self._command_parser does)."""
        state = self.factory.state
        if any((not line,
               self._command_parser(line),
               state == "NOT CONNECTED")): return
        
        if state == "GET NAME":
            self.name = line
            #self.name_enc = self.encryptor.encrypt_ECB(self.name)
            dict_to_send = Pk.makeDict(name=self.name, metadata={'newname': None})
        elif state == "CONNECTED":
            #iv, message = self.encryptor.encrypt(line)
            dict_to_send = Pk.makeDict(name=self.name, msg=line)
        line = Pk.packUp(dict_to_send)
        self.write(line)

    def _command_parser(self, line):
        """Checks if there are any commands in line.
        
        If there are, then they are dealt with. Note that
        GUI specific commands should have been dealt with
        already.
        
        If this function return True, then that means that
        the calling function should not print line.
        If it returns False, then the calling function
        *should* print line to the screen (ie insert it
        into the entrybox)."""
        if not line.startswith('/'): return
        line = line[1:].lower()
        if line == 'warning':
            self.data_received(Messages.warning_message)
            return True
        elif line == 'ping':
            if self.factory.state == "CONNECTED":
                self.write(Messages.ping_message)
                self.ping_start = time.clock()
                return True
        elif any((line == 'list', line == 'listusers')):
            if self.factory.state == "CONNECTED":
                self.getUsers()
                return True
        return False

    def getUsers(self):
        """Asks the server for a list of people in the chatroom"""
        self.write(Messages.getusers_message)

    def write(self, line):
        """Send line straight to the server. line may need
        
        to be encoded as bytes first.
        This function is to be implemented by the subclass."""
        pass
