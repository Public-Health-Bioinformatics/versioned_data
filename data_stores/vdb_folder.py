#!/usr/bin/python
## ******************************* FILE FOLDER *********************************
##

import re
import os
import vdb_common
import vdb_data_stores

class VDBFolderDataStore(vdb_data_stores.VDBDataStore):

	versions = None
	library = None
	
	def __init__(self, retrieval_obj, spec_file_id):
		"""
		Provides list of available versions where each version is indicated by the 
		existence of a folder that contains its content.  This content can be directly
		in the galaxy Versioned Data folder tree, OR it can be linked to another folder
		on the server.  In the latter case, galaxy will treat the Versioned Data folders as caches.
		View of versions filters out any folders that are used for derivative data caching.
		"""
		super(VDBFolderDataStore, self).__init__(retrieval_obj, spec_file_id)

		self.library = retrieval_obj.library
		
		versions = []
		
		# If data source spec file has no content, use the library folder directly.
		# Name of EACH subfolder should be a label for each version, including date/time and version id.
		if self.data_store_path == '':
			try:
				lib_label_len = len(self.library_label_path) +1 
			
				for item in self.library:
					# If item is under library_label_path ...
					if item['name'][0:lib_label_len] == self.library_label_path + '/':
						item_name = item['name'][lib_label_len:len(item['name'])]
						if item_name.find('/') == -1 and item_name.find('_') != -1:
							(item_date, item_version) = item_name.split('_',1)
							created = vdb_common.parse_date(item_date)	
							versions.append({'name':item_name, 'id':item_name, 'created': created})
		
			except Exception as err: 
				# This is the first call to api so api url or authentication erro can happen here.
				versions.append({
					'name':'Software Error: Unable to get version list: ' + err.message, 
					'id':'',
					'created':''
				})

		else:

			base_file_path = self.data_store_path
			#base_file_path = os.path.dirname(self.base_file_name)
			#Here we need to get directory listing of linked file location.
			for item_name in os.listdir(base_file_path): # Includes files and folders
				# Only interested in folders
				if os.path.isdir( os.path.join(base_file_path, item_name)) and  item_name.find('_') != -1:
					(item_date, item_version) = item_name.split('_',1)
					created = vdb_common.parse_date(item_date)	
					versions.append({'name':item_name, 'id':item_name, 'created': created})

		
		self.versions = sorted(versions, key=lambda x: x['name'], reverse=True)
				
	def get_version(self, version_name):
		"""
		Return server path of requested version info - BUT ONLY IF IT IS LINKED.
		IF NOT LINKED, returns None for self.version_path
		
		QUESTION: DOES GALAXY AUTOMATICALLY HANDLE tar.gz/zip decompression?
		
		@uses library_label_path string Full hierarchic label of a library file or folder, PARENT of version id folder.
		@uses base_file_name string Server absolute path to data_store spec file

		@param version_name alphaneumeric string (git tag)
		"""
		self.version_label = version_name
		self.library_version_path = os.path.join(self.library_label_path, self.version_label)

		if self.data_store_path == '':
			# In this case version content is held in library directly; 
			self.version_path = self.base_file_name

		else:

			#linked to some other folder, spec is location of base_file_name
			self.version_path = os.path.join(self.data_store_path, version_name)
		
