# GTFS Data Handling

This document explains how Bussikartta handles **GTFS (General Transit Feed Specification)** data, specifically the static transit schedule data. It covers how GTFS files are obtained, parsed, and imported into the system, how updates to the data are managed, and how the static data is used in conjunction with real-time information. Understanding GTFS handling is crucial, as it provides the foundational context (routes, stops, timetables) that make the real-time vehicle data meaningful.

## What is GTFS and Why It Matters

**GTFS** is a standard format for public transit schedules and associated geographic information【5†L95-L103】. Transit agencies (like HSL in Helsinki) publish their route schedules, stop locations, and other transit data as a GTFS package (usually a ZIP file containing multiple text files). GTFS is split into:
- **GTFS Static** (schedules): includes routes, trips, stops, stop times, calendars, etc.
- **GTFS Realtime**: a separate feed (often using protocol buffers) for live updates like vehicle positions or delays.

Bussikartta uses the GTFS static data to know **where and when vehicles are supposed to be**:
- By loading route and stop definitions, the system can display route names and stop names instead of IDs.
- By loading the timetable (trips and stop times), it can compare a bus’s actual timing to the schedule and compute delays or detect if a vehicle is off-schedule.
- Essentially, GTFS static data provides the *planned world* against which the *real-time world* is measured.

## Importing GTFS Static Files

**Source of GTFS Data:** For the Helsinki region, HSL provides a GTFS feed that is updated daily【27†L65-L72】. The latest GTFS static zip can be downloaded from HSL’s open data website (a link is typically provided, e.g., to an HSL data storage URL). Other regions (like Tampere’s TKL or Waltti cities) also provide GTFS feeds, either through separate URLs or an API (often requiring a key).

In Bussikartta, the GTFS static import process is as follows:

1. **Download the GTFS Zip:** The system either includes a script to fetch the file from a configured URL or expects the user to provide the GTFS zip file. For HSL, the daily-updated zip is accessible at a known URL【27†L65-L72】 (for example, `https://infopalvelut.storage.hsldev.com/gtfs/hsl.zip` – actual link may differ, but that’s the idea). In deployment, one can automate downloading this file periodically.
   
2. **Unzip and Parse CSV Files:** GTFS zip contains multiple text files (CSV format, usually `,` or `,` separated). Key files we parse:
   - `agency.txt` – transit agency info (not critical for our purposes except for reference).
   - `stops.txt` – list of all stops and their coordinates.
   - `routes.txt` – list of all routes (each route has an ID, short name, long name, type like bus or tram, etc.).
   - `trips.txt` – list of all trips. Each trip is an instance of a route on a specific service (e.g., a bus journey for a given day), with a trip ID, and references to route_id and service_id (which days it runs).
   - `stop_times.txt` – schedule times for each trip at each stop (sequence of stops with arrival/departure times).
   - `calendar.txt` and `calendar_dates.txt` – define the service calendar (which days the regular schedules operate, and exceptions/holidays). Important for figuring out which trips are active on a given date.
   - `shapes.txt` – (optional) geographic path for trips (sequence of lat/lon points). Useful for drawing route lines on a map.

   The import code reads these files (commonly using a CSV reader or a specialized GTFS library). Because these files can be large (HSL has tens of thousands of stop_times rows), the parsing is done carefully (streaming line by line, or using bulk copy to database for efficiency).
   
3. **Database Import:** After parsing, the data is inserted into the database tables:
   - **Stops table:** Each record from stops.txt becomes a row (stop_id, name, latitude, longitude, etc.).
   - **Routes table:** Each record from routes.txt becomes a row (route_id, short_name, long_name, type, etc.).
   - **Trips table:** Each record from trips.txt becomes a row (trip_id, route_id, service_id, headsign, direction, etc.).
   - **StopTimes table:** Each record from stop_times.txt becomes a row (trip_id, stop_id, arrival_time, departure_time, stop_sequence, etc.).
   - **Calendar/CalendarDates tables:** These can be loaded to determine service validity. (Alternatively, some systems merge this logic into filtering trips by date when needed rather than storing full calendar info.)
   - **Shapes table:** If used, each shape_id’s polyline points could be stored, or perhaps generated on the fly. (Storing shapes might be skipped if not needed immediately, to save space.)

   We ensure appropriate indexing on these tables. For example:
   - Index on `trip_id` in StopTimes (since queries will often filter by trip).
   - Composite index on (stop_id, arrival_time) if one wants to get next trips for a stop.
   - Index on route_id in Trips to get all trips of a route (though one could join trips to route for that).

4. **Data Refresh vs Update:** If this is the first import, it’s a simple insertion. For updates (like when a new GTFS feed is out), the process is typically:
   - Either **wipe and replace**: Drop or truncate the tables and insert all new records (simplest approach, ensures no stale data, but causes downtime on schedule info during the operation).
   - Or **diff and update**: Compare new data with old and apply inserts/updates/deletions. This is complex and usually not necessary if we can afford a quick downtime or if done in a transaction.
   - Bussikartta likely opts for the simpler approach: when updating GTFS, perform it during a maintenance window or when it won’t affect many users, and reload all static data fresh.
   - Using a transaction or temporary tables can ensure that until the update is fully applied, the old data remains in place for the API. After insertion, it swaps to the new data to avoid partially updated state.

5. **Verification:** After import, optionally verify counts (e.g., number of stops, routes) or log success. The system could also store the GTFS feed version (from feed_info.txt if present, which often has a feed version or valid date range) to know what data is currently loaded.

The GTFS data essentially populates the **reference tables** in our database. These do not change until a new feed is loaded (e.g., new schedules, route changes, etc., which might be weekly or seasonal for many agencies, daily for HSL as they refine data).

## Updating GTFS Data

**Frequency of Updates:** HSL provides updated static data daily【27†L65-L72】, but many of those updates may be minor. Depending on use case, we might not need to update daily. However, to ensure accuracy (especially for long-term use or if route changes occur), it’s good to update whenever a new official feed is available or at least whenever the feed’s expiration date nears. GTFS `feed_info.txt` often contains an `expiry_date` after which the data is no longer valid.

**Process to Update:**
- The deployment documentation details how to run the update (usually by re-running the import process or script). Typically:
  1. Fetch the latest GTFS zip.
  2. Stop the ingestion of real-time temporarily (to avoid processing data that might refer to old schedule in the middle of update).
  3. Run the import script to refresh static tables.
  4. Resume normal operation.
  
- If downtime needs to be minimized, one strategy is:
  - Load new data into separate tables or a temporary schema.
  - Once loaded, point the application (or swap table names) to use the new tables.
  - Drop the old tables.
  This way, the API could continue to serve from old data until the new is fully ready, then seamlessly switch. This is an advanced approach and might not be necessary unless users require 24/7 availability.

**Multiple Regions / Feeds:** If Bussikartta is extended to other regions (e.g., Tampere’s transit, VR trains):
- We might ingest multiple GTFS feeds. This can be done by adding an `agency_id` or region field to the tables, or by prefixing IDs (e.g., HSL’s stop IDs are distinct strings that might start with HSL, Tampere’s with TKL, etc., or one can namespace them).
- Alternatively, maintain separate schema or databases for each region. But that complicates cross-region queries.
- The system design currently is within a single database, so likely we incorporate an `agency` dimension. For example, HSL vs TKL route IDs might conflict, but if they do, we ensure to store them with an agency qualifier or in separate tables.
- The MQTT real-time subscriber would also have to subscribe to multiple sources (different broker or topics for different cities) and tag incoming data with the region.

At the moment, the focus is HSL (since the project name is Finnish and HSL provides both static and high-frequency data). So multiple feeds might be a future consideration.

## Cross-Referencing Static and Real-Time Data

One of the most important aspects of Bussikartta is combining static schedule info with live data. Here’s how that works:

- **Matching Vehicles to Trips:** Each real-time vehicle update needs to be associated with the corresponding planned trip (if possible). In HSL’s feed, messages often include either a `trip_id` or enough information to infer it (like start time, route, direction). According to the MQTT topic structure, it includes a trip identifier and a start time【47†L79-L87】【47†L95-L103】. In the JSON, sometimes a `oper` (operational number) and `start` might appear. We attempt to use that to find a matching trip in the Trips table.
  - If a direct trip_id is given in the data (some feeds do give a GTFS trip_id), then it’s straightforward: join vehicle position to trip via that ID.
  - If not, we might match by route and schedule: e.g., if we know the vehicle’s line (route) and we have its next stop and an approximate schedule time, we could guess which trip from today’s schedule it corresponds to. This is complicated and not 100% reliable if multiple trips overlap. However, HSL’s high-frequency feed likely provides enough info to determine the exact trip.

- **Using Stop Times for Delays:** Once a vehicle is linked to a trip, we can compare its actual timestamps to the planned times in `stop_times`:
  - If the feed gives `next_stop_id` and the vehicle’s current status (maybe whether it’s departing or approaching), we can find in `stop_times` the scheduled arrival time for that `trip_id` at that `stop_id`.
  - By comparing the current time (or a provided timestamp `tsi`) with the scheduled time, we get a delay. For example, if a bus was scheduled to depart Stop X at 10:30:00 but it’s now 10:33:00 and it has not yet departed, it’s 3 minutes late.
  - The system could compute this on the fly for each update and even store the `delay_seconds` or `delay_minutes` in the `vehicle_positions` table. This way, the API can directly return the latest known delay for each vehicle without recomputation.
  - Alternatively, the API can compute delay when serving data: e.g., for each vehicle in the response, do a quick lookup of the corresponding stop_times entry for [trip_id, next_stop] and compute difference. This may add some overhead per request, but with indexes it should be fine. Caching could also be used (delay doesn’t need millisecond accuracy, so a cached value for a minute is acceptable).

- **Enriching API Responses:** Thanks to static data, the API can provide friendly information:
  - Instead of just `route_id` (which might be an internal code like “HSL:1050”), it can include `route_short_name` (e.g., “550”) and `route_long_name` (“Westendinasema - Itäkeskus”) from the routes table.
  - For stops, instead of just an ID, it can include the stop’s name (“Railway Square” etc.) if relevant in a response (like when listing a vehicle’s next stop).
  - It can also indicate the final destination of the trip by looking up the trip’s headsign or last stop in stop_times.
  - These enhancements make the frontend (and any API consumer) simpler, as it doesn’t have to do its own lookups for basic info.

- **Handling Schedule Exceptions:** GTFS has calendar exceptions (like holiday schedules or special events). On a given date, some trips might not run or extra trips might exist. The import of calendar and calendar_dates allows the system to know which trips are active **today**. The real-time feed typically only gives updates for trips that are actually running, so probably we won’t get a vehicle for a trip that isn’t running. But when computing delays, we should ensure we’re using the correct schedule for that day.
  - One way to handle this is to only load (or mark) trips that are active today. For example, run a filtering at import or query time using the service_id and the calendar tables. In practice, since HSL updates daily and presumably only includes active trips for current or near-future days, we might assume data is current.
  - Another approach is ignoring calendar and just trust that if a vehicle is reported on a trip, that trip is valid at that time.

- **Future or Past Data:** Bussikartta mainly focuses on “now.” But if one wanted to query “how late was the bus on trip X yesterday,” the data is in our database (historical positions). We would then also need the schedule of yesterday (which should still be the same trip, since we keep past days’ trips until the feed updates). Over time, old trips might be pruned. If the GTFS feed updated and changed trip IDs, we might lose reference to old trip IDs for historical data. One mitigation is to keep old static data or at least keep trip records around even if they are not in current schedule (maybe mark them inactive). For simplicity, we may not do that unless historical analysis is a goal.

## GTFS-Realtime (Protocol Buffers) Handling

While HSL uses a JSON-over-MQTT format, many agencies use GTFS-Realtime (GTFS-RT) which is a protobuf format. Bussikartta’s architecture could accommodate that if needed:
- GTFS-RT provides three types of messages: **Vehicle Positions**, **Trip Updates**, and **Service Alerts**. Vehicle Positions is akin to what we’re getting via HSL’s feed (though in HSL we get more frequent data). Trip Updates include delays and predicted times explicitly.
- If we were to ingest a GTFS-RT Trip Updates feed (for example, HSL also provides one via a different API【46†L77-L84】), we might get direct delay information without computing it. However, since the high-frequency feed is comprehensive and we compute delays ourselves, we currently don’t ingest Trip Updates.
- For other cities on Waltti, if using the Digitransit MQTT broker, the messages might already be GTFS-RT binary. In that case, the ingestion module would need a protobuf decoder. There are libraries (Google’s gtfs-realtime-bindings for Python) to decode those into objects. Once decoded, the handling is similar: insert positions into DB, use trip_ids and delay fields from TripUpdate if needed.
- Bussikartta’s GTFS handling focus has been static data and the high-frequency feed, but the system is flexible to incorporate these other real-time sources if needed, thanks to the robust GTFS static foundation and an extensible ingestion pipeline.

## Summary: How Static and Real-Time Work Together

1. **Initial setup:** Load GTFS static data into the database. Now the system knows all stops, routes, and schedules.
2. **Real-time running:** As vehicles move, we receive updates and log them. Each update is tagged (explicitly or implicitly) with which trip it belongs to.
3. **Delay calculation:** Using the schedule, for each vehicle we can find the next timing point. If a bus is passing stop A at 12:05 but was scheduled at 12:00, we mark it ~5 minutes late. This gets updated as it moves.
4. **User/API query:** A client asks for the status of a certain route or vehicle. The API returns information like “Bus 123 (route 550) is 5 minutes late, last seen at Stop A at 12:05, next stop B at 12:10 scheduled (12:05 actual).”
5. **Update schedule:** A new timetable is effective from next Monday – we update the GTFS data over the weekend. The new data gets loaded, and the next week’s real-time positions will automatically line up against the new schedule (since the trip IDs and times have been updated in the DB).

The combination of GTFS static and real-time feeds allows Bussikartta to present a richer picture than just dots on a map – it can tell how those dots relate to the expected transit service. It transforms raw location data into actionable information like delays and service quality.

## Handling GTFS Data Quality and Edge Cases

- **Missing Data:** Sometimes GTFS static might lack certain optional files (e.g., no shapes.txt) – the system should handle that gracefully (e.g., if shapes are not present, the map simply won’t draw route lines, which is fine).
- **Incorrect IDs:** If a real-time feed references an unknown trip or stop (perhaps due to a data mismatch or a special extra service not in static feed), the system should handle it. Typically:
  - If a `trip_id` from real-time isn’t in the DB, we might log it and skip delay calc for that vehicle (treat it as no schedule info, so delay unknown). This could happen for unscheduled extras or if our static data is outdated.
  - If a `stop_id` isn’t found, similarly, skip naming that stop.
- **Time zone and Midnight rollover:** GTFS times in stop_times can go beyond 24:00 (e.g., 26:30 for 2:30 AM next day). Bussikartta needs to interpret these properly relative to the service day. The import likely converts those to absolute timestamps or stores times as text with a day offset. When comparing current time to scheduled time, take care if a trip goes past midnight.
- **Performance of Join:** Combining live and static data is frequent but static tables are not huge (stops maybe a few thousand, routes a few hundred, stop_times large but indexed by trip). The API’s queries typically will filter by trip or route which is efficient. Still, ensure that any join in a SQL query has proper indexes and perhaps limit the scope (for example, when asking for “next departures at stop X”, only look at trips active today).
- **Memory:** If needed, some static data (like a map of stop_id to Stop name) could be cached in memory in the backend to avoid hitting the database for every name lookup. For example, on startup, load all stops into a dictionary. Since stops are a few thousand entries, that’s trivial in memory. Then the API can quickly translate stop IDs to names without a DB query. This is a trade-off (cache consistency if data updates, but static data updates infrequently and the backend could restart on GTFS update anyway).
- **Testing GTFS Import:** The project might include a smaller sample GTFS (or a subset of data) to test the pipeline. Always test that the parser correctly maps columns to fields and that all necessary data is loaded.

## Example Walk-through

To illustrate, consider an example after the GTFS is loaded:

- Route **550** has a trip (ID `HSL:1050_Ti_20230615_001`) scheduled to leave *Itäkeskus* at 12:00 and arrive *Westend* at 13:00, with many stops in between.
- At 12:30, our MQTT feed sees a bus location at latitude X, longitude Y, which corresponds to somewhere near a stop, and the message indicates it’s that trip. We insert a record: vehicle 123, trip_id `..._001`, time 12:30, location (X,Y).
- We look up that trip in stop_times. Let’s say at 12:30 it was supposed to be at *Otaniemi* stop at 12:25. Clearly it’s behind schedule. We compute: supposed to depart Otaniemi at 12:25, now 5 minutes late departing Otaniemi. We save `delay_seconds = 300` in the DB for that position.
- The API’s `/vehicles` endpoint when requested at 12:31 finds the latest position for vehicle 123, sees delay 300s, and finds next_stop in message or by seeing the next stop sequence after Otaniemi from stop_times. It returns JSON like:
  ```json
  {
    "vehicle_id": "123",
    "route": "550",
    "location": { "lat": X, "lon": Y },
    "last_stop": "Otaniemi",
    "last_stop_departure_scheduled": "12:25",
    "last_stop_departure_actual": "12:30",
    "delay_minutes": 5,
    "next_stop": "Keilaniemi",
    "next_stop_eta": "12:35 (scheduled 12:30)"
  }
  ```
  (Exact format may vary; the key is static data allowed us to fill in those names and scheduled times).

- If the schedule updates next day, that trip_id might change (because date in it changes). The next day’s realtime feed will reference `..._20230616_...` trip. As long as we loaded the new feed, we have that trip and so on.

This interplay ensures **riders/developers see not just where vehicles are, but whether they’re on time** – the core purpose of Bussikartta.

---

By carefully handling GTFS static data – keeping it up-to-date and accurately linking it with incoming realtime data – Bussikartta provides a reliable and insightful view of transit operations. The GTFS ingestion and cross-referencing process might be complex under the hood, but it results in a seamless experience where live data is always contextualized by schedule expectations. This document covered the mechanics of that process. In the next documentation sections, we cover how the frontend leverages this data and the specifics of the API endpoints that deliver both static and dynamic data to users.


