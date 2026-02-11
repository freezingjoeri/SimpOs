SimpOs – Text-based Experimental OS
===================================

SimpOs is a lightweight, purely text-based "fake OS" that runs in a terminal.
It is designed with an old-school DOS/UNIX feeling and a modern hacker aesthetic.

This repository contains a Python implementation that you can run locally,
embed in a minimal Linux VM, or extend with your own AI.


Quick start – Windows
---------------------

1. Open een terminal in de map waar `main.py` staat (bijv. `SimpOs`).

2. Maak een virtualenv en installeer dependencies:

   ```bash
   cd SimpOs
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start SimpOs:

   ```bash
   python main.py
   ```

4. Eerste keer opstarten:

   - Je ziet het boot‑logo en daarna een **First time setup** wizard.
   - Vul je **naam** in (owner van het systeem).
   - Kies een **admin‑code** (tweemaal invoeren om te bevestigen).
   - Deze gegevens worden opgeslagen in `simp_config.json`.

5. Daarna kom je in de **login**:

   - Normale user: typ een willekeurige username die **niet** `admin` is.
   - Admin: username `admin`, admin‑code die je net gekozen hebt.


One-command install op Linux (via GitHub)
-----------------------------------------

Dit voorbeeld is geschreven voor **Ubuntu Server** (22.04/24.04), maar werkt
ook op de meeste andere Debian‑achtige distro’s.

1. Installeer basis‑tools (éénmalig, als ze nog niet staan):

   ```bash
   sudo apt update
   sudo apt install -y git python3 python3-venv
   ```

2. Haal SimpOs binnen en start het install‑script  
   (stap voor stap, exact zo intypen):

   ```bash
   # 1) Repo ophalen (maakt map 'SimpOs' of 'simpos')
   git clone https://github.com/freezingjoeri/SimpOs.git

   # 2) Naar de projectmap gaan waar main.py staat
   cd SimpOs          # of cd simpos, afhankelijk van de mapnaam op jouw systeem

   # 3) Install‑script draaien
   bash install_linux.sh
   ```

   - Als `cd SimpOs` een fout geeft, doe dan eerst `ls` om de exacte
     mapnaam te zien en gebruik die (bijv. `simpos`).
   - Het script draait altijd in de map waar het zelf staat en zoekt
     niets meer in `~/SimpleOs` of andere paden.

2. Het script:

   - maakt een virtualenv,
   - installeert de dependencies,
   - zet auto‑start in `~/.bash_profile` of `~/.profile`:

     ```bash
     cd "$HOME/SimpOs" && source .venv/bin/activate && python main.py
     ```

3. Daarna start SimpOs **automatisch** zodra je inlogt op die Linux shell (bijv. in een VirtualBox‑VM).


Handmatig updaten op Ubuntu (zonder menu)
-----------------------------------------

Je kunt altijd zelf updaten via git (bijvoorbeeld als het settings‑menu nog
niet beschikbaar is):

```bash
cd SimpOs   # of de map waar je project staat
git pull --ff-only
```

Als je een andere remote gebruikt (fork, eigen repo), pas dan de URL aan:

```bash
cd SimpOs   # of de map waar je project staat
git remote set-url origin https://github.com/<jouw-gebruiker>/<jouw-repo>.git
git pull --ff-only
```

Configuratiebestanden zoals `simp_config.json` blijven hierbij staan; alleen
de code die onder git valt wordt bijgewerkt.


Home‑scherm & navigatie
-----------------------

Na inloggen zie je het **home‑scherm** met het SimpOs‑logo en een lijst opties.
Gebruik **pijltjes (↑/↓)** en **ENTER** om te kiezen:

- **Open command line** – gaat naar de klassieke prompt `user@SimpOs:~$`.
- **Settings** – opent het instellingenmenu:
  - *Server / OS info* – toont info over Ubuntu/Linux/Windows, kernel, Python, load, tijd.
  - *Check for updates* – kijkt of de GitHub‑remote bereikbaar is en of er nieuwe commits zijn.
  - *Update from GitHub* – haalt de laatste versie op met `git pull` (alleen admin).
- **Admin tools** – admin‑menu (ook met pijltjes):
  - Security logs bekijken.
  - API‑key instellen.
  - Online AI aan/uit.
  - Huidige config tonen.
- **AI console** – direct een vraag aan SimpAI stellen.
- **Shutdown** – SimpOs afsluiten.
- **Reboot** – SimpOs opnieuw opstarten.

In de command‑line zelf kun je nog steeds handmatig commands typen:

- `help`, `status`, `ai`, `netstat`, `whoami`, `admin`, `settings`, `apps`, `home`, `reset`, `reboot`, `shutdown`, enz.


Apps manager
------------

SimpOs heeft een eenvoudige **apps manager**:

- De apps staan in de map `apps/` in de projectroot.
- Gebruik het home‑menu → **Apps**, of typ `apps` in de command‑line.
- In het apps‑menu kun je:
  - alle apps zien die in `apps/` staan;
  - een app starten (Python‑scripts `*.py` via `python`, andere bestanden via `bash`);
  - een **custom install command** uitvoeren in de `apps/` map om extra tools te installeren
    (bijvoorbeeld een script downloaden of een klein programma neerzetten).

Let op: install‑commando’s draaien als de huidige Linux‑user. Voer hier alleen
commando’s uit die je vertrouwt.

Stubs for future features:

- `mkdir`, `touch`, `ls` – placeholders voor een toekomstige virtuele filesystem‑laag.


Admin & configuratie
--------------------

Configuratie staat in `simp_config.json` (wordt bij eerste run aangemaakt).

- Tijdens de **First time setup** kies je je eigen admin‑code.
- Alleen admin kan:
  - Security logs bekijken (via `admin`).
  - API‑key instellen of leegmaken.
  - Online AI aan/uit zetten.
  - GitHub‑URL voor updates instellen (via `settings` → *Update from GitHub*).
  - **Factory reset** uitvoeren (via `settings` → *Factory reset* of het `reset`‑commando).
    - Hierbij moet je **nogmaals** de admin‑code invullen én `RESET` typen.

Logo aanpassen
--------------

Het ASCII‑logo dat je ziet bij de boot‑sequence en op het home‑scherm staat in
het bestand `simp_logo.txt` in de projectroot.

- Pas dat bestand aan met je eigen ASCII‑art.
- Bij de volgende start of zodra het home‑scherm wordt getekend, gebruikt
  SimpOs automatisch de nieuwe versie van het logo.


Adding your own AI (important)
------------------------------

SimpAI supports two modes:

- Local/offline: hard-coded answers, no internet.
- Online: hook for your own AI API.

To plug in your own AI:

1. Open `simp_os/ai.py`.
2. Locate the `_handle_online()` method.
3. Replace the placeholder body with your API integration, for example:

   ```python
   import requests  # or openai, etc.

   def _handle_online(self, question: str) -> None:
       if not (self.cfg.allow_online_ai and self.cfg.api_key):
           print_colored("ACCESS DENIED – ADMIN CODE REQUIRED or API key missing.", color=ERROR)
           return

       headers = {"Authorization": f"Bearer {self.cfg.api_key}"}
       # Call your API here and print the response:
       response_text = "... result from your API ..."
       print_colored(response_text, color=AI_COLOR)
       self.status.last_action = "online_answer"
   ```

4. Run SimpOs, log in as admin, run `admin` and:

   - Option 2: set your API key.
   - Option 3: enable online AI.
   - Then run `ai online` to switch the mode.


Running inside a VM / ISO idea
------------------------------

This project itself is a terminal program, not a full kernel.
To run it from an ISO in a VM (VirtualBox, etc.), you can:

1. Take a tiny Linux distribution (TinyCore, Alpine, Debian netinst, etc.).
2. Install Python and copy this `SimpOs` folder into the VM.
3. Configure the system to auto-start SimpOs after boot, for example by:
   - Adding `python /path/to/SimpOs/main.py` to `.bash_profile` or
   - Creating a systemd service that runs on TTY login.
4. Use the tools of that distribution (`genisoimage`, `mkisofs`, `xorriso` or
   `virt-manager` tools) to create a bootable ISO from that VM disk/image.

The exact commands depend on the Linux distro you choose; once you pick one,
you can ask the assistant for a distro-specific ISO recipe.


Project structure
-----------------

- `main.py` – entry point.
- `simp_os/kernel.py` – boot sequence, logo, command loop.
- `simp_os/command_parser.py` – command routing.
- `simp_os/auth.py` – user login and admin verification.
- `simp_os/security.py` – security logs and failed login counter.
- `simp_os/ai.py` – SimpAI implementation and API hooks.
- `simp_os/config.py` – config loading/saving (admin code, AI mode, API key).
- `simp_os/utils.py` – colors, typing effect, helpers.
- `requirements.txt` – Python dependencies.
- `simp_config.json` – generated runtime config.


Future expansion hooks
----------------------

The code already reserves commands and structure for:

- Virtual filesystem simulation (`mkdir`, `touch`, `ls`).
- Package installer and module system.
- Network scanner and hacker-style educational tools.
- Encrypted storage.

You can add new commands by registering them in
`CommandParser._register_builtin_commands()` and implementing their handlers.





ubuntu server:
als het niet werkt zoals het hier boven staat doe dan dit:

cd SimpOs/SimpleOs
sed -i 's/\r$//' install_linux.sh
chmod +x install_linux.sh
./install_linux.sh
daarna reboot


