import jenkins


def client(username, password, host='http://10.245.162.49:8080'):
    return jenkins.Jenkins(host,
                           username=username,
                           password=password)


def mojo_matrix(client):
    views = client.get_jobs(view_name='MojoMatrix')
    return views


def main():
    print("Gathering results from the last Mojo runs")
