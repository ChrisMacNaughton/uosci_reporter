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
            try:
                series = run['url'].split('U_OS=')[-1].split('/')[0]
                if results.get(job['name']) is None:
                    results[job['name']] = {}
                date = datetime.fromtimestamp(run['timestamp'] / 1000)
                thirty_days_ago = datetime.now() - timedelta(days=30)
                if date < thirty_days_ago:
                    continue
                results[job['name']][series] = {
                    'successful': run['result'] == "SUCCESS",
                    'url': run['url'],
                    'date': date,
                }
            except Exception as e:
                print("Exception: {}".format(e))
                pass
        return results
