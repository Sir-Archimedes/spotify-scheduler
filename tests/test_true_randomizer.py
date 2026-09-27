import json
import random
import tempfile
import unittest
from pathlib import Path

from true_randomizer import (
    TRUE_RANDOM_HISTORY_SIZE,
    build_true_random_queue,
    load_true_random_history,
    update_true_random_history,
)


def tracks(count):
    return [f"spotify:track:{index:03d}" for index in range(count)]


class TrueRandomizerTests(unittest.TestCase):
    def test_large_playlist_prefers_non_recent_tracks(self):
        source_tracks = tracks(200)
        recent = source_tracks[:30]

        queue = build_true_random_queue(source_tracks, recent, rng=random.Random(1))
        non_recent_count = len([uri for uri in source_tracks if uri not in set(recent)])

        self.assertEqual(len(queue), 100)
        self.assertTrue(all(uri not in recent for uri in queue[:min(non_recent_count, 100)]))

    def test_no_history_returns_all_available_tracks_without_duplicates(self):
        source_tracks = tracks(50)

        queue = build_true_random_queue(source_tracks, rng=random.Random(2))

        self.assertEqual(len(queue), 50)
        self.assertEqual(len(queue), len(set(queue)))
        self.assertEqual(set(queue), set(source_tracks))

    def test_playlist_smaller_than_history_still_returns_valid_queue(self):
        source_tracks = tracks(10)
        recent = tracks(30)

        queue = build_true_random_queue(source_tracks, recent, rng=random.Random(3))

        self.assertEqual(len(queue), 10)
        self.assertEqual(len(queue), len(set(queue)))
        self.assertEqual(set(queue), set(source_tracks))

    def test_duplicate_track_uris_are_removed(self):
        source_tracks = tracks(5) + [tracks(5)[0], tracks(5)[1]]

        queue = build_true_random_queue(source_tracks, rng=random.Random(4))

        self.assertEqual(len(queue), 5)
        self.assertEqual(len(queue), len(set(queue)))

    def test_corrupt_history_json_recovers_safely(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "true_random_history.json"
            history_path.write_text("{not-json", encoding="utf-8")
            logs = []

            history = load_true_random_history(str(history_path), logs.append)

        self.assertEqual(history, {})
        self.assertTrue(any("malformed" in message for message in logs))

    def test_consecutive_blocks_avoid_first_block_history(self):
        source_tracks = tracks(200)

        first_queue = build_true_random_queue(source_tracks, rng=random.Random(5))
        history = update_true_random_history([], first_queue, TRUE_RANDOM_HISTORY_SIZE)
        second_queue = build_true_random_queue(source_tracks, history, rng=random.Random(6))

        self.assertEqual(len(history), TRUE_RANDOM_HISTORY_SIZE)
        self.assertTrue(all(uri not in history for uri in second_queue[:100]))


if __name__ == "__main__":
    unittest.main()
