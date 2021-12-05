import os
import sys
import datetime
import re
from PIL import Image
from PIL.ExifTags import TAGS

from .text_to_datetime import text_to_datetime

class ExifError(AttributeError):
    pass

class PhotoMetadata:
    def __init__(self, filepath):
        self.filepathpath = os.path.abspath(path)
        self.filename = os.path.splitext(os.path.os.path.basename(path))[0]
        # initialisation to false as None is used in case datetime can not be extracted
        self.__exif_datetime: datetime.datetime = False
        self.__filename_datetime: datetime.datetime = False



    def __get_exif_data(self):
        ret = {}
        try:
            image = Image.open(self.filepathpath)
            info = image._getexif()
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                ret[decoded] = value
            return ret
        except IOError:
            message = f"[W] IOError when accessing '{self.filepathpath }'"
            if DEBUG:
                print(message)
            raise ExifError(message)

    @property
    def exif_datetime(self):
        if self.__exif_datetime is False:
            self.__exif_datetime = self.__get_exif_datetime()

        return self.__exif_datetime

    @property
    def exif_datetime(self):
        if self.__filename_datetime is False:
            self.__filename_datetime = self.__get_filename_datetime()

        return self.__filename_datetime


    def __get_exif_datetime(self):
        """Returns the date and time from image (if available)"""

        time_tags = [('DateTimeOriginal','SubsecTimeOriginal'),# when img taken
                     ('DateTimeDigitized','SubsecTimeDigitized'), # when img stored digitally
                     ('DateTime','SubsecTime') # when img file was changed
                    ]
        #for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2, 2.3
        try:
            exif = self.__get_exif_data(self.filepath)
        except ExifError:
            message = f"[W] Could not get Exif data for '{self.filepath}'"
            print(message)
            return None

        for time_tag in time_tags:
            exif_time, exif_subsec = exif.get(time_tag[0]), exif.get(time_tag[1],0)
            try:
                return self.__exif_time_to_datetime(time, subsec)
            except ExifError:
                continue

        message = f"[W] Failed to get any date using all available Exif time tags for '{self.filepath}'"
        print(message)
        return None

    @staticmethod
    def __exif_time_to_datetime(exif_time, exif_subsec):
        exif_time = exif_time[0] if type(exif_time) == tuple else exif_time # PILLOW 3.0 returns tuples now
        exif_subsec = exif_subsec[0] if type(exif_subsec) == tuple else exif_subsec

        try:
            exif_time_combined = f'{exif_time}.{exif_subsec}'
            time = datetime.strptime(exif_time_combined,'%Y:%m:%d %H:%M:%S.%f')
            return time
        except:
            message = f"[W] Could not get date from existing EXIF data '{exif_time_combined}' for file '{filepath}'"
            if DEBUG:
                print(message)
            raise ExifError(message)


    def __get_filename_datetime(self):
        return text_to_datetime(self.filename)


    @property
    def date_from_exif(self):
        return self.exif_datetime.date

    @property
    def time_from_exif(self):
        return self.exif_datetime.time

    @property
    def date_from_filename(self):
        return self.filename_datetime.time

    @property
    def time_from_filename(self):
        return self.filename_datetime.time


    def has_date_conflict(self):
        if self.date_from_exif is None and self.date_from_filename is None:
            return True
        if self.date_from_exif == self.date_from_filename:
            return False
        return True

    def has_time_conflict(self):
        if self.time_from_exif is None and self.time_from_filename is None:
            return True

        if self.time_from_exif == self.time_from_filename:
            return False
        return True
