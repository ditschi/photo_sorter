import subprocess
import argparse
import os
import re
import sys
import shutil
import glob
import filecmp



owerwrite_existing_dates = True

# -------- convenience methods -------------

PARSER = argparse.ArgumentParser(description="Script to add date to folder name according to te pictures contained.")
PARSER.add_argument("-d", "--dir", help="Directory that is recursively parsed and contained folders are renamed.",
                    default=".")


def parse_args():
    args = PARSER.parse_args()
    return args


# def images_in_folder(folder):
#     image_counter = len(glob.glob1(folder, "*.jpg"))
#     image_counter += len(glob.glob1(folder, "*.jepg"))
#     if image_counter == 0:
#         return False
#     return True


def main():
    # loop through all sub-folders

    # per folder if no date yet
    # get oldest and newest date
    # calculate folder prefix
    # rename folder
    args = parse_args()

    found_files = list()

    for dir_path, dirs, files in os.walk(args.dir):
        if "@eaDir" in dir_path:
            # print("...skipping dir_path '{}'".format(os.path.join(dir_path)))
            continue

        for file in files:
            if "@eaDir" not in file:
                found_files.append(os.path.join(dir_path, file))

    print("Found '{}' files in directory '{}'".format(len(found_files), os.path.abspath(args.dir)))

    for file in found_files:
        filename, extension = os.path.splitext(file)
        original_filename = None

        for ending in ["_1", "_2", "_3"]:
            if filename.endswith(ending):
                original_filename = filename.replace(ending, "") + extension
                print(original_filename)

        if not original_filename:
            continue

        if original_filename in found_files:
            if filecmp.cmp(original_filename, file):
                print("will remove '{}' because '{}' exists and is duplicate".format(file, original_filename))
            else:
                print("not removing '{}' because no duplicate was found".format(file, original_filename))
        else:
            print("renaming '{}' to '{}'".format(file, original_filename))


if __name__ == '__main__':
    main()
