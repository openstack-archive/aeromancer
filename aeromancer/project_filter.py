import argparse
import logging

from aeromancer.db.models import Project

LOG = logging.getLogger(__name__)


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
            help=('projects to limit search, '
                  'by exact name or glob-style patterns'),
        )

    @classmethod
    def from_parsed_args(cls, parsed_args):
        return cls(projects=parsed_args.projects)

    def __init__(self, projects):
        self.exact = []
        self.patterns = []
        for p in projects:
            if '*' in p:
                self.patterns.append(p.replace('*', '%'))
            else:
                self.exact.append(p)
        self.projects = projects

    def update_query(self, query):
        the_filter = ()
        if self.exact:
            LOG.debug('filtering on projects in %s', self.exact)
            the_filter += (Project.name.in_(self.exact),)
        if self.patterns:
            LOG.debug('filtering on projects matching %s', self.patterns)
            the_filter += tuple(Project.name.ilike(p)
                                for p in self.patterns)
        if the_filter:
            query = query.filter(*the_filter)
        return query
