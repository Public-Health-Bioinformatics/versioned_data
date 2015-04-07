import vdb_common
import vdb_retrieval # For message text

class VDBDataStore(object):

	"""
		Provides data store engine super-class with methods to list available versions, and to generate a version (potentially providing a link to cached version).  Currently have options for git, folder, and kipper.
		
		get_data_store_gateway() method loads the appropriate data_stores/vdb_.... data store variant.
		
	"""
	
	def __init__(self, retrieval_obj, spec_file_id):
		"""
		Note that api is only needed for data store type = folder.
		
		@init self.type
		@init self.base_file_name
		@init self.library_label_path
		@init self.data_store_path
		@init self.global_retrieval_date
		
		@sets self.library_version_path
		@sets self.version_label
		@sets self.version_path
		"""
	
		self.admin_api = retrieval_obj.admin_api
		self.library_id = retrieval_obj.library_id
		self.library_label_path = retrieval_obj.get_library_label_path(spec_file_id)
		try:
			# Issue: Error probably gets trapped but is never reported back to Galaxy from thread via <code file="versioned_data_form.py" /> form's call?
			# It appears galaxy user needs more than just "r" permission on this file, oddly? 
			spec = self.admin_api.libraries.show_folder(self.library_id, spec_file_id)

		except IOError as e:
			print 'Tried to fetch library folder spec file: %s.  Check permissions?"' % spec_file_id
			print "I/O error({0}): {1}".format(e.errno, e.strerror)			
			sys.exit(1)

		self.type = retrieval_obj.test_data_store_type(spec['name'])

		#Server absolute path to data_store spec file (can be Galaxy .dat file representing Galaxy library too.

		self.base_file_name = spec['file_name'] 

		# In all cases a pointer file's content (data_store_path) 
		# should point to a real server folder (that galaxy has permission to read).
		# Exception to this is for pointer.folder, where content can be empty, 
		# in which case idea is to use library folder contents directly.
 
		with open(self.base_file_name,'r') as path_spec:
			self.data_store_path = path_spec.read().strip()
			if len(self.data_store_path) > 0:
				# Let people forget to put a trailing slash on the folder path.
				if not self.data_store_path[-1] == '/':
					self.data_store_path += '/'
		
		# Generated on subsequent subclass call
		self.library_version_path = None
		self.version_label = None
		self.version_path = None
		
	
	def get_version_options(self, global_retrieval_date=0, version_name=None, selection=False):
		"""
		Provides list of available versions of a given archive.  List is filtered by
		optional global_retrieval_date or version id.  For date filter, the version immediately 
		preceeding given datetime (includes same datetime) is returned.  
		All comparisons are done by version NAME not id, because underlying db id might change.
		
		If global_retrieval_date datetime preceeds first version, no filtering is done.
		
		@param global_retrieval_date long unix time date to test entry against.
		@param version_name string Name of version
		@param version_id string Looks like a number, or '' to pull latest id.
		"""

		data = []

		date_match = vdb_common.date_matcher(global_retrieval_date)
		found=False

		for ptr, item in enumerate(self.versions):
			created = float(item['created'])
			item_name = item['name']

			# Note version_id is often "None", so must come last in conjunction.						
			selected = (found == False) \
				and ((item_name == version_name ) or date_match.next(created))
				
			if selected == True:
				found = True
				if selection==True:
					return item_name

			# Folder type data stores should already have something resembling created date in name.
			if type(self).__name__ in 'VDBFolderDataStore VDBBiomajDataStore':
				item_label = item['name']
			else:
				item_label = vdb_common.lightDate(created) + '_' + item['name']

			data.append([item_label, item['name'], selected]) 
	
		if not found and len(self.versions) > 0:
			if global_retrieval_date: # Select oldest date version since no match above.
				item_name = data[-1][1]
				data[-1][2] = True
			else:
				item_name = data[0][1]
				data[0][2] = True
			if selection == True: 
				return item_name		


		# For cosmetic display: Natural sort takes care of version keys that have mixed characters/numbers
		data = sorted(data, key=lambda el: vdb_common.natural_sort_key(el[0]), reverse=True) #descending

		#Always tag the first item as the most current one
		if len(data) > 0:
			data[0][0] = data[0][0] + ' (current)'
		else:
			data.append([vdb_retrieval.VDB_DATASET_NOT_AVAILABLE + ' Is pointer file content right? : ' + self.data_store_path,'',False])

		"""
		globalFound = False
		for i in range(len(data)):
			if data[i][2] == True:
				globalFound = True
				break

		if globalFound == False:
			data[0][2] = True 			# And select it if no other date has been selcted

		"""

		return data	


	def get_version(self, version_name):
		# All subclasses must define this.
		pass
