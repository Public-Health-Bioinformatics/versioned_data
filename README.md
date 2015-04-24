# Versioned Data System
The Galaxy and command line Versioned Data System manages the retrieval of current and past versions of selected reference sequence databases from local data stores.

---

0. Overview
1. [Setup for Admins](doc/setup.md)
  1. [Galaxy tool installation](doc/galaxy_tool_install.md)
  2. [Server data stores](doc/data_stores.md)
  3. [Data store examples](doc/data_store_examples.md)
  4. [Galaxy "Versioned Data" library setup](doc/galaxy_library.md)
  5. [Workflow configuration](doc/workflows.md)
  6. [Permissions, security, and maintenance](doc/maintenance.md)
  7. [Problem solving](doc/problem_solving.md)
2. [Using the Galaxy Versioned data tool](doc/galaxy_tool.md)
3. [System Design](doc/design.md)
4. [Background Research](doc/background.md)
5. [Server data store and galaxy library organization](doc/data_store_org.md)
6. [Data Provenance and Reproducibility](doc/data_provenance.md)
7. [Caching System](doc/caching.md)

---

## Overview

This tool can be used on a server both via the command line and via the Galaxy bioinformatics workflow platform using the "Versioned Data" tool.  Different kinds of content are suited to different archiving technologies, so the system provides a few  storage system choices.

* Fasta sequences - accession ids, descriptions and their sequences - are suited to storage as 1 line key-value pair records in a key-value store.  Here we introduce a low-tech file-based database plugin for this kind of data called **Kipper**.  It is  suited entirely to the goal of producing complete versioned files.  This covers much of the sequencing archiving problem for reference databases.  Consult https://github.com/Public-Health-Bioinformatics/kipper for up-to-date information on Kipper.

* A **git** archiving system plugin is also provided for software file tree archiving, with a particular file differential (diff) compression benefit for documents that have sentence-like lines added and deleted between versions.  

* Super-large files that are not suited to Kipper or git can be handled by a simple "**folder**" data store holds each version of file(s) in a separate compressed archive.

* **Biomaj** (our reference database maintenance software) can be configured to download and store separate version files.  A Biomaj plugin allows direct selection of versioned files within its "data bank" folders.

The Galaxy Versioned Data tool below, shows the interface for retrieving versions of reference database.  The tool lets you select the fasta database to retrieve, and then one or more workflows.  The system then generates and caches the versioned data in the data library; then links it into one's history; then runs the workflow(s) to get the derivative data (a Blast database say) and then caches that back into the data library.  Future requests for that versioned data and derivatives (keyed by workflow id and input data version ids) will return the data already from cache rather than regenerating it, until the cache is deleted.

![galaxy versioned data tool form](https://github.com/Public-Health-Bioinformatics/versioned_data/blob/master/doc/galaxy_tool_form.png)

## Project goals

* **To enable reproducible molecular biology research:** To recreate a search result at a certain point in time we need versioning so that search and mapping tools can look at reference sequence databases corresponding to a particular past date or version identifier.  This recall can also explain the difference between what was known in the past vs. currently.

* **To reduce hard drive space.**  Some databases are too big to keep N copies around, e.g. 5 years of 16S, updated monthly, is say, 670Mb + 668Mb + 665Mb + ....  (Compressing each file individually is an option but even better we could store just the differences between subsequent versions.)
 
* **Maximize speed of archive recall.**  Understanding that the archived version files can be large, we'd ideally like a versioned file to be retrieved in the time it takes to write a file of that size to disk.  Caching this data and its derivatives (makeblastdb databases for example) is important.

* **Improve sequence archive management.** Provide an admin interface for managing regular scheduled import and log of reference sequence databases from our own and 3rd party sources like NCBI and cpndb.ca .

* Integrate database versioning into the Galaxy workflow management software without adding a lot of complexity.

* A bonus would be to enable the efficient sharing of versioned data between computers/servers.
