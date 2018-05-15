import argparse
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import uosci.uosci_jenkins as uosci_jenkins


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
    parser.set_defaults(host='http://10.245.162.49:8080')
    parser.set_defaults(sheet='https://docs.google.com/spreadsheets/d/1d31P5Qu'
                              '_nP__gCsoy4u6egpSnG34bMjpVijKtlJSmLU')
    parser.set_defaults(filter=None)
    return parser.parse_args(args)


def execute(host,
            username,
            password,
            sheet,
            credentials,
            filter=None):
    results = fetch_results(
        host=host,
        username=username,
        password=password,
        filter=filter)
    # print(results)
    save_results_to_sheet(
        results=results,
        sheet=sheet,
        credentials=credentials)


def get_job_from_specs(name, specs={}):
    if name is '' or name is 'Spec/Bundle/Test':
        return
    return specs.get(name)


def get_spec_summary(results):
    specs = {}
    for name, spec_list in results.items():
        if specs.get(name) is None:
            for uos, job in spec_list.items():
                specs[job['spec']] = name
    return specs


def save_results_to_sheet(results, sheet, credentials):
    print("Saving results to Google Sheet")
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials, scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_url(sheet).sheet1
    specs = get_spec_summary(results)
    cells = []

    for row_id, row in enumerate(worksheet.get_all_values()):
        job = get_job_from_specs(row[1], specs)
        if job is None:
            continue
        run = results[job]
        row_id += 1
        for (col_id, field) in enumerate(row):
            if col_id in SHEET_MAPPING:
                uos = SHEET_MAPPING[col_id]
                this_run = run.get(uos)
                col_id += 1
                if this_run is not None:
                    cells.append(gspread.models.Cell(
                        col=col_id,
                        row=row_id,
                        value='=HYPERLINK("{}","{} - {}")'.format(
                            this_run['url'],
                            this_run['date'].strftime("%d-%B"),
                            this_run['state'])))
                else:
                    cells.append(gspread.models.Cell(
                        col=col_id,
                        row=row_id,
                        value='NA'))
    worksheet.update_cells(cells, value_input_option='USER_ENTERED')


def fetch_results(host,
                  username,
                  password,
                  filter=None):
    client = uosci_jenkins.Jenkins(
        host, username=username, password=password)
    jobs = client.matrix('MojoMatrix')
    # print("Jobs: {}".format(jobs))
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
    print("Gathering results from the last Mojo runs")
    args = parse_args(sys.argv[1:])
    execute(host=args.host,
            username=args.username,
            password=args.password,
            sheet=args.sheet,
            credentials=args.google_credentials,
            filter=args.filter)
