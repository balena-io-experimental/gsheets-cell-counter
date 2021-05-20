"""Command line interface to interact with GSheets Cell Counter tool."""
from collections import Counter

import click
from gsheets_cell_counter import get_service


@click.command()
@click.argument('spreadsheet_id', required=True)
def get_cell_counts(spreadsheet_id: str) -> None:
    """Find the number of cells used in a given Google spreadsheet."""
    service = get_service()
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False).execute()
    sheet_cells = Counter()

    for sheet in spreadsheet['sheets']:
        title = sheet['properties']['title']
        gridProperties = sheet['properties']['gridProperties']
        cell_count = gridProperties['rowCount'] * gridProperties['columnCount']
        sheet_cells[title] = cell_count

    print(f"{str(sum(sheet_cells.values())).rjust(7)}: {spreadsheet['properties']['title']}")
