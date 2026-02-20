# Wartung

In dieser Ansicht können Sie den Status verschiedener Teile des Systems überwachen und nach Bedarf diverse Wartungsaufgaben durchführen.

## Suchindizes

Suchindizes sind das, was es der Anwendung ermöglicht, schnell nach bestimmten Inhalten zu suchen. Sie werden automatisch erstellt, wenn Sie neue Inhalte erstellen oder bestehende Inhalte ändern. Da es je nach Konfiguration des Systems einige Zeit dauern kann, bis neue Daten in einem Suchindex landen, kann es sein, dass die Suchindizes nicht immer aktuell sind.

In dieser Übersicht erfahren Sie Details zum Zustand der Suchindizes und können diese manuell neu erzeugen lassen.

## Vorberechnete Daten

Vorberechnete Daten sind aufwenig zu berechnende Daten, die von der Anwendung vorab erzeugt werden, um sie fertig abrufbar zu haben, wenn sie tatsächlich gebraucht werden. Sie werden automatisch erstellt, wenn Sie neue Inhalte erstellen oder bestehende Inhalte ändern. Da es je nach Konfiguration des Systems einige Zeit dauern kann, bis die Daten neu berechnet werden, kann es sein, dass die vorberechneten Daten nicht immer aktuell sind.

Zu den vorberechneten Daten gehören beispielsweise die Fundstellenabdeckung von Ressourcen und Aggregationen von Annotationsdaten.

## Interne Bereinigung

Diese Routine löscht abgelaufene Zugangstokens und Nachrichten, um die Datenbank zu bereinigen.

## Hintergrundprozesse

Viele Vorgänge mit langer Laufzeit werden als Hintergrundprozesse ausgeführt. Den Status dieser Hintergrundprozesse können Sie hier einsehen und ggf. Einträge zu beendeten oder fehlgeschlagenen Prozessen löschen.

## Email-Setup

Die eigentlichen EMail-Einstellungen können nur über die für das API-Deployment verwendeten Umgebungsvariablen geändert werden. Sie haben an dieser Stelle jedoch die Möglichkeit, das EMail-Setup zu überprüfen, indem Sie eine Test-EMail vom System an Ihre EMail-Adresse senden lassen.
