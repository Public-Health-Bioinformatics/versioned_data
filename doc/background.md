# Background Research

### Git Archiving

Git was investigated as a generic solution for versioning textual files but in a number of cases its performance was detrimental.  Initially the git archive option seemed to fail on fasta files of any size.  In tests git was replacing one version with another by a diff that contained deletes of every original line followed by inserts of every line in new file.  

By reformatting the incoming fasta file so that each line held one fasta record >[sequence id] [description] [sequence], git's diff algorithm seemed to regain its efficiency. The traditional format:

```
>gi|324234235|whatever a description
ATGCCGTAAGATTC ...
ATGCCGTAAGATTC ...
ATGCCGTAAGATTC ...
>gi|25345345|another entry
etc.
```

was converted to a 1 line format:

```
>gi|324234235|whatever a description [tab] ATGCCGTAAGATTCATGCCGTAAGATTCATGCCGTAAGATTC ...
>gi|25345345|another entry ...
```

This approach seemed to archive fasta files very efficiently.  However it turned out this only worked for some kinds of fasta data.  Git's file differential algorithm failed possibly because of a lack of variation from line to line of a file - it may need lines to have different lengths, word count, or variation in character content (it seemed to be ok for some nucleotide data, but we found it occasionally failed on uniprot v1 to v11 protein data.

There is a git feature to disable diff analysis for files above a certain file size, which then makes git archive size comparable to a straight text-file compression algorithm (zip/gzip).  Overall, a practical limit of 15gb has been reported for git archive size.  The main barrier seems to be content format; archive retrieval does get slower over time if diffs are being calculated. 

Git also has has very high memory requirements to do its processing, which is a server liability.  Tests indicate that for some inputs, git is successful for file sizes up to at least a few gigabytes.  

### XML Archiving

We also examined the versioning of XML content.  The XArch: http://xarch.sourceforge.net/ approach is very promising as a generic solution, though it entails slow processing due to the nature of xml documents.  It compares current and past xml documents and datestamps the additions/deletions to an xml structure.  A good article summarizing the XML archive problem: http://useless-factor.blogspot.ca/2008/01/matching-diffing-and-merging-xml.html


### Other Database Solutions

A number of key-value databases exist (e.g. LevelDB, LMDB, and DiscoDB) but they are designed to gain quick access to individual key-value entries, not to query properties of each key essential to version construction, namely to filter every key in the database by when it was created or deleted.  Some key-value databases have features that could support speedy version retrieval.  

Google's Leveldb - a straight key-value file based database - may work, though we would need to think up a scheme for including create & delete times in the key for each fasta identifier.  Possibly 1 key=fasta id record indicating existence of fasta identifier sequence; and subsequent fastaId.created.deleted key as per the keydb solution.  An advantage here is that compression is built-in.  In the case where incoming data consists a full file to synchronize with, inserts are easy to account for - but deletes can be very tricky since finding them involves scanning through the entire leveldb's key list, with the assumption that they are sorted the same way as the incoming data (the keydb approach) (VERIFY THIS???)

For processing an incoming entire version of key-value content, the functionality required is that the keys are stored in a reliable sort order, and that they can be read fast sequentially .  During this loop we can retrieve all the create/update/delete transactions of each key by version or date.  (Usually the db has no ability to structure the value data though, so we would usually have to create such a schema).  This is basically what keydb does.

For processing separate incoming files that contain only inserts and deletes, the job is much the same, only we skip swaths of the master database content.  At some point it becomes more attractive performance-wise to implement an indexed key value store, thus avoiding the sorting and sequential access necessary for simpler key-value dbs.
