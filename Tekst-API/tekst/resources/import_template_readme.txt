Properties prefixed with an underscore are purely for informational purposes and can be omitted in the actual import file.
The array 'units' holds the data you want to import. Each unit represents data for one location.
The '_unitSchema' object gives you a schema and description a unit has to follow to be valid.
Every unit you provide MUST keep the exact 'nodeId' property from this template!
For locations the resource already has contents for, the unit's other properties (see '_unitSchema') are optional.
Already existing data units will be updated with the data given in the respective unit object.
Units targeting locations the resource has no contents for yet MUST follow '_unitSchema'!
To skip data import for a specific location, just remove the respective unit object from 'units'.
