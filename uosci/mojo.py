import argparse
import sys
import pprint

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
                        required=True)
    parser.add_argument('-p', '--password',
                        help='Jenkins password',
                        required=True)
    parser.add_argument('-t', '--host',
                        help='Jenkins host')
    parser.add_argument('-f', '--filter',
                        help='Filter results by job name')
    parser.set_defaults(host='http://10.245.162.49:8080')
    parser.set_defaults(filter=None)
    return parser.parse_args(args)


def execute(host,
            username,
            password,
            filter=None):
    client = uosci_jenkins.Jenkins(
        host, username=username, password=password)
    jobs = client.matrix('MojoMatrix')
    # print("Jobs: {}".format(jobs))
    results = []
    for job in jobs:
        if 'test' not in job['name']:
            continue
        if filter is not None:
            if filter not in job['name']:
                continue
        results.append(client.job_result(job))
    pprint.pprint(results)


def main():
    print("Gathering results from the last Mojo runs")
    args = parse_args(sys.argv[1:])
    execute(args.host, args.username, args.password, args.filter)
