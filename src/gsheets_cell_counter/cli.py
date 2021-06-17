"""Command line interface to interact with GSheets Cell Counter tool."""
from collections import Counter

import click
from gsheets_cell_counter import get_service, Cell


def print_count(title: str, count: int) -> None:
    """Print a single observation of title and count."""
    print(f'{str(count).rjust(7)}: {title}')


@click.command()
@click.argument('spreadsheet_id', required=True)
@click.option('--recommend', '-r', 'show_recommendations', is_flag=True,
              help='Show sheet optimization recommendations.')
def get_cell_counts(spreadsheet_id: str, show_recommendations: bool) -> None:
    """Find the number of cells used in a given Google spreadsheet."""
    service = get_service()
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False).execute()
    spreadsheet_title = spreadsheet['properties']['title']
    sheet_cells = Counter()

    print(f'Processing "{spreadsheet_title}" spreadsheet...')
    for sheet in spreadsheet['sheets']:
        title = sheet['properties']['title']
        properties = sheet['properties']['gridProperties']

        active_cell = Cell(properties['rowCount'], properties['columnCount'])
        sheet_cells[title] = active_cell.count

        if show_recommendations:
            try:
                values = service.spreadsheets().values() \
                    .get(spreadsheetId=spreadsheet_id, range=title).execute()['values']
            except KeyError:
                values = [[]]
            value_count = sum(1 for row in values for value in row if len(value))

            print(f'Sheet "{title}" has {value_count} values in {active_cell.count} cells '
                  f'({100 * value_count / active_cell.count:.2f}% density)', end=' - ')
            optimal_cell = Cell(len(values), max(len(row) for row in values))
            print(f'{active_cell.index} can be trimmed to {optimal_cell.index} to save '
                  f'{active_cell.count - optimal_cell.count}'
                  f' (or {100 * (1 - optimal_cell.count / active_cell.count):.2f}%) cells' if active_cell != optimal_cell
                  else 'cannot be optimized', end='.\n')
    print('...done.')

    print('COUNTS BY SHEET:')
    for title, count in sheet_cells.most_common():
        print_count(title, count)
    print('TOTAL:')
    print_count(spreadsheet_title, sum(sheet_cells.values()))


if __name__ == '__main__':
    get_cell_counts()
