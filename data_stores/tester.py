#!/usr/bin/python
# -*- coding: utf-8 -*-
import optparse
import sys
import difflib
import os
		

class MyParser(optparse.OptionParser):
	"""
	 From http://stackoverflow.com/questions/1857346/python-optparse-how-to-include-additional-info-in-usage-output
	 Provides a better class for displaying formatted help info in epilog() portion of optParse; allows for carriage returns.
	"""
	def format_epilog(self, formatter):
		return self.epilog

def stop_err( msg ):
    sys.stderr.write("%s\n" % msg)
    sys.exit(1)
    
	
def __main__(self):

	
	"""
	(This is run only in context of command line.)
	FUTURE: ALLOW GLOB IMPORT OF ALL FILES OF GIVEN SUFFX, each to its own version, initial date taken from file date
	FUTURE: ALLOW dates of versions to be adjusted.
	""" 
	options, args = self.get_command_line()
	self.options = options
	
	if options.test_ids: 
		return self.test(options.test_ids)
			

def get_command_line(self):
	"""
	*************************** Parse Command Line *****************************
	
	"""
	parser = MyParser(
		description = 'Tests a program against given input/output files.',
		usage = 'tester.py [program] [input files] [output files] [parameters]',
		epilog="""
		
		    
	parser.add_option('-t', '--tests', dest='test_ids', help='Enter "all" or comma-separated id(s) of tests to run.')

	return parser.parse_args()



def test(self, test_ids):
	# Future: read this spec from test-data folder itself?
	tests = {
		'1': {'input':'a1','outputs':'','options':''}
	}
	self.test_suite('keydb.py', test_ids, tests, '/tmp/')


def test_suite(self, program, test_ids, tests, output_dir):

	if test_ids == 'all':
		 test_ids = sorted(tests.keys())
	else:
		 test_ids = test_ids.split(',')

	for test_id in test_ids:
		if test_id in tests:
			test = tests[test_id]
			test['program'] = program
			test['base_dir'] = base_dir = os.path.dirname(__file__)
			executable = os.path.join(base_dir,program)
			if not os.path.isfile(executable):
				stop_err('\n\tUnable to locate ' + executable)
			# Each output file has to be prefixed with the output (usualy /tmp/) folder 
			test['tmp_output'] = (' ' + test['outputs']).replace(' ',' ' + output_dir)
			# Note: output_dir output files don't get cleaned up after each test.  Should they?!
			params = '%(base_dir)s/%(program)s %(base_dir)s/test-data/%(input)s%(tmp_output)s %(options)s' % test
			print("Test " + test_id + ': ' + params)
			print("................")
			os.system(params)
			print("................") 
			for file in test['outputs'].split(' '):
				try:
					f1 = open(test['base_dir'] + '/test-data/' + file)
					f2 = open(output_dir + file)
				except IOError as details:
					stop_err('Error in test setup: ' + str(details)+'\n')

				#n=[number of context lines
				diff = difflib.context_diff(f1.readlines(), f2.readlines(), lineterm='',n=0)
				# One Galaxy issue: it doesn't convert entities when user downloads file. 
				# BUT IT appears to when generating directly to command line?
				print '\nCompare ' + file
				print '\n'.join(list(diff))     
					
		else:
			stop_err("\nExpecting one or more test ids from " + str(sorted(tests.keys())))

	stop_err("\nTest finished.")
	
		
if __name__ == '__main__':

	keydb = KeyDb()
	keydb.__main__()

