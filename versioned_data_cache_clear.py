#!/usr/bin/python

"""
****************************** versioned_data_cache_clear.py ******************************
 Call this script directly to clear out all but the latest galaxy Versioned Data data library
 and server data store cached folder versions.

 SUGGEST RUNNING THIS UNDER GALAXY OR LESS PRIVILEGED USER, BUT the versioneddata_api_key file does need to be readable by the user.
 
"""
import vdb_retrieval
import vdb_common
import glob
import os

# Note that globals from vdb_retrieval can be referenced by prefixing with vdb_retrieval.XYZ
# Note that this script uses the admin_api established in vdb_retrieval.py

retrieval_obj = vdb_retrieval.VDBRetrieval()
retrieval_obj.set_admin_api()
retrieval_obj.user_api = retrieval_obj.admin_api
retrieval_obj.set_datastores()

workflow_keepers = [] #stack of Versioned Data library dataset_ids that if found in a workflow data input folder key name, can be saved; otherwise remove folder.
library_folder_deletes = []
library_dataset_deletes = []

# Cycle through datastores, listing subfolders under each, sorted.  
# Permanently delete all but latest subfolder.
for data_store in retrieval_obj.data_stores:
	spec_file_id = data_store['id']
	# STEP 1:  Determine data store type and location
	data_store_spec = retrieval_obj.admin_api.libraries.show_folder(retrieval_obj.library_id, spec_file_id)
	data_store_type = retrieval_obj.test_data_store_type(data_store_spec['name'])

	if not data_store_type in 'folder biomaj': # Folders are static - they don't do caching.

		base_folder_id = data_store_spec['folder_id']
		ds_obj = retrieval_obj.get_data_store_gateway(data_store_type, spec_file_id)

		print

		#Cycle through library tree; have to look at the whole thing since there's no /[string]/* wildcard search:
		folders = retrieval_obj.get_library_folders(ds_obj.library_label_path)
		for ptr, folder in enumerate(folders):
	
			# Ignore folder that represents data store itself:		
			if ptr == 0: 
				print 'Data Store ::' + folder['name']

			# Keep most recent cache item
			elif ptr == len(folders)-1:
				print 'Cached Version ::' + folder['name']
				workflow_keepers.extend(folder['files'])
				
			# Drop version caches that are further in the past:
			else:
				print 'Clearing version cache:' + folder['name']
				library_folder_deletes.extend(folder['id'])
				library_dataset_deletes.extend(folder['files'])

	
		# Now auto-clean versioned/ folders too?
		print "Server loc: " + ds_obj.data_store_path	

		items = os.listdir(ds_obj.data_store_path)
		items = sorted(items, key=lambda el: vdb_common.natural_sort_key(el), reverse=True)
		count = 0
		for name in items:

			# If it is a directory and it isn't the master or symlinked "current" one:
			# Add ability to skip sym-linked folders too?
			version_folder=os.path.join(ds_obj.data_store_path, name)
			if not name == 'master' \
				and os.path.isdir(version_folder) \
				and not os.path.islink(version_folder):

				count += 1
				if count == 1:
					print "Keeping cache:" + name
				else:
					print "Dropping cache:" + name
					for root2, dirs2, files2 in os.walk(version_folder):
						for version_file in files2:
							full_path = os.path.join(root2, version_file)
							print "Removing " +	full_path						
							os.remove(full_path)
						#Not expecting any subfolders here.
							
					os.rmdir(version_folder)		


# Permanently delete specific data library datasets:
for item in library_dataset_deletes:
	retrieval_obj.admin_api.libraries.delete_library_dataset(retrieval_obj.library_id, item['id'], purged=True)


# NEED Bioblend API WAY TO DELETE GALAXY LIBRARY FOLDERS!!!!!!!!!!!!!!!!!!!
if 'folders' in dir(retrieval_obj.admin_api):
	for folder in library_folder_deletes:
		retrieval_obj.admin_api.folders.delete(folder['id'])

"""	  

Galaxy next_stable has new API item:

for delete you send http DELETE request to {{url}}/api/folders/{{encoded_folder_id}}?key={{key}}

On Mon Jan 12 2015 at 3:01:56 PM Dooley, Damion <Damion.Dooley@bccdc.ca> wrote:
Hi Martin - Following up on this - I think your API folder delete commit is : https://bitbucket.org/galaxy/galaxy-central/commits/8f76a6abc5d7d5c98b6c148c4cfe75cc1c159e90  

"""


print workflow_keepers

workflow_cache_folders = retrieval_obj.get_library_folders('/'+ vdb_retrieval.VDB_WORKFLOW_CACHE_FOLDER_NAME+'/')

for folder in workflow_cache_folders:
	dataset_ids = folder['name'].split('_') #input dataset ids separated by underscore 
	count = 0
	for id in dataset_ids:
		if id in workflow_keepers:
			count += 1

	# If every input dataset in workflow cache exists in library cache, then keep it.
	if count == len(dataset_ids):
		continue

	# We have one or more cached datasets to drop.
	print "Dropping workflow cache: " + folder['name']
	for id in [item['id'] for item in folder['files']]:
		print id
		retrieval_obj.admin_api.libraries.delete_library_dataset(retrieval_obj.library_id, id, purged=True)

	# NOW DELETE WORKFLOW FOLDER.
	if 'folders' in dir(retrieval_obj.admin_api):
		retrieval_obj.admin_api.folders.delete(folder['id'])


