#!/usr/bin/python
	
"""
****************************** vdb_retrieval.py ******************************
 VDBRetrieval() instance called in two stages:
 1) by tool's versioned_data.xml form (dynamic_option field) 
 2) by its executable versioned_data.py script.

"""

import os, sys, glob, time
import string
from random import choice

from bioblend.galaxy import GalaxyInstance
from requests.exceptions import ChunkedEncodingError
from requests.exceptions import ConnectionError

import urllib2
import json
import vdb_common

# Store these values in python/galaxy environment variables?
VDB_DATA_LIBRARY = 'Versioned Data'
VDB_WORKFLOW_CACHE_FOLDER_NAME = 'Workflow cache'
VDB_CACHED_DATA_LABEL = 'Cached data'

# Don't forget to add "versionedata@localhost.com" to galaxy config admin_users list.

VDB_ADMIN_API_USER = 'versioneddata'
VDB_ADMIN_API_EMAIL = 'versioneddata@localhost.com'
VDB_ADMIN_API_KEY_PATH = os.path.join(os.path.dirname(sys._getframe().f_code.co_filename), 'versioneddata_api_key.txt')
			
#kipper, git, folder and other registered handlers
VDB_STORAGE_OPTIONS = 'kipper git folder biomaj'

# Used in versioned_data_form.py
VDB_DATASET_NOT_AVAILABLE = 'This database is not currently available (no items).'
VDB_DATA_LIBRARY_FOLDER_ERROR = 'Error: this data library folder is not configured correctly.'
VDB_DATA_LIBRARY_CONFIG_ERROR = 'Error: Check folder config file: '
		

class VDBRetrieval(object):

	def __init__(self, api_key=None, api_url=None):
		"""
		This gets either trans.x.y from <code file="..."> call in versioned_data.xml,
		or it gets a call with api_key and api_url from versioned_data.py

		@param api_key_path string File path to temporary file containing user's galaxy api_key
		@param api_url string contains http://[ip]:[port] for handling galaxy api calls.  
		
		"""
		# Initialized constants during the life of a request:
		self.global_retrieval_date = None
		self.library_id = None
		self.history_id = None
		self.data_stores = []
		
		# Entire json library structure.  item.url, type=file|folder, id, name (library path) 
		# Note: changes to library during a request aren't reflected here.
		self.library = None 		

		self.user_api_key = None	
		self.user_api = None
		#self.master_api_key = None
		self.admin_api_key = None
		self.admin_api = None
		self.api_url = None
			

	def set_trans(self, api_url, history_id, user_api_key=None): #master_api_key=None, 
		"""
		Used only on initial presentation of versioned_data.xml form.  Doesn't need admin_api
		"""
		self.history_id = history_id
		self.api_url = api_url
		self.user_api_key = user_api_key
		#self.master_api_key = master_api_key
		
		self.set_user_api()
		self.set_admin_api()		
		self.set_datastores()
		
	
	def set_api(self, api_info_path):
		"""
		"api_info_path" is provided only when user submits tool via versioned_data.py call.  
		It encodes both the api_url and the history_id of current session
		Only at this point will we need the admin_api, so it is looked up below.

		"""

		with open(api_info_path, 'r') as access:
			
			self.user_api_key = access.readline().strip()
			#self.master_api_key = access.readline().strip()
			api_info = access.readline().strip() #[api_url]-[history_id]
			self.api_url, self.history_id = api_info.split('-')
		
		self.set_user_api()
		self.set_admin_api()
		self.set_datastores()


	def set_user_api(self):
		"""
		Note: error message tacked on to self.data_stores for display back to user.
		"""
		self.user_api = GalaxyInstance(url=self.api_url, key=self.user_api_key)

		if not self.user_api:
			self.data_stores.append({'name':'Error: user Galaxy API connection was not set up correctly.  Try getting another user API key.', 'id':'none'})
			return
	
	
	def set_datastores(self):
		"""
		Provides the list of data stores that users can select versions from.
		Note: error message tacked on to self.data_stores for display back to user.
		"""
		# Look for library called "Versioned Data"
		try:
			libs = self.user_api.libraries.get_libraries(name=VDB_DATA_LIBRARY, deleted=False)
		except Exception as err: 
			# This is the first call to api so api url or authentication erro can happen here.
			self.data_stores.append({'name':'Error: Unable to make API connection: ' + err.message, 'id':'none'})
			return

		found = False
		for lib in libs:
			if lib['deleted'] == False:
				found = True
				self.library_id = lib['id']
				break;
			
		if not found:		
			self.data_stores.append({'name':'Error: Data Library [%s] needs to be set up by a galaxy administrator.' % VDB_DATA_LIBRARY, 'id':'none'})
			return

		try:
	 
			if self.admin_api:
				self.library = self.admin_api.libraries.show_library(self.library_id, contents=True) 
			else:
				self.library = self.user_api.libraries.show_library(self.library_id, contents=True) 

		except Exception as err: 
			# If data within a library is somehow messed up (maybe user has no permissions?), this can generate a bioblend errorapi.
			if err.message[-21:] == 'HTTP status code: 403':
				self.data_stores.append({'name':'Error: [%s] library needs permissions adjusted so users can view it.' % VDB_DATA_LIBRARY , 'id':'none'})
			else:
				self.data_stores.append({'name':'Error: Unable to get [%s] library contents: %s' % (VDB_DATA_LIBRARY, err.message) , 'id':'none'})
			return
			
		# Need to ensure it is sorted folder/file wise such that folders listed by date/id descending (name leads with version date/id) files will follow).
		self.library = sorted(self.library, key=lambda x: x['name'], reverse=False)

		# Gets list of data stores
		# For given library_id (usually called "Versioned Data"), retrieves folder/name
		# for any folder containing a data source specification file.  A folder should
		# have at most one of these.  It indicates the storage method used for the folder.

		for item in self.library:
			if item['type'] == "file" and self.test_data_store_type(item['name']):
				# Returns id of specification file that points to data source.
				self.data_stores.append({
					'name':os.path.dirname(item['name']),
					'id':item['id']
				})

	
	
	def set_admin_api(self):
	
		# Now fetch admin_api_key from disk, or regenerate user account and api from scratch.
		if os.path.isfile(VDB_ADMIN_API_KEY_PATH):

			with open(VDB_ADMIN_API_KEY_PATH, 'r') as access:
				self.admin_api_key = access.readline().strip()
				self.api_url = access.readline().strip()
				
		else:
			# VERIFY THAT USER IS AN ADMIN
			user = self.user_api.users.get_current_user()
			if user['is_admin'] == False:
				print "Unable to establish the admin api: you need to be in the admin_user=... list in galaxy config."
				sys.exit(1)

			#if not self.master_api_key:
			#	print "Unable to establish the admin api: no existing path to config file, and no master_api_key." + self.master_api_key
			#	sys.exit(1)

			# Generate from scratch:
			#master_api = GalaxyInstance(url=self.api_url, key=self.master_api_key)
			
			#users = master_api.users.get_users(deleted=False)
			users = self.user_api.users.get_users(deleted=False)
			for user in users:

				if user['email'] == VDB_ADMIN_API_EMAIL:
					self.admin_api_key = self.user_api.users.create_user_apikey(user['id'])

			if not self.admin_api_key:
				#Create admin api access account with dummy email address and reliable but secure password:
				# NOTE: this will only be considered an admin account if it is listed in galaxy config file as one.
				random_password = ''.join([choice(string.letters + string.digits) for i in range(15)])
				api_admin_user = self.user_api.users.create_local_user(VDB_ADMIN_API_USER, VDB_ADMIN_API_EMAIL, random_password)
				self.admin_api_key = self.user_api.users.create_user_apikey(api_admin_user['id'])

			with open(VDB_ADMIN_API_KEY_PATH, 'w') as access:
				access.write(self.admin_api_key + '\n' + self.api_url)
				
		self.admin_api = GalaxyInstance(url=self.api_url, key=self.admin_api_key)
		
		if not self.admin_api:
			print 'Error: admin Galaxy API connection was not set up correctly.  Admin user should be ' + VDB_ADMIN_API_EMAIL
			print "Unexpected error:", sys.exc_info()[0]
			sys.exit(1)
			
		
	def get_data_store_gateway(self, type, spec_file_id):
		# NOTE THAT PYTHON NEVER TIMES OUT FOR THESE CALLS - BUT IT WILL TIME OUT FOR API CALLS.
		# FUTURE: Adapt this so that any modules in data_stores/ folder are usable
		# e.g. https://bbs.archlinux.org/viewtopic.php?id=109561
		# http://stackoverflow.com/questions/301134/dynamic-module-import-in-python
		
		# ****************** GIT ARCHIVE ****************
		if type == "git": 
			import data_stores.vdb_git
			return data_stores.vdb_git.VDBGitDataStore(self, spec_file_id)
		
		# ****************** Kipper ARCHIVE ****************
		elif type == "kipper":
			import data_stores.vdb_kipper
			return data_stores.vdb_kipper.VDBKipperDataStore(self, spec_file_id)
				
		# ****************** FILE FOLDER ******************	
		elif type == "folder":
			import data_stores.vdb_folder
			return data_stores.vdb_folder.VDBFolderDataStore(self, spec_file_id)

		# ****************** FILE FOLDER ******************	
		elif type == "biomaj":
			import data_stores.vdb_biomaj
			return data_stores.vdb_biomaj.VDBBiomajDataStore(self, spec_file_id)
			
		else:
			print 'Error: %s not recognized as a valid data store type.' % type
			sys.exit( 1 )
		
	
	#For a given path leading to pointer.[git|kipper|folder|biomaj] returns suffix
	def test_data_store_type(self, file_name, file_path=None):
		if file_path and not os.path.isfile(file_path):
			return False
		
		suffix = file_name.rsplit('.',1)		
		if len(suffix) > 1 and suffix[1] in VDB_STORAGE_OPTIONS:
			return suffix[1]
		
		return False
		
		

	

	def get_library_data_store_list(self):
		"""
		For display on tool form, returns names, ids of specification files that point to data sources.
		
		@return dirs array of [[folder label], [folder_id, selected]...] 
		"""
		dirs = []
		# Gets recursive contents of library - files and folders
		for item in self.data_stores:
			dirs.append([item['name'], item['id'], False])
		
		return dirs


	def get_library_label_path(self, spec_file_id):
		for item in self.data_stores:
			if item['id'] == spec_file_id:
				return item['name']

		return None

		
	def get_library_folder_datasets(self, library_version_path, admin=False):
		"""
		Gets set of ALL dataset FILES within folder - INCLUDING SUBFOLDERS - by searching 
		through a library, examining each item's full hierarchic label
		BUT CURRENTLY: If any file has state='error' the whole list is rejected (and regenerated).
		
		WISHLIST: HAVE AN API FUNCTION TO GET ONLY A GIVEN FOLDER'S (BY ID) CONTENTS!
		
		@param library_version_path string Full hierarchic label of a library file or folder.
		
		@return array of ldda_id library dataset data association ids.	
		"""
		
		if admin:
			api_handle = self.admin_api
		else:
			api_handle = self.user_api
			
		count = 0
		while count < 4:
			try:
				items = api_handle.libraries.show_library(self.library_id, True) 
				break
			except ChunkedEncodingError:
				print "Error: Trying to fetch Versioned Data library listing. Try [" + str(count) + "]"
				time.sleep (2)
				pass
				
			count +=1	

		datasets = []
		libvpath_len = len(library_version_path) + 1
		for item in items:
			if item['type'] == "file":
				name = item['name']
				# need slash or else will match to similar prefixes.
				if name[0:libvpath_len] == library_version_path + '/': 
				
					# ISSUE seems to be that input library datasets can be queued / running, and this MUST wait till they are finished or it will plow ahead prematurely.
					
					count = 0
				
					while count < 10:
						
						try:
							lib_dataset = api_handle.libraries.show_dataset(self.library_id, item['id'])
							break
							
						except: 
							print "Unexpected error:", sys.exc_info()[0]
							sys.exit(1)

						if lib_dataset['state'] == 'running':
							time.sleep(10)
							count +=1
							continue
						
						elif lib_dataset['state'] == 'queued':
						
							# FUTURE: Check date.  If it is really stale it should be killed?
							print 'Note: library folder dataset item "%s" is [%s].  Please wait until it is finished processing, or have a galaxy administrator delete the dataset if its creation has failed.' % (name,  lib_dataset['state'])
							sys.exit(1)

						elif lib_dataset['state'] != 'ok' or not os.path.isfile(lib_dataset['file_name']):
							print 'Note: library folder dataset "%s" had an error during job.  Its state was [%s]. Regenerating.' % (name, lib_dataset['state'])
							self.admin_api.libraries.delete_library_dataset(self.library_id, item['id'], purged=True)
							return []
						
						else:
							break
							
					datasets.append(item['id'])

		
		return datasets


	def get_library_version_datasets(self, library_version_path, base_folder_id='', version_label='', version_path=''):
		"""
		Check if given library has a folder for given version_path.  If so:
		 - and it has content, return its datasets.
		 - otherwise refetch content for verison folder
		If no folder, populate the version folder with data from the archive and return those datasets.
		Version exists in external cache (or in case of unlinked folder, in EXISTING galaxy library folder).
		Don't call unless version_path contents have been established. 

		@param library_version_path string Full hierarchic label of a library file or folder with version id.

		For creation:
		@param base_folder_id string a library folder id under which version files should exist	
		@param version_label string Label to give newly created galaxy library version folder
		@param version_path string Data source folder to retrieve versioned data files from

		@return array of dataset	
		"""
		
		
		# Pick the first folder of any that match given 'Versioned Data/.../.../[version id]' path.
		# This case will always match 'folder' data store:

		folder_matches = self.get_folders(name=library_version_path) 
		
		if len(folder_matches):
			
			folder_id = folder_matches[0]['id']
			dataset_ids = self.get_library_folder_datasets(library_version_path)
		
			if len(dataset_ids) > 0:

				return dataset_ids
			
			if os.listdir(version_path) == []:
				# version_path doesn't exist for 'folder' data store versions that are datasets directly in library (i.e. not linked)
				print "Error: the data store didn't return any content for given version id.  Looked in: " + version_path
				sys.exit(1)
		
			# NOTE ONE 3rd party COMMENT THAT ONE SHOULD PUT IN file_type='fasta' FOR LARGE FILES.  Problem with that is that then galaxy can't recognize other data types.
			library_folder_datasets = self.admin_api.libraries.upload_from_galaxy_filesystem(self.library_id, version_path, folder_id, link_data_only=True, roles=None)

				
		else:
			if base_folder_id == '': #Normally shouldn't happen

				print "Error: no match to given version folder for [" + library_version_path + "] but unable to create one - missing parent folder identifier"
				return []

			# Provide archive folder with datestamped name and version (folderNew has url, id, name):
			folderNew = self.admin_api.libraries.create_folder(self.library_id, version_label, description=VDB_CACHED_DATA_LABEL, base_folder_id=base_folder_id)
			folder_id = str(folderNew[0]['id'])
			
			# Now link results to suitably named galaxy library dataset
			# Note, this command links to EVERY file/folder in version_folder source.
			# Also, Galaxy will strip off .gz suffixes - WITHOUT UNCOMPRESSING FILES!
			# So, best to prevent data store from showing .gz files in first place
			try:
				library_folder_datasets = self.admin_api.libraries.upload_from_galaxy_filesystem(self.library_id, version_path, folder_id, link_data_only=True, roles=None)

			except: 
				# Will return error if version_path folder is empty or kipper unable to create folder or db due to permissions etc.
				print "Error: a permission or other error was encountered when trying to retrieve version data for version folder [" + version_path + "]: Is the [%s] listed in galaxy config admin_users list?" % VDB_ADMIN_API_EMAIL, sys.exc_info()[0]
				sys.exit(1)


		library_dataset_ids = [dataset['id'] for dataset in library_folder_datasets]

		# LOOP WAITS UNTIL THESE DATASETS ARE UPLOADED.  
		# They still take time even for linked big data probably because they are read for metadata.
		# Not nice that user doesn't see process as soon as it starts, but timeout possibilities
		# later on down the line are more difficult to manage.
		for dataset_id in library_dataset_ids:
			# ten seconds x 60 = 6 minutes; should be longer?
			for count in range(60): 
				try:
					lib_dataset = self.admin_api.libraries.show_dataset(self.library_id, dataset_id)
					break
					
				except: 
					print "Unexpected error:", sys.exc_info()[0]
					continue

				if lib_dataset['state'] in 'running queued':
					time.sleep(10)
					count +=1
					continue
				else:
					# Possibly in a nice "ok" or not nice state here.
					break


		return library_dataset_ids


	def get_folders(self, name):
		"""
		ISSUE: Have run into this sporadic error with a number of bioblend api calls.  Means api calls may need to be wrapped in a retry mechanism:
		File "/usr/lib/python2.6/site-packages/requests/models.py", line 656, in generate
		raise ChunkedEncodingError(e)
		requests.exceptions.ChunkedEncodingError: ('Connection broken: IncompleteRead(475 bytes read)', IncompleteRead(475 bytes read))
		"""
		for count in range(3):
			try:
				return self.user_api.libraries.get_folders(self.library_id, name=name ) 
				break
				
			except:
				print 'Try (%s) to fetch library folders for "%s"' % (str(count), name)
				print sys.exc_info()[0]
				time.sleep (5)

		print "Failed after (%s) tries!" % (str(count))
		return None
				

	def get_library_folder(self, library_path, relative_path, relative_labels):
		"""
		Check if given library has folder that looks like library_path + relative_path.  
		If not, create and return resulting id.  Used for cache creation.
		Ignores bad library_path.
		
		@param library_path string Full hierarchic label of a library folder.  NOTE: Library_path must have leading forward slash for a match, i.e. /derivative_path
		@param relative_path string branch of folder tree stemming from library_path	
		@param relative_labels string label for each relative_path item
		
		@return folder_id
		"""
		created = False
		root_match = self.get_folders( name=library_path)
		
		if len(root_match):
			base_folder_id=root_match[0]['id']
			
			relative_path_array = relative_path.split('/')
			relative_labels_array = relative_labels.split('/')
			
			for ptr in range(len (relative_path_array)):

				_library_path = os.path.join(library_path, '/'.join(relative_path_array[0:ptr+1]))
				folder_matches = self.get_folders( name=_library_path)

				if len(folder_matches):
					folder_id = folder_matches[0]['id']
				else:
					dataset_key = relative_path_array[ptr]
					label = relative_labels_array[ptr]
					folder_new = self.admin_api.libraries.create_folder(self.library_id, dataset_key, description=label, base_folder_id=base_folder_id)
					folder_id = str(folder_new[0]['id'])
					
				base_folder_id = folder_id
			
			return folder_id

		return None


	def get_library_folders(self, library_label_path):
		"""
		Gets set of ALL folders within given library path.  Within each folder, lists its files as well.
		Folders are ordered by version date/id, most recent first (natural sort).
	
		NOT Quite recursive. Nested folders don't have parent info.

		@param library_version_path string Full hierarchic label of a library folder. Inside it are version subfolders, their datasets, and the pointer file.
	
		@return array of ids of the version subfolders and also their dataset content ids
		"""
		
		folders = []
		libvpath_len = len(library_label_path)
		for item in self.library:

			name = item['name']
			if name[0:libvpath_len] == library_label_path: 

				# Skip any file that is immediately under library_label_path			
				if item['type'] == 'file':
					file_key_val = item['name'].rsplit('/',1)
					#file_name_parts = file_key_val[1].split('.')
					if file_key_val[0] == library_label_path:
					#and len(file_name_parts) > 1 \
					#and file_name_parts[1] in VDB_STORAGE_OPTIONS:
						continue

				if item['type'] == 'folder':
					folders.append({'id':item['id'], 'name':item['name'], 'files':[]})
				
				else:
					# Items should be sorted ascending such that each item is contained in previous folder.
					folders[-1]['files'].append({'id':item['id'], 'name':item['name']})
	
		return folders

	
	def get_workflow_data(self, workflow_list, datasets, version_id):
		"""
		Run each workflow in turn, given datasets generated above.
		See if each workflow's output has been cached.
		If not, run workflow and reestablish output data
		Complexity is that cache could be:
		1) in user's history.
		2) in library data folder called "derivative_cache" under data source folder  (as created by this galaxy install)
		3) in external data folder ..."/derivative_cache" (as created by this galaxy install)
			BUT other galaxy installs can't really use this unless they know metadata on workflow that generated it
			In future we'll design a system for different galaxies to be able to read metadata to determine if they can use the cached workflow data here.

		ISSUE Below: Unless it is a really short workflow, run_workflow() returns before work is actually complete.  DO WE NEED TO DELAY UNTIL EVERY SINGLE OUTPUT DATASET IS "ok", not just "queued" or "running"?  OR IS SERVER TO LIBRARY UPLOAD PAUSE ABOVE ENOUGH?
														
		Note, workflow_list contains only ids for items beginning with "versioning: "
		FUTURE IMPROVEMENT: LOCK WORKFLOW: VULNERABILITY: IF WORKFLOW CHANGES, THAT AFFECTS REPRODUCABILITY.

		FUTURE: NEED TO ENSURE EACH dataset id not found in history is retrieved from cache.				
		FUTURE: Check to see that EVERY SINGLE workflow output 
		has a corresponding dataset_id in history or library, 
		i.e. len(workflow['outputs']) == len(history_dataset_ids)
		But do we know before execution how many outputs (given conditional output?)

		@param workflow_list
		@param datasets: an array of correct data source versioned datasets that are inputs to tools and workflows
		@param version_id
		
		"""
		for workflow_id in workflow_list.split():
			
			workflows = self.admin_api.workflows.get_workflows(workflow_id, published=True)

			if not len(workflows):
				# Error occurs if admin_api user doesn't have permissions on this workflow???  
				# Currently all workflows have to be shared with VDB_ADMIN_API_EMAIL.  
				# Future: could get around this by using publicly shared workflows via "import_shared_workflow(workflow_id)"
				print 'Error: unable to run workflow - has it been shared with the Versioned Data tool user email address "%s" ?' % VDB_ADMIN_API_EMAIL
				sys.exit(1)
				
			for workflow_summary in workflows:

				workflow = self.admin_api.workflows.show_workflow(workflow_id)
				print 'Doing workflow: "' + workflow_summary['name'] + '"'	

				if len(workflow['inputs']) == 0:
					print "ERROR: This workflow is not configured correctly - it needs at least 1 input dataset step." 
				
				# FUTURE: Bring greater intelligence to assigning inputs to workflow?!!!
				if len(datasets) < len(workflow['inputs']):
				
					print 'Error: workflow requires more inputs (%s) than are available in retrieved datasets (%s) for this version of retrieved data.' % (len(workflow['inputs']), len(datasets))
					sys.exit(1)
					
				codings = self.get_codings(workflow, datasets)
				(workflow_input_key, workflow_input_label, annotation_key, dataset_map) = codings
				
				history_dataset_ids = self.get_history_workflow_results(annotation_key)

				if not history_dataset_ids:

					library_cache_path = os.path.join("/", VDB_WORKFLOW_CACHE_FOLDER_NAME, workflow_id, workflow_input_key)

					# This has to be privileged api admin fetch.
					library_dataset_ids = self.get_library_folder_datasets(library_cache_path, admin=True)
				
					if not len(library_dataset_ids):
						# No cache in library so run workflow

						# Create admin_api history
						admin_history = self.admin_api.histories.create_history()
						admin_history_id = admin_history['id']
				
						# If you try to run a workflow that hasn't been shared with you, it seems to go a bit brezerk.  
						work_result = self.admin_api.workflows.run_workflow(workflow_id, dataset_map=dataset_map, history_id=admin_history_id) 

						# Then copy (link) results back to library so can match in future
						self.cache_datasets(library_cache_path, work_result, workflow_summary, codings, version_id, admin_history_id)

						# Now return the new cached library dataset ids:
						library_dataset_ids =  self.get_library_folder_datasets(library_cache_path, admin=True)
						""" If a dataset is purged, its purged everywhere... so don't purge!  Let caching system do that.
						THIS APPEARS TO HAPPEN TOO QUICKLY FOR LARGE DATABASES; LEAVE IT TO CACHING MECHANISM TO CLEAR.  OR ABOVE FIX TO WAIT UNTIL DS IS OK.
						self.admin_api.histories.delete_history(admin_history_id, purge=False)
						"""
						
					# Now link library cache workflow results to history and add key there for future match.
					self.update_history(library_dataset_ids, annotation_key, version_id)




	def update_history(self, library_dataset_ids, annotation, version_id):
		"""
		Copy datasets from library over to current history if they aren't already there.
		Must cycle through history datasets, looking for "copied_from_ldda_id" value.  This is available only with details view.
		
		@param library_dataset_ids array List of dataset Ids to copy from library folder
		@param annotation string annotation to add (e.g. Path of original version folder added as annotation)
		@param version_id string Label to add to copied dataset in user's history
		"""
		history_datasets = self.user_api.histories.show_history(self.history_id, contents=True, deleted=False, visible=True, details='all' , types=None) # ,
		
		datasets = []
		for dataset_id in library_dataset_ids:
			# USING ADMIN_API because that's only way to get workflow items back... user_api doesn't nec. have view rights on newly created workflow items.  Only versioneddata@localhost.com has perms.
			ld_dataset = self.admin_api.libraries.show_dataset(self.library_id, dataset_id)

			if not ld_dataset['state'] in 'ok running queued':
			
				print "Error when linking to library dataset cache [" + ld_dataset['name'] + ", " + ld_dataset['id'] + "] - it isn't in a good state: " + ld_dataset['state']
				sys.exit(1)
			
			if not os.path.isfile(ld_dataset['file_name']):
				pass
				#FUTURE: SHOULD TRIGGER LIBRARY REGENERATION OF ITEM?
				
			library_ldda_id = ld_dataset['ldda_id']
			
			# Find out if library dataset item is already in history, and if so, just return that item.
			dataset = None		
			for dataset2 in history_datasets:
				
				if 'copied_from_ldda_id' in dataset2 \
				and dataset2['copied_from_ldda_id'] == library_ldda_id \
				and dataset2['state'] in 'ok running' \
				and dataset2['accessible'] == True:
					dataset = dataset2
					break
			
			if not dataset: # link in given dataset from library

				dataset = self.user_api.histories.upload_dataset_from_library(self.history_id, dataset_id)
				
				# Update dataset's label - not necessary, just hinting at its creation.
				new_name = dataset['name']
				if dataset['name'][-len(version_id):] != version_id:
					new_name += ' ' + version_id

				self.user_api.histories.update_dataset(self.history_id, dataset['id'], name=new_name, annotation = annotation) 
			
			datasets.append({
				'id': dataset['id'], 
				'ld_id': ld_dataset['id'],
				'name': dataset['name'], 
				'ldda_id': library_ldda_id, 
				'library_dataset_name': ld_dataset['name'],
				'state': ld_dataset['state']
			})

		return datasets


	def get_codings(self, workflow, datasets):
		"""
		Returns a number of coded lists or arrays for use in caching or displaying workflow results.
		Note: workflow['inputs'] = {u'23': {u'label': u'Input Dataset', u'value': u''}},
		Note: step_id is not incremental.
		Note: VERY COMPLICATED because of hda/ldda/ld ids

		FUTURE: IS METADATA AVAILABLE TO BETTER MATCH WORKFLOW INPUTS TO DATA SOURCE RECALL VERSIONS?
		ISSUE: IT IS ASSUMED ALL INPUTS TO WORKFLOW ARE AVAILABLE AS DATASETS BY ID IN LIBRARY.  I.e.
		one can't have a workflow that also makes reference to another just-generated file in user's 
		history.
		"""
		db_ptr = 0
		dataset_map = {}
		workflow_input_key = []
		workflow_input_labels = []

		for step_id, ds_in in workflow['inputs'].iteritems():
			input_dataset_id = datasets[db_ptr]['ld_id']
			ldda_id = datasets[db_ptr]['ldda_id']
			dataset_map[step_id] = {'src': 'ld', 'id': input_dataset_id} 
			workflow_input_key.append(ldda_id) #like dataset_index but from workflow input perspective
			workflow_input_labels.append(datasets[db_ptr]['name'])
			db_ptr += 1
			
		workflow_input_key = '_'.join(workflow_input_key)
		workflow_input_labels = ', '.join(workflow_input_labels)
		annotation_key = workflow['id'] + ":" + workflow_input_key
		
		return (workflow_input_key, workflow_input_labels, annotation_key, dataset_map)


	def get_history_workflow_results(self, annotation):
		"""	
		See if workflow-generated dataset exists in user's history.  The only way to spot this 
		is to find some dataset in user's history that has workflow_id in its "annotation" field.
		We added the specific dataset id's that were used as input to the workflow as well as the 
		workflow key since same workflow could have been run on different inputs.
		
		@param annotation_key string Contains workflow id and input dataset ids..
		"""
		history_datasets = self.user_api.histories.show_history(self.history_id, contents=True, deleted=False, visible=True, details='all') # , types=None
		dataset_ids = []
		
		for dataset in history_datasets:
			if dataset['annotation'] == annotation:
				if dataset['accessible'] == True  and dataset['state'] == 'ok':
					dataset_ids.append(dataset['id'])
				else: 
					print "Warning: dataset " + dataset['name'] + " is in an error state [ " + dataset['state'] + "] so skipped!"
					
		return dataset_ids


	def cache_datasets(self, library_cache_path, work_result, workflow_summary, codings, version_id, history_id):
		""" 
		Use the Galaxy API to LINK versioned data api admin user's history workflow-created item(s) into the appropriate Versioned Data Workflow Cache folder.  Doing this via API call so that metadata is preserved, e.g. preserving that it is a product of makeblastdb/formatdb and all that entails.  Only then does Galaxy remain knowledgeable about datatype/data collection.		
		
		Then user gets link to workflow dataset in their history.  (If a galaxy user deletes a workflow dataset in their history they actually only deletes their history link to that dataset. True of api admin user?)
		
		FUTURE: have the galaxy-created data shared from a server location?
		"""

		(workflow_input_key, workflow_input_label, annotation_key, dataset_map) = codings

		# This will create folder if it doesn't exist:
		_library_cache_labels = os.path.join("/", VDB_WORKFLOW_CACHE_FOLDER_NAME, workflow_summary['name'], 'On ' + workflow_input_label)
		folder_id = self.get_library_folder("/", library_cache_path, _library_cache_labels)
		if not folder_id: # Case should never happen
			print 'Error: unable to determine library folder to place cache in:' + library_cache_path
			sys.exit(1)

		
		for dataset_id in work_result['outputs']:
			# We have to mark each dataset entry with the Workflow ID and input datasets it was generated by. 
			# No other way to know they are associated. ADD VERSION ID TO END OF workflowinput_label?
			label = workflow_summary['name'] +' on ' + workflow_input_label 
			
			# THIS WILL BE IN ADMIN API HISTORY
			self.admin_api.histories.update_dataset(history_id, dataset_id, annotation = annotation_key, name=label) 

			# Upload dataset_id and give it description 'cached data'
			if 'copy_from_dataset' in dir(self.admin_api.libraries):
				# IN BIOBLEND LATEST:
				self.admin_api.libraries.copy_from_dataset(self.library_id, dataset_id, folder_id, VDB_CACHED_DATA_LABEL + ": version " + version_id)
			else:
				self.library_cache_setup_privileged(folder_id, dataset_id, VDB_CACHED_DATA_LABEL + ": version " + version_id)



	def library_cache_setup_privileged(self, folder_id, dataset_id, message):
		"""
		Copy a history HDA into a library LDDA (that the current admin api user has add permissions on)
		in the given library and library folder.  Requires that dataset_id has been created by admin_api_key user.	 Nicola Soranzo [nicola.soranzo@gmail.com will be adding to BIOBLEND eventually.
	
		We tried linking a Versioned Data library Workflow Cache folder to the dataset(s) a non-admin api user has just generated.  It turns out API user that connects the two must be both a Library admin AND the owner of the history dataset being uploaded, or an error occurs.  So system can't do action on behalf of non-library-privileged user.  Second complication with that approach is that there is no Bioblend API call - one must do this directly in galaxy API via direct URL fetc.

		NOTE: This will raise "HTTPError(req.get_full_url(), code, msg, hdrs, fp)" if given empty folder_id for example
	
		@see def copy_hda_to_ldda( library_id, library_folder_id, hda_id, message='' ):
		@see https://wiki.galaxyproject.org/Events/GCC2013/TrainingDay/API?action=AttachFile&do=view&target=lddas_1.py

		@uses library_id: the id of the library which we want to query.
	
		@param dataset_id: the id of the user's history dataset we want to copy into the library folder.
		@param folder_id: the id of the library folder to copy into.
		@param message: an optional message to add to the new LDDA.
		"""



		full_url = self.api_url + '/libraries' + '/' + self.library_id + '/contents'
		url = self.make_url( self.admin_api_key, full_url )
			
		post_data = {
		'folder_id'     : folder_id,
		'create_type'   : 'file',
		'from_hda_id'   : dataset_id,
		'ldda_message'  : message
		}

		req = urllib2.Request( url, headers = { 'Content-Type': 'application/json' }, data = json.dumps(  post_data ) )
		#try:

		results = json.loads( urllib2.urlopen( req ).read() ) 
		return


	#Expecting to phase this out with bioblend api call for library_cache_setup()
	def make_url(self, api_key, url, args=None ):
		# Adds the API Key to the URL if it's not already there.
		if args is None:
			args = []
		argsep = '&'
		if '?' not in url:
			argsep = '?'
		if '?key=' not in url and '&key=' not in url:
			args.insert( 0, ( 'key', api_key ) )
		return url + argsep + '&'.join( [ '='.join( t ) for t in args ] )



