## Data Provenance and Reproducibility

When a user selects particular version id or date for versioned data retrieval, this is recorded for future reference, and can be seen in a history item's "View details" (info icon) report, in the "Input Parameters" section.  But if a user left the global date field blank or didn't select a particular version of a data source, they or another user can still rerun a Versioned Data retrieval to recreate the results by noting the original history item's view details "Created" date and entering it into the global retrieval date of the form.  

![A history dataset has a detailed view link](history_view_details.png)

![Data provenance information is available in the detail view](history_dataset_details.png)

Also, particular dates/versions of a Versioned Data history item's retrieved data are shown in its "Edit Attributes" (pencil icon) report in the "Info" field.

Because Galaxy also preserves the version id of any galaxy tool it runs (e.g. the makeblastdb version #), rerunning a history/workflow that has these tools should also apply the appropriate software version to generate the secondary data as well. 
However, the tool version ids contained within a workflow are not recorded by the versioned data tool per se.; they exist only in the selected workflow's design template, so some care must be taken to freeze or version any workflows used to generate derivative data.
