from docker import Client
from docker.utils import kwargs_from_env

from .container import ContainerList
from .repository import Repository


class ServerVersion(object):
    def __init__(self, version=None, api_version=None, kernel_version=None,
                 git_commit=None, go_version=None, osname=None, arch=None):
        self.version = version
        self.api_version = api_version
        self.kernel_version = kernel_version
        self.git_commit = git_commit
        self.go_version = go_version
        self.os = osname
        self.arch = arch

    @classmethod
    def from_api(cls, version_dict: dict):
        return cls(
            version=version_dict.get('Version'),
            api_version=version_dict.get('ApiVersion'),
            git_commit=version_dict.get('GitCommit'),
            go_version=version_dict.get('GoVersion'),
            osname=version_dict.get('Os'),
            arch=version_dict.get('Arch'),
            kernel_version=version_dict.get('KernelVersion'),
        )

    def __repr__(self):
        return '<HostVersion [version={version}, ' \
               'api_version={api_version}, ' \
               'go_version={go_version}, ' \
               'git_commit={git_commit}, ' \
               'os={os}, ' \
               'kernel_version={kernel_version}, ' \
               'arch={arch}]>'\
            .format(**self.__dict__)


class Connection(object):
    def __init__(self, docker: Client):
        self.client = docker
        self._version = None
        self._static_info = None

    def containers(self, all=True):
        return ContainerList(self, all=all)

    @property
    def driver(self):
        return self.client.info().get('Driver')

    @property
    def images(self):
        return Repository(self)

    @property
    def is_local(self):
        return self.client.base_url.startswith('unix://')

    @property
    def repository(self):
        return Repository(self)

    @property
    def version(self):
        if not self._version:
            self._version = ServerVersion.from_api(self.client.version())
        return self._version

    @classmethod
    def from_env(cls):
        kwargs = kwargs_from_env()
        return cls(Client(**kwargs))