# Resource permissions

- `S` = superuser/admin
- `O` = owner of the resource
- `W` = user with write access
- `R` = user with read access
- `U` = regular user (not owner)
- `V` = visitor (not signed in at all)

| | private | proposed | public |
| --- | --- | --- | --- |
| read contents | `S` `O` `W` `R` | `S` | _everyone_ |
| write contents | `S` `O` `W` | `S` | `S` `O` |
| change settings | `S` `O` `W` | `S` | `S` `O` |
| set read/write access | `S` `O` | – | – |
| set owners | `S` `O` | `S` | `S` |
| delete resource | `S` `O` | – | – |
| propose publication | `S` `O` | – | – |
| revoke proposal | – | `S` `O` | – |
| publish resource | – | `S` | – |
| revoke publication | – | – | `S` |
