# Info-Seiten

Info-Seiten geben Ihnen die Möglichkeit, Ihren Nutzer\*innen zusätzliche, statische Informationen zur Verfügung zu stellen. Diese können mehrsprachig angelegt und bei Bedarf nur bestimmten Nutzer\*innengruppen zugänglich gemacht werden.

## Eine neue Seite anlegen

Klicken Sie oben rechts auf das Plus-Symbol, um eine neue Seite anzulegen. Der **Titel** einer Seite wird automatisch als Überschrift ersten Ranges über dem Inhalt der Seite angezeigt.

Der **Schlüssel** ist eine kurze Zeichenfolge, die die Seite im System identifiziert. Wenn Sie eine Seite in mehreren Sprachen anlegen wollen, müssen die Schlüssel der verschiedenen Versionen identisch sein. So kann das System die verschiedenen Versionen einer Seite als eine Einheit behandeln und je nach Spracheinstellung der Nutzer\*innen die richtige Version anzeigen.

Unter "**Anzeigen für**" können Sie festlegen, welcher Grupe von Nutzer\*innen die Seite angezeigt werden soll. Standardmäßig wird eine neue Seite allen Nutzer\*innen – auch nicht angemeldeten – angezeigt.

Mit dem numerischen Wert unter **Sortierreihenfolge** können Sie festlegen, in welcher Reihenfolge die Infoseiten in der Navigation aufgeführt werden sollen.

## Inhalt einer Seite bearbeiten

### Visueller Editor

Der visuelle Editor bietet Ihnen die Möglichkeit, den Inhalt einer Seite mit Hilfe von grafischen Werkzeugen zu formatieren. Auf diese Weise sind Inhalte leicht wartbar und bleiben automatisch an das Design der Seite angepasst.

### HTML-Editor

Falls Sie speziellen HTML-Code einbauen möchten, können Sie den HTML-Editor nutzen. Hier können Sie den HTML-Quellcode der Seite direkt selbst bearbeiten. Bitte beachten Sie, dass Sie dabei auf korrekte Syntax achten müssen. Legen Sie außerdem **kein komplettes HTML-Dokument** an, sondern lediglich den Inhalt des `<body>`-Tags. Dieser wird dann vom System in die bestehende Seite eingebunden.

Bitte beachten Sie, dass beim Wechsel zurück zum visuellen Editor alle HTML-Tags und -Attribute aus dem HTML-Editor entfernt werden, die dem visuellen Editor nicht bekannt sind. Dies kann zu einem Verlust von Inhalten und Formatierungen führen. Bitte nutzen Sie daher den HTML-Editor nur, wenn Sie sich mit HTML auskennen und sich sicher sind, dass Sie den Quelltext selbst verfassen möchten.

### Grafiken

Grafiken werden in Form von bestehenden URLs eingefügt. Es können keine Grafiken hochgeladen werden. Sie müssen also ggf. zunächst dafür sorgen, dass Ihre Grafiken auf einem Server liegen, von dem aus sie eingebunden werden können. Dafür können sie auch den speziellen Ordner für statische Dateien nutzen, der von Tekst automatisch eingebunden wird. Lesen Sie dazu mehr in der Deployment-Anleitung im [Tekst-Handbuch](https://vedawebproject.github.io/Tekst/).

## Eine bestehende Seite bearbeiten

Wählen Sie im Auswahlfeld einfach die Seite aus, die Sie bearbeiten möchten. Die Bearbeitungsmaske wird dann automatisch eingeblendet.
