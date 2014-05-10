"""This file holds constant variables."""

# These constants are used to indicate the state/mode the client/server is in
STATE_GETNAME = "GETNAME"
STATE_CONNECTED = "CONNECTED"
STATE_NOT_CONNECTED = "NOT CONNECTED"
STATE_CHAT = "CHAT"

#####################
# Some constants used by lex.py and the views.
# These constants are used to label different parts of messages,
# so they can be dealt with spearately.
MENTION = 'MENTION'
HYPERLINK = 'HYPERLINK'
WHITESPACE = 'WHITESPACE'
NORMAL = 'NORMAL'
#####################