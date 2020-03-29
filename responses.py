RESPONSE_HELP = "**Send your model number and I will attempt to convert it into an equivalent Meraki model.**\n\n" + \
                "*Available commands:*  \n" + \
                "**/list [switches/mapping]**: Lists all switches or mappings in the database.  \n" + \
                "**/edit [KEY]**: Edits the switch matching the key provided (keys returned from the list command, in the format MODEL+NETWORK_MODULE).  \n" + \
                "**/add**: Adds a new switch to the database.  \n" + \
                "**/remove [PK]**: Removes a switch from the database.  \n" + \
                "**/allow [USER_ID]**: Allows a user to edit the database.  \n" + \
                "**/disallow [USER_ID]**: Disallows a user from editing the database.  \n" + \
                "**/export**: Exports a CSV copy of the current database for bulk editing.  \n" + \
                "**/import**: Imports a CSV of the current database for bulk editing."

RESPONSE_NOT_IMPLEMENTED = "This feature is not yet implemented."
RESPONSE_NO_PERMISSION = "Sorry, you don't have permission to do that."
RESPONSE_COMMAND_NOT_RECOGNISED = "Unrecognised command!\n\nSee /help for a list of available commands."
