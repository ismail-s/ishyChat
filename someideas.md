#Ideas on further development

(note that this is just some notes of mine-feel free to comment/improve them)
##Redesigning the packets
###What we want to be able to do (that involves client and server)

* We want the clients and server to be able to send/receive messages
* We want to be able to send pings
* We want to be able to change name during conversations-maybe just do this how they do it in irc as a single command
* We want to be able to get a list of clients from the server


Metadata-this is a big fat list. Items are just strings, and lists within metadata are arguments of the previous item.

```python
{'type'    : 'text/image/file' # Type of message being sent
 'message' : 'msg',
 'name'    : 'jim',            # (eg green..., client, server)
 'metadata': {'ping/pong': True,
              'newname': 'john',
              'gotname': True,
              'getusers': True,
              'gotusers': ['list_of_all_users']
             },
}
```

##Tkinter hyperlinks
###Some links to follow up on

These are related to setting up hyperlinks for Tkinter

* https://mail.python.org/pipermail/tkinter-discuss/2008-August/001618.html
* http://effbot.org/zone/tkinter-text-hyperlink.htm, http://effbot.org/zone/copyright.htm

###Discussion
* For the Tkinter hyperlinks, there can be a separate hyperlnks module.
* Then, when text is to be added, it is parsed and a list of tuples/lists is made by some separate view-independent code.
* Each tuple has a fragment of text and what type of text it is (eg normal, hyperlink, @mention)
* Then, we can run through and insert each text fragment with the corresponding tags

##CLI view
* This may require using addReader/addWriter-this needs further research/testing

##Image support
* Images will have to be limited in filesize and size in textbox
* For CLI View, look into:
 * http://stevendkay.wordpress.com/2009/09/08/generating-ascii-art-from-photographs-in-python/
 * http://playpython.blogspot.co.uk/2012/08/generate-ascii-image-of-yours.html
