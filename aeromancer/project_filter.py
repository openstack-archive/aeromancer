import argparse


from aeromancer.db.models import Project


class ProjectFilter(object):
    """Manage the arguments for filtering queries by project.
    """

    @staticmethod
    def add_arguments(parser):
        """Given an argparse.ArgumentParser add arguments.
        """
        grp = parser.add_argument_group('Project Filter')
        grp.add_argument(
            '--project',
            action='append',
            default=[],
            dest='projects',
            help='projects to limit search, by exact name',
        )

    @classmethod
    def from_parsed_args(cls, parsed_args):
        return cls(projects=parsed_args.projects)

    def __init__(self, projects):
        self.projects = projects

    def update_query(self, query):
        if self.projects:
            query = query.filter(
                Project.name.in_(self.projects)
            )
        return query
