import jenkins as jenkins


class Jenkins(jenkins.Jenkins):
    def matrix(self, view_name):
        views = self.get_jobs(view_name=view_name)
        return views
