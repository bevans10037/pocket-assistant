# Pocket Assistant! :)
## Sorting tools for Analogue Pocket

This is a program I've written to help me clean up my own Analogue Pocket's SD card. It can do a few different jobs that I think are useful (see the Features section below), and I hope you find at least one of them useful too!

### Guide
- Download Updater/pocket_assistant.py, and place it on your Analogue Pocket's SD card (also in a folder called Updater).
- Ensure all prerequisites are also downloaded and, if applicable, in the right place (see the Prerequisites section below).
- (Optional) You can also download the update.bat file, which will automatically run pocket_updater.exe and pocket_assistant.py for you - put this on the root of the SD card!

### Prerequisites
- Python 3, from https://www.python.org/
- The Python library Pillow, from https://pillow.readthedocs.io/en/stable/installation.html
- The pocker_updater.exe utility from https://github.com/mattpannella/pocket-updater-utility/releases, to be placed in Updater, the same folder as this program
- node.js, from https://nodejs.org/en/download
- The image processor, downloaded from https://github.com/agg23/Analogue-Pocket-Image-Process/tree/master, to be placed in Updater/_assistantimages/Analogue-Pocket-Image-Process-master

### Features
- Asset cleaning: When you download or update a core that comes with JSON files, this will hide the JSONs you don't want automatically, and rename the ones you do to anything you like. For example, although the jtaliens core may specify that the primary version of Crime Fighters is the "Crime Fighters (World 2 players)" JSON file, and this program can instead move that JSON to a separate folder for unused games, then take the "Crime Fighters (US 4 players)" json from the "_alternatives" folder, and rename it to "Crime Fighters" in the main folder. It will even repeat this every time the core gets updated!
- Core cloning: When you have a core with multiple JSON files, this will make copies of the core so each JSON has its own core. (This requires asset cleaning to be enabled.)
- Autostart: For all supported JSON-reliant cores - which is most of them - if you only have one JSON file in the directory, this will make the core automatically load it. (This requires asset cleaning to be enabled.)
- Platform cleaning: When you download a core with an unusual category, this will prompt you for information to fill in its platform data yourself. This is primarily for use with Jotego's cores.
- Video setting correction: This will integer scale all cores, except for any you tell us not to, and also rotate cores in 90 degree increments.
- Rename core platforms: This will change the associated platform for any core you ask us to. For example, you may want to link the Spiritualized NES core with the Famicom Disk System platform, or the Jotego jtcps1 core with the CPS1 platform - this will handle changing that every time the core updates.
- Generate favourite cores: This will create copies of cores that automatically start a specific game you want. For example, it can copy the agg23 SNES core, and rename it to be a dedicated Super Metroid core that automatically boots the game, accessing the same save data file as the normal core too.
- Generate alt cores: This will create alternate versions of cores. For example, you may want a TATE version of certain arcade cores, or a version of the Spiritualized Super Game Boy core that uses the Super Game Boy 2 BIOS. This would then allow you to switch between the two versions on your device, without having to manually change the settings with a computer.

### Top tips!
- If you want a separately selectable TATE version of, for instance, the pram0d garegga core, you should use both the alt core generator and the video setting correction tools together. Include the entry "pram0d.garegga-TATE":"pram0d.garegga" in "altCoreList" in the core_data.json so the program will maintain a copy of the core under that name, and then include the name given in the platform JSON for garegga in "rotateBy90" or "rotateBy270" (depending on which way you want the screen to be rotated), and put "pram0d.garegga" in "useOriginalRatio". This will rotate any core connected to the garegga platform, excluding the original core.
- Be careful with how many separate platforms you have on your system at one time. As of firmware version 1.1, I found that, at around 250 JSON files in the Platforms/ folder (even though most of these weren't linked to any existing cores, and I'd just copied them over from the Spiritualized platform pack), some cores started to be skipped from the openFPGA list. This may become an issue with core cloning and favourite cores both being turned on.
