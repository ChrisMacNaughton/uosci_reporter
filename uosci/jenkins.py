import jenkins


def client(username, password, host='http://10.245.162.49:8080'):
    return jenkins.Jenkins(host,
                           username=username,
                           password=password)


def matrix(client, view_name):
    views = client.get_jobs(view_name=view_name)
    return views


def main():
    print("Gathering results from the last Mojo runs")
