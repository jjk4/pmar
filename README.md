# 💿️ Python Music Auto Rip (PMAR)
This program auto-detects CDs in a drive, rips it to mp3 (or other formats) with "abcde", searches for album covers and adds them to the id3 tags of the ripped mp3s.
The only thing You have to do is put in the CD, close the tray and wait 😎

## Installation
This Repo is tested on Ubuntu Desktop 23.04, but it should work on the most Debian-based distros too. No support for Windows or Mac yet.

#### Install Prerequisites
`sudo apt install abcde lame cdparanoia id3v2 git`

#### Download PMAR
`git clone https://github.com/jjk4/pmar && cd pmar`

### Create directories for temporary files
```
mkdir -p output
mkdir -p tempdir
mkdir -p tempdir/music
mkdir -p tempdir/pictures
```
#### Create Python venv
```
python3 -m venv venv
source venv/bin/activate
```

#### Install required python modules
`pip install Google-Images-Search pillow mutagen python-dotenv`

## Configuration
There are 2 configuration files. *abcde.conf* for configuring abcde (you can leave this as it is) and *.env*.

#### Copy example config files
```
cp .env_example .env
cp abcde.conf_example abcde.conf
```
#### Configuring *.env*:
`DEVICE = "/dev/sr0"`
This is the device file of your disk drive. Usually it is */dev/sr0*. If you have multiple drives, it could be */dev/sr1*, */dev/sr2*, and so on. 

`ABCDE_CONF = "abcde.conf"`
This is the path to your abcde.conf file. You can leave it as it is.

`OUTPUT_DIR = "output/"`
This is the path where all the ripped music is saved to. This path can be relative or absolute. Be careful about the "/" in the end.

###### Configuring Google API Keys
(see [https://pypi.org/project/Google-Images-Search/](https://pypi.org/project/Google-Images-Search/))
-   Visit [https://console.developers.google.com](https://console.developers.google.com) and create a project.

-   Visit [https://console.developers.google.com/apis/library/customsearch.googleapis.com](https://console.developers.google.com/apis/library/customsearch.googleapis.com) and enable "Custom Search API" for your project. Here you get the API key for the config file.

-   Visit [https://console.developers.google.com/apis/credentials](https://console.developers.google.com/apis/credentials) and generate API key credentials for your project.

-   Visit [https://cse.google.com/cse/all](https://cse.google.com/cse/all) and in the web form where you create/edit your custom search engine enable "Image search" option and for "Sites to search" option select "Search the entire web but emphasize included sites". Here you get the Search Key / Search ID for your config file

Put in the `GOOGLE_API_KEY = ""` and `GOOGLE_SEARCH_KEY = ""`

## Starting
Now we're set up. If you're not seeing "(venv)" before your terminal prompt, do
`source venv/bin/activate`
again.
Now you can start the script with
`python3 ./rip.py`

You can now insert a CD. When the process is finished, it will be automatically ejected.
## Credits
This project was inspired by [Actionschnitzel](https://github.com/actionschnitzel)