# versioned_data
The Versioned Data System manages the retrieval of current and past versions of selected reference sequence databases from a local data store.

---

Versioned Data System

0. Overview
1. Setup for Admins
  1. Galaxy tool installation
  2. Server data stores
  3. Data store examples
  4. Galaxy "Versioned Data" library setup
  5. Workflow configuration
  6. Permissions, security, and maintenance
  7. Problem solving
2. Using the Galaxy Versioned data tool
3. System Design
4. Background Research
5. Server data store and galaxy library organization
6. Git Data Store
7. Caching System
8. Future Development
9. Python utilities

---

## Overview

The Versioned Data System on Salk manages the retrieval of current and past versions of selected reference sequence databases.  This tool can be used on Salk both via the command line and via the galaxy platform using the BCCDC "Versioned Data" tool.  Different kinds of content are suited to different archiving technologies, so the system providea alternative storage systems based on archival content.

* Fasta sequences - accession ids, descriptions and their sequences - are suited to storage as 1 line key-value pair records in a key-value store.  Here we introduce a low-tech file-based database plugin for this kind of data called **Kipper**.  It is  suited entirely to the goal of producing complete versioned files.  This covers much of the sequencing archiving problem for reference databases.  Consult https://github.com/Public-Health-Bioinformatics/kipper for up-to-date information on Kipper.

* A git archiving system plugin is also provided for software file tree archiving, with a particular file differential (diff) compression benefit for documents that have sentence-like lines added and deleted between versions.  Git's diff file processing does not perform reliably for long fasta sequence files or files whose contents are re-ordered between versions.  Git's diff functionality can be turned off so that each document is simply stored as a gzip style compressed file.

* Super-large files that are not suited to Kipper or git can be handled by a simple "**folder**" data store holds each version of file(s) in a separate compressed archive.

* **Biomaj** (our reference database maintenance software) can be configured to download and store separate version files.  A Biomaj plugin allows direct selection of versioned files within its "data bank" folders.

The Galaxy Versioned Data tool below, shows the interface for retrieving versions of reference database.  The tool lets you select the fasta database to retrieve, and then one or more workflows.  The system then generates and caches the versioned data in the data library; then links it into one's history; then runs the workflow(s) to get the derivative data (a Blast database say) and then caches that back into the data library.  Future requests for that versioned data and derivatives (keyed by workflow id and input data version ids) will return the data already from cache rather than regenerating it, until the cache is deleted.


## Project goals

* **To enable reproducible molecular biology research:** To recreate a search result at a certain point in time we need versioning so that search and mapping tools can look at reference sequence databases corresponding to a particular past date or version identifier.  This recall can also explain the difference between what was known in the past vs. currently.

* **To reduce hard drive space.**  Some databases are too big to keep N copies around, e.g. 5 years of 16S, updated monthly, is say, 670Mb + 668Mb + 665Mb + ....  (Compressing each file individually is an option but even better we could store just the differences between subsequent versions.)
 
* **Maximize speed of archive recall.**  Understanding that the archived version files can be large, we'd ideally like a versioned file to be retrieved in the time it takes to write a file of that size to disk.  Caching this data and its derivatives (makeblastdb databases for example) is important.

* **Improve sequence archive management.** Provide an admin interface for managing regular scheduled import and log of reference sequence databases from our own and 3rd party sources like NCBI and cpndb.ca .

* Integrate database versioning into the Galaxy workflow management software without adding a lot of complexity.

* A bonus would be to enable the efficient sharing of versioned data between computers/servers.
