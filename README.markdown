An random collection of (mostly) python code I wouldn't use in production.

projects:

* **Fixture Factory** - Automate Django fixture creation with this library.  The project is inspired by factoryboy and currently used by the HunchWorks project 

* **IPython Scripting** - Write scripts that utilize IPython syntax and take advantage of the full IPython feature set.  Including shell integration, lazy syntax, magic functions and aliases, input and output history, etc.

* **Markov Chains** - for random sequence generation.  Works on input split by space or by character, depending on how you configure it


bin:

* **bash_wrapper.py** - wrap bash scripts in python to enable colorized logging, controlled workflow, and some basic bash-python integration.
* **bliptv_video_downloader.py** - given a bliptv video id
 * **cssparser.py** - reformat css from web into readable version
* **grepfieldmixin.py** - Make objects with useful variants of grep and field methods
* **ipyscript.py** - compile and execute IPython scripts
* **join.py** - Inner or Outer join two csvs on a given column (ie join key)
* **markovchain.py** - sym link to markov project 
* **matching_utils.py**
* **md5_async.py** - asynchronous md5 sum against multiple files. 
* **mixins.py** - 'make' functions to make using mixins/multiple inheritance easier.
* **multidb_query.py** - execute sql queries against two (remote) databases, merge results, and drop into ipython shell. Super useful!  
* **myip** - outputs public ip
* **peekable.py** - make an iterator peekable (ie look ahead, but don't call next() )
* **poisson_gradient_descent.py** - an example implementation that's both ugly and customized to a particular project
* **tmux-sessions.sh** - sym link to tmux project
* **tmux_backup.sh** - sym link to tmux project

bin/helper_files:
* **email_settings.py** - used by bin/bash_wrapper.py to send emails
* **query.sql** - used by multidb_query.py if no query doc provided

