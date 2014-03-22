#Some ideas for how the packets that are sent/received look

(note that this is just some notes of mine-feel free to comment/improve them)

##What we want to be able to do (that involves client and server)

* We want the clients and server to be able to send/receive messages
* We want to be able to send pings
* We want to be able to change name during conversations-maybe just do this how they do it in irc as a single command
* We want to be able to get a list of clients from the server


Metadata-this is a big fat list. Items are just strings, and lists within metadata are arguments of the previous item.

'''JSON
{'message' : msg,
 'name'    : name (eg green..., client, server),
 'metadata;: [ping/pong, changename, [newname], gotname, getusers/gotusers],
}
'''
