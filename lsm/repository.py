from collections.abc import Iterator

from .image import Image


class Repository(Iterator):
    def __init__(self, docker):
        self.docker = docker

        self._images = []
        self._iter = None

        self.refresh()

    def _index(self):
        self._by_tag = {
            repo_tag: image
            for image in self._images
            for repo_tag in image.get('RepoTags', [])
            if repo_tag != '<none>:<none>'
        }
        self._by_id = {
            image['Id']: image
            for image in self._images
            if 'Id' in image
        }

    def get(self, name, tag='latest'):
        wanted_tag = '{name}:{tag}'.format(name=name, tag=tag)
        if ':' in name:
            wanted_tag = name
        if wanted_tag in self._by_tag:
            return Image.from_repository(self._by_tag[wanted_tag], self)
        return None

    def get_id(self, id):
        if ':' in id:
            id = id.split(':').pop(0)
        if id in self._by_id:
            return Image.from_repository(self._by_id[id], self)
        return None

    def refresh(self):
        self._images = self.docker.client.images(all=True)
        self._iter = iter(self._images)
        self._index()

    def __len__(self):
        return len(self._images)

    def __next__(self):
        return Image.from_repository(next(self._iter), self)
