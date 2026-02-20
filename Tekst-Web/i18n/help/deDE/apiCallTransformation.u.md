# Transformation für Daten aus API-Abfragen

Der Ressourcentyp "API-Abruf" fügt Inhalte als HTML in die Seite ein. Wenn die API, bei der die Daten abgefragt werden, jedoch kein HTML ausliefert – denn das ist selten der Fall, eher werden Daten z.B. als JSON ausgeliefert – dann müssen diese Daten zunächst zu HTML transformiert werden. Dies geschieht mit Hilfe einer JavaScript-Transformationsfunktion, die Sie hier definieren können.

## Die Transformationsfunktion

Die Transformationsfunktion muss die Daten, die von der API zurückgegeben wurden, transformieren und einen HTML-String zurückgeben, der als Inhalt gerendert werden kann.

⚠️ **WICHTIG:** Fügen Sie als Transformationsfunktion ausschließlich einen **Funktionskörper** ein, also **keine gesamte Funktionsdeklaration** mit Argumenten! Der Funktionskörper muss einen HTML-String mittels eines `return`-Statements zurückgeben. Innerhalb des Funktionskörpers haben Sie automatisch Zugriff auf die im Folgenden beschriebenen Variablen.

### `this.data`

Über den Identifier `this.data` haben Sie Zugriff auf die Daten, die von der API zurückgegeben wurden. Es handelt sich um ein **Array von Objekten** der folgenden Form:

```json
[
  {
    "key": "keyOfTheApiCall",
    "data": "{\"name\": \"foo\"}"
  },
  {
    "key": "keyOfAnotherApiCall",
    "data": "{\"name\": \"bar\"}"
  }
]
```

⚠️ **WICHTIG:** Beachten Sie, dass die Daten als String vorliegen und noch in der Transformationsfunktion geparst werden müssen! D.h. im Falle von JSON-Daten z.B. mittels `JSON.parse(this.data[0].data)`!

Für jeden API-Abruf, der im jeweiligen Inhalt der Ressource definiert ist, existiert also ein Objekt im Array `this.data`. Jedes dieser Objekte enthält den `key` des API-Abrufs und die zurückgegebenen Daten `data` als String.

### `this.context`

Die Variable `this.context` referenziert ein Objekt, das die im jeweiligen Inhalt definierten "zusätzlichen Daten für die Transformationsfunktion" enthält. Diese sind bereits mit `JSON.parse` geparst und können direkt verwendet werden.

### Beispiel für eine Transformationsfunktion

Eine einfache Transformationsfunktion, welche die JSON-Daten aus dem obigen Beispiel in HTML umwandelt, könnte z.B. so aussehen:

```
const data = this.data.map((d) => ({ ...d, data: JSON.parse(d.data) }));
return data.map((d) => `
    <h1>API-Call: ${d.key}</h1>
    <p><b>Name:</b> ${d.data.name}</p>
`).join('');
```

## Abhängigkeiten

Falls Ihre JavaScript-Transformationsfunktion Abhängigkeiten zu externen Bibliotheken hat, können Sie URLs zu diesen Bibliotheken in der Konfiguration angeben. Diese werden dann im Browser geladen und stehen der Transformationsfunktion zur Laufzeit zur Verfügung.
