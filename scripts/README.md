# Batch utilities

Run these Windows Command Prompt utilities inside the dedicated lab VM. The Pin utility executes the input programs; it does not manage VM snapshots, upload results, or enforce the agent's execution timeouts.

## Instrument 64-bit executables with Pin

```bat
run_pin_batch.bat "C:\samples"
```

This processes `.exe` files directly in the input directory with the bundled 64-bit Pin and `calltrace.dll`. Each trace is saved to `agent/out/pin-batch/<sample-name>.txt` relative to the repository. Programs run until Pin exits. Use the main agent for controlled runs with timeouts and snapshot restoration.

Override the Pin executable, Pintool DLL, and output directory when needed:

```bat
run_pin_batch.bat "C:\samples" "C:\pin\pin.exe" "C:\tools\custom.dll" "C:\traces"
```

## Create one ZIP per sample

Create a text file containing one sample basename per line, without `.exe`. Spaces in names are preserved. The list is a local configuration file; use basenames from the specified sample directory.

```bat
zip_samples.bat "C:\lists\samples.txt" "C:\samples"
```

This uses `C:\Program Files\7-Zip\7z.exe` and writes ZIPs under `agent/compressed/batch/`. Optional arguments override the output directory and 7-Zip executable:

```bat
zip_samples.bat "C:\lists\samples.txt" "C:\samples" "C:\archives" "C:\7-Zip\7z.exe"
```

Both scripts validate their inputs and return a nonzero exit code for missing inputs, an empty batch, or a tool failure. Neither script recursively scans subdirectories.
