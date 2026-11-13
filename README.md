# BootRepair

A GTK4/libadwaita app for Linux that finds out **why Windows does not start** and repairs it,
from a Linux system on the same computer. English and German (Deutsch).

- **Read-only diagnosis.** Disks are attached with `losetup --read-only` and mounted `-o ro`.
- **Sorted findings.** Critical, then Warning, then Info. Each finding sits on the Windows boot chain
  (firmware → Boot Manager → BCD → winload → kernel & boot drivers → Session Manager → logon) and comes
  with an explanation, the evidence, and step-by-step manual repair instructions for the Windows
  recovery command prompt. The guide can be saved as a web page to read on a phone.
- **One-click repairs, only when you choose them.** Every file is backed up first, and
  *Undo last repair* restores the original bytes.

It covers the common causes:

- stuck Windows Updates (`pending.xml`)
- broken or stale BCD entries
- missing `bootmgfw.efi` and firmware boot entries
- storage-driver and filter-driver problems (0x7B)
- missing or zeroed system files
- corrupt registry hives
- crash dumps and the event log
- disk health (SMART)
- hibernation and BitLocker

## Install (Arch Linux)

```sh
git clone https://github.com/Bot320/bootrepair && cd bootrepair
makepkg -si        # runs the tests and installs
bootrepair         # asks for the admin password via polkit
```

Optional: `ntfs-3g`, `cryptsetup` (BitLocker), `smartmontools`, `efibootmgr`.

## Command line

```sh
sudo bootrepair-helper analyze /dev/sdXN           # text report (--json for everything)
sudo bootrepair-helper --lang de analyze /dev/sdXN # German
sudo bootrepair-helper undo                        # undo the last repair
bootrepair-helper list                             # drives and partitions
```

## Safety

- Registry and BCD edits only rewrite existing cells in place, then re-check the whole structure and
  read it back. They never touch hives with unreplayed transaction logs.
- The Windows volume is only written through the kernel `ntfs3` driver, which refuses unclean volumes.
- Hibernated and BitLocker volumes are never written to.

## Development

```sh
python3 -m unittest discover -s tests   # fixture disk with synthetic hives: analysis, every repair, undo
python3 tools/messages.py check         # translation catalog (bootrepair/locale_de.py) is complete
```

## Deutsch

BootRepair findet heraus, warum Windows nicht startet, und repariert es von Linux aus. Die Analyse ist rein
lesend. Reparaturen laufen nur auf Wunsch, mit Sicherung und „Rückgängig“. Die Sprache folgt dem System
und lässt sich im Menü umstellen.

License: GPL-3.0-or-later
