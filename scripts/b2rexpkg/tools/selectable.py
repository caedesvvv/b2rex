import Blender

from ogredotscene import Selectable

class SelectablePack(object):
    def __init__(self):
        self._pack = []
    def add(self, selectable):
        self._pack.append(selectable)
    def reset(self):
        for selectable in self._pack:
            selectable.setSelected(0)
        Blender.Draw.Redraw(1)

class SelectableRegion(Selectable):
    def __init__(self, selected, region_uuid, app, pack):
        Selectable.__init__(self, selected)
        self.region_uuid = region_uuid
        self.app = app
        self._pack = pack
        self._pack.add(self)
    def setSelected(self, value):
        if value:
            self._pack.reset()
        self.app.setRegion(self.region_uuid)
        return Selectable.setSelected(self, value)
    def select(self):
        self._pack.reset()
        self.app.setRegion(self.region_uuid)
        return Selectable.select(self)
    def deselect(self):
        return Selectable.deselect(self)

