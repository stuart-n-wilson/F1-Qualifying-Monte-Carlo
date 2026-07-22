import fastf1 as f1
import pandas as pd
import os
import time

os.makedirs("fastf1_cache", exist_ok=True)
f1.Cache.enable_cache("fastf1_cache")

start_year = 2018
end_year = 2026

for year in range(start_year, end_year + 1):
    try:
        schedule = f1.get_event_schedule(year, include_testing=False)
    except Exception as e:
        print(f"Could not load schedule for {year}: {e}")
        continue

    # Only past events
    past_events = schedule.loc[schedule["EventDate"] <= pd.Timestamp.today(), "EventName"].to_list()

    for gp in past_events:
        try:
            session = f1.get_session(year, gp, 'Q')
            session.load(laps=True, telemetry=False, weather=False, messages=False)
            time.sleep(2)
            print(f"✓ {year} {gp} — {len(session.laps)} laps")
        except Exception as e:
            print(f"✗ {year} {gp} — failed: {e}")

print("\nCaching complete.")