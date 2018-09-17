# Documentation

## Introduction

Project Wiki is inspired by ProjectForum of which the service has been discontinued. This is also the reason why Project Wiki is created.

### What it is for and who should use it

Project Wiki is essentially an online multi-user notebook. It aims to allow scientists and researchers to document their research and share it among their co-workers. Though, it is not limited to research. Anyone who needs a tool like this is welcome to use it.

## Features

### Server reload

If on `super-admin` page `server reload` is clicked, the server will shutdown Project Wiki, and restart it. 
This is useful for reloading Project Wiki remotely, because glitches might happen and cause Project Wiki to behave strangely.

### Multiple groups

Log in as super adminstrator on Cover page, and create a new group. When a new group is created, its first group admin can be either a new user or an existing user. If it were an existing user, the email and password filled in do not change the original ones.

### Different roles

There are 4 roles for an account to access Project Wiki.

* Super
	* Can basically do anything.
* Admin
	* Add users
	* Read/Write pages
* User
	* Read/Write pages
* Guest
	* Only Read pages

There should be only one account being `Super`. Also, the only way to create a `Super` is to use command-line, `python manage.py create_admin`. `Super` is really just designed to manage Project Wiki, and its email address is the one used to send notification emails, so it is better to use other account for normal activities.<br>
The other 3 roles are group-specific, and an account can have different roles in different groups. As an example, an account can be `Admin` in group 1, `User` in group 2, and `Guest` in group 3.

### Wiki page

User can create new pages and edit existing pages using Markdown syntax.

Once a new group is created, a new database, a new folder, and a empty group homepage are generated.

### Comment

User can also comment on a page, using the same Markdown syntax as editing a page. Moreover, one can use `[@user1]` to notified `user1` to read the page.

### Rename - update references and changes

Any page except homepage can be renamed. After a page is renamed, all the pages which reference it and previous versions that contains it will also be updated.

### History

Once page content is modified, the differences between the current and previous version will be achived. These archived versions can then be used to view the differences between versions, and recover previous versions.

### Table of contents

With markdown, one can input headings which would be used to generate table of contents.

### Keypages

Keypages can be added by group admins, and will be displayed in the sidebar.

### Changes

In the sidebar, the 5 most recently changed pages are listed. The timestamp is the time when the latest change is made.

### Upload

Files can be uploaded to Project Wiki.

### Edit - Markdown, real-time renderring

In editing page, the input markdown is renderred in real time.
On the top left corner, there is a menu button.
When you hover over it, a few options pop up.

* Upload - upload files to Project Wiki and append references to the end of markdown code
* Preview - show/hide the editing part
* Save - save changes
* Cancel - return to page
* Drap & drop
	* If a text file is dropped in editing section (left part of the page), its content will filled in automatically. DO NOT other types of files, because they will also be read as text file.
	* When a file or files are dropped in the preview section (right part of the page), they will be uploaded, and their file id will be appended at the bottom of editing section.

### References

All wiki pages can reference each other. The reference page shows a list of pages which reference its corresponding wiki page.

### Group admin privileges

* Add new accounts to group, and also edit them
* List all uploaded files
* **Delete files and pages**

### Markdown - python != js

When editing a page, the real-time renderring is done with a [Javascript library](https://github.com/chjj/marked). However, when markdown code is sent to server, Project Wiki uses a [Python library](https://pythonhosted.org/Markdown/). These two libraries uses completely different algorithms, so there might be differences between renderred html.

[Another Python library](https://github.com/lepture/mistune) tries to mimic the Javascript library mentioned above, but it is not quite there yet. If it matures, a future update might switch to it.

### Full text search

Users can search pages that contain input keywords. Priorities: title > content > comment.<br>
The search functionality is based on the native full text search feature in MongoDB.
In order to achieve it, MongoDB text-indexes words.
Here, the default language is English, which only means it is optimized to search English language, but not limited to.
Note that MongoDB supports many languages, but Chinese and a few other languages are only supported in Enterprise version.
[More details](https://docs.mongodb.com/manual/reference/text-search-languages/)

## How to setup, start, and shutdown Project Wiki

### Mac OS

#### Setup

* Install Python 3.6 (with pip)
* [Download and install mongodb](https://docs.mongodb.com/manual/tutorial/)
* [Download and install Caddy](https://caddyserver.com/tutorial/beginner)

Modify `config.py` and `Caddyfile` accordingly. Make sure MongoDB and caddy are not running.

Run the following commands.

```
$ cd /path/to/Project-Wiki/macosx
$ bash setup.sh
```

Now the server is setup. To start it,

```
$ bash start.sh
```

If the IP in `Caddyfile` remains `0.0.0.0`, Project Wiki can only be accessed via server IP on local network.
To enable automatic HTTPS for secure data transmission, a few requirements should be satisfied, [detailed here](https://caddyserver.com/docs/automatic-https).
If setup correctly, Project Wiki will be available at `https:\\<your.domain>`.

#### Start

```
$ cd /path/to/Project-Wiki/macosx
$ bash start.sh
```

#### Shutdown

```
$ cd /path/to/Project-Wiki/macosx
$ bash stop.sh
```

#### Backup

* Copy the entire `Project_Wiki_Data` folder.

#### Retore

* Modify `config.py` and `Caddyfile` accordingly
* Move the backup `Project_Wiki_Data` folder to the parent directory of `Project-Wiki`

### Windows

Tested on `Window 7 Enterprise 64-bit`

#### Setup

* Install Python 3.6 (with pip)
* [Download and install mongodb](https://docs.mongodb.com/manual/tutorial/)
	* Interactive Installation - double-click the .msi file
	* Use default installation directory (C:\Program Files\MongoDB\Server\3.4\)
	* **DO NOT SETUP MongoDB ENVIRONMENT YOURSELF.** It will be setup automatically in `setup.bat`.
* [Download and install Caddy](https://caddyserver.com/tutorial/beginner)
	* Extract `caddy.exe` in downloaded zip file
	* Put `caddy.exe` in Project-Wiki folder

Modify `config.py` and `Caddyfile` accordingly. Make sure MongoDB and caddy are not running.

When installing MongoDB, if you chose `Custom`, and change installation directory, you will need to modify `setup.bat` accordingly.

Right-click `setup.bat` in `windows` folder, and run it as administrator.

#### Start

Right-click `start.bat` in `windows` folder, and run it as administrator.

#### Shutdown

* Close the console that runs Project Wiki.
* Right-click `stop.bat` in `windows` folder, and run it as administrator.
	* The `stop.bat` will stop `pythonw.exe` in background processes.
	* Be aware if you have other `pythonw.exe` running.

#### Backup

* Copy the entire `Project_Wiki_Data` folder.

#### Retore

* Modify `config.py` and `Caddyfile` accordingly
* Run `setup.bat` as administrator first
* Move the backup `Project_Wiki_Data` folder to the parent directory of `Project-Wiki`

### Linux

To be honest, Linux is the best choise to host a server, and the process and shell script should be almost the same to Mac OS. 
However, I do not possess a Linux machine at hand and hence the lack of instructions. 

On the other hand, if you are a Linux user, I am sure you can figure it out yourself. :)

## Customize

### Landing page

The default background image of the landing page is a bird eye photo of Brigham Young University. 
To change it, rename your own picture `cover.jpg`, and replace app/static/images/cover.jpg with it. 

## Notes

### [Caddy](https://caddyserver.com/tutorial/beginner)

    $ caddy -conf /path/to/Caddyfile

### MongoDB

#### Native

Backup database

	$ mongodump --out <back dir> --username <username> --password <password>

Restore database

	$ mongorestore --username <username> --password <password> <backup dir>

#### Setup mongodb docker container

    $ docker run --name my_mongo --restart=always -d -p 27017:27017 mongo:3.4.4 mongod --auth
    ($ docker run --name my_mongo --restart=always -d -p 27017:27017 -v <host dir>:/backup mongo:3.4.4 /bin/bash -c "mkdir /backup; mongod --auth")
    $ docker exec -it my_mongo bash
    # mongo
    > use admin
    > db.createUser({user:"foouser",pwd:"foopwd",roles:[{role:"root",db:"admin"}]})
    > exit
    # exit


## TO DO

* Sort search results, recent pages, and other lists
* Advanced search
* Update editor
* Button to hide Side bar
* Update mongoengine for the next release
* Use cloud service rather than hosting server by ourselves
* Private groups
* Configure right-click of file link

* **Mobile app**
	* One button upload
