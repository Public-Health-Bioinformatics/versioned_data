#!/usr/bin/python
## ********************************* GIT ARCHIVE *******************************
##

import os, sys
import vdb_common
import vdb_data_stores
import subprocess
import datetime

class VDBGitDataStore(vdb_data_stores.VDBDataStore):

	def __init__(self, retrieval_obj, spec_file_id):
		"""
		Archive is expected to be in "master/" subfolder of data_store_path on server.  
		"""
		super(VDBGitDataStore, self).__init__(retrieval_obj, spec_file_id)
		self.command = 'git'
		gitPath = self.data_store_path + 'master/'
		if not os.path.isdir(os.path.join(gitPath,'.git') ):
			print "Error: Unable to locate git archive file: " + gitPath
			sys.exit(1) 
		
		command = [self.command, '--git-dir=' + gitPath + '.git', '--work-tree=' + gitPath, 'for-each-ref','--sort=-*committerdate', "--format=%(*committerdate:raw) %(refname)"]
		#	to list just 1 id: command.append('refs/tags/' + version_id)
		# git --git-dir=/.../NCBI_16S/master/.git --work-tree=/.../NCBI_16S/master/ tag
		items, error = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		items = items.split("\n") #Loop through list of tags
		versions = []
		for ptr, item in enumerate(items):

			# Ignore master branch name; time is included as separate field in all other cases
			if item.strip().find(" ") >0: 
				(vtime, voffset, name) = item.split(" ")
				created = vdb_common.get_unix_time(vtime, voffset)
				item_name = name[10:] #strip 'refs/tags/' part off
				versions.append({'name':item_name, 'id':item_name, 'created': created})
		
		self.versions = versions

	
	def get_version(self, version_name):
		"""
		Returns server folder path to version folder containing git files for a given version_id (git tag)
		
		FUTURE: TO AVOID USE CONFLICTS FOR VERSION RETRIEVAL, GIT CLONE INTO TEMP FOLDER 
		with -s / --shared and -n / --no-checkout (to avoid head build) THEN CHECKOUT version
		...
		REMOVE CLONE GIT REPO

		@param galaxy_instance object A Bioblend galaxy instance
		@param library_id string Identifier for a galaxy data library
		@param library_label_path string Full hierarchic label of a library file or folder, PARENT of version id folder.

		@param base_folder_id string a library folder id under which version files should exist	
		@param version_id alphaneumeric string (git tag)
		
		"""
		version = self.get_metadata_version(version_name)
		
		if not version:
			print 'Error: Galaxy was not able to find the given version id in the %s data store.' % self.version_path
			sys.exit( 1 )
			
		version_name = version['name']
		self.version_path = os.path.join(self.data_store_path, version_name)
		self.version_label = vdb_common.lightDate(version['created']) + '_v' + version_name
		self.library_version_path = os.path.join(self.library_label_path, self.version_label)

		# If Data Library Versioned Data folder doesn't exist for this version, then create it
		if not os.path.exists(self.version_path):
			try:		
				os.mkdir(self.version_path)
			except:
				print 'Error: Galaxy was not able to create data store folder "%s".  Check permissions?' % self.version_path
				sys.exit( 1 )

		if os.listdir(self.version_path) == []: 	
			
			git_path = self.data_store_path + 'master/'
			# RETRIEVE LIST OF FILES FOR GIVEN GIT TAG (using "ls-tree".  
			# It can happen independently of git checkout)

			command = [self.command,  '--git-dir=%s/.git' % git_path, 'ls-tree','--name-only','-r', version_name]
			items, error = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			git_files = items.split('\n')
		
			# PERFORM GIT CHECKOUT 
			command = [self.command, '--git-dir=%s/.git' % git_path, '--work-tree=%s' % git_path, 'checkout', version_name]
			results, error = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()		
		
			vdb_common.move_files(git_path, self.version_path, git_files)



	def get_metadata_version(self, version_name=''):
		if version_name == '':
			return self.versions[0]

		for version in self.versions:
			if str(version['name']) == version_name:
				return version
							
		return False
		
		
