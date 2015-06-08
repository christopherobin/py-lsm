from datetime import datetime

from .image import Image

class ContainerList(object):
    def __init__(self, docker, all=False):
        self.docker = docker
        self._containers = self.docker.client.containers(all=all)
        self._index()

    def _index(self):
        self._by_name = {
            name[1:]: container
            for container in self._containers
            for name in container.get('Names')
            if name
        }
        self._by_id = {
            container.get('Id'): container
            for container in self._containers
        }

    def create(self, image, **kwargs):
        if isinstance(image, Image):
            image = image.id

        self.docker.create_container(image=image, **kwargs)

    def get(self, name):
        if name in self._by_name:
            return Container.from_api(self._by_name[name], self.docker)
        return None

class Container(object):
    def __init__(self, container_id, status, created, ports, command, image_id, names, docker):
        self.id = container_id
        self.status = status
        self.created = created
        self.ports = ports
        self.command = command
        self.image_id = image_id
        self.names = names
        self.docker = docker

    @classmethod
    def from_api(cls, data, docker):
        return cls(
            container_id=data.get('Id'),
            status=data.get('Status'),
            created=datetime.fromtimestamp(data.get('Created')),
            ports=data.get('Ports'),
            command=data.get('Command'),
            image_id=data.get('Image'),
            names=data.get('Names'),
            docker=docker
        )

    @classmethod
    def create(cls, docker):
        pass

    @property
    def image(self):
        return self.docker.repository.get_id(self.image_id)

    @property
    def short_id(self):
        return self.id[:12]

    def __repr__(self):
        return '<Container [' \
               'id={short_id}, ' \
               'image_id={image_id}, ' \
               'status={status}]>'.format(
            short_id=self.short_id,
            image_id=self.image_id[:12],
            status=self.status
        )
