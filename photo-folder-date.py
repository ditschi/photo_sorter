import subprocess
import argparse
import os
import re
import sys
import shutil
import glob
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime, timedelta
import locale

DEBUG = None

owerwrite_existing_dates = True

# -------- convenience methods -------------

PARSER = argparse.ArgumentParser(description="Script to add date to folder name according to te pictures contained.")
PARSER.add_argument("-d", "--dir", help="Directory that is recursively parsed and contained folders are renamed.",
                    required=True)
PARSER.add_argument("-t", "--test", help="Test-mode: only write do log file what would be done.", action="store_true")
PARSER.add_argument("-f", "--force",
                    help="Force renaming - this will rename also if a folder name already contains a date.",
                    action="store_true")
PARSER.add_argument("--debug", help="More debug output.", action="store_true")



def getExifData(filename):
    ret = {}
    try:
        image = Image.open(filename)
        info = image._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
        return ret
    except IOError:
        if DEBUG:
            print("[W] IOError when accessing '{}'".format(filename))
        return None
    
    


def ImageDate(filename):
    """Returns the date and time from image(if available)\nfrom Orthallelous"""
    TTags=[('DateTimeOriginal','SubsecTimeOriginal'),#when img taken
    ('DateTimeDigitized','SubsecTimeDigitized'),#when img stored digitally
    ('DateTime','SubsecTime')]#when img file was changed
    #for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2, 2.3
    exif=getExifData(filename)
    if exif is None:
        print("[E] Could not get Exif data for '{}'".format(filename))
        return None
    
    for i in TTags:
        dT, sub = exif.get(i[0]), exif.get(i[1],0)
        dT = dT[0] if type(dT) == tuple else dT#PILLOW 3.0 returns tuples now
        sub = sub[0] if type(sub) == tuple else sub
        if dT!=None:break#got valid time
    if dT==None:return#found no time tags
    
    try:
        T=datetime.strptime('{}.{}'.format(dT,sub),'%Y:%m:%d %H:%M:%S.%f')
        #T=time.mktime(timeIOError when accessingIOError when accessing.strptime(dT,'%Y:%m:%d %H:%M:%S'))+float('0.'+sub)
        return T
    except:
        print("[W] Could not get image date '{}'".format(filename))
        return None


def parse_args():
    global DEBUG
    args = PARSER.parse_args()
    DEBUG = args.debug
    return args

def images_in_folder(folder):
    image_counter = len(glob.glob1(folder, "*.jpg"))
    image_counter += len(glob.glob1(folder, "*.jepg"))
    if image_counter == 0:
        return False
    return True


def main():
    # loop through all sub-folders

    # per folder if no date yet
    # get oldest and newest date
    # calculate folder prefix
    # rename folder
    args = parse_args()
    

    log_file = open('photo-folder-rename.log', 'w')
    log_file.write("### Renaming folders log on {} ###\n".format(str(datetime.now())))
    log_file.write("source;destination\n")

    for dir_path, dirs, files in os.walk(args.dir):
        if "@eaDir" in dir_path:
                #print("...skipping dir_path '{}'".format(os.path.join(dir_path)))
                continue
            
        for directory in dirs:
            if "@eaDir" in directory:
                #print("...skipping directory '{}' in '{}'".format(directory, dir_path))
                continue
            if not images_in_folder(os.path.join(dir_path,directory)):
                #print("...skipping directory '{}' without pictures".format(os.path.join(dir_path, directory)))
                continue
            

            # detect folders that already have a date
            regexp = re.compile(r'^\d{2,4}')
            if (regexp.search(directory) and not args.force):
                #print("[i] directory '{}' is skipped because it has already a date".format(directory))
                continue
            
            if DEBUG:
                print("Running in directory '{}'".format(os.path.join(dir_path, directory)))
                
            pictures_found = False
            old_date = None
            new_date = None
            for filename in os.listdir(os.path.join(dir_path,directory)):
                extensions = ('.jpg', '.jpeg')
                if os.path.splitext(os.path.join(dir_path,directory,filename))[-1].lower() in extensions:
                    #print("Checking image '{}'".format(filename))

                    #get date
                    try:
                        current_date = ImageDate(os.path.join(dir_path, directory,filename))
                        #print current_date
                        if current_date is None:
                            log_file.write("[W] Could not get the date of a picture -> skipping directory '{}'".format(os.path.join(dir_path, directory)))
                            pictures_found = False
                            break
                        if new_date is None or old_date is None:
                            new_date = current_date
                            old_date = current_date
                            pictures_found = True
                        elif current_date.__gt__(new_date):
                            new_date = current_date
                        elif current_date.__lt__(old_date):
                            old_date = current_date
                    except AttributeError:
                        if DEBUG:
                            log_file.write("[W] AttributeError when accessing date of '{}' -> skipping directory '{}'".format(filename, os.path.join(dir_path, directory)))
                        pictures_found = False
                        break
                    #if DEBUG:
                        #print "current_: " + str(current_date) + "->" + "{}_{}_{}".format(current_date.strftime('%d'), current_date.strftime('%m'), current_date.year)
                        #print "old_date: " + str(old_date) + "->" + "{}_{}_{}".format(old_date.strftime('%d'), old_date.strftime('%m'), old_date.year)
                        #print "new_date: " + str(new_date) + "->" + "{}_{}_{}".format(new_date.strftime('%d'), new_date.strftime('%m'), new_date.year)
                        #print()


            if (pictures_found):
                try:
                    dir_base_name = re.search(r'^[\d\-_\.]* ?(.*)', directory).group(1)
                except:
                    print("[W] directory base name pattern did not match '{}'".format(directory))

                # check the found dates
                #if DEBUG:
                    #print "old_date: " + str(old_date) + "->" + "{}_{}_{}".format(old_date.strftime('%d'), old_date.strftime('%m'), old_date.year)
                    #print "new_date: " + str(new_date) + "->" + "{}_{}_{}".format(new_date.strftime('%d'), new_date.strftime('%m'), new_date.year)

                if old_date.date() == new_date.date():
                    # all pictures on one day
                    folder_date = old_date.date()
                else:
                    if (old_date.year == new_date.year):
                        if (old_date.month == new_date.month):
                            # only days are different
                            folder_date = "{}-{}".format(old_date.year, old_date.strftime('%m'))
                        else:
                            # months are different
                            folder_date = "{}".format(old_date.year)
                    else:
                        # different years
                        folder_date = "{} - {}".format(old_date.year, new_date.year)
                        
                if DEBUG:
                    print(" -> folder_date: ", folder_date)

                # rename directory
                old_dirname = directory
                new_dirname = "{} {}".format(folder_date, dir_base_name)
                old_dir_path = os.path.join(dir_path,old_dirname)
                new_dir_path = os.path.join(dir_path,new_dirname)
                
                
                print("Renaming folder '{}' -> '{}'".format(old_dirname, new_dirname))
                if new_date.year - old_date.year > 1:
                    message = "[W] more than one year of photos in '{}'".format(new_dir_path)
                    print(message)
                    log_file.write(message + "\n")
                log_file.write("{};{}\n".format(old_dir_path, new_dir_path))
                if not args.test:
                    os.rename(old_dir_path, new_dir_path)

    log_file.close()


if __name__ == '__main__':
    main()
