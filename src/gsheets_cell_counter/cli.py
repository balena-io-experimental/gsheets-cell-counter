"""Command line interface to interact with GSheets Cell Counter tool."""
from collections import Counter

import click
from gsheets_cell_counter import get_service, Index
from time import sleep


def print_count(title: str, count: int) -> None:
    """Print a single observation of title and count."""
    print(f'{str(count).rjust(7)}: {title}')


@click.command()
@click.argument('spreadsheet_id', required=True)
@click.option('--tabs', '-t','show_tab_counts', is_flag=True, help='Print cell counts of individual tabs.')
@click.option('--verbose', '-v', 'show_verbose_progress', is_flag=True, help='Show verbose output.')
def get_cell_counts(spreadsheet_id: str, show_tab_counts: bool, show_verbose_progress: bool) -> None:
    """Find the number of cells used in a given Google spreadsheet."""
    service = get_service()
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False).execute()
    spreadsheet_title = spreadsheet['properties']['title']
    sheet_cells = Counter()

    print(f'Processing "{spreadsheet_title}" spreadsheet...')
    for sheet in spreadsheet['sheets']:
        title = sheet['properties']['title']
        gridProperties = sheet['properties']['gridProperties']

        try:
            values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=title).execute()['values']
        except KeyError:
            values = [[]]
        value_count = sum(1 for row in values for value in row if len(value))
        cell_count = gridProperties['rowCount'] * gridProperties['columnCount']
        sheet_cells[title] = cell_count

        if show_verbose_progress:
            print(f'Sheet "{title}" has {value_count} values in {cell_count} cells '
                  f'({value_count / cell_count:.2f}% density)', end=' - ')
            actual_cell = Index.to_letternumber(gridProperties["rowCount"], gridProperties["columnCount"])
            optimal_cell = Index.to_letternumber(len(values), max(len(row) for row in values))
            print(f'{actual_cell} can be trimmed to {optimal_cell}.' if actual_cell != optimal_cell
                  else 'cannot be optimized.')
    print('...done.')

    print('COUNTS BY SHEET:')
    if show_tab_counts:
        for title, count in sheet_cells.most_common():
            print_count(title, count)
    print('TOTAL:')
    print_count(spreadsheet_title, sum(sheet_cells.values()))

if __name__ == '__main__':
    get_cell_counts()
