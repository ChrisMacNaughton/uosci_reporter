from datetime import datetime, timedelta

import jenkins as jenkins


class Jenkins(jenkins.Jenkins):
    def matrix(self, view_name):
        views = self.get_jobs(view_name=view_name)
        return views

    def job_result(self, job):
        """
        Fetches the latest job results from Jenkins for the
        configured job
        """
        job_info = self.get_job_info(job['name'])
        build_info = self.get_build_info(
            job['name'],
            job_info['lastBuild']['number'],
            depth=1)
        results = {}
        for run in build_info['runs']:
            series = get_series_from_url(run['url'])
            details = result_from_run(run)
            if details is not None:
                results[series] = details
        return results


def result_from_run(run):
    """
    Summarizes a run from Jenkins API

    :param run: Details of the run from Jenkins
    :type dict
    :returns Summary of the run
    :rtype dict
    """
    date = datetime.fromtimestamp(run['timestamp'] / 1000)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    if date < thirty_days_ago:
        return
    return {
        'successful': run['result'] == "SUCCESS",
        'url': run['url'],
        'date': date,
    }


def get_series_from_url(url):
    """
    Breaks a Jenkins job URL out to retrieve U_OS combination


    :param url: Jenkins job URL
    :type str
    :returns: Ubuntu/OpenStack combination
    :rtype: Option(str)
    """
    if 'U_OS' in url:
        return url.split('U_OS=')[-1].split('/')[0]
