# Ressourcen-Berechtigungen

- `S` = Superuser/Admin
- `O` = Besitzer\*in der Ressource
- `W` = Benutzer\*in mit Schreibzugriff
- `R` = Benutzer\*in mit Lesezugriff
- `U` = Reguläre Benutzer\*in (nicht Besitzer\*in)
- `V` = Besucher\*in (nicht angemeldet)

| | privat | vorgeschlagen | öffentlich |
| --- | --- | --- | --- |
| Inhalte lesen | `S` `O` `W` `R` | `S` | _jede\*r_ |
| Inhalte schreiben | `S` `O` `W` | `S` | `S` `O` |
| Einstellungen ändern | `S` `O` `W` | `S` | `S` `O` |
| Schreib-/Lesezugriff ändern | `S` `O` | – | – |
| Besitzer\*innen ändern | `S` `O` | `S` | `S` |
| Ressource löschen | `S` `O` | – | – |
| Veröffentlichung vorschlagen | `S` `O` | – | – |
| Vorschlag zurückziehen | – | `S` `O` | – |
| Ressource veröffentlichen | – | `S` | – |
| Veröffetnlichung zurückziehen | – | – | `S` |
