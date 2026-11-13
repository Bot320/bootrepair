"""Domain knowledge: stop codes, status codes, event meanings and repair recipes."""

from .guide import WINRE, LINUX, WINDOWS  # noqa: F401  (re-exported for the analyzers)
from .i18n import _, N_

# code -> (name, boot stage most likely involved, meaning)
BUGCHECKS = {
    0x0000000A: ("IRQL_NOT_LESS_OR_EQUAL", "kernel", N_("A driver accessed invalid memory at a high IRQL - usually a faulty driver, sometimes bad RAM.")),
    0x0000001A: ("MEMORY_MANAGEMENT", "kernel", N_("Memory-manager corruption - often defective RAM or a buggy driver.")),
    0x0000001E: ("KMODE_EXCEPTION_NOT_HANDLED", "kernel", N_("A kernel-mode driver raised an exception nobody handled.")),
    0x00000024: ("NTFS_FILE_SYSTEM", "kernel", N_("The NTFS driver hit corruption on the volume - run chkdsk, check the disk.")),
    0x0000002E: ("DATA_BUS_ERROR", "disk", N_("Hardware memory parity error - RAM or hardware fault.")),
    0x00000032: ("PHASE1_INITIALIZATION_FAILED", "kernel", N_("Kernel phase-1 initialisation failed.")),
    0x0000003B: ("SYSTEM_SERVICE_EXCEPTION", "kernel", N_("Exception in a system service - usually a faulty driver.")),
    0x0000003F: ("NO_MORE_SYSTEM_PTES", "kernel", N_("System page table entries exhausted - leaking driver.")),
    0x0000004E: ("PFN_LIST_CORRUPT", "kernel", N_("Page frame list corrupt - driver bug or defective RAM.")),
    0x00000050: ("PAGE_FAULT_IN_NONPAGED_AREA", "kernel", N_("Invalid memory referenced - faulty driver, antivirus filter, or bad RAM.")),
    0x00000051: ("REGISTRY_ERROR", "winload", N_("Severe registry error - a hive is corrupt or I/O to it failed.")),
    0x0000005C: ("HAL_INITIALIZATION_FAILED", "kernel", N_("The HAL could not initialise - firmware/ACPI problem or wrong HAL.")),
    0x00000067: ("CONFIG_INITIALIZATION_FAILED", "winload", N_("Registry could not be initialised - SYSTEM hive missing or unreadable.")),
    0x0000006B: ("PROCESS1_INITIALIZATION_FAILED", "kernel", N_("Phase-1 process initialisation failed - corrupt system files (often after a failed update).")),
    0x0000006F: ("SESSION3_INITIALIZATION_FAILED", "session", N_("Session manager initialisation failed - corrupt system files.")),
    0x00000074: ("BAD_SYSTEM_CONFIG_INFO", "winload", N_("The SYSTEM registry hive is corrupt or contains invalid configuration.")),
    0x00000077: ("KERNEL_STACK_INPAGE_ERROR", "disk", N_("Kernel stack could not be read from the page file - disk or controller failure.")),
    0x00000078: ("PHASE0_EXCEPTION", "kernel", N_("Exception during kernel phase 0 - firmware/hardware or HAL problem.")),
    0x0000007A: ("KERNEL_DATA_INPAGE_ERROR", "disk", N_("Kernel data could not be read from disk - bad sectors, failing disk, loose cable or controller fault.")),
    0x0000007B: ("INACCESSIBLE_BOOT_DEVICE", "kernel", N_("Windows lost access to the system disk during startup - missing/disabled storage driver (AHCI/RAID/VMD/NVMe change), filter driver problem, or file-system corruption.")),
    0x0000007E: ("SYSTEM_THREAD_EXCEPTION_NOT_HANDLED", "kernel", N_("A system thread crashed - usually a specific driver.")),
    0x0000007F: ("UNEXPECTED_KERNEL_MODE_TRAP", "kernel", N_("CPU trap in kernel mode - hardware fault, overclock or driver.")),
    0x0000008E: ("KERNEL_MODE_EXCEPTION_NOT_HANDLED", "kernel", N_("Kernel-mode exception - faulty driver or RAM.")),
    0x0000009C: ("MACHINE_CHECK_EXCEPTION", "disk", N_("CPU machine check - hardware failure.")),
    0x0000009F: ("DRIVER_POWER_STATE_FAILURE", "kernel", N_("A driver did not complete a power transition (often during resume/Fast Startup).")),
    0x000000A5: ("ACPI_BIOS_ERROR", "kernel", N_("The firmware's ACPI tables are not compatible - update the BIOS/UEFI.")),
    0x000000BE: ("ATTEMPTED_WRITE_TO_READONLY_MEMORY", "kernel", N_("A driver wrote to read-only memory.")),
    0x000000C2: ("BAD_POOL_CALLER", "kernel", N_("Invalid pool request by a driver.")),
    0x000000C4: ("DRIVER_VERIFIER_DETECTED_VIOLATION", "kernel", N_("Driver Verifier caught a driver bug - Verifier is enabled on this system.")),
    0x000000C5: ("DRIVER_CORRUPTED_EXPOOL", "kernel", N_("A driver corrupted pool memory.")),
    0x000000D1: ("DRIVER_IRQL_NOT_LESS_OR_EQUAL", "kernel", N_("A driver accessed paged/invalid memory at raised IRQL.")),
    0x000000ED: ("UNMOUNTABLE_BOOT_VOLUME", "kernel", N_("The boot volume could not be mounted - file-system corruption or disk I/O failure.")),
    0x000000EF: ("CRITICAL_PROCESS_DIED", "session", N_("A critical system process (smss, csrss, wininit, services, lsass...) died - corrupt system files, failed update, or malware/AV interference.")),
    0x000000F4: ("CRITICAL_OBJECT_TERMINATION", "session", N_("A critical process terminated - often disk I/O failure or corrupt files.")),
    0x000000F7: ("DRIVER_OVERRAN_STACK_BUFFER", "kernel", N_("A driver overran a stack buffer.")),
    0x000000FC: ("ATTEMPTED_EXECUTE_OF_NOEXECUTE_MEMORY", "kernel", N_("Execution of non-executable memory - driver bug.")),
    0x000000FE: ("BUGCODE_USB_DRIVER", "kernel", N_("USB driver error.")),
    0x00000101: ("CLOCK_WATCHDOG_TIMEOUT", "kernel", N_("A CPU core stopped responding - hardware, overclock or firmware.")),
    0x00000109: ("CRITICAL_STRUCTURE_CORRUPTION", "kernel", N_("Kernel code/data was modified - driver bug, bad RAM or rootkit.")),
    0x00000116: ("VIDEO_TDR_FAILURE", "logon", N_("The graphics driver could not be reset.")),
    0x00000117: ("VIDEO_TDR_TIMEOUT_DETECTED", "logon", N_("The graphics driver stopped responding (live dump).")),
    0x00000119: ("VIDEO_SCHEDULER_INTERNAL_ERROR", "logon", N_("Graphics scheduler error - GPU driver.")),
    0x00000124: ("WHEA_UNCORRECTABLE_ERROR", "disk", N_("Fatal hardware error reported by the CPU/chipset (CPU, RAM, PCIe, overclock, power).")),
    0x00000133: ("DPC_WATCHDOG_VIOLATION", "kernel", N_("A driver spent too long at DPC level - storage (often SATA/NVMe firmware) or other driver.")),
    0x00000139: ("KERNEL_SECURITY_CHECK_FAILURE", "kernel", N_("A kernel data structure was corrupted - driver bug or incompatible driver.")),
    0x0000013A: ("KERNEL_MODE_HEAP_CORRUPTION", "kernel", N_("Kernel heap corruption - driver bug.")),
    0x00000141: ("VIDEO_ENGINE_TIMEOUT_DETECTED", "logon", N_("Graphics engine timeout (live dump).")),
    0x00000144: ("BUGCODE_USB3_DRIVER", "kernel", N_("USB 3 driver error.")),
    0x00000154: ("UNEXPECTED_STORE_EXCEPTION", "disk", N_("Memory store component exception - frequently a failing disk or storage driver.")),
    0x0000015F: ("CONNECTED_STANDBY_WATCHDOG_TIMEOUT_LIVEDUMP", "kernel", N_("Modern standby watchdog.")),
    0x0000019C: ("WIN32K_POWER_WATCHDOG_TIMEOUT", "logon", N_("Win32k power watchdog.")),
    0x000001CA: ("SYNTHETIC_WATCHDOG_TIMEOUT", "kernel", N_("System hang watchdog.")),
    0x000001D4: ("UCMUCSI_LIVEDUMP", "kernel", N_("USB-C live dump.")),
    0x00000193: ("VIDEO_DXGKRNL_LIVEDUMP", "logon", N_("Graphics live dump.")),
    0xC000021A: ("STATUS_SYSTEM_PROCESS_TERMINATED", "session", N_("winlogon or csrss terminated - corrupt system files, failed update, third-party software or mismatched system DLLs.")),
    0xC0000218: ("STATUS_CANNOT_LOAD_REGISTRY_FILE", "winload", N_("A registry hive file could not be loaded - corrupt or missing hive.")),
    0xC0000221: ("STATUS_IMAGE_CHECKSUM_MISMATCH", "kernel", N_("A driver or system DLL is corrupt (checksum mismatch).")),
    0x1000007E: ("SYSTEM_THREAD_EXCEPTION_NOT_HANDLED_M", "kernel", N_("A system thread crashed - usually a specific driver.")),
    0x1000008E: ("KERNEL_MODE_EXCEPTION_NOT_HANDLED_M", "kernel", N_("Kernel-mode exception - faulty driver or RAM.")),
    0x100000EA: ("THREAD_STUCK_IN_DEVICE_DRIVER_M", "logon", N_("Graphics driver stuck.")),
}

# Stop codes that by themselves mean "this machine cannot get through startup".
BOOT_BLOCKING_BUGCHECKS = {0x7B, 0xED, 0x74, 0x51, 0x67, 0x6B, 0x6F, 0xEF, 0xF4, 0xC000021A,
                           0xC0000218, 0xC0000221, 0x7A, 0x24, 0x154, 0x77, 0x5C, 0x78, 0x32, 0xA5}

NTSTATUS = {
    0x00000000: "STATUS_SUCCESS",
    0xC0000001: "STATUS_UNSUCCESSFUL (a required device or file could not be accessed)",
    0xC0000005: "STATUS_ACCESS_VIOLATION",
    0xC0000006: "STATUS_IN_PAGE_ERROR (disk read failed)",
    0xC000000D: "STATUS_INVALID_PARAMETER (BCD entry invalid)",
    0xC000000E: "STATUS_NO_SUCH_DEVICE (the boot device was not found)",
    0xC000000F: "STATUS_NO_SUCH_FILE (BCD or a boot file is missing)",
    0xC0000010: "STATUS_INVALID_DEVICE_REQUEST",
    0xC0000017: "STATUS_NO_MEMORY",
    0xC0000022: "STATUS_ACCESS_DENIED",
    0xC0000032: "STATUS_DISK_CORRUPT_ERROR (file-system structures are corrupt)",
    0xC0000034: "STATUS_OBJECT_NAME_NOT_FOUND (boot volume / device object not found - storage driver not loaded)",
    0xC000003A: "STATUS_OBJECT_PATH_NOT_FOUND",
    0xC000006D: "STATUS_LOGON_FAILURE",
    0xC0000098: "STATUS_FILE_INVALID (a boot file / SYSTEM hive is corrupt)",
    0xC000009A: "STATUS_INSUFFICIENT_RESOURCES",
    0xC000009C: "STATUS_DEVICE_DATA_ERROR (bad sectors on the disk)",
    0xC000009D: "STATUS_DEVICE_NOT_CONNECTED (disk disappeared - cable, controller or power)",
    0xC00000BA: "STATUS_FILE_IS_A_DIRECTORY",
    0xC0000102: "STATUS_FILE_CORRUPT_ERROR (corrupt file or file-system structure)",
    0xC0000135: "STATUS_DLL_NOT_FOUND (a required system DLL is missing)",
    0xC0000139: "STATUS_ENTRYPOINT_NOT_FOUND (mismatched system DLL versions - typically a broken update)",
    0xC0000142: "STATUS_DLL_INIT_FAILED",
    0xC000014C: "STATUS_REGISTRY_CORRUPT",
    0xC000014F: "STATUS_UNRECOGNIZED_VOLUME (volume is not a recognised file system)",
    0xC000016A: "STATUS_DISK_OPERATION_FAILED (disk failure / bad blocks)",
    0xC0000185: "STATUS_IO_DEVICE_ERROR (disk or controller I/O error)",
    0xC000018B: "STATUS_NO_TRUST_SAM_ACCOUNT",
    0xC0000221: "STATUS_IMAGE_CHECKSUM_MISMATCH (corrupt system file)",
    0xC0000225: "STATUS_NOT_FOUND (boot device or BCD entry not found)",
    0xC0000359: "STATUS_INVALID_IMAGE_WIN_32 (wrong-architecture binary)",
    0xC0000428: "STATUS_INVALID_IMAGE_HASH (digital signature of a boot file is invalid)",
    0xC000A004: "STATUS_AUTHIP_FAILURE",
    0xC0000454: "STATUS_INVALID_TOKEN",
}

WIN32_ERRORS = {
    "2": "The system cannot find the file specified",
    "3": "The system cannot find the path specified",
    "5": "Access is denied",
    "50": "The request is not supported",
    "193": "Not a valid Win32 application",
    "577": "Windows cannot verify the digital signature for this file",
    "1053": "The service did not respond in a timely fashion",
    "1058": "The service is disabled",
    "1068": "The dependency service or group failed to start",
    "1075": "The dependency service does not exist or has been marked for deletion",
    "1077": "No attempts to start the service since last boot",
    "1275": "This driver has been blocked from loading",
    "1450": "Insufficient system resources",
    "31": "A device attached to the system is not functioning",
}


def bugcheck_name(code):
    return BUGCHECKS.get(code, (f"0x{code:08X}", "kernel", ""))[0]


def bugcheck_text(code):
    name = BUGCHECKS.get(code, (None,))[0]
    return f"0x{code:08X} {name}" if name else f"0x{code:08X}"


def status_text(code):
    s = NTSTATUS.get(code)
    return f"0x{code:08X} {s}" if s else f"0x{code:08X}"


def win32_error(param):
    """'%%2' -> text"""
    p = str(param).strip()
    if p.startswith("%%"):
        p = p[2:]
    return WIN32_ERRORS.get(p, f"error {p}")


# Device setup classes whose filter drivers sit in the boot-critical storage path.
STORAGE_CLASSES = {
    "{4d36e967-e325-11ce-bfc1-08002be10318}": N_("Disk drives"),
    "{71a27cdd-812a-11d0-bec7-08002be2092f}": N_("Volumes"),
    "{4d36e97b-e325-11ce-bfc1-08002be10318}": N_("Storage controllers (SCSI/RAID/NVMe)"),
    "{4d36e96a-e325-11ce-bfc1-08002be10318}": N_("IDE ATA/ATAPI controllers"),
    "{533c5b84-ec70-11d2-9505-00c04f79deaf}": N_("Volume shadow copies"),
}
OTHER_FILTER_CLASSES = {
    "{4d36e965-e325-11ce-bfc1-08002be10318}": N_("DVD/CD-ROM drives"),
    "{4d36e96b-e325-11ce-bfc1-08002be10318}": N_("Keyboards"),
    "{4d36e96f-e325-11ce-bfc1-08002be10318}": N_("Mice"),
    "{36fc9e60-c465-11cf-8056-444553540000}": N_("USB controllers"),
    "{4d36e97d-e325-11ce-bfc1-08002be10318}": N_("System devices"),
}

# Linux controller kind -> Windows storage drivers that can boot from it.
STORAGE_DRIVERS = {
    "nvme": ["stornvme", "secnvme", "iaStorVD", "iaStorAVC", "iaStorAC", "iaStorRST", "WDNVME", "samsungnvme"],
    "vmd": ["iaStorVD", "iaStorAVC", "iaStorAC", "iaStorRST"],
    "ahci": ["storahci", "iaStorA", "iaStorAC", "iaStorAVC", "iaStorV", "amdsata", "amd_sata", "msahci",
             "amdsbs", "nvstor"],
    "raid": ["iaStorVD", "iaStorAVC", "iaStorAC", "iaStorA", "iaStorV", "rcraid", "rcbottom", "amdraid",
             "nvraid", "megasas", "megasas2i", "megasas35i", "percsas", "percsas2i", "percsas3i", "arcsas",
             "storahci"],
    "usb": ["USBSTOR", "UASPStor"],
    "virtio": ["viostor", "vioscsi"],
    "scsi": ["LSI_SAS", "LSI_SAS2i", "LSI_SAS3i", "LSI_SCSI", "storvsc", "vmscsi", "pvscsi", "viostor", "vioscsi"],
}

SERVICE_START = {0: "Boot", 1: "System", 2: "Automatic", 3: "Manual", 4: "Disabled"}
ERROR_CONTROL = {0: "Ignore", 1: "Normal", 2: "Severe", 3: "Critical"}

# Files without which a given stage cannot complete. (path relative to the volume root, stage, role)
CRITICAL_FILES = [
    ("Windows\\System32\\ntoskrnl.exe", "kernel", N_("Windows kernel")),
    ("Windows\\System32\\hal.dll", "kernel", N_("Hardware Abstraction Layer")),
    ("Windows\\System32\\ci.dll", "winload", N_("Code Integrity (driver signature verification)")),
    ("Windows\\System32\\kdcom.dll", "winload", N_("kernel debugger transport (loaded by winload)")),
    ("Windows\\System32\\pshed.dll", "winload", N_("Platform Specific Hardware Error Driver")),
    ("Windows\\System32\\BOOTVID.dll", "winload", N_("boot video driver")),
    ("Windows\\System32\\drivers\\CLFS.SYS", "winload", N_("Common Log File System driver")),
    ("Windows\\System32\\drivers\\ntfs.sys", "kernel", N_("NTFS file-system driver")),
    ("Windows\\System32\\drivers\\disk.sys", "kernel", N_("disk class driver")),
    ("Windows\\System32\\drivers\\classpnp.sys", "kernel", N_("storage class support driver")),
    ("Windows\\System32\\drivers\\partmgr.sys", "kernel", N_("partition manager")),
    ("Windows\\System32\\drivers\\volmgr.sys", "kernel", N_("volume manager")),
    ("Windows\\System32\\drivers\\volmgrx.sys", "kernel", N_("dynamic volume manager")),
    ("Windows\\System32\\drivers\\mountmgr.sys", "kernel", N_("mount manager")),
    ("Windows\\System32\\drivers\\fltMgr.sys", "kernel", N_("file-system filter manager")),
    ("Windows\\System32\\drivers\\ksecdd.sys", "kernel", N_("kernel security support")),
    ("Windows\\System32\\drivers\\cng.sys", "kernel", N_("kernel cryptography")),
    ("Windows\\System32\\drivers\\Wdf01000.sys", "kernel", N_("kernel-mode driver framework")),
    ("Windows\\System32\\drivers\\acpi.sys", "kernel", N_("ACPI driver")),
    ("Windows\\System32\\drivers\\pci.sys", "kernel", N_("PCI bus driver")),
    ("Windows\\System32\\smss.exe", "session", N_("Session Manager")),
    ("Windows\\System32\\csrss.exe", "session", N_("Client/Server Runtime (critical process)")),
    ("Windows\\System32\\wininit.exe", "session", N_("Windows start-up application (critical process)")),
    ("Windows\\System32\\services.exe", "session", N_("Service Control Manager (critical process)")),
    ("Windows\\System32\\ntdll.dll", "session", N_("NT layer DLL")),
    ("Windows\\System32\\kernel32.dll", "session", N_("Win32 base API")),
    ("Windows\\System32\\KernelBase.dll", "session", N_("Win32 base API")),
    ("Windows\\System32\\autochk.exe", "session", N_("boot-time disk check")),
    ("Windows\\System32\\lsass.exe", "logon", N_("Local Security Authority (critical process)")),
    ("Windows\\System32\\winlogon.exe", "logon", N_("Windows Logon")),
    ("Windows\\System32\\LogonUI.exe", "logon", N_("logon screen")),
    ("Windows\\System32\\userinit.exe", "logon", N_("user initialisation")),
    ("Windows\\explorer.exe", "logon", N_("desktop shell")),
]

HIVES = [
    ("SYSTEM", "winload", "0x00000074 BAD_SYSTEM_CONFIG_INFO / 0xc0000098"),
    ("SOFTWARE", "session", "0x00000074 BAD_SYSTEM_CONFIG_INFO / 0xC000021A"),
    ("SAM", "logon", "0xC000021A / logon failure"),
    ("SECURITY", "logon", "0xC000021A / lsass failure"),
    ("DEFAULT", "logon", "logon failure"),
]

# Boot-relevant System.evtx events: (provider, id) -> (severity, title, explanation)
EVENTS = {
    ("Microsoft-Windows-Kernel-Power", 41): ("warning", N_("Unexpected restart (Kernel-Power 41)"),
        N_("The system restarted without shutting down cleanly: it crashed, hung, lost power or was reset.")),
    ("EventLog", 6008): ("warning", N_("Previous shutdown was unexpected (EventLog 6008)"),
        N_("The previous session ended without a clean shutdown.")),
    ("Microsoft-Windows-WER-SystemErrorReporting", 1001): ("warning", N_("Blue screen recorded (BugCheck 1001)"),
        N_("Windows recorded a bug check (blue screen) after rebooting.")),
    ("BugCheck", 1001): ("warning", N_("Blue screen recorded (BugCheck 1001)"),
        N_("Windows recorded a bug check (blue screen) after rebooting.")),
    ("Service Control Manager", 7026): ("warning", N_("Boot-start or system-start drivers failed to load (SCM 7026)"),
        N_("One or more drivers that start during boot did not load.")),
    ("Service Control Manager", 7000): ("info", N_("Service failed to start (SCM 7000)"),
        N_("A service could not be started.")),
    ("Service Control Manager", 7001): ("info", N_("Service dependency failed (SCM 7001)"),
        N_("A service could not start because a service it depends on failed.")),
    ("Service Control Manager", 7009): ("info", N_("Service start timed out (SCM 7009)"),
        N_("A service did not respond in time during startup (can make boot hang).")),
    ("Service Control Manager", 7022): ("info", N_("Service hung on starting (SCM 7022)"),
        N_("A service hung while starting.")),
    ("Service Control Manager", 7023): ("info", N_("Service terminated with an error (SCM 7023)"),
        N_("A service stopped with an error during startup.")),
    ("Service Control Manager", 7024): ("info", N_("Service terminated with a service-specific error (SCM 7024)"),
        N_("A service stopped with an error.")),
    ("Service Control Manager", 7031): ("info", N_("Service crashed (SCM 7031)"), N_("A service terminated unexpectedly.")),
    ("Service Control Manager", 7034): ("info", N_("Service crashed (SCM 7034)"), N_("A service terminated unexpectedly.")),
    ("disk", 7): ("warning", N_("Bad block on disk (disk 7)"),
        N_("The disk reported a bad block - the drive has unreadable sectors.")),
    ("disk", 11): ("warning", N_("Disk controller error (disk 11)"),
        N_("The driver detected a controller error - cable, port, controller or the drive itself.")),
    ("disk", 51): ("warning", N_("Paging I/O error (disk 51)"),
        N_("An error was detected during a paging operation - typically a failing disk or connection.")),
    ("disk", 52): ("critical", N_("Disk predicts its own failure (disk 52, S.M.A.R.T.)"),
        N_("The drive's S.M.A.R.T. self-monitoring predicts that it will fail.")),
    ("disk", 153): ("warning", N_("Disk I/O retried (disk 153)"),
        N_("I/O operations had to be retried - an early sign of a failing disk or connection.")),
    ("Ntfs", 55): ("warning", N_("NTFS corruption detected (Ntfs 55)"),
        N_("NTFS found corrupt file-system structures on a volume.")),
    ("Microsoft-Windows-Ntfs", 55): ("warning", N_("NTFS corruption detected (Ntfs 55)"),
        N_("NTFS found corrupt file-system structures on a volume.")),
    ("Microsoft-Windows-Ntfs", 98): ("warning", N_("Volume reported as corrupt (Ntfs 98)"),
        N_("NTFS reported that a volume is corrupt and needs to be checked with chkdsk.")),
    ("Microsoft-Windows-Ntfs", 137): ("info", N_("NTFS transaction error (Ntfs 137)"),
        N_("The default transaction resource manager could not start - often file-system corruption.")),
    ("Microsoft-Windows-Ntfs", 140): ("warning", N_("NTFS failed to flush data (Ntfs 140)"),
        N_("The system failed to flush data to the transaction log - corruption may occur.")),
    ("volmgr", 46): ("info", N_("Crash dump initialisation failed (volmgr 46)"),
        N_("Windows could not prepare crash dumps - blue screens may leave no dump file.")),
    ("volmgr", 161): ("info", N_("Dump file creation failed (volmgr 161)"),
        N_("A crash dump could not be written - often not enough disk space or a page-file problem.")),
    ("Microsoft-Windows-WHEA-Logger", 1): ("warning", N_("Fatal hardware error (WHEA 1)"), N_("A fatal hardware error occurred.")),
    ("Microsoft-Windows-WHEA-Logger", 18): ("warning", N_("Fatal hardware error (WHEA 18)"),
        N_("A fatal CPU/machine-check hardware error occurred.")),
    ("Microsoft-Windows-WHEA-Logger", 19): ("info", N_("Corrected hardware error (WHEA 19)"), N_("A corrected hardware error occurred.")),
    ("Microsoft-Windows-WHEA-Logger", 17): ("info", N_("Corrected PCIe error (WHEA 17)"), N_("A corrected PCI Express error occurred.")),
    ("Microsoft-Windows-WHEA-Logger", 46): ("warning", N_("Fatal memory/PCIe error (WHEA 46)"), N_("A fatal hardware error occurred.")),
    ("Microsoft-Windows-WHEA-Logger", 47): ("info", N_("Corrected memory error (WHEA 47)"), N_("A corrected memory error occurred.")),
    ("storahci", 129): ("warning", N_("Storage controller reset (storahci 129)"),
        N_("The SATA disk stopped responding and the controller had to be reset.")),
    ("stornvme", 129): ("warning", N_("NVMe controller reset (stornvme 129)"),
        N_("The NVMe disk stopped responding and had to be reset.")),
    ("stornvme", 11): ("warning", N_("NVMe controller error (stornvme 11)"), N_("The NVMe controller reported an error.")),
    ("iaStorA", 9): ("warning", N_("Intel RST device timeout (iaStorA 9)"), N_("The disk did not respond within the timeout.")),
    ("iaStorAC", 129): ("warning", N_("Intel RST controller reset (iaStorAC 129)"), N_("The disk stopped responding.")),
    ("Microsoft-Windows-Kernel-PnP", 219): ("info", N_("Driver failed to load for a device (Kernel-PnP 219)"),
        N_("A device driver failed to load.")),
    ("Microsoft-Windows-Kernel-Boot", 29): ("info", N_("Fast Startup failed (Kernel-Boot 29)"),
        N_("Windows failed to resume from its Fast Startup image and did a full boot.")),
    ("Microsoft-Windows-StartupRepair", 1002): ("info", N_("Startup Repair ran (StartupRepair 1002)"),
        N_("Startup Repair attempted to fix the system.")),
    ("Microsoft-Windows-Winlogon", 6004): ("info", N_("Winlogon notification failure (Winlogon 6004)"),
        N_("A Winlogon notification subscriber failed.")),
}

# Events that mark a successful boot / clean shutdown.
BOOT_OK_EVENTS = {("EventLog", 6005), ("Microsoft-Windows-Kernel-General", 12)}
SHUTDOWN_OK_EVENTS = {("EventLog", 6006), ("Microsoft-Windows-Kernel-General", 13), ("User32", 1074)}


def hive_edit_steps(reg_lines, hive="SYSTEM"):
    """Steps that edit an offline registry hive from the recovery prompt."""
    return [
        WINRE,
        _(t"Load Windows' {hive} registry hive under a temporary name:\n"
          t"`reg load HKLM\\OFFLINE C:\\Windows\\System32\\config\\{hive}`"),
        *reg_lines,
        _("Unload the hive again, otherwise the change is not saved:\n`reg unload HKLM\\OFFLINE`"),
    ]


CHKDSK = N_("Check and repair the file system of the Windows volume:\n`chkdsk C: /f`")
CHKDSK_R = N_("Check the file system and scan for unreadable sectors (takes a long time):\n`chkdsk C: /f /r`")
UNINSTALL_UPDATES = (N_("Leave the command prompt (`exit`) and choose Troubleshoot → Advanced options → "
                     "Uninstall Updates → “Uninstall latest quality update”."))
SYSTEM_RESTORE = (N_("Leave the command prompt (`exit`) and choose Troubleshoot → Advanced options → System Restore, "
                  "then pick a restore point from before the problem started."))
BACKUP_FIRST = (N_("Copy your important files to another disk first. Every further start attempt stresses a "
                "failing drive."))
