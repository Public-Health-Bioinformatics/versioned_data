
def version_cache_setup(dataset_id, data_file_cache_folder, cacheable_dataset):
	""" UNUSED: Idea was to enable caching of workflow products outside of galaxy for use by others.
		CONSIDER METACODE.  NOT INTEGRATED, NOT TESTED.
	"""
	data_file_cache_name = os.path.join(data_file_cache_folder, dataset_id ) #'blastdb.txt'
	if os.path.isfile(data_file_cache_name):
		pass
	else:
		if os.path.isdir(data_file_cache_folder):
			shutil.rmtree(data_file_cache_folder)
		os.makedirs(data_file_cache_folder)
		# Default filename=false means we're supplying the filename.
		gi.datasets.download_dataset(dataset_id, file_path=data_file_cache_name, use_default_filename=False, wait_for_completion=True) # , maxwait=12000) is a default of 3 hours

		# Generically, any dataset might have subfolders - to check we have to
		# see if galaxy dataset file path has contents at _files suffix. 
		# Find dataset_id in version retrieval history datasets, and get its folder path, and copy _files over...
		galaxy_dataset_folder = cacheable_dataset['file_name'][0:-4] + '_files'
		time.sleep(2)
		if os.path.isdir(galaxy_dataset_folder) \
		and not os.path.isdir(data_file_cache_folder + '/files/'):
			print 'Copying ' + galaxy_dataset_folder + ' to ' + data_file_cache_folder
			# Copy program makes target folder.
			shutil.copytree(galaxy_dataset_folder, data_file_cache_folder + '/files/') # , symlinks=False, ignore=None
			
