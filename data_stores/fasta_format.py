#!/usr/bin/python		
# Simple comparison and conversion tools for big fasta data

import sys, os, optparse

VERSION = "1.0.0"

class MyParser(optparse.OptionParser):
	"""
	Provides a better class for displaying formatted help info.
	From http://stackoverflow.com/questions/1857346/python-optparse-how-to-include-additional-info-in-usage-output.
	"""
	def format_epilog(self, formatter):
		return self.epilog


def split_len(seq, length):
	return [seq[i:i+length] for i in range(0, len(seq), length)]


def check_file_path(file_path, message = "File "):
		
	path = os.path.normpath(file_path)
	# make sure any relative paths are converted to absolute ones
	if not os.path.isdir(os.path.dirname(path)) or not os.path.isfile(path): 
		# Not an absolute path, so try default folder where script was called:
		path = os.path.normpath(os.path.join(os.getcwd(), path) )
		if not os.path.isfile(path):
			print message + "[" + file_path + "] doesn't exist!"
			sys.exit(1)

	return path
		

class FastaFormat(object):

	def __main__(self):

		options, args = self.get_command_line()

		if options.code_version:
			print VERSION
			return VERSION
	
		if len(args) > 0:
			file_a = check_file_path(args[0])
		else: file_a = False
		
		if len(args) > 1:
			file_b = check_file_path(args[1])
		else: file_b = False			

		if options.to_fasta == True:
			# Transform from key-value file to regular fasta format: 1 line for identifier and description(s), remaining 80 character lines for fasta data.

			with sys.stdout as outputFile :
				for line in open(file_a,'r') if file_a else sys.stdin:
					line_data =	line.rsplit('\t',1)
					if len(line_data) > 1:
						outputFile.write(line_data[0] + '\n' + '\n'.join(split_len(line_data[1],80)) )
					else:
						# Fasta one-liner didn't have any sequence data
						outputFile.write(line_data[0])
					
			#outputFile.close() 	#Otherwise terminal never looks like it closes?
	
	
		elif options.to_keyvalue == True:	
			# Transform from fasta format to key-value format:
			# Separates sequence lines are merged and separated from id/description line by a tab.
			with sys.stdout as outputFile:
				start = True
				for line in open(file_a,'r') if file_a else sys.stdin:
					if line[0] == ">":
						if start == False:
							outputFile.write('\n')
						else:
							start = False
						outputFile.write(line.strip() + '\t')

					else:
						outputFile.write(line.strip())	


		elif options.compare == True:

			if len(args) < 2:
				print "Error: Need two fasta file paths to compare"
				sys.exit(1)
			
			file_a = open(file_a,'r')
			file_b = open(file_b,'r')

			p = 3 
			count_a = 0
			count_b = 0
			sample_length = 50

			while True: 

				if p&1: 
					a = file_a.readline() 
					count_a += 1

				if p&2: 
					b = file_b.readline() 
					count_b += 1
		
				if not a or not b: # blank line still has "cr\lf" in it so doesn't match here 
					print "EOF"
					break 

				a = a.strip() 
				b = b.strip()
		
				if a == b: 
					p = 3 
		
				elif a < b: 
					sys.stdout.write('f1 ln %s: -%s\nvs.   %s \n' % (count_a, a[0:sample_length] , b[0:sample_length])) 
					p = 1 
		
				else: 
					sys.stdout.write('f2 ln %s: +%s\nvs.   %s \n' % (count_b, b[0:sample_length] , a[0:sample_length]))
					p = 2 

	
				if count_a % 1000000 == 0:
					print "At line %s:" % count_a

				# For testing:
				#if count_a > 50:
				#	
				#	print "Quick exit at line 500"
				#	sys.exit(1)
	

			for line in file_a.readlines(): 
				count_a += 1
				sys.stdout.write('f1 ln %s: -%s\nvs.   %s \n' % (count_a, line[0:sample_length] )) 

			for line in file_b.readlines():
				count_b += 1 
				sys.stdout.write('f2 ln %s: +%s\nvs.   %s \n' % (count_b, line[0:sample_length] )) 

		
		

	def get_command_line(self):
		"""
		*************************** Parse Command Line *****************************
	
		"""
		parser = MyParser(
			description = 'Tool for comparing two fasta files, or transforming fasta data to single-line key-value format, or visa versa.',
			usage = 'fasta_format.py [options]',
			epilog="""
	Note: This tool uses stdin and stdout for transforming fasta data.
			
	Convert from key-value data to fasta format data:
		fasta_format.py [file] -f --fasta 
		cat [file] | fasta_format.py -f --fasta 
		
	Convert from fasta format data to key-value data:	
		fasta_format.py [file] -k --keyvalue 
		cat [file] | fasta_format.py -k --keyvalue 

	Compare two fasta format files:	
		fasta_format.py [file1] [file2] -c --compare 

	Return version of this code:	
		fasta_format.py -v --version 		

""")

		parser.add_option('-c', '--compare', dest='compare', default=False, action='store_true', 
			help='Compare two fasta files')

		parser.add_option('-f', '--fasta', dest='to_fasta', default=False, action='store_true', 
			help='Transform key-value file to fasta file format')

		parser.add_option('-k', '--keyvalue', dest='to_keyvalue', default=False, action='store_true', 
			help='Transform fasta file format to key-value format')

		parser.add_option('-v', '--version', dest='code_version', default=False, action='store_true', 
			help='Return version of this code.')

		return parser.parse_args()
	

if __name__ == '__main__':

	fasta_format = FastaFormat()
	fasta_format.__main__()
	
