import argparse
import sys

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
    parser.set_defaults(host='http://10.245.162.49:8080')
    return parser.parse_args(args)


def execute(host,
            username,
            password):
    client = uosci_jenkins.Jenkins(
        host, username=username, password=password)
    jobs = client.matrix('MojoMatrix')
    print("Jobs: {}".format(jobs))


def main():
    print("Gathering results from the last Mojo runs")
    args = parse_args(sys.argv[1:])
    execute(args.host, args.username, args.password)
