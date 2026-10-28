# dbi-analyzer

A Windows malware analysis tool for collecting static information, monitoring execution, and performing dynamic binary instrumentation (DBI). The server organizes results and controls a VirtualBox virtual machine; the agent runs the analysis tools inside the VM.

## How it works

1. The server restores a VM snapshot and starts the Windows guest.
2. A scheduled task starts the agent when the user logs on to Windows.
3. The agent queries the hashes already registered on the server and selects an unregistered sample from `agent/in/`.
4. The analysis tools process the sample. The agent compresses the results and uploads them to the server.
5. The VM shuts down. While analysis is enabled, the server repeats the cycle from the snapshot.
6. When no new samples remain, the agent asks the server to disable analysis.

Samples are identified by their SHA-256 hash. Each agent run processes one sample; the batch progresses because server records persist across VM snapshot restores.

## Requirements

| Environment | Requirements |
| --- | --- |
| Host | Windows, Python 3 with `pip`, VirtualBox, and permission to configure host-only networking. |
| Virtual machine | 64-bit Windows, Python 3 with `pip` available on `PATH`, and an account with administrator privileges to set up the agent. |
| Communication | The VM must reach the host's host-only IP address on TCP port `5000`. |
| Tools | Executables, rules, and scripts at the expected paths under `agent/tools/`. |

Each component's Python dependencies are pinned in its own `requirements.txt`. Installing these packages with `pip` does not install external executables.

**The agent executes the samples.** Use a dedicated lab VM with host-only networking, no personal data, and no shared folders containing host files. Run the agent scripts inside that VM. The server does not implement authentication; restrict access to the lab network.

## 1. Set up the server on the host

Obtain the project and open Command Prompt at the repository root. The terminal examples in this document use Windows Command Prompt (`cmd.exe`).

### Configure VirtualBox and the server address

Check these settings before starting:

| File | Setting | Current value |
| --- | --- | --- |
| `server/app.py` | `SERVER_IP` | `192.168.56.10` |
| `server/virtualbox_manager.py` | `VBOXMANAGE_PATH` | `C:\Program Files\Oracle\VirtualBox\VBoxManage.exe` |

Change these values if your environment uses a different address or installation path. At startup, the server configures the first available host-only adapter, or creates one, and writes the address to `agent/server_ip.txt`.

### Install dependencies and start the server

```bat
cd server
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python app.py
```

Keep the terminal open. For subsequent runs, activate the virtual environment and run `python app.py`, always from `server/`: the project uses relative paths to locate the agent and save results.

The SQLite database at `server/malware_data.db` and its tables are created automatically on first startup. You do not need to run migrations to start with a new database.

Open [Analysis Control](http://localhost:5000/analysis) on the host. Inside the VM, the same service should be available at [http://192.168.56.10:5000/analysis](http://192.168.56.10:5000/analysis) if you kept the default IP address. Allow TCP port `5000` through the firewall for the lab network if needed.

The `server/run_server.bat` script also installs dependencies and starts Flask. Run it from the `server/` directory if you use this launcher.

## 2. Set up the VM and agent

### Configure communication

1. Create a 64-bit Windows VM in VirtualBox and install Python with the option to add it to `PATH`.
2. Set the VM's network adapter 1 to **Host-only**, using the adapter configured by the server.
3. Configure the Windows guest with an unused IP address on the same subnet. With the default configuration and subnet mask `255.255.255.0`, an example is `192.168.56.20`; `192.168.56.10` belongs to the host.
4. Inside the VM, confirm that you can open `http://192.168.56.10:5000/samples`. An empty database returns an empty JSON list (`[]`).

### Download and install the agent

With the server running, open this address inside the VM:

```text
http://192.168.56.10:5000/download-agent
```

Extract the ZIP to a local folder in the VM, such as `C:\dbi-agent`, and check that `server_ip.txt` contains the host's address. If you changed the default IP address, replace it in this document's examples as well.

To install dependencies, the VM needs access to the packages used by `pip`, either over the network during setup or through a configured local source. If you use a temporary NAT adapter for installation, remove it before adding samples and creating the snapshot, leaving only host-only networking in the analysis environment.

Run `first_run.bat` as administrator **inside the VM**. This script:

- Creates the `venv` virtual environment and installs `requirements.txt`.
- Creates the `RunAnalysis` scheduled task, triggered at logon, to run `run_agent.bat` with elevated privileges.
- Runs `bcdedit /set hypervisorlaunchtype off`, changing the Windows guest's boot configuration.

Restart the VM to apply the boot configuration. Automation depends on user logon: if the VM stays on the sign-in screen, the agent will not start. For unattended batch runs, configure automatic logon for the lab account before saving the snapshot.

### Check the tools

Verify these files inside the agent folder:

| Tool | Expected paths under `tools/` |
| --- | --- |
| Detect It Easy (DIE) | `die_win64_portable_3.07/diec.exe` |
| FLOSS | `floss/floss.exe` |
| capa | `capa/capa.exe` and the `capa/capa-rules/` directory |
| YARA | `yara/yara-rules/antidebug_antivm_index.yar`, `packers_index.yar`, and rules included by these indexes |
| Process Monitor | `Procmon/Procmon64.exe` and `Procmon/ProcmonConfiguration.pmc` |
| Intel Pin | `pin-3.28-msvc-windows/ia32/bin/pin.exe`, `intel64/bin/pin.exe`, and `calltrace.dll` in `tools/obj-ia32/` and `tools/obj-intel64/` within that package |
| DynamoRIO | `DynamoRIO-Windows-9.0.1/bin32/drrun.exe`, `bin64/drrun.exe`, and `DRkill.exe` in both directories |
| Frida | `frida/call_trace.js`; Python packages are installed through `requirements.txt` |
| pefile and Vivisect | Python packages installed through `requirements.txt` |

Process Monitor uses a configuration that filters for `MaLwArEpRoCeSs.exe`, the name the agent assigns to a temporary copy of the sample. Preserve this filter when changing the `.pmc` file.

If you need to rebuild the Pin tools, see `agent/tools/pin-3.28-msvc-windows/MakePinTool.txt` in the repository.

### Add samples and create the snapshot

1. Create an `in` directory inside the agent folder if it does not exist.
2. Place the Windows executables to analyze in that directory. Samples must be extracted; the agent does not extract input ZIP archives.
3. Confirm that the agent, tools, server IP address, dependencies, and scheduled task are ready.
4. Shut down the VM and create a VirtualBox snapshot, such as `ready-for-analysis`.
5. Record the exact VM name and snapshot name.

The snapshot must contain the samples: any changes made to the VM disk afterward will be lost on the next restore. To change the batch or update the agent, prepare a new snapshot or update the snapshot used by the server.

The download ZIP is reused while `server/tmp/agent.zip` exists. After updating the agent code or IP address, remove this generated ZIP on the host before downloading it again.

## 3. Run an automatic analysis

The web interface currently uses Portuguese labels. The instructions below include those labels so you can locate the controls.

1. Leave the server running and the VM powered off.
2. Open [Analysis Control](http://localhost:5000/analysis).
3. Fill in **Nome da VM** (VM name) and **Nome do Snapshot** (snapshot name) exactly as they appear in VirtualBox.
4. Click **Iniciar** (Start).
5. Monitor the server and agent terminals and check the results pages.

In each cycle, the server restores the snapshot, configures host-only networking, and starts the VM. The agent runs the tools in this order: pefile, DIE, FLOSS, capa, YARA, Vivisect, Process Monitor, Pin, DynamoRIO, and Frida.

The server waits for the VM to shut down and forces a shutdown if the cycle exceeds **15 minutes**. The **Parar** (Stop) button disables future cycles; it does not immediately interrupt a run already in progress.

To stop the server, press `Ctrl+C` in its terminal. First disable future cycles and wait for the current VM run to finish so the agent can upload its results.

## 4. Run the agent manually

Inside the VM, open Command Prompt as administrator in the agent folder and run:

```bat
venv\Scripts\activate.bat
python analysis.py 192.168.56.10 exit-script
```

This command uses the same samples from `in/`, queries the server, and processes one unregistered sample. Repeat the command to process another sample.

The second argument sets the action to take when the run ends:

| Action | Behavior |
| --- | --- |
| `exit-script` | Exits the script and leaves Windows running. |
| `shutdown` | Shuts down Windows. |
| `restart` | Restarts Windows. |

`run_agent.bat` uses the `shutdown` action and also requests a shutdown after Python exits. The agent's finalization block handles these actions, so they may occur even after a failure; use `exit-script` when troubleshooting manually. Keep automatic analysis stopped during these tests.

## 5. View results

| Page on the host | Contents |
| --- | --- |
| [Analysis](http://localhost:5000/analysis) | VM and snapshot settings, with start and stop controls. |
| [Samples](http://localhost:5000/sample/list) | SHA-256 hashes, status, Pin, DynamoRIO, and Frida indicators, sample details, and an instrumentation summary. |
| [Tools](http://localhost:5000/sample/tools) | DIE, YARA, and capa occurrence counts, distinct sample counts, and charts generated from the stored detections. |
| [JSON list](http://localhost:5000/samples) | Record hashes and statuses used by the agent to select new samples. |

In the sample list, click **Ver Detalhes** (View Details) to open a sample's information. Click a detection or instrumentation result to filter the sample list. Filters use query parameters, preserving names that contain slashes, percent signs, or other special characters. Valid filters with no matches display an empty list.

The **Processado** (Processed) status means that the server has run its processing steps on the uploaded ZIP. Check each tool's indicators and logs, since an individual tool failure does not necessarily prevent the remaining steps from completing.

### File locations

| Location | Contents |
| --- | --- |
| `agent/in/` | Input executables inside the VM. |
| `agent/out/<sha256>/` | Outputs organized by tool, including JSON, traces, and logs. |
| `agent/compressed/<sha256>.zip` | Results compressed for upload. |
| `agent/tmp/` | Temporary files used during execution. |
| `server/results/<sha256>.zip` | Uploaded ZIP archives, preserved on the host between cycles. |
| `server/tmp/` | Files extracted for processing and the cached agent download. |
| `server/malware_data.db` | SQLite database containing records, detections, and settings. |

Local VM files return to the snapshot state on each cycle. Use the ZIP archives uploaded to the host to inspect outputs after a restore, and back up the database and `server/results/` to preserve results.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Server cannot find `VBoxManage.exe` | Check `VBOXMANAGE_PATH` in `server/virtualbox_manager.py`. |
| VM cannot reach the server | Check `SERVER_IP`, `server_ip.txt`, the guest IP address and subnet mask, the host-only adapter, and firewall access on port `5000`. |
| VM starts but the agent does not | Check Windows logon, the `RunAnalysis` task, the path to `run_agent.bat`, and Python on the account's `PATH`. |
| Snapshot restore fails or the VM is locked | Check the names in the form and VirtualBox messages in the terminal; close open VM sessions before starting the batch. |
| A tool fails or produces empty output | Check binaries, rules, sample architecture, and permissions; inspect the terminal, `errors.log` when generated, and logs in the tool's output folder. |
| The agent skips a pending sample | Selection skips any registered hash, including pending records. Investigate the failure and adjust the database record before retrying. |
| Agent changes do not appear in the VM | Regenerate `server/tmp/agent.zip`, update the VM's copy, and save a snapshot containing the new version. |
| VM control appears to run twice | Run a single server instance with `python app.py`, without the debug reloader. |

## Repository security

See [Repository security and CODEOWNERS](docs/repository-security.md) for contribution and review rules, GitHub Actions controls, and security configuration. For vulnerability reports, follow the [security policy](SECURITY.md).

## Development checks and batch utilities

After installing the server dependencies, run the dashboard regression tests from the repository root:

```bat
python -m unittest discover -s server/tests -v
```

The tests use SQLite in memory and mock network configuration, IP-file writes, and background thread startup. They do not start VirtualBox or execute samples.

See [Batch utilities](scripts/README.md) for the optional Pin and ZIP scripts.
