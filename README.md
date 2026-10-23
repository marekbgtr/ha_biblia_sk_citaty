# Biblia.sk – Jeruzalemská Biblia pre Home Assistant

Neoficiálna vlastná integrácia pre HACS. Načíta slovenský Botekov preklad
z verejnej stránky Biblia.sk. Bez API kľúča, bez úpravy configuration.yaml.
Verzia 0.1.0 je prvá skúšobná verzia, nie oficiálny produkt Biblia.sk.

## Nahratie na GitHub z pracovného PC

1. Vytvor nový **verejný** repozitár, napríklad `ha-biblia-sk`.
2. Rozbaľ ZIP. V GitHube zvoľ **Add file → Upload files** (v prázdnom repozitári odkaz **uploading an existing file**).
3. Nahraj **obsah** priečinka `ha-biblia-sk`, vrátane celého `custom_components`.
   V koreni repozitára musí byť `hacs.json`, `README.md` a `custom_components`.
   Nenahrávaj samotný ZIP ani vonkajší priečinok ako ďalšiu úroveň.
4. Ulož cez **Commit changes**. GitHub Pages netreba zapínať.
5. Pri verejnej údržbe zmeň v `custom_components/biblia_sk/manifest.json`
   `documentation` na URL svojho repozitára, `issue_tracker` na jeho `/issues`
   a `codeowners` na svoje GitHub meno v tvare `["@meno"]`.
   Predvolené odkazy smerujú na zdroj textu a všeobecný zoznam GitHub issues.

## Inštalácia cez HACS

1. HACS → menu ⋮ → **Custom repositories / Vlastné repozitáre**.
2. Vlož URL vytvoreného repozitára. Typ: **Integration / Integrácia**.
3. Vyhľadaj **Biblia.sk – Jeruzalemská Biblia**, stiahni a reštartuj HA.
4. **Nastavenia → Zariadenia a služby → Pridať integráciu → Biblia.sk**.
5. Ponechaj pripravený zoznam úryvkov a potvrď. Pri prvom nastavení musí fungovať internet.

Vznikne senzor `sensor.biblicky_citat`. Ak tento názov už existuje (napríklad
z pôvodného command_line riešenia), HA pridá príponu. Skutočný názov skontroluj
v zozname entít a použi ho v karte. Starý skript nie je pre integráciu potrebný.

## Čo integrácia robí

- Stav entity: krátky biblický odkaz.
- Atribúty: `text`, `preklad`, `url`, `datum`, `aktualne`.
- Každý deň vyberie jednu položku zo zoznamu podľa dátumu v časovom pásme HA.
- Sedem predvolených úryvkov sa opakuje po siedmich dňoch. Nie je to oficiálny
  verš dňa, náhodný výber ani liturgické čítanie.
- Kontrola každých 15 minút; po úspešnom načítaní iba lokálna cache, ďalšia
  HTTP požiadavka až ďalší deň. Nový deň sa prejaví do 15 minút.
- Cache prežije reštart HA. Pri výpadku ostane posledný citát s `aktualne: false`;
  integrácia opakuje pokus každých 15 minút.
- Ak ešte žiadnu cache nemá, HA opakuje neúspešné spustenie integrácie.
- Nastavenie/úprava zoznamu vykoná navyše jednu HTTP požiadavku na kontrolu
  prvého úryvku. Ostatné úryvky sa overia až v deň ich načítania.
- Zmena zoznamu zneplatní starú cache; pre nový zoznam treba internet.

## Zmena výberu bez YAML

V **Nastavenia → Zariadenia a služby → Biblia.sk → Konfigurovať** uprav zoznam.
Jeden úryvok na riadok, napríklad:

```text
mk 1:14-15
mt 11:28-30
1kor 13:4-7
```

Skratka knihy musí zodpovedať URL na Biblia.sk: napríklad `/bot/mk/1` → `mk`.
Jeden verš možno zapísať `mk 1:15`. Podporovaných je najviac 366 položiek a
50 súvisiacich veršov na položku. Znenie textov nie je súčasťou repozitára.

## Zobrazenie na dashboarde

V detaile entity sa celý text nachádza medzi atribútmi. Pre pohodlné zobrazenie
pridaj kartu **Markdown** a vlož obsah `examples/dashboard.yaml` do jej editora.
Toto je iba nastavenie karty, nie konfigurácia integrácie či súborov HA.

## Obmedzenia a odinštalovanie

Číta sa HTML webu, nie stabilné verejné API. Zmena stránky môže vyžadovať opravu.
Integrácia neobchádza prihlásenie a nestiahne celú Bibliu. Texty a prípadné práva
k prekladu patria ich držiteľom; licencia zdrojového kódu sa na ne nevzťahuje.
Používaj citáty s uvedením zdroja. Neposiela sa žiadny token ani informácia o HA;
Biblia.sk vidí bežnú HTTP požiadavku vrátane verejnej IP.

Odstráň integráciu v Zariadeniach a službách (zmaže jej cache), potom ju odstráň
z HACS a reštartuj HA. Nezasahuje do iných entít ani konfigurácií.

## Testy

`python -m unittest discover -s tests -v` v prostredí s Home Assistantom.
Testy používajú syntetický text a simulované odpovede; živé texty nie sú uložené
v repozitári. Konkrétny rozsah overenia je v `TESTOVANIE.md`.
