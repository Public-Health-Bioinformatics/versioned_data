# Server Data Stores

These folders hold the git, Kipper, and plain folder data stores.  A data store connection directly to a Biomaj databank is also possible, though it is limited to those databanks that have .fasta files in their /flat/ subfolder.  How you want to store your data depends on the data itself (size, format) and its frequency of use; generally large fasta databases should be held in a Kipper data store.  Generally, each git or Kipper data store needs to have:
* An appropriately named folder;
* A sub-folder called "master/", with the data store files set up in it;
* A file called "pointer.[type of data store]" which contains a path to itself.  This file will be linked into a galaxy data library.
Note that all these folders need to be accessible by the same user that runs your Galaxy installation for Galaxy integration to work.  Specifically Galaxy needs recursive rwx permissions on these folders.

To start, you may want to set up the Kipper RDP RNA database (included in the Kipper repository RDP-test-case folder, see README.md file there).  It comes complete with the folder structure and files for the Kipper example that follows.  You will have to adjust the pointer.Kipper file content appropriately.

The data store folders can be placed within a single folder, or may be in different locations on the server as desired.  In our example versioned data stores are all located under /projects2/reference_dbs/versioned/ . 

## Data Store Examples

### Kipper data store example: A data store for the RDP RNA database:
```bash
  /projects2/reference_dbs/versioned/RDP_RNA/
  /projects2/reference_dbs/versioned/RDP_RNA/pointer.kipper
  /projects2/reference_dbs/versioned/RDP_RNA/master/
  /projects2/reference_dbs/versioned/RDP_RNA/master/rdp_rna_1
  /projects2/reference_dbs/versioned/RDP_RNA/master/rdp_rna_2
  /projects2/reference_dbs/versioned/RDP_RNA/master/rdp_rna.md
```
To start a Kipper data store from scratch, go into the master folder, initialize a Kipper data store there, and import a version of a content file into the Kipper db.  

```bash
cd master/
kipper.py rdp_rna -M fasta
kipper.py rdp_rna -i [file to import] -o .
```

Kipper stores and retrieves just one file at a time. Currently there is no provision for retrieving multiple files from different Kipper data stores at once.

Note that very large temporary files can be generated during the archive/recall process.  For example, a compressed 10Gb NCBI "nr" input fasta file may be resorted and reformatted; or a 10Gb file may be transformed from Kipper format and output to a file.  For this reason we have located any necessary temporary files in the input and output folders specified in the Kipper command line.  (The system /tmp/ folder can be too small to fit them).


### Folder data store example

In this scenario the data we want to archive probably isn't of a key-value nature, nor is it amenable to diff storage via git, so we're storing each version as a separate file.  We don't need the "master" sub-folder since there is no master database, but we do need 1 additional folder to store each version's file(s).

The version folder names must be in the format **[date]_[version id]** to convey to users the date and version id of each version.  The folder names will be displayed directly in the Galaxy Versioned Data tool's selectable list of versions. Note that this can allow for various date and time granularity, e.g. "2005_v1" and "2005-01-05 10:24_v1" are both acceptable folder names. Note that several versions can be published on the same day.  

Example of a refseq50 protein database as a folder data store:

```bash
/projects/reference_dbs/versioned/refseq50/
/projects/reference_dbs/versioned/refseq50/pointer.folder
/projects/reference_dbs/versioned/refseq50/2005-01-05_v1/file.fasta
/projects/reference_dbs/versioned/refseq50/2005-01-05_v2/file.fasta
/projects/reference_dbs/versioned/refseq50/2005-02-04_v3/file.fasta	
...
/projects/reference_dbs/versioned/refseq50/2005-05-24_v4/file.fasta	
...
/projects/reference_dbs/versioned/refseq50/2005-09-27_v5/file.fasta	
```

etc...

A data store of type "folder" doesn't have to be stored outside of galaxy.  Exactly the same folder structure can be set up directly within the galaxy data library, and files can be uploaded inside them.  The one drawback to this approach is that then other (non-galaxy platform) server users can't have easy access to version data. 

Needless to say, administrators should **never delete these files since they are not cached!**

### Git Data Store example

A git data store for versions of the NCBI 16S microbial database would look like:

```
/projects2/reference_dbs/versioned/ncbi_16S/
/projects2/reference_dbs/versioned/ncbi_16S/pointer.git
/projects2/reference_dbs/versioned/ncbi_16S/master/.git (hidden file)
```

One must initialize a git repository (or clone one) into the master/ folder.  The Versioned Data system depends on use of git 'tags' to specify versions of data.  See the Git Data Store section for details.
To start a git repository from scratch, go into the master folder, initialize git there, copy versioned content into the folder, and then commit it.  Finally add a git tag that describes the version identifier.  The versioned data system only distinguishes versions by their tag name. Thus one can have several commits between versions.

```
cd master/
git init
cp [files from wherever] ./
git add [those files]
git commit -m 'various changes'
...
git add [changed files]
git commit -m 'various changes'
...
git tag -a v1 -m v1
```

Once your tag is defined it will be listed in Galaxy as a version


### Biomaj data store example

In this scenario the data we want versioned access to is sitting directly in the /flat/ folder of a Biomaj databank.  Each version is a separate file that Biomaj manages.  Biomaj can be set to keep all old versions alongside any new one it downloads, or it can limit the total # of versions to a fixed number (this limits experimental reproducibility).

*coming soon...*
