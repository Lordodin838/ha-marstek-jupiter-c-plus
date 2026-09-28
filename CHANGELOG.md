# Changelog

## 1.2.1

Das Repository heißt jetzt `ha-marstek-jupiter-c-plus` — HACS nimmt keine Repository-Namen auf, die "HACS" enthalten. `documentation` und `issue_tracker` im Manifest sowie die Links in beiden READMEs zeigen auf den neuen Namen. Am Code der Integration ändert sich nichts. Alte Links leiten weiter, ein manuelles Eingreifen ist nicht nötig.

The repository is now called `ha-marstek-jupiter-c-plus` — HACS does not accept repository names containing "HACS". The `documentation` and `issue_tracker` URLs in the manifest and the links in both READMEs point to the new name. No functional change. Old links keep redirecting, nothing to do on your side.

---

## 1.2.0

Erste reguläre Version der 1.2er-Reihe, inhaltlich identisch mit 1.2.0b2: die beiden Sensoren für Batterie-Ladeleistung und -Entladeleistung, `entry_id` für die Dienste, Testsuite auf pytest, CI auf Python 3.11 und 3.12, MQTT-Fehler-Fallback entfernt, Temperaturwerte unter 5 °C werden nicht mehr verworfen, Mindestversion Home Assistant 2024.11.0. Die vollständige Auflistung mit Begründungen steht im Abschnitt 1.2.0b2 weiter unten.

Same content as 1.2.0b2, promoted to a stable release: battery charge and discharge power sensors, `entry_id` for the services, pytest test suite, CI on Python 3.11 and 3.12, MQTT error fallback removed, temperature readings below 5 °C no longer discarded, minimum Home Assistant version 2024.11.0. See the 1.2.0b2 section below for the full list.

---

## 1.2.0b2

### New

- **Battery charge power and battery discharge power:** two sensors derived from
  *Battery power (calculated)*. *Charge power* is positive while the battery charges
  (zero otherwise), *discharge power* positive while it discharges. Both report W with
  the `power` device class and go straight into the Energy dashboard.

### Improved

- **Services `register_dump` and `read_register`** carry full names and descriptions and
  take an optional `entry_id` that selects the instance when more than one Jupiter is
  set up. With a single instance nothing changes.
- **Test suite moved to pytest:** ten files covering the register map, decoding, the
  coordinator, the sanity filter, sensors, services, diagnostics, the error watcher and
  the TCP transport.
- **CI workflow** runs pyflakes and the full suite on Python 3.11 and 3.12 in parallel.
- **Dependabot** checks GitHub Actions versions weekly.

### Fixed

- **Temperature was discarded below 5 °C.** The plausibility range for `0x000E` started
  at 5.0 °C, so in a cold garage or outdoors every winter reading was thrown away and the
  sensor silently kept showing the last autumn value. The range now starts at 0.0 °C.
  Whether the register counts below zero as int16 is still open — readings taken in frost
  are welcome in an issue.
- **The two new power sensors would have lost their names.** They were added to the
  translation files by hand but were missing from `build_translations.py`, so the next run
  of the generator would have deleted them and every entity would have fallen back to the
  device name. Both are in the generator now, and a test checks that every entity has a
  name in every language.
- **Minimum Home Assistant version corrected** from 2024.8.0 to 2024.11.0. The integration
  uses `entry.runtime_data`, passes `config_entry` to the coordinator and relies on the
  options flow providing `config_entry` itself — on 2024.8 the setup fails instead of
  reporting a version that is too old.

### Removed

- **MQTT error fallback option:** the "MQTT error sensor as second source" field is gone
  from the options, and so is the code behind it. Error codes are read exclusively over
  Modbus, which makes the integration fully local. The trade-off: a very short fault can
  slip through between two polls. Lower the polling interval or act on the
  `marstek_jupiter_error` event if that matters to you.

### Note

1.2.0b1 was cut from a tree that did not yet contain the services, test suite and CI work
described in its release notes. Everything listed there ships with this version.

---

### Deutsch

#### Neu

- **Batterie Ladeleistung und Batterie Entladeleistung:** zwei Sensoren, abgeleitet aus
  *Batterieleistung (berechnet)*. *Ladeleistung* ist positiv, solange die Batterie lädt
  (sonst null), *Entladeleistung* positiv, solange sie entlädt. Beide liefern W mit der
  `power`-Device-Klasse und lassen sich direkt im Energie-Dashboard verwenden.

#### Verbessert

- **Dienste `register_dump` und `read_register`** haben vollständige Namen und
  Beschreibungen und nehmen ein optionales `entry_id`, das bei mehreren eingerichteten
  Jupiter die gemeinte Instanz auswählt. Mit einer Instanz ändert sich nichts.
- **Testsuite auf pytest umgestellt:** zehn Dateien für Registerkarte, Dekodierung,
  Coordinator, Plausibilitätsfilter, Sensoren, Dienste, Diagnose, Fehlerbeobachter und
  TCP-Transport.
- **CI-Workflow** führt pyflakes und die volle Suite parallel auf Python 3.11 und 3.12 aus.
- **Dependabot** prüft wöchentlich die Versionen der GitHub Actions.

#### Behoben

- **Temperatur wurde unter 5 °C verworfen.** Die Plausibilitätsgrenze für `0x000E` begann
  bei 5,0 °C. Steht das Gerät kalt, wurde damit den ganzen Winter jeder Messwert verworfen,
  und der Sensor zeigte unbemerkt weiter den letzten Herbstwert. Die Grenze beginnt jetzt
  bei 0,0 °C. Ob das Register unter null als int16 weiterzählt, ist offen — Messwerte bei
  Frost gerne als Issue.
- **Die zwei neuen Leistungssensoren hätten ihre Namen verloren.** Sie waren von Hand in
  die Übersetzungsdateien eingetragen, fehlten aber in `build_translations.py`; der nächste
  Lauf des Generators hätte sie gelöscht, und dann fällt jede Entität auf den Gerätenamen
  zurück. Beide stehen jetzt im Generator, und ein Test prüft, dass jede Entität in jeder
  Sprache einen Namen hat.
- **Mindestversion von Home Assistant korrigiert**, von 2024.8.0 auf 2024.11.0. Die
  Integration nutzt `entry.runtime_data`, übergibt `config_entry` an den Coordinator und
  verlässt sich darauf, dass der Options-Flow `config_entry` selbst mitbringt — auf 2024.8
  scheitert die Einrichtung, statt eine zu alte Version zu melden.

#### Entfernt

- **MQTT-Fehlercode-Fallback:** das Optionsfeld „MQTT-Fehlersensor als zweite Quelle" ist
  entfallen, und mit ihm der Code dahinter. Fehlercodes werden ausschließlich über Modbus
  gelesen, die Integration ist damit vollständig lokal. Der Preis: ein sehr kurzer Fehler
  kann zwischen zwei Abfragen durchrutschen. Wen das stört, setzt den Abfragetakt herunter
  oder wertet das Ereignis `marstek_jupiter_error` aus.

#### Hinweis

1.2.0b1 wurde aus einem Stand gebaut, der die in den Release-Notes beschriebene Arbeit an
Diensten, Testsuite und CI noch nicht enthielt. Alles, was dort steht, ist mit dieser
Version tatsächlich enthalten.

---

## 1.2.0b1

Enthielt tatsächlich nur die beiden neuen Leistungssensoren und Dependabot. Die übrigen
Punkte der Release-Notes kamen erst mit 1.2.0b2 ins Repository.

---

## 1.1.0

- Energiezähler: PV Energie, Batterie geladen/entladen
- Status- und Diagnose-Entitäten entfernt
- TCP-Reconnect-Logik verbessert

## 1.0.1

- Bugfix: Setup-Fehler (NameError entry)

## 1.0.0

- Erste stabile Version
