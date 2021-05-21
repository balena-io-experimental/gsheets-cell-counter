"""Command line interface to interact with GSheets Cell Counter tool."""
from collections import Counter

import click
from gsheets_cell_counter import get_service


def print_count(title: str, count: int) -> None:
    """Print a single observation of title and count."""
    print(f'{str(count).rjust(7)}: {title}')


@click.command()
@click.argument('spreadsheet_id', required=True)
@click.option('--tabs', 'show_tab_counts', is_flag=True, help='Print cell counts of individual tabs.')
def get_cell_counts(spreadsheet_id: str, show_tab_counts: bool) -> None:
    """Find the number of cells used in a given Google spreadsheet."""
    service = get_service()
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False).execute()
    sheet_cells = Counter()

    for sheet in spreadsheet['sheets']:
        title = sheet['properties']['title']
        gridProperties = sheet['properties']['gridProperties']
        cell_count = gridProperties['rowCount'] * gridProperties['columnCount']
        sheet_cells[title] = cell_count

    if show_tab_counts:
        for title, count in sheet_cells.most_common():
            print_count(title, count)
    print_count(spreadsheet['properties']['title'], sum(sheet_cells.values()))
