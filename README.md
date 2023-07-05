# pocket-assistant
Sorting tools for Analogue Pocket

Prerequisites
-> The pocker_updater.exe utility from https://github.com/mattpannella/pocket-updater-utility/releases, to be placed in Updater, the same folder as this program
-> The image processor, downloaded from https://github.com/agg23/Analogue-Pocket-Image-Process/tree/master, to be placed in Updater/_assistantimages/Analogue-Pocket-Image-Process-master - note: this requires a node.js installation from https://nodejs.org/en/download

Features
-> Asset cleaning: When you download or update a core that comes with JSON files, this will hide the JSONs you don't want automatically. For example, although a core may specify that the US version of a game is the primary version, and the World version is an alternative version, this program can take the World version
-> Core cloning: When you have a core with multiple JSON files, this will make copies of the core so each JSON has its own core. (This requires asset cleaning to be enabled.)
-> Autostart: For all supported JSON-reliant cores - which is most of them - if you only have one JSON file in the directory, this will make the core automatically load it. (This requires asset cleaning to be enabled.)
-> Platform cleaning: When you download a core with an unusual category, this will prompt you for help putting it in the right place. This is primarily for use with Jotego's cores.
-> Video setting correction: This will integer scale all cores, except for any you tell us not to, and also rotate cores in 90 degree increments.
-> Rename core platforms: This will change the associated platform for any core you ask us to. For example, you may want to link the Spiritualized NES core with the Famicom Disk System platform - this will handle changing that every time the core updates.
-> Generate favourite cores: This will create copies of cores that automatically start a specific game you want. For example, it can copy the agg23 SNES core, and rename it to be a dedicated Super Metroid core that automatically boots the game and preserves your save data from the normal core too.
-> Generate alt cores: This will create alternate versions of cores. For example, you may want a TATE version of certain arcade cores, or a version of the Spiritualized Super Game Boy core that uses the Super Game Boy 2 BIOS. This would then allow you to switch between the two versions on your device, without having to manually change the settings with a computer.

Top tips!
-> If you want a TATE version of, for instance, the 
