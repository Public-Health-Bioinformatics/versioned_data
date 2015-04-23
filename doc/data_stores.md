# Server Data Stores

These folders hold the git, Kipper, and plain folder data stores.  A data store connection directly to a Biomaj databank is also possible, though it is limited to those databanks that have .fasta files in their /flat/ subfolder.  How you want to store your data depends on the data itself (size, format) and its frequency of use; generally large fasta databases should be held in a Kipper data store.  Generally, each git or Kipper data store needs to have:
* An appropriately named folder;
* A sub-folder called "master/", with the data store files set up in it;
* A file called "pointer.[type of data store]" which contains a path to itself.  This file will be linked into a galaxy data library.
Note that all these folders need to be accessible by the same user that runs your Galaxy installation for Galaxy integration to work.  Specifically Galaxy needs recursive rwx permissions on these folders.

To start, you may want to set up the Kipper RDP RNA database (included in the Kipper repository RDP-test-case folder, see README.md file there).  It comes complete with the folder structure and files for the Kipper example that follows.  You will have to adjust the pointer.Kipper file content appropriately.

The data store folders can be placed within a single folder, or may be in different locations on the server as desired.  In our example versioned data stores are all located under /projects2/reference_dbs/versioned/ . 
