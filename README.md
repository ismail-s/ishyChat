#ishyChat
A very basic chat client/server implementation written in Python and using Twisted for the connection.
Note that this is a very early in-development version, and I am not even sure whether or not to keep using Python...

Also, there is some sort of encryption in place, but it is not very good at the moment, to put it mildly.

##Features
* It works (well, this is a very early ALPHA version).
* It has a cool name.
* It is minimalistic.
* It runs over SSL, but with no authentication (yet).
* It has some undocumented syntax which allows previous messages to be quickly brought up in the entrybox (read the code to understand this). This now also works with arrow keys too (like in Terminal).
* It uses JSON when sending/receiving messages. Because JSON is cool/makes the code nicer-ish.

##TODO
* ~~Do more refactoring, putting client and server parts in their own folders, separating the classes in Client.py into separate files.~~
* Update/add docstrings
* ~~Decide on a license.~~
* Fix glitches and whatnot.
* **Test on Windows and between different machines.**
* Add ~~bold and~~ colour text to make things look nicer.
* Add ~~command-line options and~~ a gui interface for choosing address and port.
* Add a CLI interface using curses.
* Maybe add a GTK interface too.
* Add hyperlink support (using the webbrowser module).
* Add media support (well, images, and maybe other stuff).
* Add file sharing-ness (heck, I wonder if I'll even work through all the previous items on this list...).

Feel free to do any of these for me.
