from datetime import datetime
from humanize import filesize


class History(object):
    def __init__(self, image_id, created_by, created: datetime, size, tags, repo):
        self.id = image_id
        self.created_by = created_by
        self.created = created
        self.size = size
        self.tags = tags or []
        self.repo = repo

    @classmethod
    def from_api(cls, data, repo):
        return cls(
            image_id=data.get('Id'),
            created_by=data.get('CreatedBy'),
            created=datetime.fromtimestamp(data.get('Created')),
            size=data.get('Size'),
            tags=data.get('Tags'),
            repo=repo
        )

    @property
    def image(self):
        return self.repo.get_id(self.id)

    @property
    def short_id(self):
        return self.id[:12]

    def __repr__(self):
        return '<History [' \
               'id={short_id}, ' \
               'created={created}, ' \
               'size={size}]>'.format(
            short_id=self.short_id,
            created=self.created.isoformat(),
            size=filesize.naturalsize(self.size)
        )


class Image(object):
    def __init__(self, image_id, parent_id, created,
                 size, virtual_size, labels, tags, repo):
        self.id = image_id
        self.parent_id = parent_id
        self.created = created
        self.size = size
        self.virtual_size = virtual_size
        self.labels = labels
        self.tags = tags
        self.repo = repo

        self._history = None

    @property
    def data(self):
        return self.repo.conn.get_image(self.id)

    @property
    def history(self):
        if not self._history:
            self._history = [
                History.from_api(history, self.repo)
                for history in self.repo.conn.history(self.id)
            ]
        return self._history

    @property
    def parent(self):
        return self.repo.get_id(self.parent_id)

    @property
    def short_id(self):
        return self.id[:12]

    @classmethod
    def from_repository(cls, data, repo):
        return cls(
            image_id=data.get('Id'),
            created=datetime.fromtimestamp(data.get('Created')),
            size=data.get('Size'),
            virtual_size=data.get('VirtualSize'),
            labels=data.get('Labels'),
            tags=data.get('RepoTags'),
            parent_id=data.get('ParentId'),
            repo=repo
        )

    def __repr__(self):
        repo = tag = '<none>'
        # just tak the first tag if there is one
        if self.tags:
            repo, tag = self.tags[0].split(':')

        return '<Image [' \
               'repo={repo}, ' \
               'tag={tag}, ' \
               'id={short_id}, ' \
               'vsize={vsize}]>'.format(
            repo=repo,
            tag=tag,
            short_id=self.short_id,
            vsize=filesize.naturalsize(self.virtual_size)
        )