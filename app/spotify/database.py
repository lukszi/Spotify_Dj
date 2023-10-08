"""
Sqlite database wrapper to cache Tracks, TrackFeatures and TrackSections
"""
import sqlite3
from typing import Optional, List

from app.spotify.model import Track, TrackFeatures
from app.spotify.model.track import TrackSection


class Database:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.db = sqlite3.connect(file_name)
        # Create tables
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS track_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                acousticness REAL,
                danceability REAL,
                energy REAL,
                instrumentalness REAL,
                valence REAL
            );
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS track_sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loudness REAL,
                tempo REAL
            );
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id TEXT PRIMARY KEY,
                name TEXT,
                href TEXT,
                fk_section_first int,
                fk_section_last int,
                fk_features int,
                FOREIGN KEY (fk_section_first) REFERENCES track_sections(id),
                FOREIGN KEY (fk_section_last) REFERENCES track_sections(id),
                FOREIGN KEY (fk_features) REFERENCES track_features(id)
            );            
        """)

    def bulk_initialize_tracks(self, tracks: List[Track]):
        """
        Initialize all tracks from the given list with data from the database (if available)
        :param tracks: List of tracks with at least their id initialized
        """
        track_ids = [track.id for track in tracks]
        cursor = self.db.execute("""
            SELECT * FROM tracks WHERE id IN (%s)
        """ % ','.join('?' * len(track_ids)), track_ids)
        result = cursor.fetchall()
        for track in result:
            t_id = track[0]
            for t in tracks:
                if t.id == t_id:
                    t.name = track[1]
                    t.href = track[2]
                    t.features = self.get_track_features(track[5])
                    t.section_analysis = (self.get_track_section(track[3]), self.get_track_section(track[4]))

    def get_track(self, track_id: str) -> Optional[Track]:
        cursor = self.db.execute("""
            SELECT * FROM tracks WHERE id = ?
        """, (track_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            track = Track()
            track.id = result[0]
            track.name = result[1]
            track.features = self.get_track_features(result[5])
            track.section_analysis = (self.get_track_section(result[3]), self.get_track_section(result[4]))
            return track

    def insert_track(self, track: Track):
        try:
            self.db.execute("""
                INSERT INTO tracks (id, name, href, fk_section_first, fk_section_last, fk_features)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (track.id,
                  track.name,
                  track.href,
                  self.insert_track_section(track.section_analysis[0]),
                  self.insert_track_section(track.section_analysis[1]),
                  self.insert_track_features(track.features)))
            self.db.commit()
        except sqlite3.IntegrityError:
            self.db.rollback()

    def insert_track_section(self, section: TrackSection) -> int:
        cursor = self.db.execute("""
            SELECT id FROM track_sections WHERE loudness = ? AND tempo = ?
        """, (section.loudness, section.tempo))
        result = cursor.fetchone()
        if result is None:
            cursor = self.db.execute("""
                INSERT INTO track_sections (loudness, tempo) VALUES (?, ?)
            """, (section.loudness, section.tempo))
            self.db.commit()
            return cursor.lastrowid
        else:
            return result[0]

    def insert_track_features(self, features: TrackFeatures) -> int:
        cursor = self.db.execute("""
            SELECT id FROM track_features 
            WHERE acousticness = ? AND danceability = ? AND energy = ? AND instrumentalness = ? AND valence = ?
        """, (features.acousticness,
              features.danceability,
              features.energy,
              features.instrumentalness,
              features.valence))
        result = cursor.fetchone()
        if result is None:
            cursor = self.db.execute("""
                INSERT INTO track_features (acousticness, danceability, energy, instrumentalness, valence) VALUES (?, ?, ?, ?, ?)
            """, (features.acousticness,
                  features.danceability,
                  features.energy,
                  features.instrumentalness,
                  features.valence))
            self.db.commit()
            return cursor.lastrowid
        else:
            return result[0]

    def get_track_features(self, feature_id: int) -> Optional[TrackFeatures]:
        cursor = self.db.execute("""
            SELECT * FROM track_features WHERE id = ?
        """, (feature_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            return TrackFeatures(result[1], result[2], result[3], result[4], result[5])

    def get_track_features_by_track(self, track: Track) -> Optional[TrackFeatures]:
        cursor = self.db.execute("""
            SELECT track_features.* 
            FROM track join track_features on track.fk_features == track_features.id 
            WHERE track.id = ?
        """, (track.id,))
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            return TrackFeatures(result[1], result[2], result[3], result[4], result[5])

    def get_first_track_sections_by_track(self, track: Track) -> Optional[TrackSection]:
        cursor = self.db.execute("""
            SELECT track_sections.* 
            FROM track join track_sections on track.fk_section_first == track_sections.id 
            WHERE track.id = ?
        """, (track.id,))
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            return TrackSection(result[1], result[2])

    def get_last_track_sections_by_track(self, track: Track) -> Optional[TrackSection]:
        cursor = self.db.execute("""
            SELECT track_sections.* 
            FROM track join track_sections on track.fk_section_last == track_sections.id 
            WHERE track.id = ?
        """, (track.id,))
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            return TrackSection(result[1], result[2])

    def get_track_section(self, section_id: int) -> Optional[TrackSection]:
        cursor = self.db.execute("""
            SELECT * FROM track_sections WHERE id = ?
        """, (section_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            return TrackSection(result[1], result[2])
