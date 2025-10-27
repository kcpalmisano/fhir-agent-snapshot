
import os
from pathlib import Path
from time import time

class EncounterWatcher:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self._state = {}  # patient_id -> last_mtime

    def _encounters_path(self, pid):
        return self.data_dir / pid / 'Encounters.json'

    def _mtime(self, path: Path):
        try:
            return path.stat().st_mtime
        except FileNotFoundError:
            return 0.0

    def poll(self):
        changed = []
        for patient_dir in [p for p in self.data_dir.iterdir() if p.is_dir()]:
            pid = patient_dir.name
            path = self._encounters_path(pid)
            mtime = self._mtime(path)
            last = self._state.get(pid, 0.0)
            if mtime > last:
                # Update and flag as changed
                self._state[pid] = mtime
                changed.append(pid)
        return changed
