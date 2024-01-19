Properties prefixed with an underscore are purely for informational purposes and can be omitted in the actual import file.
The array 'contents' holds the data you want to import. Each content represents data for one location.
The '_contentSchema' object gives you a schema and description a content has to follow to be valid.
Every content you provide MUST keep the exact 'locationId' property from this template!
For locations the resource already has contents for, the content's other properties (see '_contentSchema') are optional.
Already existing contents will be updated with the data given in the respective content object.
Contents targeting locations the resource has no contents for yet MUST follow '_contentSchema'!
To skip data import for a specific location, just remove the respective content object from 'contents'.
