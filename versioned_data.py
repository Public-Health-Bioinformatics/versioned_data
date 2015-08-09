#!/usr/bin/python
import os
import optparse
import sys
import time
import re

import vdb_common 
import vdb_retrieval

class MyParser(optparse.OptionParser):
	"""
	 From http://stackoverflow.com/questions/1857346/python-optparse-how-to-include-additional-info-in-usage-output
	 Provides a better display of formatted help info in epilog() portion of optParse.
	"""
	def format_epilog(self, formatter):
		return self.epilog


def stop_err( msg ):
    sys.stderr.write("%s\n" % msg)
    sys.exit(1)


class ReportEngine(object):

	def __init__(self): pass

	def __main__(self):

		options, args = self.get_command_line()
		retrieval_obj = vdb_retrieval.VDBRetrieval()
		retrieval_obj.set_api(options.api_info_path)
		
		retrievals=[]
				
		for retrieval in options.retrievals.strip().strip('|').split('|'):
			# Normally xml form supplies "spec_file_id, [version list], [workflow_list]"
			params = retrieval.strip().split(',')
			
			spec_file_id = params[0]
			
			if spec_file_id == 'none':
				print 'Error: Form was selected without requesting a data store to retrieve!'
				sys.exit( 1 )
				
			# STEP 1:  Determine data store type and location
			data_store_spec = retrieval_obj.user_api.libraries.show_folder(retrieval_obj.library_id, spec_file_id)
			data_store_type = retrieval_obj.test_data_store_type(data_store_spec['name'])
			base_folder_id = data_store_spec['folder_id']			
		
			if not data_store_type:
				print 'Error: unrecognized data store type [' + data_store_type + ']'
				sys.exit( 1 )
	
			ds_obj = retrieval_obj.get_data_store_gateway(data_store_type, spec_file_id)

			if len(params) > 1 and len(params[1].strip()) > 0:			
				_versionList = params[1].strip()
				version_id = _versionList.split()[0] # VersionList SHOULD just have 1 id
			else:
				# User didn't select version_id via "Add new retrieval"
				if options.globalRetrievalDate:
					_retrieval_date = vdb_common.parse_date(options.globalRetrievalDate)
					version_id = ds_obj.get_version_options(global_retrieval_date=_retrieval_date, selection=True)
					
				else:
					version_id = ''
			
			# Reestablishes file(s) if they don't exist on disk. Do data library links to it as well.
			ds_obj.get_version(version_id)
			if ds_obj.version_path == None:
			
					print "Error: unable to retrieve version [%s] from %s archive [%s].  Archive doesn't contain this version id?" % (version_id, data_store_type, ds_obj.library_version_path)
					sys.exit( 1 )
		
			# Version data file(s) are sitting in [ds_obj.version_path] ready for retrieval.
			library_dataset_ids = retrieval_obj.get_library_version_datasets(ds_obj.library_version_path, base_folder_id, ds_obj.version_label, ds_obj.version_path)
			
			# The only thing that doesn't have cache lookup is "folder" data that isn't linked in.
			# In that case try lookup directly.	
			if len(library_dataset_ids) == 0 and data_store_type == 'folder':
				library_version_datasets = retrieval_obj.get_library_folder_datasets(ds_obj.library_version_path)
				library_dataset_ids = [item['id'] for item in library_version_datasets]
				
			if len(library_dataset_ids) == 0:
			
					print 'Error: unable to retrieve version [%s] from %s archive [%s] ' % (version_id, data_store_type, ds_obj.library_version_path)
					sys.exit( 1 )
			
			# At this point we have references to the galaxy ids of the requested versioned dataset, after regeneration
			versioned_datasets = retrieval_obj.update_history(library_dataset_ids, ds_obj.library_version_path, version_id)

			if len(params) > 2:

				workflow_list = params[2].strip() 
			
				if len(workflow_list) > 0:
					# We have workflow run via admin_api and admin_api history.	
					retrieval_obj.get_workflow_data(workflow_list, versioned_datasets, version_id)
				
		
		result=retrievals
		
		# Output file needs to exist.  Otherwise Galaxy doesn't generate a placeholder file name for the output, and so we can't do things like check for [placeholder name]_files folder.  Add something to report on?
		with open(options.output,'w') as fw:
			fw.writelines(result)


	def get_command_line(self):
		## *************************** Parse Command Line *****************************
		parser = MyParser(
			description = 'This Galaxy tool retrieves versions of prepared data sources and places them in a galaxy "Versioned Data" library',
			usage = 'python versioned_data.py [options]',
			epilog="""Details:

			This tool retrieves links to current or past versions of fasta (or other key-value text) databases from a cache kept in the data library called "Fasta Databases". It then places them into the current history so that subsequent tools can work with that data.
		""")

		parser.add_option('-r', '--retrievals', type='string', dest='retrievals',
			help='List of datasources and their versions and galaxy workflows to return')
			
		parser.add_option('-o', '--output', type='string', dest='output', 
			help='Path of output log file to create')

		parser.add_option('-O', '--output_id', type='string', dest='output_id', 
			help='Output identifier')
			
		parser.add_option('-d', '--date', type='string', dest='globalRetrievalDate', 
			help='Provide date/time for data recall.  Defaults to now.')
		
		parser.add_option('-v', '--version', dest='version', default=False, action='store_true', 
			help='Version number of this program.')
			
		parser.add_option('-s', '--api_info_path', type='string', dest='api_info_path', help='Galaxy user api key/path.')	
			
		return parser.parse_args()
			


if __name__ == '__main__':

	time_start = time.time()

	reportEngine = ReportEngine()
	reportEngine.__main__()
	
	print('Execution time (seconds): ' + str(int(time.time()-time_start)))

