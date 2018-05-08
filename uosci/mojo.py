import argparse
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import uosci.uosci_jenkins as uosci_jenkins


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


def save_results_to_sheet(results, sheet, credentials):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials, scope)
    gc = gspread.authorize(credentials)
    wks = gc.open_by_url(sheet).sheet1
    print("wks: {}".format(wks))
    data = wks.get_all_records(head=3)
    specs = {}
    for name, spec_list in results.items():
        if specs.get(name) is None:
            for uos, job in spec_list.items():
                specs[job['spec']] = name
                break
    for row in data:
        row_spec = row['Spec/Bundle/Test']
        if row_spec is '':
            continue
        job = specs.get(row_spec)
        if job is None:
            continue
        print("Updating job {}".format(job))
        print("Row: {}".format(row))
        run = results[job]
        print("Last Run: {}".format(run))
    # for i in range(wks.row_count):
    #     i+=1
    #     print("Going to fetch row {}".format(i))
    #     row = wks.row_values(i)
    #     print("Row: {}".format(row))
    #     if i > 60 and len(row) is 0:
    #         break



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
