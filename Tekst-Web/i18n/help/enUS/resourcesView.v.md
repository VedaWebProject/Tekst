# Resource Overview

This overview centrally displays all available information about the resources of the current working text. Depending on whether you are logged in with an account and what permissions you have, different functions will be available to you here.

## Filters

With the filter input field, you can filter resources according to a variety of criteria. Simply type the desired values into the field. They will then be separated by spaces and commas and evaluated individually.

## Actions

The last element in each resource information area is the actions menu. Here you can perform various actions based on your permissions, which are briefly explained below. The letter in parentheses at the end of each heading indicates which user role is minimally required for the respective action. `v` stands for simple visitors, `u` for registered and logged-in users, `o` for owners of the respective resource, and `s` for platform administrators (superusers).

### Read (`v`)

Displays this resource in isolation in the reading view.

### Create Version (`u`)

If you intend to propose a large number of changes or additions to an existing resource, creating a resource version is a good way to collect these changes and submit them as a whole. A resource version functions like a full-fledged resource but cannot be published, and the owner of the original resource can easily review and potentially accept individual changes or suggestions.

For isolated changes, it is simpler to directly use the "Correction Note" function on the respective content in the reading view.

### Settings (`o`)

Opens the settings for this resource. You will find specific information and help texts, there.

### Delete (`o`)

Deletes a resource along with all its content completely and irreversibly. Please use this function with caution and, if necessary, make a backup of the data in advance!

### Export (`v`)

Opens the export tool for this resource. This corresponds to the export function in the reading view.

### View Correction Notes (`o`)

If correction notes from other users are available for this resource, you can view, manage, review, and possibly process them here.

### Edit Content (`o`)

Opens the editing view for the contents of this resource. Here you will find specific information and help texts.

### Download Import Template (`o`)

Downloads a JSON-based template for data import into this resource. For the import to be successful, the data inserted into the template must conform to the schema provided with the template.

### Import Prepared Content (`o`)

If you have a prepared JSON file with content for this resource, you can upload it here. New contents will be created based on the import data, and existing contents will be overwritten.

### Propose for Publication (`o`)

By proposing a resource you created for publication, you make it available to all registered users of the platform so they can review it and suggest changes or additions. Platform administrators will also be informed of your proposal. If they are interested and satisfied with the quality of the data, they can publish the resource on the platform, making it accessible to the public, including non-registered users.

Resources proposed for publication cannot be edited. Additionally, any permissions granted to other users will be reset. The time during which a resource is "proposed" is for review by other users and for gathering suggestions for changes. To incorporate the suggestions, the proposal must be withdrawn first. Once the resource is revised, it can be proposed again. A publication proposal can be withdrawn as long as the resource has not been published.

When a resource is published, platform administrators initially gain sole control over it to prevent unwanted changes. You may still propose changes to the resource data later, but these must be separately approved unless the administrators add you back as an owner of the resource.

### Withdraw Publication Proposal (`o`)

Withdraws the proposal for the publication of a resource. The resource will then be visible only to its owners and can be revised "privately".

### Publish (`s`)

A resource can only be published if it has been proposed for publication beforehand. Platform administrators will then initially have sole control over the resource, making it accessible to the public, including non-registered users.

### Revoke Publication (`o`)

Reverses a publication. The resource will then be visible only to its current owners again.

### Set Resource Owners (`o`)

This function allows you to change the owners of a resource. The new owners will then have write access to the resource’s content, can change settings, and manage the resource, including adding further owners.

Therefore, only assign owners to a resource if you are sure they can take responsibility for it and you trust them!
