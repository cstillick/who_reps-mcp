# Governors data (vendored)

`src/whoreps_mcp/data/governors.json` is a **vendored snapshot** of U.S.
governors — slow-changing, so we ship it rather than depend on a paid API. It is
deliberately the only non-live tier.

## Honesty about freshness

- The file carries a top-level `as_of` date, and every `Governor` returned by the
  tools surfaces that date in its `as_of` field. Callers can always see how fresh
  the data is.
- Governorships change at predictable times (regular elections; occasional
  mid-term successions). Treat anything past `as_of` as needing verification.

## Refreshing

1. Check the authoritative current list (e.g. the National Governors Association
   roster, or each state's `.gov`).
2. Update the changed `name` / `party` (and optional `website`, `phone`,
   `term_end`) entries in `governors.json`.
3. Bump the top-level `as_of` to today.
4. Run `uv run pytest` (the OK entry is covered) and commit.

States with no governor (DC, territories) are intentionally absent; the service
emits a coverage note for them rather than inventing an office.
