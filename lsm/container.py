import arrow

from .errors import ExecReturnCodeError
from .image import Image

class ContainerList(object):
    def __init__(self, conn, all=True):
        self.all = all
        self.conn = conn
        self._containers = []
        self.refresh()

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

    def create(self, image, pull=True, rm=False, **kwargs):
        if isinstance(image, Image):
            image = image.id

        if not self.conn.repository.get(image):
            if not pull:
                return None
            self.conn.repository.pull(image, pull)

        res = self.conn.client.create_container(image=image, **kwargs)
        self.refresh()
        container = self.get(res.get('Id'))
        container.rm = rm
        return container

    def get(self, name):
        if name in self._by_name:
            return Container(self._by_name[name].get('Id'), self.conn)
        if name in self._by_id:
            return Container(self._by_id[name].get('Id'), self.conn)
        return None

    def refresh(self):
        self._containers = self.conn.client.containers(all=self.all)
        self._index()

class Container(object):
    OOMKilled, Dead, Paused, Running, Restarting, Stopped, Removed = range(1, 8)

    def __init__(self, container_id, conn):
        self.id = container_id
        self.conn = conn
        self._inspect = None
        self._removed = False
        self.inspect()
        self.rm = False

    @property
    def created(self):
        return arrow.get(self._inspect.get('Created'))

    @property
    def image(self):
        return self.conn.repository.get_id(self.image_id)

    @property
    def image_id(self):
        return self._inspect.get('Image')

    @property
    def ip(self):
        self.inspect()
        return self._inspect.get('NetworkSettings', {}).get('IPAddress')

    @property
    def name(self):
        if self._removed:
            return None
        return self._inspect.get('Name')[1:]

    @property
    def running(self):
        return self.state == Container.Running

    @property
    def short_id(self):
        return self.id[:12]

    @property
    def state(self):
        if self._removed:
            return Container.Removed

        # always refresh the container status
        self.inspect()
        if 'State' not in self._inspect:
            raise RuntimeError('invalid dict returned by inspect')
        state = self._inspect['State']

        if state.get('Dead') is True:
            return Container.Dead
        elif state.get('OOMKilled') is True:
            return Container.OOMKilled
        elif state.get('Paused') is True:
            return Container.Paused
        elif state.get('Restarting') is True:
            return Container.Restarting
        elif state.get('Running') is True:
            return Container.Running
        else:
            return Container.Stopped

    def exec(self, cmd, **options):
        res = self.conn.client.exec_create(container=self.id, cmd=cmd,
                                           **options)
        out = self.conn.client.exec_start(exec_id=res.get('Id'))
        exec_res = self.conn.client.exec_inspect(exec_id=res.get('Id'))
        if exec_res.get('ExitCode') != 0:
            raise ExecReturnCodeError(cmd[0], exec_res.get('ExitCode'), out)
        return out.decode('utf-8')

    def inspect(self):
        if self._removed:
            return
        self._inspect = self.conn.client.inspect_container(container=self.id)

    def remove(self, **options):
        if self._removed:
            return
        self.conn.client.remove_container(container=self.id, **options)
        self._removed = True

    def start(self, **options):
        if self._removed:
            raise RuntimeError('container {id} does not exists anymore'.format(self.short_id))
        self.conn.client.start(container=self.id, **options)

    def stop(self, **options):
        if self._removed:
            raise RuntimeError('container {id} does not exists anymore'.format(self.short_id))
        self.conn.client.stop(container=self.id, **options)

    def __enter__(self):
        if not self.running:
            self.start()
        return self

    def __exit__(self, exc_type, _, __):
        if self.running:
            self.stop()

        if self.rm:
            self.remove()

        if exc_type:
            return False

    def __repr__(self):
        return '<Container [' \
               'id={short_id}, ' \
               'image_id={image_id}, ' \
               'status={status}]>'.format(
            short_id=self.short_id,
            image_id=self.image_id[:12],
            state=self.state
        )
