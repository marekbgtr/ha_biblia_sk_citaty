# Overenie verzie 0.1.0

Overené 23. 10. 2026:

- Python 3.13.16 a Home Assistant Core 2025.4.4 v izolovanom testovacom prostredí.
- 11 automatických testov: spracovanie HTML a odkazov, neplatné vstupy, denná
  cache, zmena dátumu, výpadok bez cache, stará cache a obnova, zneplatnenie
  cache po zmene zoznamu, dlhý text v atribúte a validácia formulára.
- Skutočný HA flow manager: konfiguračný formulár, vytvorenie entity,
  formulár možností, zmena zoznamu, reload a unload. HTTP odpovede simulované.
- Samostatne živé načítanie všetkých siedmich predvolených úryvkov z Biblia.sk
  s rovnakým parserom. Všetkých sedem obsahovalo požadované verše.
- Kontrola syntaxe Python súborov a načítania JSON metadát.

Príkazy z koreňa repozitára, s nainštalovaným Home Assistantom:

```sh
python -m unittest discover -s tests -v
python tests/smoke.py
```

Neoverené: inštalácia zo skutočného GitHub repozitára cez HACS, reálny HAOS
na Raspberry Pi a novšie verzie HA. Ide o prvú skúšobnú verziu, nie certifikovanú
integráciu. Nezávisí od Supervisoru ani od konkrétneho hardvéru.
