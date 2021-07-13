"""Command line interface to interact with GSheets Cell Counter tool."""
from collections import Counter
from pathlib import Path
import time

import click
from gsheets_cell_counter import get_service, Cell


def print_count(title: str, count: int) -> None:
    """Print a single observation of title and count."""
    print(f'{str(count).rjust(7)}: {title}')


@click.command()
@click.argument('spreadsheet_id', required=True)
@click.argument('ignore', type=Path, required=False)
@click.option('--optimize', is_flag=True, help='Perform spreadsheet optimizations.')
@click.option('--dry-run/--no-dry-run', default=True, help='Show optimization plan, without actually doing anything.')
def get_cell_counts(spreadsheet_id: str, optimize: bool, dry_run: bool, ignore: Path) -> None:
    """Find the number of cells used in a given Google spreadsheet."""
    service = get_service()
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False).execute()
    spreadsheet_title = spreadsheet['properties']['title']
    sheet_cells = Counter()
    ignore_tabs = []
    optimize_requests = []

    print(f'Processing "{spreadsheet_title}" spreadsheet...')
    if optimize and dry_run:
        print('Note: this is only a dry run.')
    if ignore:
        if ignore.exists():
            with open(ignore, 'r') as f:
                ignore_tabs = [line.rstrip() for line in f]
        else:
            print(f"No ignore file found at {ignore}")
    for sheet in spreadsheet['sheets']:
        title = sheet['properties']['title']
        # Skip the ignored files
        if title in ignore_tabs:
            print(f"Ignoring the tab {title}")
            continue
        properties = sheet['properties']['gridProperties']
        active_cell = Cell(properties['rowCount'], properties['columnCount'])
        count = active_cell.count

        if optimize:
            try:
                values = service.spreadsheets().values() \
                    .get(spreadsheetId=spreadsheet_id, range=title).execute()['values']
            except KeyError:
                values = [[]]
            value_count = sum(1 for row in values for value in row if len(value))

            print(f'Sheet "{title}" has {value_count} values in {active_cell.count} cells '
                  f'({100 * value_count / active_cell.count:.2f}% density)', end=' - ')
            optimal_cell = Cell(len(values), max(len(row) for row in values))

            if active_cell != optimal_cell:
                print(f'{active_cell.index} can be trimmed to {optimal_cell.index} to save '
                      f'{active_cell.count - optimal_cell.count}'
                      f' (or {100 * (1 - optimal_cell.count / active_cell.count):.2f}%) cells.')
                if not dry_run:
                    optimize_requests.extend([{'deleteDimension':
                                 {'range':
                                      {'sheetId': sheet['properties']['sheetId'],
                                       'dimension': dim,
                                       'startIndex': start,
                                       'endIndex': end
                                       }
                                  }
                             } for dim, start, end in [
                                ('ROWS', optimal_cell.row + 1, active_cell.row),
                                ('COLUMNS', optimal_cell.col + 1, active_cell.col),
                            ] if start <= end])
                    count = optimal_cell.count
            else:
                print('cannot be optimized.')
        sheet_cells[title] = count
        if len(list(sheet_cells)) % 50 == 0:
            print("Wait 100 seconds to respect Google Spreadsheet API's limits")
            time.sleep(100)

    if optimize and not dry_run and len(optimize_requests):
        print('Execute the optimizations found.')
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': optimize_requests}).execute()

    print('...done.')

    print('COUNTS BY SHEET:')
    for title, count in sheet_cells.most_common():
        print_count(title, count)
    print('TOTAL:')
    print_count(spreadsheet_title, sum(sheet_cells.values()))


if __name__ == '__main__':
    get_cell_counts()
