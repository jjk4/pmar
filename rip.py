import os, sys, fcntl, time
from google_images_search import GoogleImagesSearch
from PIL import Image
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from dotenv import load_dotenv
import musicbrainzngs
from urllib.request import urlretrieve

musicbrainzngs.set_useragent("pmar", "0.1", "https://github.com/jjk4/pmar")

load_dotenv()
DEVICE = os.getenv("DEVICE")
ABCDE_CONF = os.getenv("ABCDE_CONF")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_KEY = os.getenv("GOOGLE_SEARCH_KEY")
if(os.getenv("USE_GOOGLE") == "True"):
    USE_GOOGLE = True
else:
    USE_GOOGLE = False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_drive_state(device): # 0 = no info; 1 = no disc; 2 = tray open; 3 = not ready yet; 4 = disc ok
    fd = os.open(device, os.O_NONBLOCK) or os.exit(1)
    state = fcntl.ioctl(fd, 0x5326)
    os.close(fd)
    return state

def get_id3_artist():
    filepath = "tempdir/music/"
    filepath += os.listdir("tempdir/music/")[0] + "/"
    filepath += os.listdir(filepath)[0] + "/"
    filepath += os.listdir(filepath)[0]
    audio = EasyID3(filepath)
    search_term = audio["artist"][0]
    search_term = search_term.replace("_", " ")
    return search_term

def get_id3_album():
    filepath = "tempdir/music/"
    filepath += os.listdir("tempdir/music/")[0] + "/"
    filepath += os.listdir(filepath)[0] + "/"
    filepath += os.listdir(filepath)[0]
    audio = EasyID3(filepath)
    search_term = audio["album"][0]
    search_term = search_term.replace("_", " ")
    return search_term

def download_images_google():
    _search_params = {
        'q': get_id3_artist() + " " + get_id3_album() + " Cover",
        'num': 10,
        'fileType': 'jpg|png'
    }

    gis.search(search_params=_search_params, path_to_dir=picture_directory)
    
def download_images_musicbrainz():
    try:
        artist = get_id3_artist()
        album = get_id3_album()
        artist_id = musicbrainzngs.search_artists(query=artist, limit=1)["artist-list"][0]["id"]
        album_id = musicbrainzngs.search_releases(query=album, artist=artist_id, limit=1)["release-list"][0]["id"]

        imgdata = musicbrainzngs.get_image_list(album_id)["images"]
        for image in imgdata:
            if(image["approved"] == True and image["front"] == True):
                urlretrieve(image["image"], "tempdir/pictures/musicbrainz.jpg")
                return True
        if(len(os.listdir("tempdir/pictures")) == 0):
            raise Exception("No pictures found")
    except:
        return False
    
def get_best_image():
    last_img_height = 0
    last_img_path = ""
    for filename in os.listdir(picture_directory):
        f = os.path.join(picture_directory, filename)
        img = Image.open(f)
        if(img.height > last_img_height):
            last_img_height = img.height
            if(last_img_path != ""):
                os.remove(last_img_path)
            last_img_path = f
        else:
            os.remove(f)

def resize_image():
    path = "tempdir/pictures/" + os.listdir("tempdir/pictures")[0]
    image = Image.open(path) # First convert to jpg 
    image = image.convert("RGB") # remove alphachannel
    image.save("tempdir/pictures/resized.jpg")
    image.close()
    if(os.path.getsize("tempdir/pictures/resized.jpg")>1000000): # Only save pictures > 1MB
        image = Image.open(path)
        image = image.resize((int(image.width/2), int(image.height/2)))
        image.save("tempdir/pictures/resized.jpg")
        image.close()
        
def add_images_to_id3():
    filepath = "tempdir/music/"
    filepath += os.listdir("tempdir/music/")[0] + "/"
    filepath += os.listdir(filepath)[0] + "/"
    for filename in os.listdir(filepath):
        f = os.path.join(filepath, filename)
        audio = MP3(f, ID3=ID3)
        audio.tags.add(
            APIC(
                encoding=3,  # 3 is for utf-8
                mime="image/png",  # can be image/jpeg or image/png
                type=3,  # 3 is for the cover image
                desc='Cover',
                data=open("tempdir/pictures/resized.jpg", mode='rb').read()
            )
        )
        audio.save()
        
def cleanup():
    dir_name = os.listdir("tempdir/music")[0]
    os.rename("tempdir/music/" + dir_name, OUTPUT_DIR + dir_name)
    os.system("rm -r tempdir/music/*")
    os.system("rm -r tempdir/pictures/*")

###################################################################################################################################################
picture_directory = "tempdir/pictures"
gis = GoogleImagesSearch(GOOGLE_API_KEY, GOOGLE_SEARCH_KEY)

while True:
    skip_images = False
    if(get_drive_state(DEVICE) == 4):
        print(bcolors.OKGREEN + "RIPPING CD!!!" + bcolors.ENDC)
        os.system("abcde -N -c " + ABCDE_CONF + " -d " + DEVICE)
        print(bcolors.OKGREEN + "Downloading Images..." + bcolors.ENDC)
        if(download_images_musicbrainz() == False):
            if(USE_GOOGLE):
                print(bcolors.OKCYAN + "No album art found on Musicbrainz. Searching on Google..." + bcolors.ENDC)
                download_images_google()
            else:
                skip_images = True
                print(bcolors.WARNING + "Could not find album art. Skipping" + bcolors.ENDC)
        if(not(skip_images)):
            get_best_image()
            resize_image()
            add_images_to_id3()
        print(bcolors.OKGREEN + "Finishing..." + bcolors.ENDC)
        cleanup()
        os.system("eject " + DEVICE)
        time.sleep(1)
    else:
        print(bcolors.OKGREEN + "Waiting for Disk..." + bcolors.ENDC)
        time.sleep(1)