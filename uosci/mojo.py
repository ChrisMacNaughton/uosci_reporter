import uosci.jenkins as jenkins


def main():
    print("Gathering results from the last Mojo runs")
    jobs = jenkins.matrix('MojoMatrix')
