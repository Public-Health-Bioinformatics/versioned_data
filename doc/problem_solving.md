# Problem solving

If the Galaxy API is not working, then it needs to be enabled in universe_wsgi.ini with "enable_api = True"

The "Versioned data retrieval" tool depends on the bioblend python module created for accessing Galaxy's API. This enables reading and writing to a particular Galaxy data library and to current user's history in a more elegant way. 

  `> pip install bioblend`

This loads a variety of dependencies - requests, poster, boto, pyyaml,... (For ubuntu, first install libyaml-dev first to avoid odd pyyaml error?)  (Note that this must be done as well on galaxy toolshed's install too.)

**Data library download link doesn't work**

If a data library has a version data folder that is linked to the data store elsewhere on the server, that folder's download link probably won't work until you adjust your galaxy webserver (apache or nginx) configuration.  See this and this (a note on galaxy user permissions visa vis apache user).  For the example of all data stores that are in /projects2/reference_dbs/versioned/ , Apache needs two lines for the galaxy site configuration (usually in /etc/httpd/conf/httpd.conf ).

```
XSendFile on
XSendFilePath ... (other paths)
XSendFilePath /projects2/reference_dbs/versioned/
```

Without this path, and sufficient permissions, errors will show up in the Apache httpd log, and galaxy users will find that they can't download the versioned data if it is linked from the galaxy library to other locations on the server.

**Data store version deletion**

Note: if a server data store version folder has been deleted, but a link to it still exists in the Versioned Data library, then attempting to download the dataset from there will result in an error.  Running the Versioned Data tool to request this file will regenerate it in the server data store cache. Alternately, you can delete the versioned data library version cache folder.


