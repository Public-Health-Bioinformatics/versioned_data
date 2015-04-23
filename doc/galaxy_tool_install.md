## Galaxy tool installation

1. **This step requires a restart of Galaxy**:  Edit your Galaxy config file ("universe_wsgi.conf" in older installs):
  1. Add the tool's default user name "**versioneddata@localhost.com**" to the admin_user's list line.
  1. Ensure the Galaxy API is activated: "enable_api = True"

2. Then ensure **you** have an API key (from User > Api keys menu).   

3. Login to Galaxy as an administrator, and install the Versioned Data tool.  Go to the Galaxy Admin > Tool Sheds > "Search and browse tool sheds" menu.  Currently this tool is available from the tool shed at https://toolshed.g2.bx.psu.edu/view/damion/versioned_data .  The "versioned_data" repository is located under the "sequence analysis" category.

4. After it is installed, display the tool form once in Galaxy - this allows the tool to do the remaining setup of its "versioneddata" user.  The tool automatically creates a galaxy API user (by default, versioneddata@localhost.com).  You will see an API key generated automatically as well.  **The tool (via Galaxy) automatically writes a copy of this key in a file called "versioneddata_api_key.txt" in its install file folder for reference; if you ever want to change the API key for the versioneddata user, you need to delete this file, and it will be regenerated automatically on next use of the tool by an admin.**

5. Also, ensure that the kipper.py file has the Galaxy server's system user as its owner with executable permission ( "chown galaxy kipper.py; chmod u+x kipper.py"). 


### Command-line Kipper


  Optional: If you want to work with Kipper files directly, e.g. to start a Kipper repository from scratch, then sym-link the kipper.py file that is in the Versioned Data tool code folder's /data_stores/ subfolder - you could link it as "/usr/bin/kipper" for example. 
  The tool path is shown in the "location" field when you click on "Versioned Data" tool in Galaxy's "admin > Administration > Manage installed tool shed repositories" report.  

More info on command-line kipper is available [here](https://github.com/Public-Health-Bioinformatics/kipper).
