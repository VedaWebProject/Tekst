# Schnellsuche

Die Schnellsuche ist einen Volltextsuche über alle verfügbaren Ressourcen der [ausgewählten Texte](#texte). Welche Ressourcen für die Schnellsuche verfügbar sind, hängt von Ihren Zugriffsrechten und dem Typ sowie der Konfiguration der Ressourcen ab.

## Operatoren

- `+` für UND-Verknüpfung
- `|` für ODER-Verknüpfung
- `-` negiert ein einzelnes Token
- `"` umschließt eine Sequenz von Token, um eine Phrase für die Suche zu kennzeichnen
- `*` am Ende eines Begriffs für eine Präfix-Suche
- `(` und `)` kennzeichnen den Vorrang von Suchoperatoren
- `~N` nach einem Wort für Editierdistanz (Unschärfe), wobei `N` eine Ziffer ist
- `~N` nach einer Phrase für den Wortabstand, wobei `N` eine Ziffer ist

## Einstellungen

### Texte
Legt fest, welche Texte durchsucht werden. Standardmäßig werden alle verfügbaren Texte ausgewählt. Diese Einstellung wird automatisch zurückgesetzt, wenn Sie Ihren Arbeitstext ändern.

### Alle Begriffe müssen vorkommen
Mit "_Alle Begriffe müssen vorkommen_" lässt sich bestimmen, wie einzelne Suchbegriffe logisch miteinander verknüpft sein sollen. Ist die Funktion aktiviert, werden ausschließlich Belegstellen mit Inhalten gefunden, in denen alle eingegebenen Suchbegriffe vorkommen. Andernfalls werden die Fundstellen mit den meisten Treffern einen höheren Rang in den Suchergebnissen erhalten, also solche mit weniger Treffern.

### Interpretiere Reguläre Ausdrücke
Die Schnellsuche kann Suchanfragen mit einem Regulären Ausdruck verarbeiten. Diese Funktion **deaktiviert die oben aufgelisteten Standard-Suchoperatoren**!

Der Ausdruck _muss_ in jedem Fall einem ganzen Term entsprechen – benutzen Sie also keine entsprechenden Anker (`^` am Anfang und `$` am Ende des Ausdrucks). Eine Übersicht über die verfügbare RegExp-Syntax ist in der [Dokumentation von Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/regexp-syntax.html) zu finden.

### Berücksichtige Diakritika
Ist diese Funktion aktiviert, werden eingegebene oder fehlende (!) Diakritika bei der Suche berücksichtigt und nur Inhalte mit derselben Verwendung von Diakritika gefunden.
