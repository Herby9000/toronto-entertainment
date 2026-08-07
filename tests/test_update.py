import unittest
from datetime import date, timedelta

from scripts import update


class UpdateQualityGateTests(unittest.TestCase):
    def test_accepts_substantive_calendar_when_smaller_categories_are_sparse(self):
        today = date.today()
        events = []
        for category, count in (("Music", 30), ("Comedy", 3), ("Live Events", 10)):
            for index in range(count):
                day = today + timedelta(days=120 if index == count - 1 else index)
                events.append({"category": category, "date": day.isoformat()})

        accepted, counts, span = update.acceptable(events)

        self.assertTrue(accepted)
        self.assertEqual(counts, {"Music": 30, "Comedy": 3, "Live Events": 10})
        self.assertEqual(span, 120)


if __name__ == "__main__":
    unittest.main()
