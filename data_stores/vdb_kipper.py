#!/usr/bin/python
## ********************************* Kipper *************************************
##

import vdb_common
import vdb_data_stores
import subprocess
import json
import glob
import os
import sys

class VDBKipperDataStore(vdb_data_stores.VDBDataStore):
	
	metadata = None
	versions = None
	command = None
	
	def __init__(self, retrieval_obj, spec_file_id):
		"""
		Metadata (version list) is expected in "master/" subfolder of data_store_path on server. 
		
		Future: allow for more than one database / .md file in a folder?
		"""
		super(VDBKipperDataStore, self).__init__(retrieval_obj, spec_file_id)
		# Ensure we're working with this tool's version of Kipper.
		self.command = os.path.join(os.path.dirname(sys._getframe().f_code.co_filename),'kipper.py')
		self.versions = []
			
		metadata_path = os.path.join(self.data_store_path,'master','*.md')
		metadata_files = glob.glob(metadata_path)

		if len(metadata_files) == 0:
			return			# Handled by empty list error in versioned_data_form.py
		
		metadata_file = metadata_files[0]

		with open(metadata_file,'r') as metadata_handle:
			self.metadata = json.load(metadata_handle)
			for volume in self.metadata['volumes']:
				self.versions.extend(volume['versions']) 						
	
		if len(self.versions) == 0:
			print "Error: Unable to locate metadata file: " + metadata_path
			sys.exit(1) 
		
		self.versions = sorted(self.versions, key=lambda x: x['id'], reverse=True)
				
			
	def get_version(self, version_name):
		"""
		Trigger populating of the appropriate version folder.  
		Returns path information to version folder, and its appropriate library label. 
		
		@param version_id string
		"""

		version = self.get_metadata_version(version_name)

		if not version:
			print 'Error: Galaxy was not able to find the given version id in the %s data store.' % self.version_path
			sys.exit( 1 )
		
		version_name = version['name']
		self.version_path = os.path.join(self.data_store_path, version_name)
		self.version_label = vdb_common.lightDate(version['created']) + '_v' + version_name
		
		print self.library_label_path
		print self.version_label

		self.library_version_path = os.path.join(self.library_label_path, self.version_label)

		if not os.path.exists(self.version_path):
			try:		
				os.mkdir(self.version_path)
			except:
				print 'Error: Galaxy was not able to create data store folder "%s".  Check permissions?' % self.version_path
				sys.exit( 1 )

		# Generate cache if folder is empty (can take a while):
		if os.listdir(self.version_path) == []: 

			db_file = os.path.join(self.data_store_path, 'master', self.metadata["db_file_name"] )
			command = [self.command, db_file, '-e','-I', version_name, '-o', self.version_path ]

			try:
				result = subprocess.call(command);
			except:
				print 'Error: Galaxy was not able to run the kipper.py program successfully for this job: "%s".  Check permissions?' % self.version_path
				sys.exit( 1 )
		

	def get_metadata_version(self, version_name=''):
		if version_name == '':
			return self.versions[0]

		for version in self.versions:
			if str(version['name']) == version_name:
				return version
							
		return False
		
