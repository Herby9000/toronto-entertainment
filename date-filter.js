(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.AfterDarkDates = api;
})(typeof globalThis === "object" ? globalThis : this, function () {
  function torontoDateKey(now = new Date()) {
    const parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: "America/Toronto",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).formatToParts(now);
    const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
    return `${values.year}-${values.month}-${values.day}`;
  }

  function upcomingEvents(events, now = new Date()) {
    const today = torontoDateKey(now);
    return [...events]
      .filter((event) => event.date >= today)
      .sort((left, right) => left.date.localeCompare(right.date) || left.title.localeCompare(right.title));
  }

  return { torontoDateKey, upcomingEvents };
});
