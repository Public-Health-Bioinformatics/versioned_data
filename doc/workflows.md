# Workflow configuration

**All displayed workflows must be prefixed with the keyword "Versioning:"**  This is how they are recognized by the Versioned Data tool

In order for a workflow to show up in the tool's Workflows menu, **it must be published by its author**. Currently there is no other ability to offer finer-grained access to lists of workflows by individual or user group.  

Workflow processing is accomplished on behalf of a user by launching it in a history of the versioneddata@localhost.com user.  Cache clearing will remove these file references from the data library when they are old (but as the files are often moved up to the library's cache they can still be used by others until that cache is cleared.  An admin can impersonate a "versioneddata" user to see the workflows being executed by other users.

Note that any workflow that uses additional input datasets must have those datasets set in the workflow design/template, so they must exist in a fixed location - a data library.  (Currently they can't be in the Versioned Data library). 

If a a workflow references a tool version that has been uninstalled, one will receive this error when working on it.  The only remedy is to reinstall that particular tool version, or to change the workflow to a newer version. 

```bash
  File "/usr/lib/python2.6/site-packages/bioblend/galaxyclient.py", line 104, in make_post_request r.status_code, body=r.text)
  bioblend.galaxy.client.ConnectionError: Unexpected response from galaxy: 500: {"traceback": "Traceback (most recent call last):\n  File \"/usr/local/galaxy/production1/galaxy-dist/lib/galaxy/web/framework/decorators.py\", line 244, in decorator\n    rval = func( self, trans, *args, **kwargs)\n  File \"/usr/local/galaxy/production1/galaxy-dist/lib/galaxy/webapps/galaxy/api/workflows.py\", line 231, in create\n    populate_state=True,\n  File \"/usr/local/galaxy/production1/galaxy-dist/lib/galaxy/workflow/run.py\", line 21, in invoke\n    return __invoke( trans, workflow, workflow_run_config, workflow_invocation, populate_state )\n  File \"/usr/local/galaxy/production1/galaxy-dist/lib/galaxy/workflow/run.py\", line 60, in __invoke\n    modules.populate_module_and_state( trans, workflow, workflow_run_config.param_map )\n  File \"/usr/local/galaxy/production1/galaxy-dist/lib/galaxy/workflow/modules.py\", line 1014, in populate_module_and_state\n    step_errors = module_injector.inject( step, step_args=step_args, source=\"json\" )\n  File \"/usr/local/galaxy/production1/galaxy-dist/lib/galaxy/workflow/modules.py\", line 992, in inject\n    raise MissingToolException()\nMissingToolException\n", "err_msg": "Uncaught exception in exposed API method:", "err_code": 0}
```
