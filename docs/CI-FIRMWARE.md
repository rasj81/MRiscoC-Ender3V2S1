# Custom firmware build (GitHub Actions)

Actions tab > "Build custom firmware" > Run workflow.

- **preset**: a saved configuration from `presets/`, `custom` (use the form below it), or `ALL` (build every preset).
- Custom fields mirror the Special_Configurations Configurator: printer, board, display, leveling, UBL, thermistor and the feature checkboxes.
- **firmware_source**: `upstream-latest` (default, current mriscoc code) or `this-fork`.
- Runs automatically on the 1st of each month for every preset; use Run workflow any time for a fresher build.
- Each run regenerates the config files with the current generator, checks that every selected option is really active in the generated file, compiles, and uploads the `.bin` plus the generated `Configuration*.h` as an artifact.

## Add a saved preset
1. Copy a file in `presets/` and edit `machine_name`, `env`, `features`.
2. Add its file name (without `.json`) to the `preset` options in `.github/workflows/build-firmware.yml`.

## Before flashing
Save `M503` output first. After flashing run `M502` then `M500`, and re-enter probe offset and bed limits. Read the upstream changelog.
