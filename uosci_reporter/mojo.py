import argparse
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import uosci_reporter.uosci_jenkins as uosci_jenkins


SHEET_MAPPING = {
    2: 'trusty-icehouse',
    3: 'trusty-kilo',
    4: 'trusty-liberty',
    5: 'trusty-mitaka',
    6: 'xenial-mitaka',
    7: 'xenial-newton',
    8: 'xenial-ocata',
    9: 'xenial-pike',
    10: 'xenial-queens',
    11: 'artful-pike',
    12: 'bionic-queens'
}


def parse_args(args):
    """Parse command line arguments

    :param args: List of configure functions functions
    :type list: [str1, str2,...] List of command line arguments
    :returns: Parsed arguments
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username',
                        help='Jenkins User',
                        required=False)
    parser.add_argument('-p', '--password',
                        help='Jenkins password',
                        required=False)
    parser.add_argument('-g', '--google-credentials',
                        help='Path to the downloaded Google credentials',
                        required=True)
    parser.add_argument('-t', '--host',
                        help='Jenkins host')
    parser.add_argument('-s', '--sheet',
                        help='Google Sheet URL')
    parser.add_argument('-f', '--filter',
                        help='Filter results by job name')
    parser.set_defaults(host='http://10.245.162.58:8080')
    parser.set_defaults(sheet='https://docs.google.com/spreadsheets/d/'
                              '1w7fTyG9BcAXKezEJLmNluy5POEt0H-n4ny3a17Q4Tnc')
    parser.set_defaults(filter=None)
    return parser.parse_args(args)


def execute(config,
            filter=None):
    results = fetch_results(
        host=config['jenkins']['host'],
        username=config['jenkins']['username'],
        password=config['jenkins']['password'],
        filter=filter)
    save_results_to_sheet(
        results=results,
        sheet=config['google']['sheet'],
        credentials=config['google']['credentials'])


def get_job_from_specs(name, specs={}):
    if name is '' or name is 'Spec/Bundle/Test':
        return None
    return specs.get(name)


def get_spec_summary(results):
    specs = {}
    for name, spec_list in results.items():
        for uos, job in spec_list.items():
            specs[job['spec']] = name
    return specs


def cell_for_row(column_id, row_id, run={}):
    uos = SHEET_MAPPING[column_id]
    this_run = run.get(uos)
    column_id += 1
    if this_run is not None:
        value='=HYPERLINK("{}","{} - {}")'.format(
            this_run['url'],
            this_run['date'].strftime("%d-%B"),
            this_run['state'])
    else:
        value = 'NA'
    return gspread.models.Cell(
        col=column_id,
        row=row_id,
        value=value)


def process_results_with_worksheet(results, worksheet):
    specs = get_spec_summary(results)
    cells = []

    for row_id, row in enumerate(worksheet.get_all_values()):
        for cell in get_cells_for_row(results, specs, row_id, row):
            cells.append(cell)
    return cells

def get_cells_for_row(results, specs, row_id, row):
    job = get_job_from_specs(row[1], specs)
    if job is None:
        return []
    run = results[job]
    cells = []
    for (col_id, _field) in enumerate(row):
        if col_id in SHEET_MAPPING:
            cells.append(cell_for_row(col_id, row_id + 1, run))
    return cells

def save_results_to_sheet(results, sheet, credentials):
    print("# Saving results to Google Sheet")
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials, scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_url(sheet).sheet1
    cells = process_results_with_worksheet(results, worksheet)
    if len(cells) is not 0:
        worksheet.update_cells(cells, value_input_option='USER_ENTERED')


def fetch_results(host,
                  username,
                  password,
                  filter=None):
    client = uosci_jenkins.Jenkins(
        host, username=username, password=password)
    jobs = client.matrix('MojoMatrix')
    results = {}
    for job in jobs:
        if filter_job(job['name'], filter):
            continue
        results[job['name']] = client.job_result(job)
    return results


def filter_job(job_name, filter=None):
    if 'test'not in job_name:
        return True
    if filter is not None and filter not in job_name:
        return True
    return False


def main():
    print("# Gathering results from the last Mojo runs")
    args = parse_args(sys.argv[1:])
    jenkins_conf = {
        'host': args.host,
        'username': args.username,
        'password': args.password,
    }
    google_conf = {
        'sheet': args.sheet,
        'credentials': args.google_credentials,
    }
    config = {
        'jenkins': jenkins_conf,
        'google': google_conf,
    }
    execute(config,
            filter=args.filter)
