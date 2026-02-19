# Seitensegmente

Seitensegmente sind Inhalte oder HTML-Snippets, die in bestimmte Bereiche der Seite eingebunden werden sollen, die außerhalb von Info-Seiten liegen. Im Prinzip funktionieren Sie aber sehr ähnlich.

## Eine neues Segment anlegen

Klicken Sie oben rechts auf das Plus-Symbol, um ein neues Segment anzulegen. Der **Titel** eines Seitensegments dient lediglich seiner Identifizierung im Backend und ist nicht für die Nutzer\*innen sichtbar. Wählen Sie den Titel deshalb so, dass sie daran später das Seitensegment gut wiedererkennen und zuordnen können.

Der **Typ** des Seitensegments bestimmt, wo und wie der Inhalt in die Oberfläche der Anwendung eingebunden wird:

- **Startseite**: Inhalt der Startseite. Ist keine Startseite angelegt, wird die Lese-Ansicht als Startseite angezeigt.
- **Ende von HTML head**: Wird ans Ende des HTML `<head>`-Tags eingebunden.
- **Ende von HTML body**: Wird ans Ende des HTML `<body>`-Tags eingebunden.
- **Seiten-Fußzeile (oberer Teil)**: Wird am Anfang der Fußzeile der Seite eingebunden.
- **Seiten-Fußzeile (unterer Teil)**: Wird am Ende der Fußzeile der Seite eingebunden.
- **Impressum**: Wird als Inhalt für das Impressum eingebunden.
- **Datenschutzerklärung**: Wird als Inhalt für die Datenschutzerklärung eingebunden.
- **Einführungstext auf Registrieren-Seite**: Stellen Sie hier Informationen zum Registrations- und Freischaltungs-Verfahren zur Verfügung. Erläutern Sie ihren Nutzer\*innen hier zum Beispiel, nach welchen Kriterien Konten vergeben werden und wie lange dies üblicherweise dauert.

Unter "**Anzeigen für**" können Sie festlegen, welcher Grupe von Nutzer\*innen das Segment angezeigt werden soll. Standardmäßig wird ein neues Segment allen Nutzer\*innen – auch nicht angemeldeten – angezeigt.

## Inhalt eines Segments bearbeiten

### Visueller Editor

Der visuelle Editor bietet Ihnen die Möglichkeit, den Inhalt mit Hilfe von grafischen Werkzeugen zu formatieren. Auf diese Weise sind Inhalte leicht wartbar und bleiben automatisch an das Design der Seite angepasst.

### HTML-Editor

Falls Sie speziellen HTML-Code einbauen möchten, können Sie den HTML-Editor nutzen. Hier können Sie den HTML-Quellcode direkt selbst bearbeiten. Bitte beachten Sie, dass Sie dabei auf korrekte Syntax achten müssen. Legen Sie außerdem **kein komplettes HTML-Dokument** an, sondern lediglich den Inhalt des `<body>`-Tags. Dieser wird dann vom System eingebunden.

Bitte beachten Sie, dass beim Wechsel zurück zum visuellen Editor alle HTML-Tags und -Attribute aus dem HTML-Editor entfernt werden, die dem visuellen Editor nicht bekannt sind. Dies kann zu einem Verlust von Inhalten und Formatierungen führen. Bitte nutzen Sie daher den HTML-Editor nur, wenn Sie sich mit HTML auskennen und sich sicher sind, dass Sie den Quelltext selbst verfassen möchten.

### Grafiken

Grafiken werden in Form von bestehenden URLs eingefügt. Es können keine Grafiken hochgeladen werden. Sie müssen also ggf. zunächst dafür sorgen, dass Ihre Grafiken auf einem Server liegen, von dem aus sie eingebunden werden können. Dafür können sie auch den speziellen Ordner für statische Dateien nutzen, der von Tekst automatisch eingebunden wird. Lesen Sie dazu mehr in der Deployment-Anleitung im Tekst-Handuch.

## Ein bestehendes Seitensegment bearbeiten

Wählen Sie im Auswahlfeld einfach das Segment aus, das Sie bearbeiten möchten. Die Bearbeitungsmaske wird dann automatisch eingeblendet.
