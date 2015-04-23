## Setup for Admins

The general goal with the following configuration is to enable the versioned data to be generated and used directly by server (non galaxy-platform) users; at the same time Galaxy users have access to the same versioned data system (and also have the benefit of generating derivative data via Galaxy workflows) without having to leave the Galaxy platform.  In the background a reference database scheduled import process (in our case maintained by Biomaj) keeps the master data store files up to date.

To setup the Versioned Data Tool, do the following: 

  1. [Galaxy tool installation](galaxy_tool_install.md)
  2. [Server data stores](data_stores.md)
  3. [Data store examples](data_store_examples.md)
  4. [Galaxy "Versioned Data" library setup](galaxy_library.md)
  5. [Workflow configuration](workflows.md)
  6. [Permissions, security, and maintenance](maintenance.md)
  7. [Problem solving](problem_solving.md)
  
Any galaxy user who wants to use this tool will need a Galaxy API key.  They can get one via their User menu, or a Galaxy admin can assign one for them.
