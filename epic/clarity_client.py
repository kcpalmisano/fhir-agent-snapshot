
import os, csv
from pathlib import Path

class ClarityClient:
    def __init__(self, dsn=None, uid=None, pwd=None, mock_csv=None):
        self.dsn = dsn or os.getenv('CLARITY_DSN')
        self.uid = uid or os.getenv('CLARITY_UID')
        self.pwd = pwd or os.getenv('CLARITY_PWD')
        self.mock_csv = Path(mock_csv) if mock_csv else None

        self._db = None
        if self.dsn and self.uid and self.pwd:
            try:
                import pyodbc
                conn_str = f"DSN={self.dsn};UID={self.uid};PWD={self.pwd}"
                self._db = pyodbc.connect(conn_str, timeout=5)
            except Exception as e:
                print(f"[ClarityClient] DB connection failed, falling back to CSV mock. Error: {e}")
                self._db = None

    def fetch_recent_notes(self, patient_id: str, limit=5):
        """Return list of dicts: encounter_id, note_datetime, note_type, author, note_text"""
        if self._db:
            return self._fetch_recent_notes_db(patient_id, limit)
        elif self.mock_csv:
            return self._fetch_recent_notes_csv(patient_id, limit)
        else:
            return []

    def _fetch_recent_notes_db(self, patient_id: str, limit=5):
        # Placeholder; customize with your Epic Clarity schema.
        query = f"""
        SELECT TOP {limit}
            n.encounter_id,
            n.note_datetime,
            n.note_type,
            n.author_name,
            n.note_text
        FROM NOTE_VIEW n
        WHERE n.patient_external_id = ?
        ORDER BY n.note_datetime DESC;
        """
        cursor = self._db.cursor()
        cursor.execute(query, patient_id)
        rows = cursor.fetchall()
        cols = [c[0].lower() for c in cursor.description]
        out = []
        for r in rows:
            rec = { cols[i]: r[i] for i in range(len(cols)) }
            out.append({
                'encounter_id': rec.get('encounter_id'),
                'note_datetime': str(rec.get('note_datetime')),
                'note_type': rec.get('note_type'),
                'author': rec.get('author_name'),
                'note_text': rec.get('note_text') or ''
            })
        return out

    def _fetch_recent_notes_csv(self, patient_id: str, limit=5):
        notes_path = self.mock_csv / 'notes.csv'
        out = []
        if not notes_path.exists():
            return out
        with open(notes_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('patient_id') == patient_id:
                    out.append({
                        'encounter_id': row.get('encounter_id'),
                        'note_datetime': row.get('note_datetime'),
                        'note_type': row.get('note_type'),
                        'author': row.get('author'),
                        'note_text': row.get('note_text') or ''
                    })
        out = sorted(out, key=lambda r: r['note_datetime'], reverse=True)
        return out[:limit]
