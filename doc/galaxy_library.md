**Create a galaxy data library called "Versioned Data" and add folders and "pointer" files that tell galaxy where the data stores are on the server.**

1) Set permissions so the special "versioneddata@localhost.com" user has add/update permissions on the "Versioned Data" library.
2) Then add any folder structure you want under Versioned Data.  Top level folders could be "Bacteria, Virus, Eukaryote", or "NCBI, ... ".  Underlying folders can hold versioned data for particular bacteria / virus databases, e.g. "NCBI nt".

3) Add a **"pointer.[data store type]"** file (a simple galaxy dataset file) to any folder that you want to activate as a versioned data store.  Any folder that has a "pointer.[data store type]" file in it will be treated as a folder containing versioned content, as illustrated on the right.  These folders (their names) will then be included in the Versioned Data tool's list of data stores. Within these folders, links to caches of retrieved versioned data will be kept (shown as "cached data" items in illustration).  For "folder" and "biomaj" data stores, links will be to permanent files, not cached ones.

For example, on galaxy page Shared Data > Data Libraries > Versioned Data, there is a folder/file:

  Bacterial/RDP RNA/pointer.kipper

which contains one line of text:

  /projects2/ref_databases/versioned/rdp_rna/

That enables the Versioned Data tool to list the Kipper archive as "RDP RNA" (name of folder that pointer file is in), and to know where its data store is. Beneath this folder other cached folders will accumulate.

The "upload files to a data library" page (shown at right) has the ability to link to the pointer file directly in the data store folder.  Select the displayed "Upload files from filesystem paths" option (available only if you access this form from the admin menu in Galaxy).  Enter the path and FILENAME (literally "pointer.kipper" in this case) of your pointer file. If you forget the filename, galaxy will link all the content files, which will need to be deleted before continuing.

"Preferably select the "Link to files without copying into Galaxy" option as well.  This isn't required, but linking to the pointer file enables easier diagnosis of folder path problems.

Then submit the form; if an error occurs then verify that the pointer file path is correct.

Note: a folder called "Workflow Cache" is automatically created within the Versioned Data folder to hold cached workflow results as triggered by the Versioned Data tool. No maintenance of this folder is needed.

Direct use of Data Library Folder:
The "folder" data store is designed ....
Rather than storing your data versions in a folder elsewhere on the server, you can 
