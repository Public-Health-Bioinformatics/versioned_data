#!/usr/bin/python
import re
import os
import time
import dateutil
import dateutil.parser as parser2
import datetime
import calendar

def parse_date(adate):
	"""
	Convert human-entered time into linux integer timestamp

	@param adate string Human entered date to parse into linux time

	@return integer Linux time equivalent or 0 if no date supplied
	"""
	adate = adate.strip()
	if adate > '':
	    adateP = parser2.parse(adate, fuzzy=True)
	    #dateP2 = time.mktime(adateP.timetuple())
	    # This handles UTC & daylight savings exactly
	    return calendar.timegm(adateP.timetuple())
	return 0
	

def get_unix_time(vtime, voffset=0):
	return float(vtime) - int(voffset)/100*60*60


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
	return [int(text) if text.isdigit() else text.lower()
		for text in re.split(_nsre, s)] 


class date_matcher(object):
	"""
	Enables cycling through a list of versions and picking the one that matches
	or immediately preceeds a given date.  As soon as an item is found, subsequent
	calls to date_matcher return false (because of the self.found flag)
	"""
	def __init__(self, unix_time):
		"""
		@param adate linux date/time
		"""
		self.found = False
		self.unix_time = unix_time
		
	def __iter__(self):
		return self

	def next(self, unix_datetime):
		select = False
		if (self.found == False) and (self.unix_time > 0) and (unix_datetime <= self.unix_time):
			self.found = True
			select = True
		return select


def dateISOFormat(atimestamp):
	return datetime.datetime.isoformat(datetime.datetime.fromtimestamp(atimestamp))

def lightDate(unixtime):
	return datetime.datetime.utcfromtimestamp(float(unixtime)).strftime('%Y-%m-%d %H:%M')						
	
def move_files(source_path, destination_path, file_paths):
	"""
	MOVE FILES TO CACHE FOLDER (RATHER THAN COPYING THEM) FOR GREATER EFFICIENCY.
	Since a number of data source systems have hidden / temporary files in their
	data folder structure, a list of file_paths is required to select only that
	content that should be copied over.  Note: this will leave skeleton of folders; only files are moved.
	
	Note: Tried using os.renames() but it errors when attempting to remove folders 
	from git archive that aren't empty due to files that are not to be copied.
	
	
	@param source_path string Absolute folder path to move data files from
	@param destination_path string Absolute folder path to move data files to
	@param file_paths string List of files and their relative paths from source_path root
	"""
	for file_name in file_paths:
		if len(file_name):
			print "(" + file_name + ")"
			v_path = os.path.dirname(os.path.join(destination_path, file_name))
			if not os.path.isdir(v_path): 
				os.makedirs(v_path)
			os.rename(os.path.join(source_path, file_name), os.path.join(destination_path, file_name) )

