#!/usr/bin/python
#
import os
import sys

# Extra step enables this script to locate vdb_common and vdb_retrieval 
# From http://code.activestate.com/recipes/66062-determining-current-function-name/
_self_dir = os.path.dirname(sys._getframe().f_code.co_filename)
sys.path.append(_self_dir)

import vdb_common
import vdb_retrieval

retrieval_obj = None # Global used here to manage user's currently selected retrieval info.


def vdb_init_tool_user(trans):
	"""
	Retrieves a user's api key if they have one, otherwise lets them know they need one
	This function is automatically called from versioned_data.xml form on presentation to user
	Note that this is how self.api_url gets back into form, for passage back to 2nd call via versioned_data.py
	self.api_key is passed via secure <configfile> construct. 
	ALSO: squeezing history_id in this way since no other way to pass it.
	"trans" is provided only by tool form presentation via <code file="..."> 
	 See galaxy source code at https://galaxy-dist.readthedocs.org/en/latest/_modules/galaxy/web/framework.html, 
	 See http://dev.list.galaxyproject.org/error-using-get-user-id-in-xml-file-in-new-Galaxy-td4665274.html
	 See http://dev.list.galaxyproject.org/hg-galaxy-2780-Real-Job-tm-support-for-the-library-upload-to-td4133384.html
	 master api key, set in galaxy config: #self.master_api_key = trans.app.config.master_api_key
	"""
	global retrieval_obj

	api_url = trans.request.application_url + '/api'
	history_id = str(trans.security.encode_id(trans.history.id))
	user_api_key = None
	#master_api_key = trans.app.config.master_api_key
	
	if trans.user:

		user_name = trans.user.username

		if trans.user.api_keys and len(trans.user.api_keys) > 0:
			user_api_key = trans.user.api_keys[0].key #First key is always the active one?
			items = [ { 'name': user_name, 'value': api_url + '-' + history_id, 'options':[], 'selected': True } ]

		else: 
			items = [ { 'name': user_name + ' - Note: you need a key (see "User" menu)!', 'value': '0', 'options':[], 'selected': False } ]
	
	else:
		items = [ { 'name': 'You need to be logged in to use this tool!', 'value': '1', 'options':[], 'selected': False } ]
	
	retrieval_obj = vdb_retrieval.VDBRetrieval()
	retrieval_obj.set_trans(api_url, history_id, user_api_key) #, master_api_key

	return items


def vdb_get_databases():
	"""
	Called by Tool Form, retrieves list of versioned databases from galaxy library called "Versioned Data"
	
		@return [name,value,selected] array
	"""
	global retrieval_obj
	items = retrieval_obj.get_library_data_store_list()
	
	if len(items) == 0:
		# Not great: Communicating library problem by text in form select pulldown input.
		items = [[vdb_retrieval.VDB_DATA_LIBRARY_FOLDER_ERROR, None, False]]
	
	return items


def vdb_get_versions(spec_file_id, global_retrieval_date): 
	"""
	  Retrieve applicable versions of given database.
	  Unfortunately this is only refreshed when form screen is refreshed
	
	@param dbKey [folder_id]
	
	@return [name,value,selected] array
	"""
	global retrieval_obj

	items = []
	if spec_file_id:

		data_store_spec = retrieval_obj.user_api.libraries.show_folder(retrieval_obj.library_id, spec_file_id)

		if data_store_spec: #OTHERWISE DOES THIS MEAN USER DOESN'T HAVE PERMISSIONS?  VALIDATE

			file_name = data_store_spec['name']  # Short (no path), original file name, not galaxy-assigned file_name
			data_store_type = retrieval_obj.test_data_store_type(file_name)
			library_label_path = retrieval_obj.get_library_label_path(spec_file_id)

			if not data_store_type or not library_label_path:
				# Cludgy method of sending message to user
				items.append([vdb_retrieval.VDB_DATA_LIBRARY_FOLDER_ERROR, None, False])
				items.append([vdb_retrieval.VDB_DATA_LIBRARY_CONFIG_ERROR + '"' + vdb_retrieval.VDB_DATA_LIBRARY + '/' + str(library_label_path) + '/' + file_name + '"', None, False])
				return items
			
			_retrieval_date = vdb_common.parse_date(global_retrieval_date)

			# Loads interface for appropriate data source retrieval
			ds_obj = retrieval_obj.get_data_store_gateway(data_store_type, spec_file_id)
			items = ds_obj.get_version_options(global_retrieval_date=_retrieval_date)

		else:
			items.append(['Unable to find' + spec_file_id + ':Check permissions?','',False])

	return items


def vdb_get_workflows(dbKey): 
	"""
	List appropriate workflows for database.  These are indicated by prefix "Versioning:" in name.
	Currently can see ALL workflows that are published; admin_api() receives this in all galaxy versions.
	Seems like only some galaxy versions allow user_api() to also see published workflows.
	Only alternative is to list only individual workflows that current user can see - ones they created, and published workflows; but versioneddata user needs to have permissions on these too.
	
	Future: Sensitivity: Some workflows apply only to some kinds of database
	
		@param dbKey [data_spec_id]
		@return [name,value,selected] array
	"""
	global retrieval_obj
		
	data = []
	try:
		workflows = retrieval_obj.admin_api.workflows.get_workflows(published=True)
		
	except Exception as err: 
		if err.message[-21:] == 'HTTP status code: 403':
			data.append(['Error: User does not have permissions to see workflows (or they need to be published).' , 0, False])
		else:
			data.append(['Error: In getting workflows: %s' % err.message , 0, False])
		return data

	oldName = ""
	for workflow in workflows:
		name = workflow['name']
		if name[0:11].lower() == "versioning:" and name != oldName:
			# 	Interface Bug: If an item is published and is also shared personally with a user, it is shown twice.
			data.append([name, workflow['id'], False])
		oldName = name

	return data


