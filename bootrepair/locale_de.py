"""German message catalog (msgid -> translation). Maintained with tools/messages.py."""

MESSAGES = {
    'HKLM\\SYSTEM\\{cs}\\Services\\{service}: Start -> {start}':
        'HKLM\\SYSTEM\\{cs}\\Services\\{service}: Start -> {start}',
    "Remove broken filter '{flt}' from {class_name}":
        'Defekten Filter „{flt}“ aus {class_name} entfernen',
    'Cancel pending file replace operations':
        'Ausstehende Dateiersetzungen abbrechen',
    'Turn off Driver Verifier':
        'Treiberüberprüfung (Driver Verifier) ausschalten',
    'Cancel the pending Windows Update operation':
        'Ausstehenden Windows-Update-Vorgang abbrechen',
    'Restore \\{dst} from the component store':
        '\\{dst} aus dem Komponentenspeicher wiederherstellen',
    'Restore the {hive} hive from RegBack':
        'Registrierungsstruktur {hive} aus RegBack wiederherstellen',
    'Discard the hibernation image':
        'Ruhezustandsabbild verwerfen',
    'Point the boot entry at /dev/{target_name}':
        'Starteintrag auf /dev/{target_name} zeigen lassen',
    'Make this Windows the default boot entry':
        'Dieses Windows zum Standard-Starteintrag machen',
    'Remove {names} from the boot entry':
        '{names} aus dem Starteintrag entfernen',
    'Remove the stale boot entry':
        'Veralteten Starteintrag entfernen',
    'Remove {len(objects)} stale boot entries':
        '{len(objects)} veraltete Starteinträge entfernen',
    'Restore Windows Boot Manager files on the EFI partition':
        'Dateien des Windows-Start-Managers auf der EFI-Partition wiederherstellen',
    "Add a 'Windows Boot Manager' firmware boot entry":
        'Firmware-Starteintrag „Windows Boot Manager“ anlegen',
    'Put Boot{num} (Windows Boot Manager) first in the boot order':
        'Boot{num} (Windows Boot Manager) an den Anfang der Startreihenfolge setzen',
    'Add Boot{num} (Windows Boot Manager) to the boot order':
        'Boot{num} (Windows Boot Manager) zur Startreihenfolge hinzufügen',
    'Enable firmware entry Boot{num}':
        'Firmware-Eintrag Boot{num} aktivieren',
    'Remove stale firmware entry Boot{num}':
        'Veralteten Firmware-Eintrag Boot{num} entfernen',
    'Mark Windows Setup as completed (setup.exe = 3)':
        'Windows-Setup als abgeschlossen markieren (setup.exe = 3)',
    'HKLM\\SYSTEM\\{cs}\\Services\\{service}\\StartOverride: all values -> 0':
        'HKLM\\SYSTEM\\{cs}\\Services\\{service}\\StartOverride: alle Werte -> 0',
    "Set '{service}' to start at boot":
        '„{service}“ beim Systemstart laden',
    "Disable driver '{service}'":
        'Treiber „{service}“ deaktivieren',
    "HKLM\\SYSTEM\\{cs}\\Control\\Class\\{class_guid}\\{value}: remove '{flt}'":
        'HKLM\\SYSTEM\\{cs}\\Control\\Class\\{class_guid}\\{value}: „{flt}“ entfernen',
    'HKLM\\SYSTEM\\{cs}\\Control\\Session Manager\\PendingFileRenameOperations(2): deleted':
        'HKLM\\SYSTEM\\{cs}\\Control\\Session Manager\\PendingFileRenameOperations(2): gelöscht',
    'HKLM\\SYSTEM\\{cs}\\Control\\Session Manager\\Memory Management: delete VerifyDrivers, VerifyDriverLevel':
        'HKLM\\SYSTEM\\{cs}\\Control\\Session Manager\\Memory Management: VerifyDrivers und VerifyDriverLevel löschen',
    'Windows\\WinSxS\\pending.xml: renamed to pending.xml.bootrepair-<time> (kept)':
        'Windows\\WinSxS\\pending.xml: umbenannt in pending.xml.bootrepair-<Zeit> (bleibt erhalten)',
    'COMPONENTS hive: delete PendingXmlIdentifier, NextQueueEntryIndex, AdvancedInstallersNeedResolving':
        'COMPONENTS-Struktur: PendingXmlIdentifier, NextQueueEntryIndex und AdvancedInstallersNeedResolving löschen',
    'Windows Update installs the update again later; if it keeps failing, uninstall it from WinRE':
        'Windows Update installiert das Update später erneut; schlägt es weiter fehl, deinstallieren Sie es über die Wiederherstellungsumgebung',
    '\\{dst}: replaced with \\{src} (version {version}); the old file is backed up':
        '\\{dst}: ersetzt durch \\{src} (Version {version}); die alte Datei wird gesichert',
    'Windows\\System32\\config\\{hive}: replaced by RegBack\\{hive} ({age})':
        'Windows\\System32\\config\\{hive}: ersetzt durch RegBack\\{hive} ({age})',
    '{hive}.LOG1 / .LOG2: renamed so they are not replayed onto the restored hive':
        '{hive}.LOG1 / .LOG2: umbenannt, damit sie nicht auf die wiederhergestellte Struktur angewendet werden',
    'Settings, drivers and updates installed after that date are lost':
        'Einstellungen, Treiber und Updates, die nach diesem Datum installiert wurden, gehen verloren',
    'hiberfil.sys: renamed (or removed if the volume can only be opened that way)':
        'hiberfil.sys: umbenannt (oder gelöscht, falls sich das Volume nur so öffnen lässt)',
    'Unsaved work in the hibernated session is lost; Windows does a fresh start':
        'Nicht gespeicherte Arbeit der Ruhezustandssitzung geht verloren; Windows startet neu',
    'HKLM\\{hive}\\{path}\\{name} -> {value}':
        'HKLM\\{hive}\\{path}\\{name} -> {value}',
    'BCD {l}: device and osdevice -> /dev/{target_name}':
        'BCD {l}: device und osdevice -> /dev/{target_name}',
    'BCD {{bootmgr}} default -> {label}':
        'BCD {{bootmgr}} default -> {label}',
    'BCD {label}: delete setting {element_name(e)}':
        'BCD {label}: Einstellung {element_name(e)} löschen',
    'BCD: delete {l} and remove it from the boot menu':
        'BCD: {l} löschen und aus dem Startmenü entfernen',
    'Copy \\Windows\\Boot\\EFI\\* to \\EFI\\Microsoft\\Boot\\ on the EFI partition (BCD is kept)':
        '\\Windows\\Boot\\EFI\\* nach \\EFI\\Microsoft\\Boot\\ auf der EFI-Partition kopieren (BCD bleibt erhalten)',
    'efibootmgr -c -d {disk} -p {partnum} -L "Windows Boot Manager" -l \\EFI\\Microsoft\\Boot\\bootmgfw.efi':
        'efibootmgr -c -d {disk} -p {partnum} -L "Windows Boot Manager" -l \\EFI\\Microsoft\\Boot\\bootmgfw.efi',
    "BootOrder: {','.join(order)} -> {','.join([num] + [o for o in order if o != num])}":
        "BootOrder: {','.join(order)} -> {','.join([num] + [o for o in order if o != num])}",
    "BootOrder: {','.join(order)} -> {','.join(order + [num])}":
        "BootOrder: {','.join(order)} -> {','.join(order + [num])}",
    'efibootmgr -b {num} -a':
        'efibootmgr -b {num} -a',
    "efibootmgr -b {num} -B  ('{desc}')":
        "efibootmgr -b {num} -B  ('{desc}')",
    "HKLM\\{hive}\\{path}: delete {', '.join(names)}":
        "HKLM\\{hive}\\{path}: {', '.join(names)} löschen",
    'Disk, partition table & health':
        'Festplatte, Partitionstabelle und Zustand',
    'Windows volume (NTFS, BitLocker, hibernation)':
        'Windows-Volume (NTFS, BitLocker, Ruhezustand)',
    'Boot partition & firmware boot entries':
        'Startpartition und Firmware-Starteinträge',
    'Boot configuration data (BCD)':
        'Startkonfigurationsdaten (BCD)',
    'Boot-critical system files':
        'Startkritische Systemdateien',
    'Registry hives':
        'Registrierungsstrukturen',
    'Boot drivers, storage controller & filters':
        'Starttreiber, Speichercontroller und Filter',
    'Pending updates & setup state':
        'Ausstehende Updates und Setup-Status',
    'Crash dumps & Startup Repair logs':
        'Absturzabbilder und Starthilfe-Protokolle',
    'System event log':
        'Systemereignisprotokoll',
    'Recovery options':
        'Wiederherstellungsoptionen',
    'Windows volume not available':
        'Windows-Volume nicht verfügbar',
    'Analysis step “{tname}” failed':
        'Analyseschritt „{tname}“ ist fehlgeschlagen',
    'This part of the analysis crashed; the rest of the report is still valid.':
        'Dieser Teil der Analyse ist abgestürzt; der Rest des Berichts ist trotzdem gültig.',
    'BCD store header checksum is wrong':
        'Prüfsumme im Kopf des BCD-Speichers ist falsch',
    "The BCD hive's base block checksum does not match. Boot Manager may reject the store.":
        'Die Prüfsumme des Basisblocks der BCD-Struktur stimmt nicht. Der Start-Manager lehnt den Speicher möglicherweise ab.',
    'BCD has no {{bootmgr}} object':
        'BCD enthält kein {{bootmgr}}-Objekt',
    'The store exists but lacks the Windows Boot Manager settings, so Boot Manager does not know which entries exist or which is the default.':
        'Der Speicher existiert, aber ihm fehlen die Einstellungen des Windows-Start-Managers. Der Start-Manager weiß daher nicht, welche Einträge es gibt und welcher der Standard ist.',
    'The default boot entry does not exist':
        'Der Standard-Starteintrag existiert nicht',
    '{{bootmgr}} names a default entry that is not in the store, so there is nothing to start by default.':
        '{{bootmgr}} nennt einen Standardeintrag, der nicht im Speicher vorhanden ist; standardmäßig gibt es also nichts zu starten.',
    'BCD contains no Windows Boot Loader entry at all':
        'BCD enthält überhaupt keinen Eintrag „Windows-Startladeprogramm“',
    "The store has no entry of type 'Windows Boot Loader', so Boot Manager cannot start any Windows.":
        'Der Speicher hat keinen Eintrag vom Typ „Windows Boot Loader“, daher kann der Start-Manager kein Windows starten.',
    'No BCD entry starts the Windows on {part_label(target)}':
        'Kein BCD-Eintrag startet das Windows auf {part_label(target)}',
    "BCD entry '{o.description}' has a wrong {bad}":
        'BCD-Eintrag „{o.description}“ hat ein falsches {bad}',
    "Of the two device settings of the entry, one points to this Windows partition and the other does not. 'device' is where winload is loaded from, 'osdevice' is the Windows volume the kernel boots; both must be the Windows partition.":
        'Von den beiden Geräte-Einstellungen des Eintrags zeigt eine auf diese Windows-Partition und die andere nicht. „device“ ist der Ort, von dem winload geladen wird, „osdevice“ das Windows-Volume, das der Kernel startet; beide müssen die Windows-Partition sein.',
    'This Windows is not the default boot entry':
        'Dieses Windows ist nicht der Standard-Starteintrag',
    'The entry for this Windows is not in the boot menu':
        'Der Eintrag für dieses Windows steht nicht im Startmenü',
    'It is neither the default nor listed in the display order, so Boot Manager never offers it.':
        'Er ist weder der Standard noch in der Anzeigereihenfolge aufgeführt, daher bietet der Start-Manager ihn nie an.',
    "BCD entry '{o.description}' has no loader path":
        'BCD-Eintrag „{o.description}“ hat keinen Ladeprogrammpfad',
    'Boot Manager does not know which file to start (expected \\Windows\\system32\\{want}).':
        'Der Start-Manager weiß nicht, welche Datei er starten soll (erwartet: \\Windows\\system32\\{want}).',
    "BCD systemroot '{sysroot}' does not exist on this partition":
        'BCD-systemroot „{sysroot}“ existiert auf dieser Partition nicht',
    'The loader is told to boot Windows from a directory that is not there.':
        'Das Ladeprogramm soll Windows aus einem Verzeichnis starten, das es nicht gibt.',
    'Windows is forced into Safe Mode ({B.SAFEBOOT_NAMES.get(sb, sb)}) on every start':
        'Windows wird bei jedem Start in den abgesicherten Modus gezwungen ({B.SAFEBOOT_NAMES.get(sb, sb)})',
    'Safe Mode with Command Prompt is configured':
        'Abgesicherter Modus mit Eingabeaufforderung ist eingestellt',
    'safebootalternateshell=yes starts cmd.exe instead of Explorer.':
        'safebootalternateshell=yes startet cmd.exe statt des Explorers.',
    'Driver signature enforcement is weakened (testsigning / nointegritychecks)':
        'Die Treibersignaturprüfung ist abgeschwächt (testsigning / nointegritychecks)',
    'These options let unsigned drivers load. With Secure Boot enabled the firmware/Boot Manager rejects them and Windows reports a Secure Boot policy violation; they also indicate that an unsigned driver was installed. Secure Boot on this computer: {sbstate}.':
        'Diese Optionen lassen unsignierte Treiber laden. Bei aktivem Secure Boot lehnen Firmware bzw. Start-Manager sie ab und Windows meldet eine Verletzung der Secure-Boot-Richtlinie; außerdem deuten sie darauf hin, dass ein unsignierter Treiber installiert wurde. Secure Boot auf diesem Computer: {sbstate}.',
    'The Windows entry is marked as WinPE':
        'Der Windows-Eintrag ist als WinPE markiert',
    'winpe=yes makes winload treat the installation as a preinstallation environment.':
        'winpe=yes lässt winload die Installation wie eine Vorinstallationsumgebung behandeln.',
    'Boot logging is enabled':
        'Startprotokollierung ist eingeschaltet',
    'Windows writes C:\\Windows\\ntbtlog.txt on every boot (useful for this analysis).':
        'Windows schreibt bei jedem Start C:\\Windows\\ntbtlog.txt (nützlich für diese Analyse).',
    'Automatic Repair after failed boots is suppressed':
        'Die automatische Reparatur nach fehlgeschlagenen Starts ist unterdrückt',
    'bootstatuspolicy={B.BOOTSTATUS_NAMES.get(bsp)} hides the recovery screen, so a failing Windows just reboots in a loop.':
        'bootstatuspolicy={B.BOOTSTATUS_NAMES.get(bsp)} blendet den Wiederherstellungsbildschirm aus, ein fehlerhaftes Windows startet deshalb nur in einer Schleife neu.',
    'The BCD store is corrupt':
        'Der BCD-Speicher ist beschädigt',
    "Boot Manager cannot read its configuration and stops with 'The Boot Configuration Data for your PC is missing or contains errors'.":
        'Der Start-Manager kann seine Konfiguration nicht lesen und hält mit „Die Startkonfigurationsdaten für Ihren PC fehlen oder enthalten Fehler“ an.',
    '{{bootmgr}} device points to a partition that does not exist':
        '{{bootmgr}}-Gerät zeigt auf eine Partition, die nicht existiert',
    "Boot Manager's own device (where it loads its resources from) is not present.":
        'Das eigene Gerät des Start-Managers (von dem er seine Ressourcen lädt) ist nicht vorhanden.',
    'BCD has neither a default entry nor a boot menu':
        'BCD hat weder einen Standardeintrag noch ein Startmenü',
    'Boot Manager has no entry to start.':
        'Der Start-Manager hat keinen Eintrag, den er starten könnte.',
    'The boot configuration on {part_label(ctx.boot_part)} has Windows Boot Loader entries, but none of them points to the selected Windows partition.':
        'Die Startkonfiguration auf {part_label(ctx.boot_part)} enthält Windows-Startladeprogramm-Einträge, aber keiner zeigt auf die ausgewählte Windows-Partition.',
    'Point both settings of the entry at the Windows volume:':
        'Beide Einstellungen des Eintrags auf das Windows-Volume zeigen lassen:',
    ' The entry for this Windows (“{o.description}”) is only reached via the boot menu.':
        ' Der Eintrag für dieses Windows („{o.description}“) ist nur über das Startmenü erreichbar.',
    'Make this Windows the default entry:':
        'Dieses Windows zum Standardeintrag machen:',
    'Add the entry to the boot menu:':
        'Den Eintrag zum Startmenü hinzufügen:',
    'Set the loader path:':
        'Den Ladeprogrammpfad setzen:',
    'BCD entry uses the wrong OS loader for {mode.upper()} boot':
        'BCD-Eintrag verwendet das falsche Ladeprogramm für den {mode.upper()}-Start',
    "This disk boots in {mode.upper()} mode, which requires {want}, but the entry points to '{path}'. Boot Manager cannot run that loader.":
        'Diese Festplatte startet im {mode.upper()}-Modus, der {want} benötigt, aber der Eintrag zeigt auf „{path}“. Der Start-Manager kann dieses Ladeprogramm nicht ausführen.',
    'The OS loader named in the BCD does not exist: {path}':
        'Das im BCD genannte Ladeprogramm existiert nicht: {path}',
    "Boot Manager finds the entry but the loader file is missing on the Windows partition: 'Windows failed to start ... File: \\Windows\\system32\\winload.efi'.":
        'Der Start-Manager findet den Eintrag, aber die Ladeprogrammdatei fehlt auf der Windows-Partition: „Windows konnte nicht gestartet werden … Datei: \\Windows\\system32\\winload.efi“.',
    'Set the Windows directory:':
        'Das Windows-Verzeichnis setzen:',
    'The “safeboot” option is set permanently, so Windows always starts in Safe Mode.':
        'Die Option „safeboot“ ist dauerhaft gesetzt, Windows startet daher immer im abgesicherten Modus.',
    'Remove the Safe Mode setting:':
        'Die Einstellung für den abgesicherten Modus entfernen:',
    'Remove the setting:':
        'Die Einstellung entfernen:',
    'Remove the settings that are present:':
        'Die vorhandenen Einstellungen entfernen:',
    'BCD overrides the {n} file ({v})':
        'BCD ersetzt die {n}-Datei ({v})',
    'Hibernation resume entry points to another partition':
        'Der Eintrag zum Fortsetzen aus dem Ruhezustand zeigt auf eine andere Partition',
    "Windows is hibernated, but the resume entry's hiberfile device is not this partition; resuming fails and Windows may discard the image or stop with an error.":
        'Windows befindet sich im Ruhezustand, aber das Ruhezustandsgerät des Fortsetzungseintrags ist nicht diese Partition; das Fortsetzen schlägt fehl und Windows verwirft das Abbild oder hält mit einem Fehler an.',
    'Windows Recovery Environment entry is missing from the BCD':
        'Der Eintrag der Windows-Wiederherstellungsumgebung fehlt im BCD',
    'Automatic Repair cannot start after failed boots.':
        'Die automatische Reparatur kann nach fehlgeschlagenen Starts nicht starten.',
    'Automatic recovery is disabled for this entry':
        'Die automatische Wiederherstellung ist für diesen Eintrag ausgeschaltet',
    "The boot menu contains a broken entry ('{in_menu[0]['description']}')":
        "Das Startmenü enthält einen defekten Eintrag („{in_menu[0]['description']}“)",
    'Stale boot entries point to missing partitions ({len(stale)})':
        'Veraltete Starteinträge zeigen auf fehlende Partitionen ({len(stale)})',
    'The Windows Boot Manager menu offers an entry for a Windows partition that no longer exists. Choosing it fails with 0xc000000e; it often has the same name as the working entry, which is confusing.':
        'Das Menü des Windows-Start-Managers bietet einen Eintrag für eine Windows-Partition an, die es nicht mehr gibt. Wählt man ihn, kommt der Fehler 0xc000000e; oft trägt er denselben Namen wie der funktionierende Eintrag, was verwirrend ist.',
    'Old entries for Windows installations that no longer exist. Harmless unless one is the default.':
        'Alte Einträge für Windows-Installationen, die es nicht mehr gibt. Harmlos, solange keiner davon der Standard ist.',
    'Delete the dead entries:':
        'Die toten Einträge löschen:',
    " They point to partitions that no longer exist (typical after cloning, re-partitioning or restoring an image). Boot Manager fails with “A required device isn't connected or can't be accessed”.":
        ' Sie zeigen auf Partitionen, die es nicht mehr gibt (typisch nach dem Klonen, Neupartitionieren oder Zurückspielen eines Abbilds). Der Start-Manager bricht mit „Ein erforderliches Gerät ist nicht angeschlossen oder es kann nicht darauf zugegriffen werden“ ab.',
    ' Boot Manager starts a different installation or fails.':
        ' Der Start-Manager startet eine andere Installation oder schlägt fehl.',
    'Boot Manager starts “{dobj.description if dobj else default}” by default, which lives on {ddesc}.':
        'Der Start-Manager startet standardmäßig „{dobj.description if dobj else default}“, das auf {ddesc} liegt.',
    'Boot Manager starts “{dobj.description if dobj else default}” by default.':
        'Der Start-Manager startet standardmäßig „{dobj.description if dobj else default}“.',
    'Set the loader that {mode.upper()} boot needs:':
        'Das Ladeprogramm setzen, das der {mode.upper()}-Start benötigt:',
    "Copy the loader back from Windows' own spare copy:\n`copy C:\\Windows\\System32\\Boot\\{want} C:\\Windows\\System32\\{want}`":
        'Das Ladeprogramm aus der Reservekopie von Windows zurückkopieren:\n`copy C:\\Windows\\System32\\Boot\\{want} C:\\Windows\\System32\\{want}`',
    'If that copy is missing too, let Windows repair its system files:\n`sfc /scannow /offbootdir=C:\\ /offwindir=C:\\Windows`':
        'Fehlt auch diese Kopie, lassen Sie Windows seine Systemdateien reparieren:\n`sfc /scannow /offbootdir=C:\\ /offwindir=C:\\Windows`',
    ' The “dsrepair” mode only works on domain controllers; on a normal PC it ends in a logon loop.':
        ' Der Modus „dsrepair“ funktioniert nur auf Domänencontrollern; auf einem normalen PC endet er in einer Anmeldeschleife.',
    'winload loads “{v}” instead of the standard {n}.':
        'winload lädt „{v}“ statt der Standarddatei für {n}.',
    'Remove the override so the standard {n} is loaded:':
        'Die Ersetzung entfernen, damit wieder die Standarddatei für {n} geladen wird:',
    'Register the recovery environment again:\n`reagentc /enable`':
        'Die Wiederherstellungsumgebung neu registrieren:\n`reagentc /enable`',
    'Windows Recovery Environment entry points to a missing partition':
        'Der Eintrag der Windows-Wiederherstellungsumgebung zeigt auf eine fehlende Partition',
    'Automatic Repair / WinRE will not start after failed boots.':
        'Die automatische Reparatur bzw. die Wiederherstellungsumgebung startet nach fehlgeschlagenen Starts nicht.',
    ' That file does not exist.':
        ' Diese Datei existiert nicht.',
    'Register the recovery environment again:\n`reagentc /disable\nreagentc /enable`':
        'Die Wiederherstellungsumgebung neu registrieren:\n`reagentc /disable\nreagentc /enable`',
    'Give the EFI partition the drive letter S:. It is the small FAT32 volume in the list; replace N with its number:\n`diskpart\nlist vol\nselect vol N\nassign letter=S\nexit`':
        'Geben Sie der EFI-Partition den Laufwerksbuchstaben S:. Es ist das kleine FAT32-Volume in der Liste; ersetzen Sie N durch seine Nummer:\n`diskpart\nlist vol\nselect vol N\nassign letter=S\nexit`',
    'Rebuild Windows Boot Manager, the boot configuration and the firmware boot entry:\n`bcdboot C:\\Windows /s S: /f UEFI`':
        'Windows-Start-Manager, Startkonfiguration und Firmware-Starteintrag neu erstellen:\n`bcdboot C:\\Windows /s S: /f UEFI`',
    'Create the firmware entry for Windows Boot Manager:\n`sudo efibootmgr -c -d {p[\'disk_path\']} -p {p[\'number\']} -L "Windows Boot Manager" -l \'\\EFI\\Microsoft\\Boot\\bootmgfw.efi\'`':
        'Den Firmware-Eintrag für den Windows-Start-Manager anlegen:\n`sudo efibootmgr -c -d {p[\'disk_path\']} -p {p[\'number\']} -L "Windows Boot Manager" -l \'\\EFI\\Microsoft\\Boot\\bootmgfw.efi\'`',
    'Rebuild the boot files and the boot configuration. If the disk has a separate “System Reserved” partition, give it a letter in diskpart first and use that letter after /s instead of C:\n`bcdboot C:\\Windows /s C: /f BIOS`':
        'Startdateien und Startkonfiguration neu erstellen. Hat die Festplatte eine eigene Partition „System-reserviert“, geben Sie ihr zuerst in diskpart einen Buchstaben und verwenden Sie diesen hinter /s statt C:\n`bcdboot C:\\Windows /s C: /f BIOS`',
    'Rewrite the boot code:\n`bootrec /fixmbr\nbootsect /nt60 SYS /mbr`':
        'Den Startcode neu schreiben:\n`bootrec /fixmbr\nbootsect /nt60 SYS /mbr`',
    'There is no EFI System Partition':
        'Es gibt keine EFI-Systempartition',
    "UEFI firmware can only start Windows from a FAT32 partition of type 'EFI System'. None exists on any connected disk, so there is nothing for the firmware to boot.":
        'UEFI-Firmware kann Windows nur von einer FAT32-Partition vom Typ „EFI-System“ starten. Auf keiner angeschlossenen Festplatte gibt es eine, die Firmware hat also nichts zu starten.',
    'The EFI System Partition {part_label(p)} cannot be read':
        'Die EFI-Systempartition {part_label(p)} kann nicht gelesen werden',
    "The ESP's FAT file system is damaged or it is not FAT at all. The firmware cannot load Windows Boot Manager from it.":
        'Das FAT-Dateisystem der EFI-Partition ist beschädigt, oder sie ist gar nicht FAT. Die Firmware kann den Windows-Start-Manager nicht von ihr laden.',
    'Windows boots through an EFI partition on a different disk':
        'Windows startet über eine EFI-Partition auf einer anderen Festplatte',
    "The boot files for this Windows are on {part_label(p)} (disk {p['disk']}). If that disk is removed, wiped or reordered, Windows will no longer start.":
        "Die Startdateien dieses Windows liegen auf {part_label(p)} (Festplatte {p['disk']}). Wird diese Festplatte entfernt, gelöscht oder umsortiert, startet Windows nicht mehr.",
    'Several EFI partitions are present':
        'Es gibt mehrere EFI-Partitionen',
    'Using {part_label(p)} for the analysis (it fits this Windows best). Which one the firmware actually uses is decided by the firmware boot entry (see below).':
        'Für die Analyse wird {part_label(p)} verwendet (sie passt am besten zu diesem Windows). Welche die Firmware tatsächlich nutzt, entscheidet der Firmware-Starteintrag (siehe unten).',
    'Windows Boot Manager (bootmgfw.efi) is missing from the EFI partition':
        'Der Windows-Start-Manager (bootmgfw.efi) fehlt auf der EFI-Partition',
    "The firmware has nothing to start: \\EFI\\Microsoft\\Boot\\bootmgfw.efi does not exist on {part_label(p)}. Typical after a Linux installer or a tool reformatted the ESP. The PC boots straight to the firmware setup, another OS, or shows 'no bootable device'.":
        'Die Firmware hat nichts zu starten: \\EFI\\Microsoft\\Boot\\bootmgfw.efi existiert auf {part_label(p)} nicht. Typisch, nachdem ein Linux-Installer oder ein Werkzeug die EFI-Partition neu formatiert hat. Der PC startet direkt ins Firmware-Setup, in ein anderes System oder meldet „kein startfähiges Gerät“.',
    'The BCD store is missing':
        'Der BCD-Speicher fehlt',
    "Boot Manager starts but finds no boot configuration and shows 'The Boot Configuration Data for your PC is missing or contains errors'.":
        'Der Start-Manager startet, findet aber keine Startkonfiguration und zeigt „Die Startkonfigurationsdaten für Ihren PC fehlen oder enthalten Fehler“.',
    "No 'Windows Boot Manager' entry in the firmware (NVRAM)":
        'Kein Eintrag „Windows Boot Manager“ in der Firmware (NVRAM)',
    'BOOTMGR is {status_word(st)} on the active partition':
        'BOOTMGR ist auf der aktiven Partition {status_word(st)}',
    "The partition boot code loads \\bootmgr; without it the screen shows 'BOOTMGR is missing'.":
        'Der Partitions-Startcode lädt \\bootmgr; ohne diese Datei erscheint „BOOTMGR fehlt“.',
    "BOOTMGR finds no \\Boot\\BCD and stops with 'The Boot Configuration Data for your PC is missing'.":
        'BOOTMGR findet kein \\Boot\\BCD und hält mit „Die Startkonfigurationsdaten für Ihren PC fehlen“ an.',
    'Take 300 MB from the Windows volume and create an EFI partition there:\n`diskpart\nselect vol C\nshrink desired=300\ncreate partition efi size=300\nformat quick fs=fat32 label=System\nassign letter=S\nexit`':
        'Nehmen Sie 300 MB vom Windows-Volume und legen Sie dort eine EFI-Partition an:\n`diskpart\nselect vol C\nshrink desired=300\ncreate partition efi size=300\nformat quick fs=fat32 label=System\nassign letter=S\nexit`',
    'Formatting erases everything on the EFI partition. If Linux boots from the same partition, its boot loader has to be reinstalled afterwards.':
        'Das Formatieren löscht alles auf der EFI-Partition. Startet Linux von derselben Partition, muss dessen Bootloader danach neu installiert werden.',
    'Format the EFI partition (the small volume; replace N with its number):\n`diskpart\nlist vol\nselect vol N\nformat quick fs=fat32 label=System\nassign letter=S\nexit`':
        'Die EFI-Partition formatieren (das kleine Volume; ersetzen Sie N durch seine Nummer):\n`diskpart\nlist vol\nselect vol N\nformat quick fs=fat32 label=System\nassign letter=S\nexit`',
    'Nothing needs to be done as long as both disks stay connected.':
        'Es ist nichts zu tun, solange beide Festplatten angeschlossen bleiben.',
    'Windows Boot Manager (bootmgfw.efi) is damaged ({status})':
        'Der Windows-Start-Manager (bootmgfw.efi) ist beschädigt ({status})',
    'The boot manager file exists but cannot be a valid EFI program, so the firmware refuses it.':
        'Die Datei des Start-Managers existiert, ist aber kein gültiges EFI-Programm, daher verweigert die Firmware sie.',
    'EFI partition is almost full ({human_size(free)} free)':
        'Die EFI-Partition ist fast voll ({human_size(free)} frei)',
    'Windows updates have to write new boot files to the ESP; when that fails, the boot files can be left half-updated (and the update rolls back).':
        'Windows-Updates müssen neue Startdateien auf die EFI-Partition schreiben; schlägt das fehl, bleiben die Startdateien halb aktualisiert zurück (und das Update wird zurückgenommen).',
    "The firmware's boot list has no entry that starts \\EFI\\Microsoft\\Boot\\bootmgfw.efi. ":
        'Die Startliste der Firmware hat keinen Eintrag, der \\EFI\\Microsoft\\Boot\\bootmgfw.efi startet. ',
    "Firmware entry Boot{e['num']} '{e['description']}' points to a partition that no longer exists":
        "Firmware-Eintrag Boot{e['num']} „{e['description']}“ zeigt auf eine Partition, die es nicht mehr gibt",
    'The firmware tries to load Windows Boot Manager from an EFI partition with this GUID, but no connected disk has such a partition (the ESP was re-created or the disk was replaced/cloned). The firmware skips the entry or shows a boot error.':
        'Die Firmware versucht, den Windows-Start-Manager von einer EFI-Partition mit dieser GUID zu laden, aber keine angeschlossene Festplatte hat eine solche Partition (die EFI-Partition wurde neu angelegt oder die Festplatte ersetzt/geklont). Die Firmware überspringt den Eintrag oder zeigt einen Startfehler.',
    'The firmware starts Windows Boot Manager from a different EFI partition':
        'Die Firmware startet den Windows-Start-Manager von einer anderen EFI-Partition',
    "The analysed ESP is {part_label(esp)}, but the firmware's Windows entry uses {', '.join(part_label(u) for u in used)}. The BCD on that partition decides what boots.":
        "Die analysierte EFI-Partition ist {part_label(esp)}, der Windows-Eintrag der Firmware nutzt aber {', '.join(part_label(u) for u in used)}. Was startet, entscheidet das BCD auf dieser Partition.",
    'Windows Boot Manager is not in the firmware boot order':
        'Der Windows-Start-Manager steht nicht in der Startreihenfolge der Firmware',
    'The entry exists but the firmware never tries it automatically.':
        'Der Eintrag existiert, aber die Firmware probiert ihn nie von selbst.',
    'Partition boot code of the active partition does not load BOOTMGR':
        'Der Partitions-Startcode der aktiven Partition lädt BOOTMGR nicht',
    "The volume boot record should chain to BOOTMGR. It looks like old NTLDR (XP) or foreign boot code, so 'NTLDR is missing' or similar errors appear.":
        'Der Volume-Startdatensatz sollte BOOTMGR starten. Er sieht nach altem NTLDR (XP) oder fremdem Startcode aus, daher erscheint „NTLDR fehlt“ oder ein ähnlicher Fehler.',
    'Delete boot loaders of systems that are no longer installed, and old Linux kernel images, from the EFI partition.':
        'Löschen Sie Bootloader von nicht mehr installierten Systemen und alte Linux-Kernel-Abbilder von der EFI-Partition.',
    "The fallback loader \\EFI\\Boot\\bootx64.efi is a copy of Windows Boot Manager, so the firmware may still find Windows via the disk's default entry.":
        'Der Ausweich-Loader \\EFI\\Boot\\bootx64.efi ist eine Kopie des Windows-Start-Managers; die Firmware findet Windows also eventuell noch über den Standardeintrag der Festplatte.',
    "The fallback loader \\EFI\\Boot\\bootx64.efi is not Windows' boot manager either, so this computer has no path to start Windows.":
        'Der Ausweich-Loader \\EFI\\Boot\\bootx64.efi ist auch nicht der Start-Manager von Windows; dieser Computer hat also keinen Weg, Windows zu starten.',
    'Go back, choose that EFI partition under “More options” and run the analysis again. The boot configuration on that partition is the one that decides what starts.':
        'Gehen Sie zurück, wählen Sie diese EFI-Partition unter „Weitere Optionen“ und starten Sie die Analyse erneut. Die Startkonfiguration auf dieser Partition entscheidet, was startet.',
    "Put Windows Boot Manager into the boot order:\n`sudo efibootmgr -o {','.join(order + [good[0]['num']])}`":
        "Den Windows-Start-Manager in die Startreihenfolge aufnehmen:\n`sudo efibootmgr -o {','.join(order + [good[0]['num']])}`",
    'Or open the firmware setup (usually F2 or Del right after power-on) and add “Windows Boot Manager” to the boot order there.':
        'Oder öffnen Sie das Firmware-Setup (meist F2 oder Entf direkt nach dem Einschalten) und fügen Sie dort „Windows Boot Manager“ zur Startreihenfolge hinzu.',
    'Windows Boot Manager entry is disabled in the firmware':
        'Der Eintrag des Windows-Start-Managers ist in der Firmware deaktiviert',
    'The firmware skips inactive entries.':
        'Die Firmware überspringt inaktive Einträge.',
    'Write the Windows boot code to the system partition and the first sector:\n`bootsect /nt60 SYS /mbr`':
        'Den Windows-Startcode auf die Systempartition und in den ersten Sektor schreiben:\n`bootsect /nt60 SYS /mbr`',
    'The active (system) partition {part_label(boot)} cannot be read':
        'Die aktive (System-)Partition {part_label(boot)} kann nicht gelesen werden',
    'BIOS boot starts BOOTMGR from the active partition, but its file system is unreadable.':
        'Beim BIOS-Start wird BOOTMGR von der aktiven Partition geladen, aber deren Dateisystem ist nicht lesbar.',
    "Delete the dead entry:\n`sudo efibootmgr -b {e['num']} -B`":
        "Den toten Eintrag löschen:\n`sudo efibootmgr -b {e['num']} -B`",
    "Enable the entry:\n`sudo efibootmgr -b {good[0]['num']} -a`":
        "Den Eintrag aktivieren:\n`sudo efibootmgr -b {good[0]['num']} -a`",
    'The firmware starts “{name}” first, not Windows':
        'Die Firmware startet zuerst „{name}“, nicht Windows',
    "That is normal for dual boot: Windows is started from that boot loader's menu, or from the firmware's boot menu (usually F12 or Esc right after power-on).":
        'Das ist bei Dual-Boot normal: Windows wird aus dem Menü dieses Bootloaders gestartet oder über das Startmenü der Firmware (meist F12 oder Esc direkt nach dem Einschalten).',
    'Parameter 1 is the process object that died (see the dump in WinDbg: `!analyze -v`).':
        'Parameter 1 ist das Prozessobjekt, das beendet wurde (siehe das Abbild in WinDbg: `!analyze -v`).',
    'Start Windows in Safe Mode: in Automatic Repair choose Troubleshoot → Advanced options → Startup Settings → Restart, then press 4.':
        'Starten Sie Windows im abgesicherten Modus: In der automatischen Reparatur „Problembehandlung“ → „Erweiterte Optionen“ → „Starteinstellungen“ → „Neu starten“ wählen, dann 4 drücken.',
    'In Safe Mode uninstall the program or driver you installed just before the crashes began.':
        'Deinstallieren Sie im abgesicherten Modus das Programm oder den Treiber, den Sie kurz vor Beginn der Abstürze installiert haben.',
    'If Safe Mode does not start either:':
        'Startet auch der abgesicherte Modus nicht:',
    ' It happened {len(window)} times within two days - a crash loop.':
        ' Er trat innerhalb von zwei Tagen {len(window)}-mal auf – eine Absturzschleife.',
    'Status: {status_text(st)}.':
        'Status: {status_text(st)}.',
    'Look at the disk-controller and filter-driver findings in this report first: a changed SATA/RAID/VMD setting in the firmware or a leftover storage filter driver is the usual cause.':
        'Sehen Sie sich zuerst die Befunde zu Festplattencontroller und Filtertreibern in diesem Bericht an: Eine geänderte SATA/RAID/VMD-Einstellung in der Firmware oder ein übrig gebliebener Speicher-Filtertreiber ist die übliche Ursache.',
    'If you changed the storage mode in the firmware setup recently, change it back.':
        'Haben Sie den Speichermodus im Firmware-Setup kürzlich geändert, stellen Sie ihn zurück.',
    "Check the disk's own health report:\n`sudo smartctl -a {ctx.disk['path']}`":
        "Den Zustandsbericht der Festplatte selbst prüfen:\n`sudo smartctl -a {ctx.disk['path']}`",
    'Test the memory: install memtest86+ and choose it in the boot menu:\n`sudo pacman -S memtest86+-efi`':
        'Den Arbeitsspeicher testen: memtest86+ installieren und im Startmenü auswählen:\n`sudo pacman -S memtest86+-efi`',
    'See the “Driver Verifier is enabled” finding: turning Verifier off ends this crash loop.':
        'Siehe den Befund „Treiberüberprüfung ist eingeschaltet“: Wird sie ausgeschaltet, endet diese Absturzschleife.',
    'Startup Repair root cause: {c}':
        'Ursache laut Starthilfe: {c}',
    'Boot log: last driver loaded in the most recent boot attempt':
        'Startprotokoll: zuletzt geladener Treiber beim letzten Startversuch',
    'Windows boot logging was enabled. If Windows hung or crashed during startup, the problem is usually the driver loaded right after the last one listed (or this last one itself).':
        'Die Startprotokollierung von Windows war eingeschaltet. Ist Windows beim Start hängen geblieben oder abgestürzt, liegt das Problem meist beim Treiber direkt nach dem zuletzt aufgeführten (oder bei diesem selbst).',
    '{len(live)} live kernel report(s) (non-fatal)':
        '{len(live)} Live-Kernel-Bericht(e) (nicht schwerwiegend)',
    'Live dumps record hangs/timeouts (often graphics or USB) without crashing Windows.':
        'Live-Abbilder zeichnen Hänger oder Zeitüberschreitungen auf (oft Grafik oder USB), ohne dass Windows abstürzt.',
    'Kernel crash.':
        'Kernel-Absturz.',
    'Most recent blue screen: {bugcheck_text(code)}':
        'Letzter Bluescreen: {bugcheck_text(code)}',
    'Recorded blue screen: {bugcheck_text(code)}':
        'Aufgezeichneter Bluescreen: {bugcheck_text(code)}',
    'Startup Repair ran but found no root cause':
        'Die Starthilfe lief, hat aber keine Ursache gefunden',
    "Windows' own Automatic Repair could not identify the problem.":
        'Die automatische Reparatur von Windows konnte das Problem nicht ermitteln.',
    "Windows' Automatic Repair analysed the failed start and named this as the cause.":
        'Die automatische Reparatur von Windows hat den fehlgeschlagenen Start untersucht und dies als Ursache genannt.',
    'Startup Repair names {named}. If that belongs to an add-on driver (not Microsoft), look for the matching driver finding in this report: disabling the driver is enough.':
        'Die Starthilfe nennt {named}. Gehört das zu einem Zusatztreiber (nicht von Microsoft), suchen Sie den passenden Treiber-Befund in diesem Bericht: Es genügt, den Treiber zu deaktivieren.',
    ' It could not fix it.':
        ' Sie konnte es nicht beheben.',
    'Registry I/O failure.':
        'E/A-Fehler in der Registrierung.',
    'Failed to load/initialise a hive (corrupt hive).':
        'Eine Registrierungsstruktur konnte nicht geladen oder initialisiert werden (beschädigte Struktur).',
    'Failed to read the registry (wrong data).':
        'Die Registrierung konnte nicht gelesen werden (falsche Daten).',
    'Bad hive.':
        'Ungültige Registrierungsstruktur.',
    'Disk is GPT/UEFI but this computer is currently running in legacy BIOS mode':
        'Die Festplatte ist GPT/UEFI, dieser Computer läuft aber gerade im Legacy-BIOS-Modus',
    'Windows on a GPT disk can only be started by UEFI firmware. If the firmware is set to legacy/CSM-only boot, Windows will not be found.':
        'Windows auf einer GPT-Festplatte kann nur von UEFI-Firmware gestartet werden. Ist die Firmware auf reinen Legacy/CSM-Start eingestellt, wird Windows nicht gefunden.',
    'Windows is on an MBR disk: it can only boot in legacy BIOS/CSM mode':
        'Windows liegt auf einer MBR-Festplatte: Es startet nur im Legacy-BIOS/CSM-Modus',
    'This computer is running in UEFI mode now. An MBR-installed Windows needs Compatibility Support Module (CSM/legacy boot) enabled. With CSM disabled (required for Secure Boot and standard on newer machines) the firmware will not offer this Windows at all.':
        'Dieser Computer läuft gerade im UEFI-Modus. Ein auf MBR installiertes Windows braucht das eingeschaltete Compatibility Support Module (CSM/Legacy-Start). Ist CSM aus (nötig für Secure Boot und Standard bei neueren Geräten), bietet die Firmware dieses Windows gar nicht an.',
    'Hybrid MBR detected on a GPT disk':
        'Hybrid-MBR auf einer GPT-Festplatte erkannt',
    'Besides the protective 0xEE entry the MBR contains real partition entries. Some firmware then treats the disk as MBR (legacy) and ignores the GPT, so the EFI boot entries are not used.':
        'Neben dem schützenden 0xEE-Eintrag enthält der MBR echte Partitionseinträge. Manche Firmware behandelt die Festplatte dann als MBR (Legacy) und ignoriert die GPT, sodass die EFI-Starteinträge nicht genutzt werden.',
    'Both GPT headers are damaged':
        'Beide GPT-Köpfe sind beschädigt',
    'Neither the primary nor the backup GUID partition table header is valid. The firmware cannot find any partition on this disk, so neither the EFI partition nor Windows can be found.':
        'Weder der primäre noch der Sicherungskopf der GUID-Partitionstabelle ist gültig. Die Firmware findet keine Partition auf dieser Festplatte, also weder die EFI-Partition noch Windows.',
    'GPT partition entry array is corrupt (CRC mismatch)':
        'Die GPT-Partitionsliste ist beschädigt (CRC stimmt nicht)',
    'The list of partitions does not match its checksum. UEFI firmware may ignore all partitions on this disk, so the EFI system partition and Windows cannot be found.':
        'Die Liste der Partitionen passt nicht zu ihrer Prüfsumme. UEFI-Firmware ignoriert dann eventuell alle Partitionen dieser Festplatte, sodass EFI-Systempartition und Windows nicht gefunden werden.',
    'MBR contains no boot code':
        'Der MBR enthält keinen Startcode',
    "On a legacy BIOS system the firmware executes the code in the first sector. It is empty, so the BIOS reports 'no bootable device' or skips this disk.":
        'Auf einem Legacy-BIOS-System führt die Firmware den Code im ersten Sektor aus. Er ist leer, daher meldet das BIOS „kein startfähiges Gerät“ oder überspringt diese Festplatte.',
    'No active partition on this MBR disk':
        'Keine aktive Partition auf dieser MBR-Festplatte',
    "The Windows MBR boot code starts the partition marked 'active'. None is marked, so the BIOS shows 'Missing operating system' / 'No bootable device'.":
        'Der Windows-MBR-Startcode startet die als „aktiv“ markierte Partition. Keine ist markiert, daher zeigt das BIOS „Missing operating system“ bzw. „kein startfähiges Gerät“.',
    'The disk reports S.M.A.R.T. health status FAILED':
        'Die Festplatte meldet den S.M.A.R.T.-Status FAILED',
    'The drive itself declares that it is failing. Read errors on system files, the registry or the page file make Windows crash or hang during startup, and repairs will not last.':
        'Das Laufwerk erklärt selbst, dass es ausfällt. Lesefehler bei Systemdateien, der Registrierung oder der Auslagerungsdatei lassen Windows beim Start abstürzen oder hängen, und Reparaturen halten nicht lange.',
    'Linux logged {len(hits)} I/O errors for this disk since it booted':
        'Linux hat seit dem Start {len(hits)} E/A-Fehler für diese Festplatte protokolliert',
    "The disk produced read/write errors right now under Linux - a strong sign of failing hardware, which would also break Windows' startup.":
        'Die Festplatte hat gerade unter Linux Lese-/Schreibfehler erzeugt – ein deutliches Zeichen für defekte Hardware, die auch den Windows-Start stören würde.',
    'Partition table signature is missing (sector 0 has no 0x55AA)':
        'Signatur der Partitionstabelle fehlt (Sektor 0 hat kein 0x55AA)',
    'The first sector of the disk does not carry a valid MBR/protective-MBR signature. The firmware will not consider this disk bootable.':
        'Der erste Sektor der Festplatte trägt keine gültige MBR- bzw. Schutz-MBR-Signatur. Die Firmware hält diese Festplatte nicht für startfähig.',
    'Open the firmware setup (usually F2 or Del right after power-on) and switch the boot mode to UEFI. Turn “CSM” / “Legacy only” off.':
        'Öffnen Sie das Firmware-Setup (meist F2 oder Entf direkt nach dem Einschalten) und stellen Sie den Startmodus auf UEFI. Schalten Sie „CSM“ bzw. „Legacy only“ aus.',
    'Easiest: open the firmware setup (usually F2 or Del right after power-on) and enable “CSM” / “Legacy boot”.':
        'Am einfachsten: Öffnen Sie das Firmware-Setup (meist F2 oder Entf direkt nach dem Einschalten) und schalten Sie „CSM“ bzw. „Legacy Boot“ ein.',
    'Or convert the disk to GPT so that it boots in UEFI mode. Find the disk number first:\n`diskpart\nlist disk\nexit`':
        'Oder wandeln Sie die Festplatte in GPT um, damit sie im UEFI-Modus startet. Ermitteln Sie zuerst die Festplattennummer:\n`diskpart\nlist disk\nexit`',
    'Convert it (replace 0 with the disk number), then switch the firmware to UEFI boot:\n`mbr2gpt /convert /disk:0`':
        'Umwandeln (0 durch die Festplattennummer ersetzen), dann die Firmware auf UEFI-Start umstellen:\n`mbr2gpt /convert /disk:0`',
    'Replace the hybrid MBR with a plain protective MBR (x = expert menu, n = new protective MBR, w = write):\n`sudo gdisk {dev}\nx\nn\nw`':
        'Den Hybrid-MBR durch einen einfachen Schutz-MBR ersetzen (x = Expertenmenü, n = neuer Schutz-MBR, w = schreiben):\n`sudo gdisk {dev}\nx\nn\nw`',
    'Do not write anything to this disk until the partitions are found again.':
        'Schreiben Sie nichts auf diese Festplatte, bis die Partitionen wiedergefunden sind.',
    'Search for the lost partitions and let TestDisk write the table back (Analyse → Quick Search → Write):\n`sudo testdisk {dev}`':
        'Die verlorenen Partitionen suchen und TestDisk die Tabelle zurückschreiben lassen (Analyse → Quick Search → Write):\n`sudo testdisk {dev}`',
    'Primary GPT header is damaged (backup is intact)':
        'Der primäre GPT-Kopf ist beschädigt (die Sicherung ist intakt)',
    'The firmware has to fall back to the backup GPT at the end of the disk. Most UEFI firmware does this and repairs it, but some refuse to boot from the disk.':
        'Die Firmware muss auf die Sicherungs-GPT am Ende der Festplatte ausweichen. Die meisten UEFI-Firmwares tun das und reparieren sie, manche verweigern aber den Start von der Festplatte.',
    'gdisk offers to load the backup partition table. Accept that, check the listing with p, then write it with w:\n`sudo gdisk {dev}\np\nw`':
        'gdisk bietet an, die Sicherungs-Partitionstabelle zu laden. Bestätigen Sie das, prüfen Sie die Liste mit p und schreiben Sie sie mit w:\n`sudo gdisk {dev}\np\nw`',
    "Write Windows' boot code into the first sector:\n`bootrec /fixmbr`":
        'Den Windows-Startcode in den ersten Sektor schreiben:\n`bootrec /fixmbr`',
    'MBR boot code belongs to GRUB':
        'Der MBR-Startcode gehört zu GRUB',
    'The BIOS starts GRUB, which must chain-load Windows. If the GRUB menu has no working Windows entry, Windows does not start.':
        'Das BIOS startet GRUB, das Windows weiterstarten muss. Hat das GRUB-Menü keinen funktionierenden Windows-Eintrag, startet Windows nicht.',
    'Mark the boot partition active. That is the small “System Reserved” partition if there is one, otherwise the Windows partition; use its number from “list partition”:\n`diskpart\nselect disk 0\nlist partition\nselect partition 1\nactive\nexit`':
        'Die Startpartition als aktiv markieren. Das ist die kleine Partition „System-reserviert“, falls vorhanden, sonst die Windows-Partition; verwenden Sie ihre Nummer aus „list partition“:\n`diskpart\nselect disk 0\nlist partition\nselect partition 1\nactive\nexit`',
    'Rewrite the boot files. After /s put the letter of the partition you just marked active:\n`bootrec /fixboot\nbcdboot C:\\Windows /s C: /f BIOS`':
        'Die Startdateien neu schreiben. Hinter /s den Buchstaben der Partition angeben, die Sie gerade aktiv gesetzt haben:\n`bootrec /fixboot\nbcdboot C:\\Windows /s C: /f BIOS`',
    'More than one partition is marked active':
        'Mehr als eine Partition ist als aktiv markiert',
    "Only one partition should be active; the boot code may refuse to boot ('Invalid partition table').":
        'Nur eine Partition sollte aktiv sein; sonst verweigert der Startcode eventuell den Start („Invalid partition table“).',
    'Replace the drive, then restore Windows from a backup or install it again.':
        'Ersetzen Sie das Laufwerk und stellen Sie Windows danach aus einer Sicherung wieder her oder installieren Sie es neu.',
    'NVMe drive reports a critical warning':
        'Das NVMe-Laufwerk meldet eine kritische Warnung',
    "The SSD's controller reports a critical condition. A read-only or degraded SSD prevents Windows from writing the registry, logs and page file during startup, which makes boot fail or loop.":
        'Der Controller der SSD meldet einen kritischen Zustand. Eine schreibgeschützte oder geschwächte SSD hindert Windows daran, beim Start Registrierung, Protokolle und Auslagerungsdatei zu schreiben, sodass der Start fehlschlägt oder in einer Schleife läuft.',
    "NVMe drive has {nv['media_errors']} media/data-integrity errors":
        "Das NVMe-Laufwerk hat {nv['media_errors']} Medien-/Datenintegritätsfehler",
    'Unrecoverable read errors happened on the flash. If they hit system files or the registry, Windows fails to start.':
        'Auf dem Flash-Speicher sind nicht behebbare Lesefehler aufgetreten. Treffen sie Systemdateien oder die Registrierung, startet Windows nicht.',
    'SSD has exceeded its rated write endurance':
        'Die SSD hat ihre angegebene Schreib-Lebensdauer überschritten',
    "The drive's wear indicator is at or above 100%.":
        'Der Verschleißanzeiger des Laufwerks steht bei 100 % oder darüber.',
    'Disk has unreadable sectors (pending {pending}, uncorrectable {unc})':
        'Die Festplatte hat unlesbare Sektoren (ausstehend {pending}, nicht korrigierbar {unc})',
    'Sectors that cannot be read are waiting to be remapped. If one of them holds a boot-critical file or registry data, startup fails with read errors (0x7A, 0xF4, 0xC0000185).':
        'Nicht lesbare Sektoren warten auf ihre Umlagerung. Liegt in einem davon eine startkritische Datei oder Registrierungsdaten, schlägt der Start mit Lesefehlern fehl (0x7A, 0xF4, 0xC0000185).',
    'Disk has reallocated {realloc} sectors':
        'Die Festplatte hat {realloc} Sektoren umgelagert',
    'A high and growing reallocated sector count indicates a degrading disk.':
        'Eine hohe und wachsende Zahl umgelagerter Sektoren weist auf eine nachlassende Festplatte hin.',
    'Interface CRC errors recorded ({attrs[199]})':
        'Schnittstellen-CRC-Fehler aufgezeichnet ({attrs[199]})',
    'Data corruption on the SATA cable/port happened in the past. A loose or bad cable causes random boot failures.':
        'In der Vergangenheit sind Daten auf dem SATA-Kabel bzw. -Anschluss beschädigt worden. Ein lockeres oder defektes Kabel verursacht zufällige Startfehler.',
    'Reseat the drive (cable or M.2 slot).':
        'Setzen Sie das Laufwerk neu ein (Kabel oder M.2-Steckplatz).',
    "Start the drive's long self-test and read the result when it has finished:\n`sudo smartctl -t long {disk['path']}\nsudo smartctl -a {disk['path']}`":
        "Den Langzeit-Selbsttest des Laufwerks starten und das Ergebnis lesen, wenn er fertig ist:\n`sudo smartctl -t long {disk['path']}\nsudo smartctl -a {disk['path']}`",
    'If Linux still lists the partitions, only the protective MBR is damaged. Rewrite it (x = expert menu, n = new protective MBR, w = write):\n`sudo gdisk {dev}\nx\nn\nw`':
        'Listet Linux die Partitionen noch auf, ist nur der Schutz-MBR beschädigt. Schreiben Sie ihn neu (x = Expertenmenü, n = neuer Schutz-MBR, w = schreiben):\n`sudo gdisk {dev}\nx\nn\nw`',
    'If the partitions are gone too, do not write anything to the disk. Search for the lost partitions and let TestDisk write the table back:\n`sudo testdisk {dev}`':
        'Sind auch die Partitionen weg, schreiben Sie nichts auf die Festplatte. Suchen Sie die verlorenen Partitionen und lassen Sie TestDisk die Tabelle zurückschreiben:\n`sudo testdisk {dev}`',
    'gdisk notices the damage and offers to use the backup table. Accept that, then write it with w:\n`sudo gdisk {dev}\nw`':
        'gdisk bemerkt den Schaden und bietet an, die Sicherungstabelle zu verwenden. Bestätigen Sie das und schreiben Sie sie mit w:\n`sudo gdisk {dev}\nw`',
    'Backup GPT header is missing or invalid':
        'Der Sicherungs-GPT-Kopf fehlt oder ist ungültig',
    'Typical after cloning to a larger disk. Windows usually still boots, but the disk is less resilient.':
        'Typisch nach dem Klonen auf eine größere Festplatte. Windows startet meist trotzdem, aber die Festplatte ist weniger robust.',
    'Let GRUB find Windows and add it to its menu:\n`sudo os-prober\nsudo grub-mkconfig -o /boot/grub/grub.cfg`':
        'GRUB Windows finden und ins Menü aufnehmen lassen:\n`sudo os-prober\nsudo grub-mkconfig -o /boot/grub/grub.cfg`',
    'Or give the first sector back to Windows (this removes the GRUB menu):\n`bootrec /fixmbr`':
        'Oder den ersten Sektor an Windows zurückgeben (das entfernt das GRUB-Menü):\n`bootrec /fixmbr`',
    'Select each partition that should not be active and clear its flag (replace 2 with its number):\n`diskpart\nselect disk 0\nlist partition\nselect partition 2\ninactive\nexit`':
        'Jede Partition auswählen, die nicht aktiv sein soll, und ihre Markierung entfernen (2 durch ihre Nummer ersetzen):\n`diskpart\nselect disk 0\nlist partition\nselect partition 2\ninactive\nexit`',
    'Replace the SSD.':
        'Ersetzen Sie die SSD.',
    'Read the whole drive once to see whether new errors appear:\n`sudo badblocks -sv {dev}`':
        'Das ganze Laufwerk einmal lesen, um zu sehen, ob neue Fehler auftreten:\n`sudo badblocks -sv {dev}`',
    'Keep backups current and plan to replace the SSD.':
        'Halten Sie Sicherungen aktuell und planen Sie den Austausch der SSD.',
    'Replace the disk.':
        'Ersetzen Sie die Festplatte.',
    'Keep backups current and plan to replace the disk.':
        'Halten Sie Sicherungen aktuell und planen Sie den Austausch der Festplatte.',
    'Replace the SATA cable or use another SATA port.':
        'Ersetzen Sie das SATA-Kabel oder verwenden Sie einen anderen SATA-Anschluss.',
    'Move the backup table to the real end of the disk:\n`sudo sgdisk -e {dev}`':
        'Die Sicherungstabelle an das tatsächliche Ende der Festplatte verschieben:\n`sudo sgdisk -e {dev}`',
    'Write the list back without “{flt}”:\n`reg add {key} /v {value} /t REG_MULTI_SZ /d "{joined}" /f`':
        'Die Liste ohne „{flt}“ zurückschreiben:\n`reg add {key} /v {value} /t REG_MULTI_SZ /d "{joined}" /f`',
    '“{flt}” is the only entry, so delete the whole list:\n`reg delete {key} /v {value} /f`':
        '„{flt}“ ist der einzige Eintrag, also die ganze Liste löschen:\n`reg delete {key} /v {value} /f`',
    "No driver for the disk's controller is configured to start at boot.":
        'Für den Controller der Festplatte ist kein Treiber zum Laden beim Systemstart eingerichtet.',
    'No boot-start driver for the disk controller ({kind.upper()})':
        'Kein Starttreiber für den Festplattencontroller ({kind.upper()})',
    'Session Manager will swap these Windows files very early in the next start (an installer or update that needed a restart). If one of the new files is broken or does not match the rest, startup fails right after.':
        'Die Sitzungsverwaltung tauscht diese Windows-Dateien sehr früh beim nächsten Start aus (ein Installationsprogramm oder Update, das einen Neustart brauchte). Ist eine der neuen Dateien defekt oder passt nicht zum Rest, schlägt der Start direkt danach fehl.',
    "Show the current list (it should read: {', '.join(cur) or '?'}):\n`reg query {key} /v {value}`":
        "Die aktuelle Liste anzeigen (sie sollte so lauten: {', '.join(cur) or '?'}):\n`reg query {key} /v {value}`",
    'Windows is on a USB-attached disk':
        'Windows liegt auf einer per USB angeschlossenen Festplatte',
    "Normal Windows installations cannot boot from USB (only 'Windows To Go'); the USB storage driver is not boot-start and Windows stops with INACCESSIBLE_BOOT_DEVICE.":
        'Normale Windows-Installationen können nicht von USB starten (nur „Windows To Go“); der USB-Speichertreiber lädt nicht beim Systemstart und Windows hält mit INACCESSIBLE_BOOT_DEVICE an.',
    ' Without it the kernel cannot see the disk it is booting from and stops with INACCESSIBLE_BOOT_DEVICE.':
        ' Ohne ihn sieht der Kernel die Festplatte nicht, von der er startet, und hält mit INACCESSIBLE_BOOT_DEVICE an.',
    '{len(sys_moves)} system file(s) will be replaced at the next start':
        '{len(sys_moves)} Systemdatei(en) werden beim nächsten Start ersetzt',
    'Only clean-up of temporary files left by installers (SET….tmp and similar). Harmless; it has no influence on whether Windows starts.':
        'Nur das Aufräumen temporärer Dateien von Installationsprogrammen (SET….tmp und Ähnliches). Harmlos; das hat keinen Einfluss darauf, ob Windows startet.',
    '{len(deletes)} file(s) will be deleted and {len(moves)} moved by Session Manager at the next start (installers that needed a restart). None of them replaces a Windows system file.':
        'Die Sitzungsverwaltung löscht beim nächsten Start {len(deletes)} Datei(en) und verschiebt {len(moves)} (Installationsprogramme, die einen Neustart brauchten). Keine davon ersetzt eine Windows-Systemdatei.',
    'Driver Verifier is enabled':
        'Die Treiberüberprüfung (Driver Verifier) ist eingeschaltet',
    'Driver Verifier deliberately crashes Windows (0xC4 / 0x1C4) as soon as a verified driver misbehaves. Left enabled, it often produces a boot loop.':
        'Die Treiberüberprüfung lässt Windows absichtlich abstürzen (0xC4 / 0x1C4), sobald sich ein überprüfter Treiber falsch verhält. Bleibt sie eingeschaltet, entsteht oft eine Startschleife.',
    "Drive letter C: belongs to a different partition (/dev/{pointed['name']})":
        "Laufwerksbuchstabe C: gehört zu einer anderen Partition (/dev/{pointed['name']})",
    "Windows' MountedDevices assigns C: to another partition that is also connected - typically the original disk after cloning. The system boots from this partition but gets a different drive letter, so programs, the registry and user profiles reference the other disk: logon fails, 'Preparing desktop' loops or you are logged on with a temporary profile.":
        'Die MountedDevices von Windows weisen C: einer anderen, ebenfalls angeschlossenen Partition zu – typischerweise der ursprünglichen Festplatte nach dem Klonen. Das System startet von dieser Partition, erhält aber einen anderen Laufwerksbuchstaben, sodass Programme, Registrierung und Benutzerprofile auf die andere Festplatte verweisen: Die Anmeldung schlägt fehl, „Desktop wird vorbereitet“ läuft in einer Schleife oder Sie werden mit einem temporären Profil angemeldet.',
    'Crash dumps are disabled':
        'Absturzabbilder sind ausgeschaltet',
    'Blue screens leave no dump file, so the exact crashing driver cannot be identified from dumps.':
        'Bluescreens hinterlassen keine Abbilddatei, daher lässt sich der abstürzende Treiber nicht aus Abbildern ermitteln.',
    "Storage filter driver '{f}' is broken ({cname} {vn})":
        'Speicher-Filtertreiber „{f}“ ist defekt ({cname} {vn})',
    "'{f}' is registered as a filter on the {cname} device stack, but {problem}. Every disk/volume device then fails to start, Windows loses access to its own system disk and stops with INACCESSIBLE_BOOT_DEVICE. Typical leftover of uninstalled antivirus, encryption or backup software (e.g. Acronis, Symantec, Paragon).":
        '„{f}“ ist als Filter für den Gerätestapel „{cname}“ eingetragen, aber {problem}. Dann startet kein Festplatten- bzw. Volume-Gerät, Windows verliert den Zugriff auf die eigene Systemfestplatte und hält mit INACCESSIBLE_BOOT_DEVICE an. Typischer Überrest deinstallierter Antiviren-, Verschlüsselungs- oder Sicherungssoftware (z. B. Acronis, Symantec, Paragon).',
    "Filter driver '{f}' on {cname} is broken":
        'Filtertreiber „{f}“ für {cname} ist defekt',
    "'{f}' filters {cname} but {problem}. Windows boots, but those devices do not work (e.g. no keyboard/mouse at the logon screen).":
        '„{f}“ filtert „{cname}“, aber {problem}. Windows startet, aber diese Geräte funktionieren nicht (z. B. keine Tastatur oder Maus am Anmeldebildschirm).',
    "Boot driver “{s['name']}” is {status_word(st)}":
        "Starttreiber „{s['name']}“ ist {status_word(st)}",
    "System driver “{s['name']}” is {status_word(st)}":
        "Systemtreiber „{s['name']}“ ist {status_word(st)}",
    'Connect the disk internally (SATA/NVMe) to boot it.':
        'Schließen Sie die Festplatte intern an (SATA/NVMe), um davon zu starten.',
    'The Windows disk is an NVMe SSD, but no NVMe driver (stornvme or a vendor driver) is set to start at boot. Typical when Windows was installed on a SATA disk and then cloned to NVMe.':
        'Die Windows-Festplatte ist eine NVMe-SSD, aber kein NVMe-Treiber (stornvme oder ein Herstellertreiber) lädt beim Systemstart. Typisch, wenn Windows auf einer SATA-Festplatte installiert und dann auf NVMe geklont wurde.',
    'The Windows disk is attached to an AHCI SATA controller, but the AHCI driver (storahci) is not set to start at boot. Typical after switching the firmware SATA mode from RAID/IDE to AHCI, or after moving the disk to another computer.':
        'Die Windows-Festplatte hängt an einem AHCI-SATA-Controller, aber der AHCI-Treiber (storahci) lädt nicht beim Systemstart. Typisch nach dem Umstellen des SATA-Modus in der Firmware von RAID/IDE auf AHCI oder nach dem Umzug der Festplatte in einen anderen Computer.',
    "The NVMe SSD sits behind Intel VMD / RST (the firmware's 'RAID On'/'VMD' mode). Windows needs the Intel RST VMD driver (iaStorVD) at boot, which is not configured. Typical when the BIOS storage mode was switched from AHCI to RAID/VMD, or Windows was installed without the RST driver.":
        'Die NVMe-SSD sitzt hinter Intel VMD / RST (Firmware-Modus „RAID On“ bzw. „VMD“). Windows braucht beim Start den Intel-RST-VMD-Treiber (iaStorVD), der nicht eingerichtet ist. Typisch, wenn der Speichermodus im BIOS von AHCI auf RAID/VMD umgestellt oder Windows ohne den RST-Treiber installiert wurde.',
    'The disk is behind a RAID controller whose driver is not configured as boot-start.':
        'Die Festplatte hängt an einem RAID-Controller, dessen Treiber nicht beim Systemstart lädt.',
    'The disk is a VirtIO disk but the VirtIO storage driver is not installed/boot-start.':
        'Die Festplatte ist eine VirtIO-Festplatte, aber der VirtIO-Speichertreiber ist nicht installiert bzw. lädt nicht beim Systemstart.',
    'The disk is behind a SAS/SCSI controller whose driver is not boot-start.':
        'Die Festplatte hängt an einem SAS/SCSI-Controller, dessen Treiber nicht beim Systemstart lädt.',
    'If you changed the storage mode (AHCI / RAID / VMD) in the firmware setup recently, changing it back is the quickest fix. Otherwise switch the driver on:':
        'Haben Sie den Speichermodus (AHCI / RAID / VMD) im Firmware-Setup kürzlich geändert, ist das Zurückstellen die schnellste Lösung. Andernfalls schalten Sie den Treiber ein:',
    'Easiest: open the firmware setup (usually F2 or Del) and change the storage mode from “RAID On” / “Intel RST” / “VMD” to “AHCI”. Windows then uses its built-in NVMe driver.':
        'Am einfachsten: Öffnen Sie das Firmware-Setup (meist F2 oder Entf) und stellen Sie den Speichermodus von „RAID On“ / „Intel RST“ / „VMD“ auf „AHCI“. Windows verwendet dann seinen eingebauten NVMe-Treiber.',
    "Or add Intel's RST VMD driver: download it from your PC maker on another computer, unpack it to a USB stick (here E:) and add it:\n`dism /image:C:\\ /add-driver /driver:E:\\ /recurse`":
        'Oder fügen Sie den Intel-RST-VMD-Treiber hinzu: Laden Sie ihn auf einem anderen Computer beim Hersteller Ihres PCs herunter, entpacken Sie ihn auf einen USB-Stick (hier E:) und fügen Sie ihn hinzu:\n`dism /image:C:\\ /add-driver /driver:E:\\ /recurse`',
    'Change the controller mode in the firmware setup back to what it was when Windows was installed.':
        'Stellen Sie den Controller-Modus im Firmware-Setup wieder auf den Wert, der bei der Installation von Windows eingestellt war.',
    "Or add the controller's driver: unpack it to a USB stick (here E:) and add it:\n`dism /image:C:\\ /add-driver /driver:E:\\ /recurse`":
        'Oder fügen Sie den Treiber des Controllers hinzu: Entpacken Sie ihn auf einen USB-Stick (hier E:) und fügen Sie ihn hinzu:\n`dism /image:C:\\ /add-driver /driver:E:\\ /recurse`',
    '{len(pairs)} leftover temporary file(s) will be deleted at the next start':
        '{len(pairs)} übrig gebliebene temporäre Datei(en) werden beim nächsten Start gelöscht',
    '{len(pairs)} file operation(s) are pending for the next start':
        '{len(pairs)} Dateivorgang/-vorgänge stehen für den nächsten Start aus',
    'Simplest: disconnect the other (old) disk and start Windows.':
        'Am einfachsten: Trennen Sie die andere (alte) Festplatte und starten Sie Windows.',
    "The driver is configured to load at boot (group “{s['group'] or '-'}”, error control {ERROR_CONTROL.get(ec, ec)}), but its file \\{rel} is {status_word(st)}.":
        "Der Treiber soll beim Systemstart geladen werden (Gruppe „{s['group'] or '-'}“, Fehlerbehandlung {ERROR_CONTROL.get(ec, ec)}), aber seine Datei \\{rel} ist {status_word(st)}.",
    "The driver is configured to load while the kernel starts (group “{s['group'] or '-'}”, error control {ERROR_CONTROL.get(ec, ec)}), but its file \\{rel} is {status_word(st)}.":
        "Der Treiber soll beim Kernelstart geladen werden (Gruppe „{s['group'] or '-'}“, Fehlerbehandlung {ERROR_CONTROL.get(ec, ec)}), aber seine Datei \\{rel} ist {status_word(st)}.",
    ' With error control Critical/Severe Windows aborts the start (or falls back to Last Known Good).':
        ' Bei Fehlerbehandlung „Critical“/„Severe“ bricht Windows den Start ab (oder greift auf die letzte als funktionierend bekannte Konfiguration zurück).',
    ' Windows continues without it (Event 7026), which is only harmful if the device it serves is needed.':
        ' Windows fährt ohne ihn fort (Ereignis 7026); das schadet nur, wenn das Gerät, das er bedient, gebraucht wird.',
    'Make the {primary} driver start at boot (0 = boot start):\n`reg add HKLM\\OFFLINE\\{csname}\\Services\\{primary} /v Start /t REG_DWORD /d 0 /f`':
        'Den Treiber {primary} beim Systemstart laden (0 = Start beim Booten):\n`reg add HKLM\\OFFLINE\\{csname}\\Services\\{primary} /v Start /t REG_DWORD /d 0 /f`',
    'Remove the override that keeps it switched off. “Unable to find” just means there is none:\n`reg delete HKLM\\OFFLINE\\{csname}\\Services\\{primary}\\StartOverride /f`':
        'Die Ersetzung entfernen, die ihn ausgeschaltet hält. „Der angegebene Registrierungsschlüssel bzw. Wert wurde nicht gefunden“ bedeutet nur, dass es keine gibt:\n`reg delete HKLM\\OFFLINE\\{csname}\\Services\\{primary}\\StartOverride /f`',
    '{vname} runs a program that does not exist ({exe})':
        '{vname} startet ein Programm, das nicht existiert ({exe})',
    'Session Manager runs these native programs before Windows starts. A missing one delays boot and indicates a removed tool (often antivirus/cleaner leftovers).':
        'Die Sitzungsverwaltung führt diese nativen Programme aus, bevor Windows startet. Ein fehlendes verzögert den Start und deutet auf ein entferntes Werkzeug hin (oft Reste von Antivirus- oder Aufräumprogrammen).',
    'Cancel the pending operations:\n`reg delete "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager" /v PendingFileRenameOperations /f`':
        'Die ausstehenden Vorgänge abbrechen:\n`reg delete "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager" /v PendingFileRenameOperations /f`',
    'Switch Driver Verifier off:\n`reg delete "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager\\Memory Management" /v VerifyDrivers /f\nreg delete "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager\\Memory Management" /v VerifyDriverLevel /f`':
        'Die Treiberüberprüfung ausschalten:\n`reg delete "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager\\Memory Management" /v VerifyDrivers /f\nreg delete "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager\\Memory Management" /v VerifyDriverLevel /f`',
    'no such service (driver was uninstalled but the filter entry remained)':
        'Dienst existiert nicht (der Treiber wurde deinstalliert, aber der Filtereintrag ist geblieben)',
    'If this driver belongs to software you uninstalled, it only needs to be switched off.':
        'Gehört dieser Treiber zu Software, die Sie deinstalliert haben, muss er nur ausgeschaltet werden.',
    'Remove the stale C: drive-letter assignment':
        'Veraltete Zuordnung des Laufwerksbuchstabens C: entfernen',
    'service is disabled (Start=4)':
        'Dienst ist deaktiviert (Start=4)',
    "Switch the driver off (4 = disabled):\n`reg add HKLM\\OFFLINE\\{csname}\\Services\\{s['name']} /v Start /t REG_DWORD /d 4 /f`":
        "Den Treiber ausschalten (4 = deaktiviert):\n`reg add HKLM\\OFFLINE\\{csname}\\Services\\{s['name']} /v Start /t REG_DWORD /d 4 /f`",
    'A disk check (chkdsk) is scheduled for the next start':
        'Eine Datenträgerprüfung (chkdsk) ist für den nächsten Start geplant',
    'Windows will run autochk before starting. On a damaged disk this can take very long.':
        'Windows führt vor dem Start autochk aus. Auf einer beschädigten Festplatte kann das sehr lange dauern.',
    'Non-standard BootExecute entry: {entry}':
        'Nicht-standardmäßiger BootExecute-Eintrag: {entry}',
    'A program runs natively before Windows starts (often antivirus boot-time scan or defrag tools). If it hangs, Windows hangs with it.':
        'Ein Programm läuft nativ, bevor Windows startet (oft ein Antivirus-Scan beim Start oder Defragmentierwerkzeuge). Hängt es, hängt Windows mit.',
    'Or let Windows assign the drive letters again at the next start. The volume it starts from becomes C::\n`reg delete HKLM\\OFFLINE\\MountedDevices /va /f`':
        'Oder Windows die Laufwerksbuchstaben beim nächsten Start neu vergeben lassen. Das Volume, von dem es startet, wird C::\n`reg delete HKLM\\OFFLINE\\MountedDevices /va /f`',
    'driver file {status_word(st)}: \\{rel}':
        'Treiberdatei {status_word(st)}: \\{rel}',
    'Reset {vname} to the Windows default:\n`reg add "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager" /v {vname} /t REG_MULTI_SZ /d "autocheck autochk *" /f`':
        '{vname} auf den Windows-Standard zurücksetzen:\n`reg add "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager" /v {vname} /t REG_MULTI_SZ /d "autocheck autochk *" /f`',
    'Empty {vname}:\n`reg add "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager" /v {vname} /t REG_MULTI_SZ /d "" /f`':
        '{vname} leeren:\n`reg add "HKLM\\OFFLINE\\{csname}\\Control\\Session Manager" /v {vname} /t REG_MULTI_SZ /d "" /f`',
    'No System event log found':
        'Kein Systemereignisprotokoll gefunden',
    '\\Windows\\System32\\winevt\\Logs\\System.evtx does not exist.':
        '\\Windows\\System32\\winevt\\Logs\\System.evtx existiert nicht.',
    'Errors on other drives ({len(other)} events) - not the Windows disk':
        'Fehler auf anderen Laufwerken ({len(other)} Ereignisse) – nicht die Windows-Festplatte',
    'These disk / file-system errors belong to other drives (e.g. a USB disk), not to the disk Windows starts from, so they do not explain a startup failure. Worth checking that drive separately.':
        'Diese Festplatten- bzw. Dateisystemfehler gehören zu anderen Laufwerken (z. B. einer USB-Festplatte), nicht zu der, von der Windows startet; sie erklären also keinen Startfehler. Es lohnt sich aber, das betreffende Laufwerk separat zu prüfen.',
    ' This happened {n} time(s) in the last 30 days of the log.':
        ' Das ist in den letzten 30 Tagen des Protokolls {n}-mal passiert.',
    "Read the disk's own health report:\n`sudo smartctl -a {dev}`":
        'Den Zustandsbericht der Festplatte selbst lesen:\n`sudo smartctl -a {dev}`',
    'Reseat the drive (SATA cable or M.2 slot). For SATA, try another cable and port.':
        'Setzen Sie das Laufwerk neu ein (SATA-Kabel oder M.2-Steckplatz). Bei SATA ein anderes Kabel und einen anderen Anschluss probieren.',
    'Undo overclocking in the firmware setup, including memory profiles (XMP/EXPO).':
        'Nehmen Sie Übertaktungen im Firmware-Setup zurück, auch Speicherprofile (XMP/EXPO).',
    'If memory is fine, update the firmware (BIOS) and check temperatures and the power supply.':
        'Ist der Arbeitsspeicher in Ordnung, aktualisieren Sie die Firmware (BIOS) und prüfen Sie Temperaturen und Netzteil.',
    'If the report lists blue screens, follow those findings. Without a blue screen the usual causes are the power supply, overheating, or the power button held down during a hang.':
        'Listet der Bericht Bluescreens auf, folgen Sie diesen Befunden. Ohne Bluescreen sind die üblichen Ursachen das Netzteil, Überhitzung oder ein während eines Hängers gedrückt gehaltener Einschaltknopf.',
    'Usually harmless leftovers. If a named service belongs to software you no longer use, uninstall that software once Windows runs again.':
        'Meist harmlose Überreste. Gehört ein genannter Dienst zu Software, die Sie nicht mehr verwenden, deinstallieren Sie sie, sobald Windows wieder läuft.',
    'System event log could not be read':
        'Das Systemereignisprotokoll konnte nicht gelesen werden',
    'Windows started':
        'Windows gestartet',
    ' Repeated unexpected restarts indicate a crash/boot loop or hardware/power problems.':
        ' Wiederholte unerwartete Neustarts deuten auf eine Absturz- bzw. Startschleife oder auf Hardware- oder Stromversorgungsprobleme hin.',
    ' Last occurrence: {newest.time:%Y-%m-%d %H:%M} UTC.':
        ' Zuletzt aufgetreten: {newest.time:%Y-%m-%d %H:%M} UTC.',
    'Clean shutdown / restart':
        'Sauber heruntergefahren / neu gestartet',
    " Among them storage drivers: {', '.join(sorted(bad))}.":
        " Darunter Speichertreiber: {', '.join(sorted(bad))}.",
    ' Usually leftovers of uninstalled software; harmless unless the device is needed.':
        ' Meist Überreste deinstallierter Software; harmlos, solange das Gerät nicht gebraucht wird.',
    " Affected core services: {', '.join(sorted(names & IMPORTANT_SERVICES))}. Failures here cause black screens or logon problems.":
        " Betroffene Kerndienste: {', '.join(sorted(names & IMPORTANT_SERVICES))}. Fehler hier führen zu schwarzen Bildschirmen oder Anmeldeproblemen.",
    'Volume checked: healthy (Ntfs 98)':
        'Volume geprüft: fehlerfrei (Ntfs 98)',
    ' - other drive':
        ' – anderes Laufwerk',
    '{len(snaps)} System Restore snapshot(s) exist':
        '{len(snaps)} Systemwiederherstellungspunkt(e) vorhanden',
    'System Restore from WinRE can return Windows to an earlier, working state (programs installed since then are removed, personal files stay).':
        'Die Systemwiederherstellung aus der Wiederherstellungsumgebung kann Windows auf einen früheren, funktionierenden Stand zurücksetzen (seitdem installierte Programme werden entfernt, persönliche Dateien bleiben).',
    'A previous Windows installation (Windows.old) exists':
        'Eine frühere Windows-Installation (Windows.old) ist vorhanden',
    'Going back to the previous version is possible (Automatic Repair → Troubleshoot → Advanced options → Uninstall Updates → “Uninstall latest feature update”) within the rollback period.':
        'Die Rückkehr zur vorherigen Version ist innerhalb der Rücksetzfrist möglich (automatische Reparatur → „Problembehandlung“ → „Erweiterte Optionen“ → „Updates deinstallieren“ → „Neuestes Funktionsupdate deinstallieren“).',
    'In Automatic Repair choose Troubleshoot → Advanced options → System Restore, then pick a restore point from before the problem started.':
        'In der automatischen Reparatur „Problembehandlung“ → „Erweiterte Optionen“ → „Systemwiederherstellung“ wählen und einen Wiederherstellungspunkt von vor dem Problem auswählen.',
    'Windows Recovery Environment is disabled':
        'Die Windows-Wiederherstellungsumgebung ist ausgeschaltet',
    'Automatic Repair and the advanced startup options are not available from this disk; you will need a Windows USB stick for repairs.':
        'Automatische Reparatur und erweiterte Startoptionen stehen auf dieser Festplatte nicht zur Verfügung; für Reparaturen brauchen Sie einen Windows-USB-Stick.',
    'Fast Startup is enabled':
        'Schnellstart ist eingeschaltet',
    'Windows does not fully shut down; the next start resumes a saved kernel session. This hides some driver problems and makes dual-boot disk access risky.':
        'Windows fährt nicht vollständig herunter; der nächste Start setzt eine gespeicherte Kernelsitzung fort. Das verdeckt manche Treiberprobleme und macht den Festplattenzugriff bei Dual-Boot riskant.',
    'Turn the recovery environment back on:\n`reagentc /enable`':
        'Die Wiederherstellungsumgebung wieder einschalten:\n`reagentc /enable`',
    'Turn Fast Startup off:\n`powercfg /h off`':
        'Den Schnellstart ausschalten:\n`powercfg /h off`',
    'Let Windows check and repair its own system files (takes 10-30 minutes):\n`sfc /scannow /offbootdir=C:\\ /offwindir=C:\\Windows`':
        'Windows seine eigenen Systemdateien prüfen und reparieren lassen (dauert 10–30 Minuten):\n`sfc /scannow /offbootdir=C:\\ /offwindir=C:\\Windows`',
    "If sfc reports that it could not repair everything, repair the component store from a Windows installation USB stick of the same version. Find the stick's drive letter with “list vol” (here D:) and check whether it contains install.wim or install.esd:\n`dir D:\\sources\\install.*`":
        'Meldet sfc, dass es nicht alles reparieren konnte, reparieren Sie den Komponentenspeicher von einem Windows-Installations-USB-Stick derselben Version. Ermitteln Sie mit „list vol“ den Laufwerksbuchstaben des Sticks (hier D:) und prüfen Sie, ob er install.wim oder install.esd enthält:\n`dir D:\\sources\\install.*`',
    'Repair the component store (for install.esd write esd: instead of wim: and install.esd), then run sfc once more:\n`DISM /Image:C:\\ /Cleanup-Image /RestoreHealth /Source:wim:D:\\sources\\install.wim:1 /LimitAccess`':
        'Den Komponentenspeicher reparieren (bei install.esd esd: statt wim: und install.esd schreiben), danach sfc noch einmal ausführen:\n`DISM /Image:C:\\ /Cleanup-Image /RestoreHealth /Source:wim:D:\\sources\\install.wim:1 /LimitAccess`',
    "winload loads this file before the kernel starts; without it Windows stops with 'Windows failed to start ... File: <path>' (Recovery screen).":
        'winload lädt diese Datei, bevor der Kernel startet; ohne sie hält Windows mit „Windows konnte nicht gestartet werden … Datei: <Pfad>“ an (Wiederherstellungsbildschirm).',
    'winload has to load this file together with the kernel; if it is missing or broken the start stops on the recovery screen naming the file, or the kernel crashes right after.':
        'winload muss diese Datei zusammen mit dem Kernel laden; fehlt sie oder ist sie defekt, bleibt der Start auf dem Wiederherstellungsbildschirm mit diesem Dateinamen stehen, oder der Kernel stürzt direkt danach ab.',
    'This program/library is needed by the critical system processes started right after the kernel; startup ends in a blue screen.':
        'Dieses Programm bzw. diese Bibliothek wird von den kritischen Systemprozessen gebraucht, die direkt nach dem Kernel starten; der Start endet in einem Bluescreen.',
    'Needed for the logon phase; Windows starts but ends in a black screen, logon loop or immediate sign-out.':
        'Wird für die Anmeldephase gebraucht; Windows startet, endet aber in einem schwarzen Bildschirm, einer Anmeldeschleife oder einer sofortigen Abmeldung.',
    '{len(bad)} boot-critical system files are missing or damaged':
        '{len(bad)} startkritische Systemdateien fehlen oder sind beschädigt',
    'Many core files are affected at once, which points to file-system corruption, a failed/aborted update, or files deleted by a cleanup tool or malware. Windows stops at the first one it needs.':
        'Viele Kerndateien sind gleichzeitig betroffen. Das deutet auf Dateisystemschäden, ein fehlgeschlagenes oder abgebrochenes Update oder von einem Aufräumprogramm bzw. Schadsoftware gelöschte Dateien hin. Windows hält bei der ersten an, die es braucht.',
    '{len(unreadable)} system file(s) could not be read from Linux':
        '{len(unreadable)} Systemdatei(en) konnten unter Linux nicht gelesen werden',
    "Usually these are compressed with Windows' CompactOS/WOF compression which the Linux NTFS driver cannot decompress, or the file is a reparse point. Not necessarily a problem - but they could not be verified. Read errors on a failing disk look the same, so check the disk findings.":
        'Meist sind diese mit der CompactOS/WOF-Komprimierung von Windows gepackt, die der Linux-NTFS-Treiber nicht entpacken kann, oder die Datei ist ein Analysepunkt. Nicht unbedingt ein Problem – sie konnten nur nicht überprüft werden. Lesefehler einer defekten Festplatte sehen genauso aus, prüfen Sie daher die Festplatten-Befunde.',
    'Boot-critical file {status_word(st)}: \\{rel}':
        'Startkritische Datei {status_word(st)}: \\{rel}',
    'Windows keeps an older copy of this hive (RegBack, {size}, from {rb_time}). Keep the damaged file under another name and put the copy in its place:\n`cd C:\\Windows\\System32\\config\nren {name} {name}.broken\nren {name}.LOG1 {name}.LOG1.broken\nren {name}.LOG2 {name}.LOG2.broken\ncopy RegBack\\{name} {name}`':
        'Windows hat eine ältere Kopie dieser Struktur (RegBack, {size}, vom {rb_time}). Benennen Sie die beschädigte Datei um und setzen Sie die Kopie an ihre Stelle:\n`cd C:\\Windows\\System32\\config\nren {name} {name}.broken\nren {name}.LOG1 {name}.LOG1.broken\nren {name}.LOG2 {name}.LOG2.broken\ncopy RegBack\\{name} {name}`',
    'Settings, drivers and updates installed after that date are lost.':
        'Einstellungen, Treiber und Updates, die nach diesem Datum installiert wurden, gehen verloren.',
    'If there is no restore point, the remaining options are restoring a full backup or reinstalling Windows (copy your files off first).':
        'Gibt es keinen Wiederherstellungspunkt, bleiben nur das Zurückspielen einer vollständigen Sicherung oder eine Neuinstallation von Windows (kopieren Sie Ihre Dateien vorher weg).',
    'Registry hive {name} is missing':
        'Registrierungsstruktur {name} fehlt',
    '\\Windows\\System32\\config\\{name} does not exist. Windows cannot start without it.':
        '\\Windows\\System32\\config\\{name} existiert nicht. Ohne sie kann Windows nicht starten.',
    'Registry hive {name} is structurally damaged':
        'Registrierungsstruktur {name} ist strukturell beschädigt',
    'Registry hive {name} cannot be read':
        'Registrierungsstruktur {name} kann nicht gelesen werden',
    'Reading the hive file failed - bad sectors or file-system corruption.':
        'Das Lesen der Strukturdatei ist fehlgeschlagen – fehlerhafte Sektoren oder Dateisystemschäden.',
    'Registry hive {name} is corrupt':
        'Registrierungsstruktur {name} ist beschädigt',
    'The {name} hive has internal corruption. Windows tries to repair hives from their .LOG files; when that fails it stops with a registry/configuration bug check.':
        'Die Struktur {name} ist intern beschädigt. Windows versucht, Strukturen aus ihren .LOG-Dateien zu reparieren; schlägt das fehl, hält es mit einem Registrierungs- bzw. Konfigurationsfehler (Bluescreen) an.',
    'SYSTEM hive has no valid current control set':
        'Die SYSTEM-Struktur hat keinen gültigen aktuellen ControlSet',
    'HKLM\\SYSTEM\\Select\\Current points to a ControlSet that does not exist, so winload has no driver/service configuration to boot with.':
        'HKLM\\SYSTEM\\Select\\Current zeigt auf einen ControlSet, der nicht existiert; winload hat also keine Treiber- und Dienstkonfiguration für den Start.',
    'The {name} hive is not a valid registry file any more. Windows stops during startup.':
        'Die Struktur {name} ist keine gültige Registrierungsdatei mehr. Windows hält beim Start an.',
    " Logs present: {', '.join(logs)}.":
        " Vorhandene Protokolle: {', '.join(logs)}.",
    ' No transaction logs are available.':
        ' Es gibt keine Transaktionsprotokolle.',
    'Registry hive {name} has unflushed changes in its log files':
        'Die Registrierungsstruktur {name} hat noch nicht übernommene Änderungen in ihren Protokolldateien',
    'Normal after an unclean shutdown: Windows replays the .LOG files at the next start.':
        'Normal nach einem unsauberen Herunterfahren: Windows spielt die .LOG-Dateien beim nächsten Start ein.',
    'Registry hive {name} was not saved completely and has no logs':
        'Die Registrierungsstruktur {name} wurde nicht vollständig gespeichert und hat keine Protokolle',
    'The hive was being written when Windows went down and the transaction logs that would complete it are missing - recent configuration changes may be lost or inconsistent.':
        'Die Struktur wurde gerade geschrieben, als Windows ausfiel, und die Transaktionsprotokolle, die sie vervollständigen würden, fehlen – kürzliche Konfigurationsänderungen können verloren oder widersprüchlich sein.',
    ' Without it, winload cannot load the system configuration.':
        ' Ohne sie kann winload die Systemkonfiguration nicht laden.',
    'Undo the update that is waiting to be installed:\n`dism /image:C:\\ /cleanup-image /revertpendingactions`':
        'Das Update rückgängig machen, das auf seine Installation wartet:\n`dism /image:C:\\ /cleanup-image /revertpendingactions`',
    'A Windows Update operation is pending (WinSxS\\pending.xml)':
        'Ein Windows-Update-Vorgang steht aus (WinSxS\\pending.xml)',
    "An update was staged and will be completed during the next start ('Working on updates' / 'Preparing Windows'). If completing it fails, Windows rolls back and restarts - often in an endless 'Undoing changes made to your computer' loop.":
        'Ein Update wurde bereitgestellt und wird beim nächsten Start abgeschlossen („Updates werden bearbeitet“ / „Windows wird vorbereitet“). Schlägt das fehl, nimmt Windows es zurück und startet neu – oft in einer endlosen Schleife „Die an Ihrem Computer vorgenommenen Änderungen werden rückgängig gemacht“.',
    "If dism reports an error, set the update's instruction file aside by hand:\n`ren C:\\Windows\\WinSxS\\pending.xml pending.xml.old`":
        'Meldet dism einen Fehler, legen Sie die Anweisungsdatei des Updates von Hand beiseite:\n`ren C:\\Windows\\WinSxS\\pending.xml pending.xml.old`',
    'A feature update was rolled back':
        'Ein Funktionsupdate wurde zurückgenommen',
    '$WINDOWS.~BT\\Sources\\Rollback exists: an upgrade to a newer Windows version failed and was undone.':
        '$WINDOWS.~BT\\Sources\\Rollback existiert: Ein Upgrade auf eine neuere Windows-Version ist fehlgeschlagen und wurde rückgängig gemacht.',
    'A feature update is staged or in progress ($WINDOWS.~BT)':
        'Ein Funktionsupdate ist bereitgestellt oder läuft ($WINDOWS.~BT)',
    'Windows Setup files for an upgrade are on the disk.':
        'Setup-Dateien für ein Windows-Upgrade liegen auf der Festplatte.',
    'Servicing reports a reboot in progress':
        'Die Wartung meldet einen laufenden Neustart',
    'Component Based Servicing was in the middle of a reboot-time operation.':
        'Die komponentenbasierte Wartung war mitten in einem Vorgang, der beim Neustart ausgeführt wird.',
    'Windows is stuck in Setup / OOBE mode':
        'Windows hängt im Setup-/OOBE-Modus fest',
    "The registry still says that Windows Setup is running. Every start launches the setup phase again ('Windows installation cannot proceed' / 'The computer restarted unexpectedly or encountered an unexpected error') instead of the normal logon.":
        'Laut Registrierung läuft das Windows-Setup noch. Jeder Start beginnt die Setup-Phase von vorn („Die Windows-Installation kann nicht fortgesetzt werden“ / „Der Computer wurde unerwartet neu gestartet, oder es ist ein unerwarteter Fehler aufgetreten“) statt der normalen Anmeldung.',
    'When the error message appears, press Shift+F10. A command prompt opens.':
        'Wenn die Fehlermeldung erscheint, drücken Sie Umschalt+F10. Eine Eingabeaufforderung öffnet sich.',
    'Tell Windows Setup that its last phase has finished, then restart:\n`reg add HKLM\\SYSTEM\\Setup\\Status\\ChildCompletion /v setup.exe /t REG_DWORD /d 3 /f\nshutdown /r /t 0`':
        'Dem Windows-Setup mitteilen, dass seine letzte Phase abgeschlossen ist, dann neu starten:\n`reg add HKLM\\SYSTEM\\Setup\\Status\\ChildCompletion /v setup.exe /t REG_DWORD /d 3 /f\nshutdown /r /t 0`',
    'If this was an aborted upgrade to a new Windows version, go back to the old one instead: in Automatic Repair choose Troubleshoot → Advanced options → Uninstall Updates → “Uninstall latest feature update”.':
        'War es ein abgebrochenes Upgrade auf eine neue Windows-Version, kehren Sie stattdessen zur alten zurück: In der automatischen Reparatur „Problembehandlung“ → „Erweiterte Optionen“ → „Updates deinstallieren“ → „Neuestes Funktionsupdate deinstallieren“ wählen.',
    ' Windows has not recorded a successful start since this update was staged (last successful start: {last_boot:%Y-%m-%d %H:%M} UTC).':
        ' Windows hat seit der Bereitstellung dieses Updates keinen erfolgreichen Start mehr aufgezeichnet (letzter erfolgreicher Start: {last_boot:%Y-%m-%d %H:%M} UTC).',
    'Windows last started as build {lbv[0]}.{lbv[1]}, but the registry already reports update level .{ubr} - the update was only partly installed':
        'Windows wurde zuletzt als Build {lbv[0]}.{lbv[1]} gestartet, die Registrierung meldet aber schon den Update-Stand .{ubr} – das Update wurde nur teilweise installiert',
    " Startup Repair names a recent driver update as the cause, and these are that update's driver files still waiting to be swapped in at the next start.":
        ' Die Starthilfe nennt ein kürzliches Treiberupdate als Ursache, und dies sind die Treiberdateien dieses Updates, die noch auf den Austausch beim nächsten Start warten.',
    ' No pending update or driver file operations are left on the disk now, so the change it refers to has been undone or cleared. If Windows still fails, run Startup Repair once more.':
        ' Auf der Festplatte stehen jetzt keine Update- oder Treiberdateivorgänge mehr aus; die genannte Änderung wurde also rückgängig gemacht oder entfernt. Startet Windows weiterhin nicht, führen Sie die Starthilfe noch einmal aus.',
    'Windows does not start':
        'Windows startet nicht',
    "Windows does not start: {top['title']}":
        "Windows startet nicht: {top['title']}",
    ' Windows started successfully afterwards, on {last_boot:%Y-%m-%d %H:%M} UTC.':
        ' Windows ist danach erfolgreich gestartet, am {last_boot:%Y-%m-%d %H:%M} UTC.',
    'Failed starts happened before the event log service could run':
        'Fehlgeschlagene Starts endeten, bevor der Ereignisprotokolldienst laufen konnte',
    'The System event log ends at {last_log:%Y-%m-%d %H:%M} UTC, but crash dumps / Startup Repair logs are newer. The failing starts therefore die early (kernel, boot drivers or Session Manager), before Windows can write events.':
        'Das Systemereignisprotokoll endet am {last_log:%Y-%m-%d %H:%M} UTC, aber Absturzabbilder bzw. Starthilfe-Protokolle sind neuer. Die fehlgeschlagenen Starts brechen also früh ab (Kernel, Starttreiber oder Sitzungsverwaltung), bevor Windows Ereignisse schreiben kann.',
    'Windows has a critical problem':
        'Windows hat ein kritisches Problem',
    "Critical problem: {top['title']}":
        "Kritisches Problem: {top['title']}",
    ' This is newer than the last successful start ({last_boot:%Y-%m-%d %H:%M} UTC).':
        ' Das ist neuer als der letzte erfolgreiche Start ({last_boot:%Y-%m-%d %H:%M} UTC).',
    'Startup breaks at stage “{stage}”.':
        'Der Start bricht in der Phase „{stage}“ ab.',
    'Analysis incomplete':
        'Analyse unvollständig',
    'Analysis incomplete: {inc}':
        'Analyse unvollständig: {inc}',
    'No definite boot blocker was found in the parts that could be analysed.':
        'In den Teilen, die analysiert werden konnten, wurde kein eindeutiges Starthindernis gefunden.',
    'Boot partition, boot configuration, system files, registry and drivers look intact.':
        'Startpartition, Startkonfiguration, Systemdateien, Registrierung und Treiber sehen intakt aus.',
    'No definite boot blocker found':
        'Kein eindeutiges Starthindernis gefunden',
    'No definite boot blocker found - but there are warnings':
        'Kein eindeutiges Starthindernis gefunden – aber es gibt Warnungen',
    'No problems found':
        'Keine Probleme gefunden',
    'No problems found that would prevent Windows from starting':
        'Keine Probleme gefunden, die den Start von Windows verhindern würden',
    "The most important warning: {top['title']}.":
        "Die wichtigste Warnung: {top['title']}.",
    'no readable NTFS volume':
        'kein lesbares NTFS-Volume',
    'NTFS boot sector is damaged':
        'Der NTFS-Startsektor ist beschädigt',
    'Open the partition in TestDisk:\n`sudo testdisk {dev}`':
        'Die Partition in TestDisk öffnen:\n`sudo testdisk {dev}`',
    'BitLocker volume unlocked read-only for analysis':
        'BitLocker-Volume für die Analyse schreibgeschützt entsperrt',
    "If Windows stops at the blue 'BitLocker recovery' screen, entering the key there lets it boot; the usual trigger is a BIOS update, Secure Boot / TPM change or a changed boot order.":
        'Hält Windows am blauen Bildschirm „BitLocker-Wiederherstellung“ an, startet es nach Eingabe des Schlüssels dort; der übliche Auslöser ist ein BIOS-Update, eine Änderung an Secure Boot bzw. TPM oder eine geänderte Startreihenfolge.',
    'No Windows installation on this partition':
        'Keine Windows-Installation auf dieser Partition',
    'The volume mounts fine, but there is no \\Windows\\System32 directory. Either the wrong partition was selected, or the Windows directory was deleted.':
        'Das Volume lässt sich einbinden, aber es gibt kein Verzeichnis \\Windows\\System32. Entweder wurde die falsche Partition ausgewählt, oder das Windows-Verzeichnis wurde gelöscht.',
    'no Windows directory found':
        'kein Windows-Verzeichnis gefunden',
    'NTFS boot sector is destroyed (backup copy is intact)':
        'Der NTFS-Startsektor ist zerstört (die Sicherungskopie ist intakt)',
    'The first sector of the Windows volume no longer identifies it as NTFS, so nothing - neither Boot Manager nor Windows - can open the volume. The backup boot sector at the end of the partition is still valid, so this is repairable.':
        'Der erste Sektor des Windows-Volumes kennzeichnet es nicht mehr als NTFS, daher kann nichts – weder der Start-Manager noch Windows – das Volume öffnen. Der Sicherungs-Startsektor am Ende der Partition ist noch gültig; das ist also reparierbar.',
    "The volume's boot sector has invalid geometry, so the volume cannot be opened by Boot Manager or Windows.":
        'Der Startsektor des Volumes hat eine ungültige Geometrie, daher können weder der Start-Manager noch Windows das Volume öffnen.',
    'Choose Advanced → Boot → “Backup BS”. That copies the intact backup boot sector over the damaged one.':
        '„Advanced“ → „Boot“ → „Backup BS“ wählen. Das kopiert den intakten Sicherungs-Startsektor über den beschädigten.',
    'Choose Advanced → Boot → “Rebuild BS”, let it search, and write the result if the file listing (“List”) shows your files.':
        '„Advanced“ → „Boot“ → „Rebuild BS“ wählen, suchen lassen und das Ergebnis schreiben, wenn die Dateiliste („List“) Ihre Dateien zeigt.',
    'Volume is BitLocker-encrypted - Windows itself could not be analysed':
        'Das Volume ist mit BitLocker verschlüsselt – Windows selbst konnte nicht analysiert werden',
    'Without the recovery key the contents (BCD target, registry, drivers, logs) cannot be read. Only disk-level and boot-partition checks were done. Note: a BitLocker volume that asks for the recovery key at boot is usually caused by a firmware/TPM/Secure Boot change, not damage.':
        'Ohne den Wiederherstellungsschlüssel lassen sich die Inhalte (BCD-Ziel, Registrierung, Treiber, Protokolle) nicht lesen. Es wurden nur Prüfungen der Festplatte und der Startpartition durchgeführt. Hinweis: Verlangt ein BitLocker-Volume beim Start den Wiederherstellungsschlüssel, liegt das meist an einer Änderung an Firmware, TPM oder Secure Boot, nicht an einem Schaden.',
    'BitLocker volume locked':
        'BitLocker-Volume gesperrt',
    'NTFS file system is larger than its partition':
        'Das NTFS-Dateisystem ist größer als seine Partition',
    "The partition was shrunk (or moved) without shrinking the NTFS volume first. Windows' boot loader and NTFS refuse such a volume or hit corruption at the end of the disk area, giving 0xc0000225 / UNMOUNTABLE_BOOT_VOLUME.":
        'Die Partition wurde verkleinert (oder verschoben), ohne das NTFS-Volume zuerst zu verkleinern. Das Startladeprogramm von Windows und NTFS lehnen ein solches Volume ab oder stoßen am Ende auf Beschädigungen; die Folge ist 0xc0000225 / UNMOUNTABLE_BOOT_VOLUME.',
    'NTFS metadata ($MFT) is damaged':
        'Die NTFS-Metadaten ($MFT) sind beschädigt',
    'The master file table could not be read cleanly. Boot Manager and winload cannot reliably read files from this volume.':
        'Die Master File Table konnte nicht sauber gelesen werden. Start-Manager und winload können Dateien von diesem Volume nicht zuverlässig lesen.',
    'The Windows volume cannot be mounted':
        'Das Windows-Volume kann nicht eingebunden werden',
    'Both Linux NTFS drivers refused the volume, which means its file-system structures are badly damaged. Boot Manager/winload will not be able to read Windows from it either.':
        'Beide Linux-NTFS-Treiber haben das Volume abgelehnt; seine Dateisystemstrukturen sind also schwer beschädigt. Auch Start-Manager bzw. winload werden Windows nicht davon lesen können.',
    'Windows volume could not be mounted':
        'Windows-Volume konnte nicht eingebunden werden',
    'Go back and select the partition that contains the Windows folder.':
        'Gehen Sie zurück und wählen Sie die Partition, die den Windows-Ordner enthält.',
    'Windows is hibernated / in Fast Startup state':
        'Windows befindet sich im Ruhezustand bzw. Schnellstart-Zustand',
    'Windows volume is full ({human_size(free)} free)':
        'Das Windows-Volume ist voll ({human_size(free)} frei)',
    'Windows needs free space during startup for the registry hives, the page file, logs and update servicing. With the volume full, startup hangs, loops or ends in a crash.':
        'Windows braucht beim Start freien Platz für die Registrierungsstrukturen, die Auslagerungsdatei, Protokolle und die Update-Wartung. Ist das Volume voll, hängt der Start, läuft in einer Schleife oder endet in einem Absturz.',
    'The selected partition is empty (no file system)':
        'Die ausgewählte Partition ist leer (kein Dateisystem)',
    'The start of the partition is all zeros - the partition was wiped, re-created or overwritten.':
        'Der Anfang der Partition besteht nur aus Nullen – die Partition wurde gelöscht, neu angelegt oder überschrieben.',
    'The selected partition does not contain NTFS (found: {kind})':
        'Die ausgewählte Partition enthält kein NTFS (gefunden: {kind})',
    'Windows can only be installed on NTFS. Either the wrong partition was selected or the volume was reformatted.':
        'Windows lässt sich nur auf NTFS installieren. Entweder wurde die falsche Partition ausgewählt, oder das Volume wurde neu formatiert.',
    ' The backup boot sector is still valid.':
        ' Der Sicherungs-Startsektor ist noch gültig.',
    'Find the 48-digit recovery key: sign in at https://account.microsoft.com/devices/recoverykey with the Microsoft account used on this PC, or look for your printout.':
        'Den 48-stelligen Wiederherstellungsschlüssel finden: Melden Sie sich unter https://account.microsoft.com/devices/recoverykey mit dem Microsoft-Konto an, das auf diesem PC verwendet wird, oder suchen Sie Ihren Ausdruck.',
    'Go back, select this partition again, enter the key under “More options” and repeat the analysis.':
        'Gehen Sie zurück, wählen Sie diese Partition erneut, geben Sie den Schlüssel unter „Weitere Optionen“ ein und wiederholen Sie die Analyse.',
    'BitLocker unlock failed - Windows itself could not be analysed':
        'Entsperren von BitLocker fehlgeschlagen – Windows selbst konnte nicht analysiert werden',
    'The recovery key was not accepted (or cryptsetup cannot open this BitLocker version).':
        'Der Wiederherstellungsschlüssel wurde nicht angenommen (oder cryptsetup kann diese BitLocker-Version nicht öffnen).',
    'BitLocker unlock failed':
        'Entsperren von BitLocker fehlgeschlagen',
    'Grow the partition back to at least the size of the file system. Use GParted, keep the start of the partition where it is and only move its end.':
        'Vergrößern Sie die Partition wieder mindestens auf die Größe des Dateisystems. Verwenden Sie GParted, lassen Sie den Anfang der Partition, wo er ist, und verschieben Sie nur das Ende.',
    'NTFS volume is marked dirty':
        'Das NTFS-Volume ist als fehlerhaft („dirty“) markiert',
    "Windows did not unmount the volume cleanly (crash, power loss, forced shutdown, or a disk check was requested). At the next start autochk runs; on a damaged disk this can hang or loop ('Scanning and repairing drive C:').":
        'Windows hat das Volume nicht sauber getrennt (Absturz, Stromausfall, erzwungenes Ausschalten oder eine angeforderte Datenträgerprüfung). Beim nächsten Start läuft autochk; auf einer beschädigten Festplatte kann das hängen oder sich wiederholen („Laufwerk C: wird überprüft und repariert“).',
    "If chkdsk cannot open the volume either, copy the whole partition to an image file on another disk before trying anything else (replace the two paths):\n`sudo ddrescue {ctx.target['path']} /path/to/windows.img /path/to/windows.map`":
        "Kann auch chkdsk das Volume nicht öffnen, kopieren Sie zuerst die ganze Partition in eine Abbilddatei auf einer anderen Festplatte, bevor Sie etwas anderes versuchen (die beiden Pfade ersetzen):\n`sudo ddrescue {ctx.target['path']} /path/to/windows.img /path/to/windows.map`",
    "Then let TestDisk look for the file system in the partition:\n`sudo testdisk {ctx.target['path']}`":
        "Dann TestDisk in der Partition nach dem Dateisystem suchen lassen:\n`sudo testdisk {ctx.target['path']}`",
    'hiberfil.sys contains a valid hibernation image, so Boot Manager will try to resume that image instead of booting fresh. If the disk was changed in the meantime (by Linux, by a partition tool, or a different PC) the resume crashes or the volume gets corrupted.':
        'hiberfil.sys enthält ein gültiges Ruhezustandsabbild, daher versucht der Start-Manager, dieses Abbild fortzusetzen, statt neu zu starten. Wurde die Festplatte in der Zwischenzeit verändert (durch Linux, ein Partitionierungswerkzeug oder einen anderen PC), stürzt das Fortsetzen ab oder das Volume wird beschädigt.',
    'Try to start Windows normally first; it may simply resume.':
        'Versuchen Sie zuerst, Windows normal zu starten; vielleicht setzt es einfach fort.',
    'If resuming fails, delete the hibernation image. Unsaved work from that session is lost, and Windows then starts fresh:\n`del /a C:\\hiberfil.sys`':
        'Schlägt das Fortsetzen fehl, löschen Sie das Ruhezustandsabbild. Nicht gespeicherte Arbeit dieser Sitzung geht verloren, und Windows startet neu:\n`del /a C:\\hiberfil.sys`',
    'Turn hibernation and Fast Startup off so this cannot happen again:\n`powercfg /h off`':
        'Ruhezustand und Schnellstart ausschalten, damit das nicht wieder passiert:\n`powercfg /h off`',
    'Delete the downloaded update files (Windows downloads them again when needed):\n`rd /s /q C:\\Windows\\SoftwareDistribution\\Download`':
        'Die heruntergeladenen Update-Dateien löschen (Windows lädt sie bei Bedarf erneut herunter):\n`rd /s /q C:\\Windows\\SoftwareDistribution\\Download`',
    'Delete temporary files:\n`del /s /q C:\\Windows\\Temp\\*`':
        'Temporäre Dateien löschen:\n`del /s /q C:\\Windows\\Temp\\*`',
    'If that is not enough, move large personal files (videos, downloads) to another drive. Aim for at least 10 GB free.':
        'Reicht das nicht, verschieben Sie große persönliche Dateien (Videos, Downloads) auf ein anderes Laufwerk. Ziel: mindestens 10 GB frei.',
    'Very little free space on the Windows volume ({human_size(free)})':
        'Sehr wenig freier Platz auf dem Windows-Volume ({human_size(free)})',
    'Updates fail and can roll back at boot when less than a few GB are free.':
        'Updates schlagen fehl und können beim Start zurückgenommen werden, wenn weniger als einige GB frei sind.',
    'Go back and check that you selected the right partition.':
        'Gehen Sie zurück und prüfen Sie, ob Sie die richtige Partition ausgewählt haben.',
    'If Windows really was here, stop writing to this disk and search for the lost file system:\n`sudo testdisk {dev}`':
        'War Windows wirklich hier, schreiben Sie nichts mehr auf diese Festplatte und suchen Sie nach dem verlorenen Dateisystem:\n`sudo testdisk {dev}`',
    'Go back and select the partition that contains Windows.':
        'Gehen Sie zurück und wählen Sie die Partition, die Windows enthält.',
    'Check the recovery key (48 digits in 8 groups of 6) and run the analysis again.':
        'Prüfen Sie den Wiederherstellungsschlüssel (48 Ziffern in 8 Gruppen zu 6) und starten Sie die Analyse erneut.',
    'Do not use the Linux tool ntfsfix for this: it only clears the flag without repairing anything.':
        'Verwenden Sie dafür nicht das Linux-Werkzeug ntfsfix: Es entfernt nur die Markierung, ohne etwas zu reparieren.',
    ' The volume is currently mounted read-write by Linux, which is exactly that risk.':
        ' Das Volume ist gerade unter Linux beschreibbar eingebunden – genau dieses Risiko.',
    'Delete or move large personal files until at least 10 GB are free.':
        'Löschen oder verschieben Sie große persönliche Dateien, bis mindestens 10 GB frei sind.',
    "Analysing /dev/{part['name']}":
        "Analyse von /dev/{part['name']}",
    'Cancel':
        'Abbrechen',
    'Restart':
        'Neu starten',
    'Repairing {target}':
        'Reparatur von {target}',
    'Undo':
        'Rückgängig machen',
    'Please wait - BootRepair is still working':
        'Bitte warten – BootRepair arbeitet noch',
    'Cancelling - unmounting…':
        'Wird abgebrochen – Einbindungen werden gelöst…',
    'Partitions are mounted read-only; nothing is written.':
        'Partitionen werden schreibgeschützt eingebunden; es wird nichts geschrieben.',
    'Report copied':
        'Bericht kopiert',
    'Restart into Windows?':
        'In Windows neu starten?',
    'The computer restarts now and starts Windows Boot Manager once. The start after that uses the normal boot order again. Save your work in other apps first.':
        'Der Computer startet jetzt neu und startet einmalig den Windows-Start-Manager. Der Start danach verwendet wieder die normale Startreihenfolge. Speichern Sie vorher Ihre Arbeit in anderen Programmen.',
    'Repairing…':
        'Reparatur läuft…',
    'Waiting for administrator authorisation…':
        'Warte auf Administratorberechtigung…',
    'Repair finished':
        'Reparatur abgeschlossen',
    'Undo repair?':
        'Reparatur rückgängig machen?',
    'Restoring the original files':
        'Originaldateien werden wiederhergestellt',
    'Error':
        'Fehler',
    'Back':
        'Zurück',
    'Diagnoses why Windows does not start and repairs it - analysis is read-only, every repair is backed up and can be undone.':
        'Findet heraus, warum Windows nicht startet, und repariert es – die Analyse ist schreibgeschützt, jede Reparatur wird gesichert und kann rückgängig gemacht werden.',
    'Analysis cancelled':
        'Analyse abgebrochen',
    'The analysis could not be completed':
        'Die Analyse konnte nicht abgeschlossen werden',
    'Save repair guide':
        'Reparaturanleitung speichern',
    'Save report':
        'Bericht speichern',
    'Saved {f.get_basename()}':
        '{f.get_basename()} gespeichert',
    'Backing up and applying the selected repairs…':
        'Ausgewählte Reparaturen werden gesichert und angewendet…',
    'The repair could not be completed':
        'Die Reparatur konnte nicht abgeschlossen werden',
    'Firmware entries that were deleted cannot be re-created.':
        'Gelöschte Firmware-Einträge können nicht neu angelegt werden.',
    'Undoing…':
        'Wird rückgängig gemacht…',
    'Undo finished':
        'Rückgängig gemacht',
    'Details':
        'Details',
    'Unknown error':
        'Unbekannter Fehler',
    'Could not save: {e.strerror}':
        'Speichern nicht möglich: {e.strerror}',
    'Undo failed':
        'Rückgängigmachen fehlgeschlagen',
    'Could not set up the restart':
        'Der Neustart konnte nicht vorbereitet werden',
    'Windows starts at the next restart ({e.message})':
        'Windows startet beim nächsten Neustart ({e.message})',
    'Restores every file and setting changed by this repair.':
        'Stellt jede Datei und Einstellung wieder her, die diese Reparatur geändert hat.',
    'Restores every file and setting changed by the most recent repair.':
        'Stellt jede Datei und Einstellung wieder her, die die letzte Reparatur geändert hat.',
    "\\{dst_rel} restored from \\{p['src']} ({os.path.getsize(dst)} bytes)":
        "\\{dst_rel} aus \\{p['src']} wiederhergestellt ({os.path.getsize(dst)} Bytes)",
    'hiberfil.sys renamed - Windows will do a fresh start':
        'hiberfil.sys umbenannt – Windows startet neu',
    'object {guid} not found':
        'Objekt {guid} nicht gefunden',
    'created Boot{n}':
        'Boot{n} angelegt',
    "BootOrder: {','.join(order)} -> {','.join(new)}":
        "BootOrder: {','.join(order)} -> {','.join(new)}",
    'Boot{num} activated':
        'Boot{num} aktiviert',
    'Boot{num} removed':
        'Boot{num} entfernt',
    'invalid control set name':
        'ungültiger ControlSet-Name',
    "'{p['filter']}' is no longer in {p['value']} - nothing to do":
        "„{p['filter']}“ ist nicht mehr in {p['value']} – nichts zu tun",
    'no pending operations left':
        'keine ausstehenden Vorgänge mehr',
    'values already gone':
        'Werte bereits entfernt',
    '\\Windows\\WinSxS\\pending.xml renamed to pending.xml.bootrepair-{c.stamp}':
        '\\Windows\\WinSxS\\pending.xml umbenannt in pending.xml.bootrepair-{c.stamp}',
    'nothing pending any more':
        'nichts mehr ausstehend',
    'invalid hive':
        'ungültige Struktur',
    'RegBack copy is empty':
        'RegBack-Kopie ist leer',
    '{hive} restored from RegBack':
        '{hive} aus RegBack wiederhergestellt',
    'hiberfil.sys is already gone':
        'hiberfil.sys ist bereits entfernt',
    'entries already point at this partition':
        'Einträge zeigen bereits auf diese Partition',
    'BCD key {path} not found':
        'BCD-Schlüssel {path} nicht gefunden',
    '{{bootmgr}} has no default setting to change':
        '{{bootmgr}} hat keine Standardeinstellung, die geändert werden könnte',
    'unexpected identifier format':
        'unerwartetes Format der Kennung',
    'target entry not found':
        'Zieleintrag nicht gefunden',
    "\\EFI\\Microsoft\\Boot\\{str(rel).replace('/', chr(92))}":
        "\\EFI\\Microsoft\\Boot\\{str(rel).replace('/', chr(92))}",
    'copied {len(out)} files':
        '{len(out)} Dateien kopiert',
    "efibootmgr {' '.join(args)}: {(r.stderr or r.stdout).strip()}":
        "efibootmgr {' '.join(args)}: {(r.stderr or r.stdout).strip()}",
    'invalid boot entry number':
        'ungültige Nummer des Starteintrags',
    'invalid disk/partition':
        'ungültige Festplatte/Partition',
    '{partition} not found':
        '{partition} nicht gefunden',
    "Windows is hibernated (Fast Startup). Writing to it now would be lost or corrupt the volume when Windows resumes. Include 'Discard the hibernation image' or boot Windows and shut it down fully first.":
        'Windows befindet sich im Ruhezustand (Schnellstart). Was jetzt geschrieben wird, geht beim Fortsetzen verloren oder beschädigt das Volume. Wählen Sie zusätzlich „Ruhezustandsabbild verwerfen“, oder starten Sie Windows und fahren Sie es vorher vollständig herunter.',
    'unknown repair actions: {unknown}':
        'unbekannte Reparaturvorgänge: {unknown}',
    "partition {info['path']} not found":
        "Partition {info['path']} nicht gefunden",
    '\\{rel} not found':
        '\\{rel} nicht gefunden',
    '\\{rel} has unsaved transaction-log data (sequence {h.seq1}/{h.seq2}); editing it from Linux could lose that data. Let Windows/WinRE start once, or use the manual steps.':
        '\\{rel} hat noch nicht übernommene Transaktionsprotokolldaten (Sequenz {h.seq1}/{h.seq2}); eine Bearbeitung unter Linux könnte diese Daten verlieren. Lassen Sie Windows bzw. die Wiederherstellungsumgebung einmal starten, oder verwenden Sie die manuellen Schritte.',
    "source \\{p['src']} is not a valid program file":
        "Quelle \\{p['src']} ist keine gültige Programmdatei",
    '{lp.name} renamed':
        '{lp.name} umbenannt',
    'BCD object {g} no longer exists':
        'BCD-Objekt {g} existiert nicht mehr',
    'verification failed: entry does not point at the target after the change':
        'Überprüfung fehlgeschlagen: Der Eintrag zeigt nach der Änderung nicht auf das Ziel',
    'invalid element id':
        'ungültige Element-Kennung',
    'refusing to delete the default entry':
        'der Standardeintrag wird nicht gelöscht',
    'repairs on BitLocker-encrypted volumes are not supported yet - use the manual steps':
        'Reparaturen an BitLocker-verschlüsselten Volumes werden noch nicht unterstützt – verwenden Sie die manuellen Schritte',
    'the Windows partition is not mounted writable':
        'die Windows-Partition ist nicht beschreibbar eingebunden',
    'the boot partition is not mounted writable':
        'die Startpartition ist nicht beschreibbar eingebunden',
    'no boot partition given':
        'keine Startpartition angegeben',
    "restored {e['rel']}":
        "{e['rel']} wiederhergestellt",
    "cannot open the Windows volume for writing: {e}. If it is marked dirty, run 'chkdsk C: /f' from WinRE first (BootRepair will not write to an unclean NTFS).":
        'Das Windows-Volume kann nicht zum Schreiben geöffnet werden: {e}. Ist es als fehlerhaft markiert, führen Sie zuerst in der Wiederherstellungsumgebung „chkdsk C: /f“ aus (BootRepair schreibt nicht auf ein unsauberes NTFS).',
    "removed {e['rel']}":
        "{e['rel']} entfernt",
    "renamed {e['to']} back to {e['from']}":
        "{e['to']} zurück in {e['from']} umbenannt",
    'firmware entry change reverted':
        'Änderung am Firmware-Eintrag rückgängig gemacht',
    "cannot recreate a deleted firmware entry ({e.get('note', '')})":
        "ein gelöschter Firmware-Eintrag kann nicht neu angelegt werden ({e.get('note', '')})",
    'Getting to the Windows recovery command prompt':
        'So erreichen Sie die Eingabeaufforderung der Windows-Wiederherstellung',
    'In the Windows recovery command prompt':
        'In der Eingabeaufforderung der Windows-Wiederherstellung',
    'In a Linux terminal':
        'In einem Linux-Terminal',
    'Later, once Windows runs again (administrator command prompt)':
        'Später, wenn Windows wieder läuft (Eingabeaufforderung als Administrator)',
    'Start the PC and choose Windows. After two failed starts in a row Windows opens “Automatic Repair” by itself; choose “Advanced options” there. If that screen never appears, boot from a Windows installation USB stick and choose “Repair your computer”.':
        'Schalten Sie den PC ein und wählen Sie Windows. Nach zwei fehlgeschlagenen Starts hintereinander öffnet Windows von selbst die „Automatische Reparatur“; wählen Sie dort „Erweiterte Optionen“. Erscheint dieser Bildschirm nie, starten Sie von einem Windows-Installations-USB-Stick und wählen Sie „Computerreparaturoptionen“.',
    'Choose Troubleshoot → Advanced options → Command Prompt.':
        'Wählen Sie „Problembehandlung“ → „Erweiterte Optionen“ → „Eingabeaufforderung“.',
    'Drive letters are often different in the recovery environment. List the volumes:\n`diskpart\nlist vol\nexit`':
        'In der Wiederherstellungsumgebung sind die Laufwerksbuchstaben oft anders. Die Volumes auflisten:\n`diskpart\nlist vol\nexit`',
    'Yours is the {size} NTFS volume labelled “{lab}”.':
        'Ihres ist das {size} große NTFS-Volume mit der Bezeichnung „{lab}“.',
    'Yours is the {size} NTFS volume.':
        'Ihres ist das {size} große NTFS-Volume.',
    'Your EFI partition is the {size} FAT32 volume.':
        'Ihre EFI-Partition ist das {size} große FAT32-Volume.',
    'Check the letter:\n`dir C:\\Windows`\nIf that reports “File Not Found”, try D:, E: and so on, and use the letter that works instead of C: in every command.':
        'Den Buchstaben prüfen:\n`dir C:\\Windows`\nMeldet das „Datei nicht gefunden“, probieren Sie D:, E: usw. und verwenden Sie in jedem Befehl den funktionierenden Buchstaben statt C:.',
    'Steps that need it tell you how to give it the letter S:.':
        'Schritte, die sie brauchen, erklären, wie Sie ihr den Buchstaben S: geben.',
    'Repair guide - {name}':
        'Reparaturanleitung – {name}',
    'Repair guide for {name}':
        'Reparaturanleitung für {name}',
    "created {report['generated'][:16].replace('T', ' ')} UTC by BootRepair {report['version']}":
        "erstellt {report['generated'][:16].replace('T', ' ')} UTC mit BootRepair {report['version']}",
    'Work through the sections from top to bottom and try to start Windows after each one. Commands are typed exactly as shown, one line at a time, each followed by Enter.':
        'Arbeiten Sie die Abschnitte von oben nach unten ab und versuchen Sie nach jedem, Windows zu starten. Befehle werden genau so eingegeben, wie sie dastehen, eine Zeile nach der anderen, jeweils gefolgt von der Eingabetaste.',
    'This guide calls the Windows volume C:.':
        'Diese Anleitung nennt das Windows-Volume C:.',
    'No manual repair steps are needed.':
        'Es sind keine manuellen Reparaturschritte nötig.',
    'STOPS WINDOWS':
        'VERHINDERT DEN START',
    'SHOULD BE FIXED':
        'SOLLTE BEHOBEN WERDEN',
    'What you see on screen:':
        'Was auf dem Bildschirm steht:',
    'BEFORE YOU START':
        'BEVOR SIE BEGINNEN',
    'Evidence':
        'Belege',
    'Check and repair the file system of the Windows volume:\n`chkdsk C: /f`':
        'Das Dateisystem des Windows-Volumes prüfen und reparieren:\n`chkdsk C: /f`',
    'Check the file system and scan for unreadable sectors (takes a long time):\n`chkdsk C: /f /r`':
        'Das Dateisystem prüfen und nach unlesbaren Sektoren suchen (dauert lange):\n`chkdsk C: /f /r`',
    'Leave the command prompt (`exit`) and choose Troubleshoot → Advanced options → Uninstall Updates → “Uninstall latest quality update”.':
        'Verlassen Sie die Eingabeaufforderung (`exit`) und wählen Sie „Problembehandlung“ → „Erweiterte Optionen“ → „Updates deinstallieren“ → „Neuestes Qualitätsupdate deinstallieren“.',
    'Leave the command prompt (`exit`) and choose Troubleshoot → Advanced options → System Restore, then pick a restore point from before the problem started.':
        'Verlassen Sie die Eingabeaufforderung (`exit`) und wählen Sie „Problembehandlung“ → „Erweiterte Optionen“ → „Systemwiederherstellung“; wählen Sie dann einen Wiederherstellungspunkt von vor dem Problem.',
    'Copy your important files to another disk first. Every further start attempt stresses a failing drive.':
        'Kopieren Sie zuerst Ihre wichtigen Dateien auf eine andere Festplatte. Jeder weitere Startversuch belastet ein ausfallendes Laufwerk.',
    'Disk drives':
        'Laufwerke',
    'Volumes':
        'Volumes',
    'Storage controllers (SCSI/RAID/NVMe)':
        'Speichercontroller (SCSI/RAID/NVMe)',
    'IDE ATA/ATAPI controllers':
        'IDE-ATA/ATAPI-Controller',
    'Volume shadow copies':
        'Volumeschattenkopien',
    'DVD/CD-ROM drives':
        'DVD/CD-ROM-Laufwerke',
    'Keyboards':
        'Tastaturen',
    'Mice':
        'Mäuse',
    'USB controllers':
        'USB-Controller',
    'System devices':
        'Systemgeräte',
    'A driver accessed invalid memory at a high IRQL - usually a faulty driver, sometimes bad RAM.':
        'Ein Treiber hat bei hohem IRQL auf ungültigen Speicher zugegriffen – meist ein fehlerhafter Treiber, manchmal defekter Arbeitsspeicher.',
    'Memory-manager corruption - often defective RAM or a buggy driver.':
        'Beschädigung in der Speicherverwaltung – oft defekter Arbeitsspeicher oder ein fehlerhafter Treiber.',
    'A kernel-mode driver raised an exception nobody handled.':
        'Ein Kernelmodus-Treiber hat eine Ausnahme ausgelöst, die niemand behandelt hat.',
    'The NTFS driver hit corruption on the volume - run chkdsk, check the disk.':
        'Der NTFS-Treiber ist auf Beschädigungen im Volume gestoßen – chkdsk ausführen, Festplatte prüfen.',
    'Hardware memory parity error - RAM or hardware fault.':
        'Paritätsfehler im Arbeitsspeicher – Arbeitsspeicher- oder Hardwarefehler.',
    'Kernel phase-1 initialisation failed.':
        'Initialisierungsphase 1 des Kernels ist fehlgeschlagen.',
    'Exception in a system service - usually a faulty driver.':
        'Ausnahme in einem Systemdienst – meist ein fehlerhafter Treiber.',
    'System page table entries exhausted - leaking driver.':
        'Systemseitentabelleneinträge erschöpft – ein Treiber gibt Speicher nicht frei.',
    'Page frame list corrupt - driver bug or defective RAM.':
        'Seitenrahmenliste beschädigt – Treiberfehler oder defekter Arbeitsspeicher.',
    'Invalid memory referenced - faulty driver, antivirus filter, or bad RAM.':
        'Zugriff auf ungültigen Speicher – fehlerhafter Treiber, Antivirus-Filter oder defekter Arbeitsspeicher.',
    'Severe registry error - a hive is corrupt or I/O to it failed.':
        'Schwerer Registrierungsfehler – eine Struktur ist beschädigt oder der Zugriff darauf ist fehlgeschlagen.',
    'The HAL could not initialise - firmware/ACPI problem or wrong HAL.':
        'Die HAL konnte nicht initialisiert werden – Firmware-/ACPI-Problem oder falsche HAL.',
    'Registry could not be initialised - SYSTEM hive missing or unreadable.':
        'Die Registrierung konnte nicht initialisiert werden – SYSTEM-Struktur fehlt oder ist nicht lesbar.',
    'Phase-1 process initialisation failed - corrupt system files (often after a failed update).':
        'Prozessinitialisierung in Phase 1 fehlgeschlagen – beschädigte Systemdateien (oft nach einem fehlgeschlagenen Update).',
    'Session manager initialisation failed - corrupt system files.':
        'Initialisierung der Sitzungsverwaltung fehlgeschlagen – beschädigte Systemdateien.',
    'The SYSTEM registry hive is corrupt or contains invalid configuration.':
        'Die SYSTEM-Registrierungsstruktur ist beschädigt oder enthält eine ungültige Konfiguration.',
    'Kernel stack could not be read from the page file - disk or controller failure.':
        'Der Kernel-Stack konnte nicht aus der Auslagerungsdatei gelesen werden – Festplatten- oder Controllerfehler.',
    'Exception during kernel phase 0 - firmware/hardware or HAL problem.':
        'Ausnahme in Kernelphase 0 – Firmware-/Hardware- oder HAL-Problem.',
    'Kernel data could not be read from disk - bad sectors, failing disk, loose cable or controller fault.':
        'Kerneldaten konnten nicht von der Festplatte gelesen werden – fehlerhafte Sektoren, ausfallende Festplatte, lockeres Kabel oder Controllerfehler.',
    'Windows lost access to the system disk during startup - missing/disabled storage driver (AHCI/RAID/VMD/NVMe change), filter driver problem, or file-system corruption.':
        'Windows hat beim Start den Zugriff auf die Systemfestplatte verloren – fehlender oder deaktivierter Speichertreiber (Wechsel bei AHCI/RAID/VMD/NVMe), Problem mit einem Filtertreiber oder Dateisystemschaden.',
    'A system thread crashed - usually a specific driver.':
        'Ein Systemthread ist abgestürzt – meist ein bestimmter Treiber.',
    'CPU trap in kernel mode - hardware fault, overclock or driver.':
        'CPU-Trap im Kernelmodus – Hardwarefehler, Übertaktung oder Treiber.',
    'Kernel-mode exception - faulty driver or RAM.':
        'Ausnahme im Kernelmodus – fehlerhafter Treiber oder Arbeitsspeicher.',
    'CPU machine check - hardware failure.':
        'CPU-Maschinenprüfung – Hardwareausfall.',
    'A driver did not complete a power transition (often during resume/Fast Startup).':
        'Ein Treiber hat einen Energiezustandswechsel nicht abgeschlossen (oft beim Fortsetzen bzw. Schnellstart).',
    "The firmware's ACPI tables are not compatible - update the BIOS/UEFI.":
        'Die ACPI-Tabellen der Firmware sind nicht kompatibel – BIOS/UEFI aktualisieren.',
    'A driver wrote to read-only memory.':
        'Ein Treiber hat in schreibgeschützten Speicher geschrieben.',
    'Invalid pool request by a driver.':
        'Ungültige Pool-Anforderung durch einen Treiber.',
    'Driver Verifier caught a driver bug - Verifier is enabled on this system.':
        'Die Treiberüberprüfung hat einen Treiberfehler entdeckt – sie ist auf diesem System eingeschaltet.',
    'A driver corrupted pool memory.':
        'Ein Treiber hat Pool-Speicher beschädigt.',
    'A driver accessed paged/invalid memory at raised IRQL.':
        'Ein Treiber hat bei erhöhtem IRQL auf ausgelagerten bzw. ungültigen Speicher zugegriffen.',
    'The boot volume could not be mounted - file-system corruption or disk I/O failure.':
        'Das Startvolume konnte nicht eingebunden werden – Dateisystemschaden oder Festplatten-E/A-Fehler.',
    'A critical system process (smss, csrss, wininit, services, lsass...) died - corrupt system files, failed update, or malware/AV interference.':
        'Ein kritischer Systemprozess (smss, csrss, wininit, services, lsass …) ist beendet worden – beschädigte Systemdateien, fehlgeschlagenes Update oder Störung durch Schadsoftware bzw. Antivirus.',
    'A critical process terminated - often disk I/O failure or corrupt files.':
        'Ein kritischer Prozess wurde beendet – oft Festplatten-E/A-Fehler oder beschädigte Dateien.',
    'A driver overran a stack buffer.':
        'Ein Treiber hat einen Stapelpuffer überschritten.',
    'Execution of non-executable memory - driver bug.':
        'Ausführung von nicht ausführbarem Speicher – Treiberfehler.',
    'USB driver error.':
        'USB-Treiberfehler.',
    'A CPU core stopped responding - hardware, overclock or firmware.':
        'Ein CPU-Kern reagiert nicht mehr – Hardware, Übertaktung oder Firmware.',
    'Kernel code/data was modified - driver bug, bad RAM or rootkit.':
        'Kernelcode bzw. -daten wurden verändert – Treiberfehler, defekter Arbeitsspeicher oder Rootkit.',
    'The graphics driver could not be reset.':
        'Der Grafiktreiber konnte nicht zurückgesetzt werden.',
    'The graphics driver stopped responding (live dump).':
        'Der Grafiktreiber reagiert nicht mehr (Live-Abbild).',
    'Graphics scheduler error - GPU driver.':
        'Fehler im Grafik-Scheduler – GPU-Treiber.',
    'Fatal hardware error reported by the CPU/chipset (CPU, RAM, PCIe, overclock, power).':
        'Schwerer Hardwarefehler, gemeldet von CPU bzw. Chipsatz (CPU, Arbeitsspeicher, PCIe, Übertaktung, Stromversorgung).',
    'A driver spent too long at DPC level - storage (often SATA/NVMe firmware) or other driver.':
        'Ein Treiber hat zu lange auf DPC-Ebene verbracht – Speicher (oft SATA/NVMe-Firmware) oder ein anderer Treiber.',
    'A kernel data structure was corrupted - driver bug or incompatible driver.':
        'Eine Kernel-Datenstruktur wurde beschädigt – Treiberfehler oder inkompatibler Treiber.',
    'Kernel heap corruption - driver bug.':
        'Beschädigung des Kernel-Heaps – Treiberfehler.',
    'Graphics engine timeout (live dump).':
        'Zeitüberschreitung der Grafik-Engine (Live-Abbild).',
    'USB 3 driver error.':
        'USB-3-Treiberfehler.',
    'Memory store component exception - frequently a failing disk or storage driver.':
        'Ausnahme in der Speicherverwaltungskomponente – häufig eine ausfallende Festplatte oder ein Speichertreiber.',
    'Modern standby watchdog.':
        'Watchdog des modernen Standbys.',
    'Win32k power watchdog.':
        'Win32k-Energie-Watchdog.',
    'System hang watchdog.':
        'Watchdog für hängendes System.',
    'USB-C live dump.':
        'USB-C-Live-Abbild.',
    'Graphics live dump.':
        'Grafik-Live-Abbild.',
    'winlogon or csrss terminated - corrupt system files, failed update, third-party software or mismatched system DLLs.':
        'winlogon oder csrss wurde beendet – beschädigte Systemdateien, fehlgeschlagenes Update, Fremdsoftware oder nicht zueinander passende System-DLLs.',
    'A registry hive file could not be loaded - corrupt or missing hive.':
        'Eine Registrierungsstrukturdatei konnte nicht geladen werden – beschädigte oder fehlende Struktur.',
    'A driver or system DLL is corrupt (checksum mismatch).':
        'Ein Treiber oder eine System-DLL ist beschädigt (Prüfsumme stimmt nicht).',
    'Graphics driver stuck.':
        'Grafiktreiber hängt.',
    'Windows kernel':
        'Windows-Kernel',
    'Hardware Abstraction Layer':
        'Hardwareabstraktionsschicht (HAL)',
    'Code Integrity (driver signature verification)':
        'Codeintegrität (Prüfung der Treibersignaturen)',
    'kernel debugger transport (loaded by winload)':
        'Transport des Kerneldebuggers (von winload geladen)',
    'Platform Specific Hardware Error Driver':
        'Plattformspezifischer Hardwarefehlertreiber',
    'boot video driver':
        'Startvideo-Treiber',
    'Common Log File System driver':
        'Treiber des Common Log File System',
    'NTFS file-system driver':
        'NTFS-Dateisystemtreiber',
    'disk class driver':
        'Datenträgerklassentreiber',
    'storage class support driver':
        'Unterstützungstreiber für Speicherklassen',
    'partition manager':
        'Partitionsverwaltung',
    'volume manager':
        'Volumeverwaltung',
    'dynamic volume manager':
        'Verwaltung dynamischer Volumes',
    'mount manager':
        'Bereitstellungsverwaltung',
    'file-system filter manager':
        'Filter-Manager des Dateisystems',
    'kernel security support':
        'Kernel-Sicherheitsunterstützung',
    'kernel cryptography':
        'Kernel-Kryptografie',
    'kernel-mode driver framework':
        'Kernelmodus-Treiberframework',
    'ACPI driver':
        'ACPI-Treiber',
    'PCI bus driver':
        'PCI-Bustreiber',
    'Session Manager':
        'Sitzungsverwaltung',
    'Client/Server Runtime (critical process)':
        'Client/Server-Laufzeit (kritischer Prozess)',
    'Windows start-up application (critical process)':
        'Windows-Startanwendung (kritischer Prozess)',
    'Service Control Manager (critical process)':
        'Dienststeuerungs-Manager (kritischer Prozess)',
    'NT layer DLL':
        'NT-Schicht-DLL',
    'Win32 base API':
        'Win32-Basis-API',
    'boot-time disk check':
        'Datenträgerprüfung beim Start',
    'Local Security Authority (critical process)':
        'Lokale Sicherheitsautorität (kritischer Prozess)',
    'Windows Logon':
        'Windows-Anmeldung',
    'logon screen':
        'Anmeldebildschirm',
    'user initialisation':
        'Benutzerinitialisierung',
    'desktop shell':
        'Desktop-Shell',
    'Unexpected restart (Kernel-Power 41)':
        'Unerwarteter Neustart (Kernel-Power 41)',
    'The system restarted without shutting down cleanly: it crashed, hung, lost power or was reset.':
        'Das System wurde ohne sauberes Herunterfahren neu gestartet: Es ist abgestürzt, hing, hatte keinen Strom mehr oder wurde zurückgesetzt.',
    'Previous shutdown was unexpected (EventLog 6008)':
        'Das vorherige Herunterfahren war unerwartet (EventLog 6008)',
    'The previous session ended without a clean shutdown.':
        'Die vorherige Sitzung endete ohne sauberes Herunterfahren.',
    'Blue screen recorded (BugCheck 1001)':
        'Bluescreen aufgezeichnet (BugCheck 1001)',
    'Windows recorded a bug check (blue screen) after rebooting.':
        'Windows hat nach dem Neustart einen Fehlerabbruch (Bluescreen) aufgezeichnet.',
    'Boot-start or system-start drivers failed to load (SCM 7026)':
        'Treiber für Boot- oder Systemstart konnten nicht geladen werden (SCM 7026)',
    'One or more drivers that start during boot did not load.':
        'Einer oder mehrere Treiber, die beim Start laden, wurden nicht geladen.',
    'Service failed to start (SCM 7000)':
        'Dienst konnte nicht gestartet werden (SCM 7000)',
    'A service could not be started.':
        'Ein Dienst konnte nicht gestartet werden.',
    'Service dependency failed (SCM 7001)':
        'Dienstabhängigkeit fehlgeschlagen (SCM 7001)',
    'A service could not start because a service it depends on failed.':
        'Ein Dienst konnte nicht starten, weil ein Dienst fehlgeschlagen ist, von dem er abhängt.',
    'Service start timed out (SCM 7009)':
        'Zeitüberschreitung beim Dienststart (SCM 7009)',
    'A service did not respond in time during startup (can make boot hang).':
        'Ein Dienst hat beim Start nicht rechtzeitig reagiert (kann den Start hängen lassen).',
    'Service hung on starting (SCM 7022)':
        'Dienst hängt beim Starten (SCM 7022)',
    'A service hung while starting.':
        'Ein Dienst hing beim Starten.',
    'Service terminated with an error (SCM 7023)':
        'Dienst mit Fehler beendet (SCM 7023)',
    'A service stopped with an error during startup.':
        'Ein Dienst wurde beim Start mit einem Fehler beendet.',
    'Service terminated with a service-specific error (SCM 7024)':
        'Dienst mit dienstspezifischem Fehler beendet (SCM 7024)',
    'A service stopped with an error.':
        'Ein Dienst wurde mit einem Fehler beendet.',
    'Service crashed (SCM 7031)':
        'Dienst abgestürzt (SCM 7031)',
    'A service terminated unexpectedly.':
        'Ein Dienst wurde unerwartet beendet.',
    'Service crashed (SCM 7034)':
        'Dienst abgestürzt (SCM 7034)',
    'Bad block on disk (disk 7)':
        'Fehlerhafter Block auf der Festplatte (disk 7)',
    'The disk reported a bad block - the drive has unreadable sectors.':
        'Die Festplatte hat einen fehlerhaften Block gemeldet – das Laufwerk hat unlesbare Sektoren.',
    'Disk controller error (disk 11)':
        'Fehler des Festplattencontrollers (disk 11)',
    'The driver detected a controller error - cable, port, controller or the drive itself.':
        'Der Treiber hat einen Controllerfehler erkannt – Kabel, Anschluss, Controller oder das Laufwerk selbst.',
    'Paging I/O error (disk 51)':
        'E/A-Fehler beim Auslagern (disk 51)',
    'An error was detected during a paging operation - typically a failing disk or connection.':
        'Bei einem Auslagerungsvorgang wurde ein Fehler erkannt – typischerweise eine ausfallende Festplatte oder Verbindung.',
    'Disk predicts its own failure (disk 52, S.M.A.R.T.)':
        'Die Festplatte sagt ihren eigenen Ausfall voraus (disk 52, S.M.A.R.T.)',
    "The drive's S.M.A.R.T. self-monitoring predicts that it will fail.":
        'Die S.M.A.R.T.-Selbstüberwachung des Laufwerks sagt voraus, dass es ausfallen wird.',
    'Disk I/O retried (disk 153)':
        'Festplatten-E/A wiederholt (disk 153)',
    'I/O operations had to be retried - an early sign of a failing disk or connection.':
        'E/A-Vorgänge mussten wiederholt werden – ein frühes Zeichen für eine ausfallende Festplatte oder Verbindung.',
    'NTFS corruption detected (Ntfs 55)':
        'NTFS-Beschädigung erkannt (Ntfs 55)',
    'NTFS found corrupt file-system structures on a volume.':
        'NTFS hat auf einem Volume beschädigte Dateisystemstrukturen gefunden.',
    'Volume reported as corrupt (Ntfs 98)':
        'Volume als beschädigt gemeldet (Ntfs 98)',
    'NTFS reported that a volume is corrupt and needs to be checked with chkdsk.':
        'NTFS hat gemeldet, dass ein Volume beschädigt ist und mit chkdsk geprüft werden muss.',
    'NTFS transaction error (Ntfs 137)':
        'NTFS-Transaktionsfehler (Ntfs 137)',
    'The default transaction resource manager could not start - often file-system corruption.':
        'Der Standard-Transaktionsressourcenmanager konnte nicht starten – oft ein Dateisystemschaden.',
    'NTFS failed to flush data (Ntfs 140)':
        'NTFS konnte Daten nicht schreiben (Ntfs 140)',
    'The system failed to flush data to the transaction log - corruption may occur.':
        'Das System konnte Daten nicht in das Transaktionsprotokoll schreiben – Beschädigungen sind möglich.',
    'Crash dump initialisation failed (volmgr 46)':
        'Initialisierung von Absturzabbildern fehlgeschlagen (volmgr 46)',
    'Windows could not prepare crash dumps - blue screens may leave no dump file.':
        'Windows konnte keine Absturzabbilder vorbereiten – Bluescreens hinterlassen eventuell keine Abbilddatei.',
    'Dump file creation failed (volmgr 161)':
        'Erstellen der Abbilddatei fehlgeschlagen (volmgr 161)',
    'A crash dump could not be written - often not enough disk space or a page-file problem.':
        'Ein Absturzabbild konnte nicht geschrieben werden – oft zu wenig Speicherplatz oder ein Problem mit der Auslagerungsdatei.',
    'Fatal hardware error (WHEA 1)':
        'Schwerer Hardwarefehler (WHEA 1)',
    'A fatal hardware error occurred.':
        'Ein schwerer Hardwarefehler ist aufgetreten.',
    'Fatal hardware error (WHEA 18)':
        'Schwerer Hardwarefehler (WHEA 18)',
    'A fatal CPU/machine-check hardware error occurred.':
        'Ein schwerer CPU- bzw. Maschinenprüfungs-Hardwarefehler ist aufgetreten.',
    'Corrected hardware error (WHEA 19)':
        'Korrigierter Hardwarefehler (WHEA 19)',
    'A corrected hardware error occurred.':
        'Ein korrigierter Hardwarefehler ist aufgetreten.',
    'Corrected PCIe error (WHEA 17)':
        'Korrigierter PCIe-Fehler (WHEA 17)',
    'A corrected PCI Express error occurred.':
        'Ein korrigierter PCI-Express-Fehler ist aufgetreten.',
    'Fatal memory/PCIe error (WHEA 46)':
        'Schwerer Speicher-/PCIe-Fehler (WHEA 46)',
    'Corrected memory error (WHEA 47)':
        'Korrigierter Speicherfehler (WHEA 47)',
    'A corrected memory error occurred.':
        'Ein korrigierter Speicherfehler ist aufgetreten.',
    'Storage controller reset (storahci 129)':
        'Speichercontroller zurückgesetzt (storahci 129)',
    'The SATA disk stopped responding and the controller had to be reset.':
        'Die SATA-Festplatte hat nicht mehr reagiert und der Controller musste zurückgesetzt werden.',
    'NVMe controller reset (stornvme 129)':
        'NVMe-Controller zurückgesetzt (stornvme 129)',
    'The NVMe disk stopped responding and had to be reset.':
        'Die NVMe-Festplatte hat nicht mehr reagiert und musste zurückgesetzt werden.',
    'NVMe controller error (stornvme 11)':
        'NVMe-Controllerfehler (stornvme 11)',
    'The NVMe controller reported an error.':
        'Der NVMe-Controller hat einen Fehler gemeldet.',
    'Intel RST device timeout (iaStorA 9)':
        'Zeitüberschreitung eines Intel-RST-Geräts (iaStorA 9)',
    'The disk did not respond within the timeout.':
        'Die Festplatte hat nicht innerhalb der Zeitüberschreitung reagiert.',
    'Intel RST controller reset (iaStorAC 129)':
        'Intel-RST-Controller zurückgesetzt (iaStorAC 129)',
    'The disk stopped responding.':
        'Die Festplatte hat nicht mehr reagiert.',
    'Driver failed to load for a device (Kernel-PnP 219)':
        'Treiber für ein Gerät konnte nicht geladen werden (Kernel-PnP 219)',
    'A device driver failed to load.':
        'Ein Gerätetreiber konnte nicht geladen werden.',
    'Fast Startup failed (Kernel-Boot 29)':
        'Schnellstart fehlgeschlagen (Kernel-Boot 29)',
    'Windows failed to resume from its Fast Startup image and did a full boot.':
        'Windows konnte nicht aus seinem Schnellstart-Abbild fortsetzen und hat vollständig neu gestartet.',
    'Startup Repair ran (StartupRepair 1002)':
        'Die Starthilfe lief (StartupRepair 1002)',
    'Startup Repair attempted to fix the system.':
        'Die Starthilfe hat versucht, das System zu reparieren.',
    'Winlogon notification failure (Winlogon 6004)':
        'Fehler einer Winlogon-Benachrichtigung (Winlogon 6004)',
    'A Winlogon notification subscriber failed.':
        'Ein Empfänger von Winlogon-Benachrichtigungen ist fehlgeschlagen.',
    "Load Windows' {hive} registry hive under a temporary name:\n`reg load HKLM\\OFFLINE C:\\Windows\\System32\\config\\{hive}`":
        'Die Registrierungsstruktur {hive} von Windows unter einem vorübergehenden Namen laden:\n`reg load HKLM\\OFFLINE C:\\Windows\\System32\\config\\{hive}`',
    'Unload the hive again, otherwise the change is not saved:\n`reg unload HKLM\\OFFLINE`':
        'Die Struktur wieder entladen, sonst wird die Änderung nicht gespeichert:\n`reg unload HKLM\\OFFLINE`',
    'General':
        'Allgemein',
    'Disk & firmware':
        'Festplatte & Firmware',
    'The firmware reads the disk, the partition table and finds the boot partition.':
        'Die Firmware liest die Festplatte und die Partitionstabelle und findet die Startpartition.',
    'Boot Manager':
        'Start-Manager',
    'The firmware starts Windows Boot Manager (bootmgfw.efi on UEFI, BOOTMGR on BIOS).':
        'Die Firmware startet den Windows-Start-Manager (bootmgfw.efi bei UEFI, BOOTMGR bei BIOS).',
    'Boot configuration (BCD)':
        'Startkonfiguration (BCD)',
    'Boot Manager reads the BCD store to find out which Windows to start and where it lives.':
        'Der Start-Manager liest den BCD-Speicher, um herauszufinden, welches Windows er starten soll und wo es liegt.',
    'OS loader (winload)':
        'Ladeprogramm (winload)',
    'winload reads the Windows volume, the SYSTEM hive, the kernel, the HAL and all boot-start drivers.':
        'winload liest das Windows-Volume, die SYSTEM-Struktur, den Kernel, die HAL und alle Starttreiber.',
    'Kernel & boot drivers':
        'Kernel & Starttreiber',
    'The kernel initialises, boot drivers start and the storage stack mounts the system volume.':
        'Der Kernel initialisiert sich, Starttreiber starten und der Speicherstapel bindet das Systemvolume ein.',
    'Session Manager & services':
        'Sitzungsverwaltung & Dienste',
    'smss, csrss, wininit and services.exe start; pending updates and disk checks run here.':
        'smss, csrss, wininit und services.exe starten; ausstehende Updates und Datenträgerprüfungen laufen hier.',
    'Logon':
        'Anmeldung',
    'winlogon, LogonUI, userinit and the shell start.':
        'winlogon, LogonUI, userinit und die Shell starten.',
    'warning':
        'Warnung',
    'fails':
        'schlägt fehl',
    'not analysed':
        'nicht analysiert',
    'Critical - prevents Windows from starting':
        'Kritisch – verhindert den Start von Windows',
    'Warnings - may be involved':
        'Warnungen – möglicherweise beteiligt',
    'Additional information':
        'Zusätzliche Informationen',
    'BootRepair report':
        'BootRepair-Bericht',
    'Generated {gen} - version {ver}':
        'Erstellt {gen} – Version {ver}',
    'Windows partition':
        'Windows-Partition',
    'Disk':
        'Festplatte',
    'Verdict':
        'Ergebnis',
    'Boot chain':
        'Startkette',
    'Boot partition':
        'Startpartition',
    'Crash dumps':
        'Absturzabbilder',
    'Boot-relevant events (newest first)':
        'Startrelevante Ereignisse (neueste zuerst)',
    'How to fix by hand':
        'Manuelle Reparatur',
    'Stage':
        'Phase',
    'stop code':
        'Stoppcode',
    'BootRepair can fix this':
        'BootRepair kann das beheben',
    'Every changed file is backed up first and can be restored with “Undo last repair”.':
        'Jede geänderte Datei wird vorher gesichert und lässt sich mit „Letzte Reparatur rückgängig machen“ wiederherstellen.',
    'Repair it yourself':
        'Selbst reparieren',
    'How to fix':
        'So beheben Sie es',
    'Copied':
        'Kopiert',
    'Recovery command prompt':
        'Eingabeaufforderung der Wiederherstellung',
    'Windows has its own repair environment. All steps marked “In the Windows recovery command prompt” are typed there.':
        'Windows hat eine eigene Reparaturumgebung. Alle Schritte mit der Kennzeichnung „In der Eingabeaufforderung der Windows-Wiederherstellung“ werden dort eingegeben.',
    'REPAIR GUIDE':
        'REPARATURANLEITUNG',
    'Guide copied':
        'Anleitung kopiert',
    'Repair guide':
        'Reparaturanleitung',
    'Save as a web page (to read on your phone while repairing)':
        'Als Webseite speichern (zum Lesen auf dem Handy während der Reparatur)',
    'Copy the whole guide as text':
        'Die ganze Anleitung als Text kopieren',
    'Work through the problems from top to bottom and try to start Windows after each one. Linux is not running while you repair Windows, so save this guide as a web page (save button above) and open it on your phone.':
        'Arbeiten Sie die Probleme von oben nach unten ab und versuchen Sie nach jedem, Windows zu starten. Während Sie Windows reparieren, läuft Linux nicht – speichern Sie diese Anleitung daher als Webseite (Speichern-Knopf oben) und öffnen Sie sie auf Ihrem Handy.',
    'Before you start':
        'Bevor Sie beginnen',
    'Nothing needs to be repaired by hand.':
        'Es muss nichts von Hand repariert werden.',
    'Let BootRepair do this instead…':
        'Das stattdessen BootRepair erledigen lassen…',
    'Stops Windows':
        'Verhindert den Start',
    'Should be fixed':
        'Sollte behoben werden',
    'Analysing…':
        'Analyse läuft…',
    'low risk':
        'geringes Risiko',
    'medium risk':
        'mittleres Risiko',
    'high risk':
        'hohes Risiko',
    'Repair automatically':
        'Automatisch reparieren',
    'BootRepair writes to your disk for these repairs. Every file is backed up first, and "Undo last repair" in the menu restores it byte for byte. Select what to do:':
        'Für diese Reparaturen schreibt BootRepair auf Ihre Festplatte. Jede Datei wird vorher gesichert, und „Letzte Reparatur rückgängig machen“ im Menü stellt sie Byte für Byte wieder her. Wählen Sie aus, was geschehen soll:',
    'Repairs need the Windows volume to be closed cleanly. If it is hibernated or marked dirty, BootRepair refuses to write to it.':
        'Reparaturen setzen ein sauber geschlossenes Windows-Volume voraus. Befindet es sich im Ruhezustand oder ist es als fehlerhaft markiert, schreibt BootRepair nicht darauf.',
    'Repair':
        'Reparieren',
    'What was done':
        'Was getan wurde',
    'Analyse again':
        'Erneut analysieren',
    'Some repairs failed':
        'Einige Reparaturen sind fehlgeschlagen',
    'The original files have been restored.':
        'Die Originaldateien wurden wiederhergestellt.',
    'Run the analysis again to confirm, then try starting Windows. If it still fails, the new report shows what is left.':
        'Analysieren Sie zur Kontrolle erneut und versuchen Sie dann, Windows zu starten. Schlägt es weiter fehl, zeigt der neue Bericht, was noch übrig ist.',
    'Original files saved in':
        'Originaldateien gespeichert in',
    'Restart into Windows':
        'In Windows neu starten',
    'Undo these repairs':
        'Diese Reparaturen rückgängig machen',
    'Undo complete':
        'Rückgängig gemacht',
    'Repairs applied':
        'Reparaturen angewendet',
    'Save repair guide as web page…':
        'Reparaturanleitung als Webseite speichern…',
    'Save report as Markdown…':
        'Bericht als Markdown speichern…',
    'Save report as JSON…':
        'Bericht als JSON speichern…',
    'Copy report':
        'Bericht kopieren',
    'Undo last repair…':
        'Letzte Reparatur rückgängig machen…',
    'About BootRepair':
        'Über BootRepair',
    'Choose another partition':
        'Andere Partition wählen',
    'Restart into Windows…':
        'In Windows neu starten…',
    'Where startup stops':
        'Wo der Start abbricht',
    'Boot- and system-start drivers':
        'Boot- und Systemstart-Treiber',
    'Device class filters':
        'Filter der Geräteklassen',
    'Boot-critical files':
        'Startkritische Dateien',
    'Storage controller driver':
        'Treiber des Speichercontrollers',
    'Boot log (ntbtlog.txt)':
        'Startprotokoll (ntbtlog.txt)',
    'Servicing / setup state':
        'Wartungs- und Setup-Status',
    'Disk & partition table':
        'Festplatte & Partitionstabelle',
    'Windows volume':
        'Windows-Volume',
    'Disk health (SMART)':
        'Festplattenzustand (SMART)',
    'Pending file operations':
        'Ausstehende Dateivorgänge',
    'Session Manager start programs':
        'Startprogramme der Sitzungsverwaltung',
    'Menu':
        'Menü',
    'In the order they should be fixed. Open one for the explanation, the evidence and the repair.':
        'In der Reihenfolge, in der sie behoben werden sollten. Öffnen Sie eines für Erklärung, Belege und Reparatur.',
    'Background information - nothing here stops Windows':
        'Hintergrundinformationen – nichts davon verhindert den Start',
    'default':
        'Standard',
    'Firmware boot entries (this computer)':
        'Firmware-Starteinträge (dieser Computer)',
    'Crash dumps ({len(crashes)})':
        'Absturzabbilder ({len(crashes)})',
    'Newest first':
        'Neueste zuerst',
    'Startup Repair log (SrtTrail.txt)':
        'Starthilfe-Protokoll (SrtTrail.txt)',
    'Latest Startup Repair session':
        'Letzte Starthilfe-Sitzung',
    "{srt['info'].get('repair_attempts', '?')} repair attempt(s)":
        "{srt['info'].get('repair_attempts', '?')} Reparaturversuch(e)",
    "{s['records']} records from {s['first'][:10]} to {s['last'][:10]} · last start {last_start} · last clean shutdown {last_shutdown}":
        "{s['records']} Einträge vom {s['first'][:10]} bis {s['last'][:10]} · letzter Start {last_start} · letztes sauberes Herunterfahren {last_shutdown}",
    "Boot-relevant events ({len(evs['timeline'])})":
        "Startrelevante Ereignisse ({len(evs['timeline'])})",
    'Analysis log':
        'Analyseprotokoll',
    '(no device/path settings)':
        '(keine Geräte- oder Pfadeinstellungen)',
    'Repair automatically ({n})':
        'Automatisch reparieren ({n})',
    '  (live report)':
        '  (Live-Bericht)',
    'Authentication was cancelled. Administrator rights are needed to access the disk.':
        'Die Authentifizierung wurde abgebrochen. Für den Zugriff auf die Festplatte sind Administratorrechte nötig.',
    'Could not start the BootRepair helper: {e.message}':
        'Das BootRepair-Hilfsprogramm konnte nicht gestartet werden: {e.message}',
    'Not authorised, or no polkit authentication agent is running. Alternatively run in a terminal:  {cmd}':
        'Nicht berechtigt, oder es läuft kein Polkit-Authentifizierungsagent. Alternativ in einem Terminal ausführen:  {cmd}',
    'The helper exited with code {code}.':
        'Das Hilfsprogramm wurde mit Code {code} beendet.',
    'unknown error':
        'unbekannter Fehler',
    'Automatic':
        'Automatisch',
    'Language':
        'Sprache',
    'Holds Windows Boot Manager and the boot configuration':
        'Enthält den Windows-Start-Manager und die Startkonfiguration',
    'Look for drives again':
        'Erneut nach Laufwerken suchen',
    'Analyse':
        'Analysieren',
    'Which Windows does not start?':
        'Welches Windows startet nicht?',
    'BootRepair only reads your disks while it analyses them. Nothing is changed until you choose a repair yourself.':
        'BootRepair liest Ihre Festplatten während der Analyse nur. Es wird nichts verändert, bis Sie selbst eine Reparatur auswählen.',
    'Windows installations':
        'Windows-Installationen',
    'No partition looks like a Windows installation. Choose one under “Other partitions”.':
        'Keine Partition sieht wie eine Windows-Installation aus. Wählen Sie eine unter „Andere Partitionen“.',
    'This partition is encrypted. Enter its 48-digit recovery key so the contents can be analysed (it is used read-only and not stored).':
        'Diese Partition ist verschlüsselt. Geben Sie ihren 48-stelligen Wiederherstellungsschlüssel ein, damit der Inhalt analysiert werden kann (er wird nur lesend verwendet und nicht gespeichert).',
    'Recovery key':
        'Wiederherstellungsschlüssel',
    'More options':
        'Weitere Optionen',
    'Boot partition, event log':
        'Startpartition, Ereignisprotokoll',
    'Automatic (recommended)':
        'Automatisch (empfohlen)',
    'Read the System event log':
        'Systemereignisprotokoll lesen',
    'Finds crashes and disk errors; adds a few seconds':
        'Findet Abstürze und Festplattenfehler; dauert ein paar Sekunden länger',
    'Choose a partition':
        'Partition auswählen',
    'no file system':
        'kein Dateisystem',
    "Windows partition “{p['label']}”":
        "Windows-Partition „{p['label']}“",
    'Other partitions':
        'Andere Partitionen',
    'If Windows is somewhere unexpected, or its file system is damaged':
        'Falls Windows an unerwarteter Stelle liegt oder sein Dateisystem beschädigt ist',
    'Could not list the drives':
        'Die Laufwerke konnten nicht aufgelistet werden',
    'Note':
        'Hinweis',
    'Boot manager':
        'Start-Manager',
    'Boot config':
        'Startkonfig.',
    'Loader':
        'Lader',
    'Kernel':
        'Kernel',
    'Services':
        'Dienste',
    'Copy':
        'Kopieren',
    'How do I get there?':
        'Wie komme ich dorthin?',
    'file does not exist':
        'Datei existiert nicht',
    'cannot stat: {e.strerror}':
        'Dateiinformationen nicht abrufbar: {e.strerror}',
    'is a directory':
        'ist ein Verzeichnis',
    'file is 0 bytes':
        'Datei ist 0 Byte groß',
    'read error: {e.strerror} (file may be damaged, or WOF/LZX-compressed and unsupported by the Linux NTFS driver)':
        'Lesefehler: {e.strerror} (die Datei ist beschädigt oder WOF/LZX-komprimiert, was der Linux-NTFS-Treiber nicht unterstützt)',
    'first {len(head)} bytes are all zero (content lost, typical after a crash or power loss during an update)':
        'die ersten {len(head)} Bytes sind alle null (Inhalt verloren – typisch nach einem Absturz oder Stromausfall während eines Updates)',
    'does not start with {magic!r} (found {head[:4]!r}) - the file content is not valid':
        'beginnt nicht mit {magic!r} (gefunden: {head[:4]!r}) – der Dateiinhalt ist ungültig',
    '{st.st_size} bytes':
        '{st.st_size} Byte',
    'missing':
        'nicht vorhanden',
    'empty':
        'leer',
    'zeroed':
        'mit Nullen überschrieben',
    'invalid':
        'ungültig',
    'unreadable':
        'nicht lesbar',
    'corrupt':
        'beschädigt',
    'not recorded':
        'nicht aufgezeichnet',
    'this Windows':
        'dieses Windows',
    'partition missing':
        'Partition fehlt',
    "{bcd.get('path', '')} on /dev/{bcd.get('boot_partition', '')}":
        "{bcd.get('path', '')} auf /dev/{bcd.get('boot_partition', '')}",
    'On screen:':
        'Auf dem Bildschirm:',
    'Repair…':
        'Reparieren…',
    "Fixes: {f['title']}":
        "Behebt: {f['title']}",
    'Repair ({n})':
        'Reparieren ({n})',
    'Backup':
        'Sicherung',
    'Diagnosis':
        'Diagnose',
    "On screen: {v['stopcode']}":
        "Auf dem Bildschirm: {v['stopcode']}",
    'Problems':
        'Probleme',
    'Computer name':
        'Computername',
    'Installed':
        'Installiert',
    'Last successful start':
        'Letzter erfolgreicher Start',
    'Secure Boot (this PC)':
        'Secure Boot (dieser PC)',
    '{len(notes)} notes':
        '{len(notes)} Hinweise',
    '1 note':
        '1 Hinweis',
    "build {w['Build']}":
        "Build {w['Build']}",
    'enabled':
        'aktiviert',
    'disabled':
        'deaktiviert',
    '(inactive)':
        '(inaktiv)',
    "partition {e['partuuid']}":
        "Partition {e['partuuid']}",
    'Does not start':
        'Startet nicht',
    'Warnings':
        'Warnungen',
    "{s['critical']} critical, {s['warning']} warning(s)":
        "{s['critical']} kritisch, {s['warning']} Warnung(en)",
    'Not analysed (the Windows volume was not accessible).':
        'Nicht analysiert (das Windows-Volume war nicht zugänglich).',
    'mounted':
        'eingebunden',
    'done':
        'erledigt',
    "failed: {r.get('error', '')}":
        "fehlgeschlagen: {r.get('error', '')}",
    'must run as root':
        'muss als root laufen',
    'invalid boot entry number':
        'ungültige Nummer des Starteintrags',
    'efibootmgr failed: {(r.stderr or r.stdout).strip()}':
        'efibootmgr ist fehlgeschlagen: {(r.stderr or r.stdout).strip()}',
    'there is no repair backup to undo':
        'Es gibt keine Reparatur-Sicherung, die rückgängig gemacht werden kann',
    'Third-party drivers & security software':
        'Treiber von Drittanbietern & Sicherheitssoftware',
    " It means that a Windows start file that was replaced recently (by an update, an update rollback or a repair) did not pass Windows' integrity check. This often follows an update or rollback interrupted by a crash or power loss. Startup Repair also reports it when a third-party driver stops the start, so check the other findings in this report as well.":
        ' Das heißt: Eine Startdatei von Windows, die kürzlich ersetzt wurde (durch ein Update, das Zurücknehmen eines Updates oder eine Reparatur), hat die Integritätsprüfung von Windows nicht bestanden. Das folgt oft auf ein Update oder Zurücknehmen, das durch einen Absturz oder Stromausfall unterbrochen wurde. Die Starthilfe meldet es aber auch, wenn ein Treiber eines Drittanbieters den Start verhindert – prüfen Sie deshalb auch die anderen Befunde in diesem Bericht.',
    "last successful start: {info['last_successful_boot']}":
        "letzter erfolgreicher Start: {info['last_successful_boot']}",
    'repair attempts: {attempts}':
        'Reparaturversuche: {attempts}',
    'To start Safe Mode: on the Automatic Repair screen choose Advanced options → Troubleshoot → Advanced options → Startup Settings → Restart, then press 4 (Safe Mode) or 5 (Safe Mode with networking).':
        'So starten Sie den abgesicherten Modus: Wählen Sie im Bildschirm „Automatische Reparatur“ „Erweiterte Optionen“ → „Problembehandlung“ → „Erweiterte Optionen“ → „Starteinstellungen“ → „Neu starten“ und drücken Sie dann 4 (abgesicherter Modus) oder 5 (abgesicherter Modus mit Netzwerktreibern).',
    'To see what goes wrong in a normal start, open Startup Settings again and press 9 (“Disable automatic restart after failure”): a blue screen then stays on screen with its stop code. Pressing 2 (“Enable boot logging”) instead makes Windows write C:\\Windows\\ntbtlog.txt, which the next BootRepair analysis reads to show the last driver that loaded.':
        'Um zu sehen, was beim normalen Start schiefgeht, öffnen Sie erneut die Starteinstellungen und drücken 9 („Automatischen Neustart bei Systemfehler deaktivieren“): Ein Bluescreen bleibt dann mit seinem Stoppcode stehen. Drücken Sie stattdessen 2 („Startprotokollierung aktivieren“), schreibt Windows die Datei C:\\Windows\\ntbtlog.txt; die nächste BootRepair-Analyse liest sie und zeigt den zuletzt geladenen Treiber.',
    'normal start':
        'normaler Start',
    'Safe Mode':
        'abgesicherter Modus',
    'Safe Mode with networking':
        'abgesicherter Modus mit Netzwerktreibern',
    'Safe Mode loads only the drivers Windows itself needs. If Safe Mode works but a normal start fails, a third-party driver or program that loads at startup is the usual cause: antivirus software, backup and disk tools, or “PC repair” and tuning programs.':
        'Der abgesicherte Modus lädt nur die Treiber, die Windows selbst braucht. Funktioniert er, der normale Start aber nicht, ist meist ein Treiber oder Programm eines Drittanbieters schuld, das beim Start geladen wird: Antivirensoftware, Sicherungs- und Festplattenwerkzeuge oder „PC-Reparatur“- und Tuning-Programme.',
    'Since the last normal start on {normal.time:%Y-%m-%d %H:%M} UTC, Windows has only started in Safe Mode. ':
        'Seit dem letzten normalen Start am {normal.time:%Y-%m-%d %H:%M} UTC ist Windows nur noch im abgesicherten Modus gestartet. ',
    'The event log only records Safe Mode starts. ':
        'Das Ereignisprotokoll verzeichnet nur Starts im abgesicherten Modus. ',
    'Windows last started only in Safe Mode':
        'Windows ist zuletzt nur im abgesicherten Modus gestartet',
    'In Safe Mode, uninstall what was installed or updated shortly before the problem began, above all security software, backup or disk tools and “PC repair” or tuning programs. Then restart normally.':
        'Deinstallieren Sie im abgesicherten Modus, was kurz vor Beginn des Problems installiert oder aktualisiert wurde, vor allem Sicherheitssoftware, Sicherungs- oder Festplattenwerkzeuge und „PC-Reparatur“- oder Tuning-Programme. Starten Sie danach normal neu.',
    'Third-party drivers that Safe Mode skipped, so one of them is the most likely cause:':
        'Treiber von Drittanbietern, die der abgesicherte Modus ausgelassen hat – einer davon ist die wahrscheinlichste Ursache:',
    'Third-party drivers that load at every normal start:':
        'Treiber von Drittanbietern, die bei jedem normalen Start geladen werden:',
    'Several antivirus programs load at the same time: {names}':
        'Mehrere Antivirenprogramme werden gleichzeitig geladen: {names}',
    'Each of them hooks into every file access with its own file-system filter and early-launch driver. Antivirus vendors only support running alone: two real-time scanners can block each other while Windows starts, which shows up as hangs, freezes or crashes without a clear error.':
        'Jedes davon klinkt sich mit einem eigenen Dateisystemfilter und Frühstart-Treiber in jeden Dateizugriff ein. Die Hersteller unterstützen nur den Betrieb allein: Zwei Echtzeitscanner können sich beim Windows-Start gegenseitig blockieren, was sich als Hänger, Einfrieren oder Absturz ohne klare Fehlermeldung zeigt.',
    "In Safe Mode, remove one of them with the vendor's removal tool, which also works there (Avast: “Avast Uninstall Utility”, Bitdefender: “Bitdefender Uninstall Tool”). Keep one product, or none: Windows then switches Microsoft Defender back on.":
        'Entfernen Sie im abgesicherten Modus eines davon mit dem Entfernungswerkzeug des Herstellers, das auch dort funktioniert (Avast: „Avast Uninstall Utility“, Bitdefender: „Bitdefender Uninstall Tool“). Behalten Sie ein Produkt – oder keines: Dann schaltet Windows den Microsoft Defender wieder ein.',
    'unknown vendor':
        'unbekannter Hersteller',
}
