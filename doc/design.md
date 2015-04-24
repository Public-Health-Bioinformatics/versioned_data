# System Design

## Server Versioned data store folder and Galaxy data library folder structure

Galaxy's data library will be the main portal to the server locations where versioned data are kept.  We have designed the system so that versioned data sources usually exist outside of galaxy in "data store folders".  One assumption is that because of the size of the databases involved, and because we are mostly concerned with providing tools with direct access or access to indexes on this data, we will make use of the file system to hold and organize the data store and derived products rather than consider a SQL or NoSQL database warehouse approach.  

Our versioned data tool scans the galaxy data library for folders that signal where these data stores are. It only searches for content inside a data library called "Versioned Data". The folder hierarchy under this is flexible - a Galaxy admin can create a hierarchy to their liking, dividing versioned data first by data source (NCBI, 3rd party, etc.) or by type (viral, bacteral, rna, eucaryote, protein, nucleotide, etc.). Eventually a "versioned data folder" is encountered in the hierarchy.  It has a specific format:

A versioned data folder has a marker file that indicates what kind of archival technology is at work in it.  The marker file also yields the server file path where the archive data exists. (The data library folders themselves are just textual names and so don't provide any information for sniffing where they are or what they contain.)

* pointer.kipper signals a Kipper-managed data store.

* pointer.git signals a git-managed data store.

* pointer.folder signals a basic versioned file storage folder.  No caching mechanism applies here; files are permanent unless deleted manually by an admin.  Content of this file either points to a server folder, or is left empty to indicate that library should be used directly to store permanent versioned data folder content.

* pointer.biomaj signals a basic versioned file storage folder that points directly to Biomaj databank folders.  No caching mechanism applies here; versioned data folders exist to the extent that Biomaj has been configured to keep them.  Each data bank version folder will be examined for content in its /flat/ subfolder; those files will be listed as data to retrieve.

The marker file can have permissions set so that only Galaxy admins could see it.

Under the versioned data folder a user can see archive folders whose contents are linked to caches of particular archive data versions (version date and id indicated in folder name).  More than one sub-folder of archived data can exist since different users may have them in use.  The archived data are a COPY of the master archive folder at cache-generation time.  

For example, if using git to retrieve a version, the git database for that version is recalled, then a server folder is created to cache that archive version, and all of the git archive's contents are copied over to it.  A Galaxy Versioned Data library cached folder's files are usually symlinked to the archive copy folder elsewhere on the server; this is designed so the system can also be used independently of Galaxy by other command line tools).

If the archiving system has a cached version of a particular date available, this is marked by the presence of an "YYYY[-MM-DD-HH-MM-SS]_[VERSION ID]" folder.  If this folder does not exist, the archive needs to be regenerated. Archive dates can be as basic as year, or can include finer granularity of month, day, hour etc.

In the server data store, the folder hierarchy for a data store basically provides file storage for the data store, as well as specifically named folders for cached data.

A data store can be broken into separate volumes such that a particular volume covers a range of version ids. As well, to facilitate parallel processing, a client server can hold a master database in a set of files distinguished by the range of keys they cover, e.g. one master_a.kipper handles all keys beginning with 'a'.

```
/.../[database name]/       
  master/[datastore name]_[volume #]                   
  master/[datastore name]_[volume #]_[key prefix]     (If database is chunked by key prefix)
  [version date]_[version_id]/                        (A particular extracted version's data e.g. "2014-01-01_v5/file 1 .... file N")
```

Derivative data like blast databases are stored under a folder called "Workflow cache" that exists immediately under the versioned data library.  The folder hierarchy here consists of a folder for each workflow by workflow id, followed by a folder coded by the id's of each of the workflows inputs; these reference dataset ids that exist in the versioned data library.  The combination of workflow id and its input dataset ids yeids a cache of one or more output files that we can count on to be the right output function of the workflow + versioned data input.  In the future, this derivative data could be accessed from links under a similar folder structure in the server data store folders. 

```
  workflow_cache/                                     Contains links to galaxy generated workflow products like blast databases.
    workflow_id
      [dataset_id]_[dataset_id]...   (inputs to the workflow coded in folder name)
        Workflow output files for given dataset(s)
```
