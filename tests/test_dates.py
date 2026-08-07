import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TorontoDateFilteringTests(unittest.TestCase):
    def run_node(self, body: str):
        script = f"""
const dates = require({json.dumps(str(ROOT / 'date-filter.js'))});
{body}
"""
        result = subprocess.run(
            ["node", "-e", script], check=True, capture_output=True, text=True
        )
        return json.loads(result.stdout)

    def test_removes_past_events_and_keeps_today_first(self):
        result = self.run_node("""
const events = [
  {date: '2026-08-08', title: 'Tomorrow'},
  {date: '2026-07-14', title: 'Past'},
  {date: '2026-08-07', title: 'Today'}
];
console.log(JSON.stringify(dates.upcomingEvents(events, new Date('2026-08-07T16:00:00Z'))));
""")
        self.assertEqual([event["title"] for event in result], ["Today", "Tomorrow"])

    def test_uses_toronto_calendar_day_near_utc_midnight(self):
        result = self.run_node("""
console.log(JSON.stringify({key: dates.torontoDateKey(new Date('2026-08-08T02:00:00Z'))}));
""")
        self.assertEqual(result["key"], "2026-08-07")

    def test_page_loads_date_filter_before_application(self):
        html = (ROOT / "index.html").read_text()
        self.assertLess(html.index("date-filter.js"), html.index("app.js"))

    def test_refresh_workflow_runs_daily(self):
        workflow = (ROOT / ".github/workflows/update.yml").read_text()
        self.assertIn("cron: '17 11 * * *'", workflow)
        self.assertNotIn("cron: '17 11 * * 2'", workflow)


if __name__ == "__main__":
    unittest.main()
