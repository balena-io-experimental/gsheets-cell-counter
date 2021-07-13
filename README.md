# Google Sheets cell counter

Count cells in Google sheets.

## Usage

```
Usage: gsheets-cc [OPTIONS] SPREADSHEET_ID [IGNORE_SHEETS]

  Find the number of cells used in a given Google spreadsheet.

Options:
  --optimize                Perform spreadsheet optimizations.
  --dry-run / --no-dry-run  Show optimization plan, without actually doing
                            anything.
  --help                    Show this message and exit.
```

IGNORE_SHEETS is an optional argument which is a file path that lists the sheets to skip in a spreadsheet. Example usage:
```sh
gsheets-cc --optimize --no-dry-run 1yx4HWumAy23DGWySnKXQ2qORx1ziELiFnytT-QBFFqE ./data/customer_model.txt
```

## Prerequisites

- [Enable the Google Sheets API](https://developers.google.com/sheets/api/quickstart/python#step_1_turn_on_the) and save the  resulting `credentials.json` file to your working directory.
- Install the included Python package using [Poetry](https://github.com/balena-io/process/blob/master/process/Python_Coding_Guide.md#create-the-environment) or `pip`.
