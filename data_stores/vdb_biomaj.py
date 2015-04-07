#!/usr/bin/python
## ******************************* Biomaj FOLDER *********************************
##

import os
import time
import glob
import vdb_common
import vdb_data_stores

class VDBBiomajDataStore(vdb_data_stores.VDBDataStore):

	versions = None
	library = None
	
	def __init__(self, retrieval_obj, spec_file_id):
		"""
		Provides list of available versions where each version is a data file sitting in a Biomaj data store subfolder. e.g.

			/projects2/ref_databases/biomaj/ncbi/blast/silva_rna/   silva_rna_119/flat
			/projects2/ref_databases/biomaj/ncbi/genomes/Bacteria/  Bacteria_2014-07-25/flat

		"""
		super(VDBBiomajDataStore, self).__init__(retrieval_obj, spec_file_id)

		self.library = retrieval_obj.library
		
		versions = []
		# Linked, meaning that our data source spec file pointed to some folder on the server.
		# Name of EACH subfolder should be a label for each version, including date/time and version id.

		base_file_path = os.path.join(os.path.dirname(self.base_file_name),'*','flat','*')
		try:
			#Here we need to get subfolder listing of linked file location.
			for item in glob.glob(base_file_path):
	
				# Only interested in files, and not ones in the symlinked /current/ subfolder
				# Also, Galaxy will strip off .gz suffixes - WITHOUT UNCOMPRESSING FILES!
				# So, best to prevent data store from showing .gz files in first place.
				if os.path.isfile(item) and not '/current/' in item and not item[-3:] == '.gz':
					#Name includes last two subfolders: /[folder]/flat/[name]
					item_name = '/'.join(item.rsplit('/',3)[1:]) 
					# Can't count on creation date being spelled out in name
					created = vdb_common.parse_date(time.ctime(os.path.getmtime(item)))	
					versions.append({'name':item_name, 'id':item_name, 'created': created})

		except Exception as err: 
			# This is the first call to api so api url or authentication erro can happen here.
			versions.append({
				'name':'Error: Unable to get version list: ' + err.message, 
				'id':'',
				'created':''
			})

		self.versions = sorted(versions, key=lambda x: x['name'], reverse=True)

				
	def get_version(self, version_name):
		"""
		Return server path of requested version info

		@uses library_label_path string Full hierarchic label of a library file or folder, PARENT of version id folder.
		@uses base_file_name string Server absolute path to data_store spec file
		@param version_name alphaneumeric string
		"""
		self.version_label = version_name
		self.library_version_path = os.path.join(self.library_label_path, self.version_label)

		#linked to some other folder, spec is location of base_file_name
		self.version_path = os.path.join(self.data_store_path, version_name)

