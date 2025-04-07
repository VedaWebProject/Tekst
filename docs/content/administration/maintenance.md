# Maintenance


## Search indices updates

Updating (or recreating) the search indices is possible via

- the administration interface of the Tekst web client (_Administration_ > _Maintenance_ > _Search Indices_)
- the [Tekst-API CLI](./cli.md) (especially needed for scheduling this as a recurring maintenance task)


## Precomputed data

Creating the precomputed data (resource coverage data, resource data aggregations, ...) needed for parts of Tekst to work is possible via

- the administration interface of the Tekst web client (_Administration_ > _Maintenance_ > _Precomputed Data_)
- the [Tekst-API CLI](./cli.md) (as part of the `maintenance` command – especially needed for scheduling this as a recurring maintenance task)


## Internal cleanup

Triggering the internal cleanup routine (for deleting stale user messages, ...) is possible via

- the administration interface of the Tekst web client (_Administration_ > _Maintenance_ > _Internal Cleanup_)
- the [Tekst-API CLI](./cli.md) (as part of the `maintenance` command – especially needed for scheduling this as a recurring maintenance task)
