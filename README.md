
![Preview](https://raw.githubusercontent.com/dungntnew/sady/master/screenshoot.png "Usage..")

```bash
>> sady track -> to enjoy (๑˃̵ᴗ˂̵) 
```

### Quick Install 

(This script use for Macosx only. For ubuntu or other linux users please use manual install.)
```
$ curl "https://raw.githubusercontent.com/dungntnew/sady/master/install.sh?v=1.0" | sh 
```

### Dependences
- python >= 3.3 (asyncio requires Python 3.3 or later)
- mplayer (music player commandline version)

### Manual Initialization

Install dependences if need (MacOSX). 

( For other linux - window users , to install mplayer and python3 please type:`$ [google('how to install %s' % pkg for pkg in dependences)] `)

```
# install mplayer via homebrew
$ brew install mplayer

# install python3 
$ brew install python3
```

Clone & Install `sady` 

(For all linux users & Macosx users)
```
# clone repo to your local directory
$ SADY_HOME_DIR=~/.sady
$ git clone git@github.com:dungntnew/sady.git $SADY_HOME_DIR
$ cd $SADY_HOME_DIR

# create python env & install dependence python packages
$ virtualenv -p python3 ./env && source ./env/bin/activate
$ pip install -r requirements.txt
```

Add `sady` commandline to your bashrc (~/.bash_profile)  

(For all linux users & Macosx users)
```
$ echo "export SADY_HOME_DIR=$SADY_HOME_DIR" >> ~/.bash_profile
$ echo "alias sady='cd $SADY_HOME_DIR && ./env/bin/python3 ./__init__.py'" >> ~/.bash_profile
$ source ~/.bash_profile
```

### Run -> to enjoy (๑˃̵ᴗ˂̵)
```
$ sady -q "Lets it go Idina Menzel" 
```


### Usage

cmd mod

| command        | description      
| ------------- |:-------------:|
| any | search and play any track by name, keywords, etc.. |
| exit | to quit sady |
| search      | search track by name, keywords, singer, etc..  |
| select      | select one track index to play (auto sync)       |
| sync | sync track to play in local with track index (no param -> all)      |
| list | list all tracks in playlist (alias: ll, top)|
| next | next tracks page |
| prev | prev tracks page |

playing mod:

( ref: player --help  or man player to see help)

| command        | description      
| ------------- |:-------------:|
| q | to quit mplayer - back to sady cmd |
| space | to pause - replay track |










