# Permissions, security, and maintenance

## Permissions

When installing the Versioned Data tool, ensure that you are in the Galaxy config admin_user's list and that you have an API key.  Run the tool at least once after install, that way the tool can create its own "versioneddata" user if it isn't already there.  The tool uses this account to run data retrieval workflow jobs.

For your server data store folders, since galaxy is responsible for triggering the generation and storage of versions in them, it will need permissions. For example, assuming "galaxy" is the user account that runs galaxy:

```bash
  chown -R galaxy /projects2/reference_dbs/versioned/
  chmod u+rwx /projects2/reference_dbs/versioned/*
```

Otherwise you will be confronted with an error similar to the following error within Galaxy when you try to do a retrieval: 

```bash
  File "/usr/lib64/python2.6/subprocess.py", line 1234, in _execute_child
    raise child_exception
  OSError: [Errno 13] Permission denied"
```

## Cache Clearing

All the retrieved data store versions (except for static "folder" data stores) get cached on the server, and all the triggered galaxy workflow runs get cached in galaxy in the Versioned Data library's "Workflow cache" folder.  A special script will clear out all but the most recent version of any data store's cached versions, and remove workflow caches as appropriate.  This script is named 

  `versioned_data_cache_clear.py`

and is in the Versioned Data script's shed_tools folder.  It can be run as a monthly scheduled task.

The "versioneddata" user has a history for each workflow it runs on behalf of another user.  A galaxy admin can impersonate the "versioneddata" user to see the workflows being executed by other users, and as well, manually delete any histories that haven't been properly deleted by the cache clearing script.

Note that Galaxy won't delete a dataset if it is linked from another (user or library) context.

## Notes

In galaxy, the galaxy (i) information link from a "Versioned Data Retrieval" history job item will display all the form data collected for the job run.  One item, 

  `For user with Galaxy API Key	http://salk.bccdc.med.ubc.ca/galaxylab/api-cc628a7dffdbeca7`

is used to pass the api url, and user's current history id.  We weren't able to convey this information any other way.  The coded parameter is not the user's api key; that is kept confidential, i.e. it doesn't exist in the records of the job run.

 
