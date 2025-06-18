# Frontend Architecture

This document describes the planned architecture and design of the Bussikartta frontend. The frontend is the user-facing web application that visualizes real-time bus data on a map and provides an interface for users to interact with the system. While development of the frontend may be ongoing, the technology choices and strategies are outlined here to guide implementation and to inform new developers of the approach.

## Technology Stack

The frontend will be built with **React** as the core framework for building the user interface. In addition, we are using modern tools and libraries to streamline development and provide a responsive, interactive experience:

- **React** (with Hooks and functional components): A component-based approach to build a dynamic single-page application. React’s declarative nature fits well for updating many elements (bus markers) in response to state changes (live data).
- **Tailwind CSS**: A utility-first CSS framework that allows rapid styling directly in component classes. This ensures a consistent design system and speeds up UI development by avoiding writing a lot of custom CSS. It’s highly customizable (we can define a theme for the app’s look and feel).
- **MapLibre GL JS**: An open-source mapping library (fork of Mapbox GL JS) for rendering interactive maps. MapLibre can display Mapbox Vector Tiles or raster tiles for the basemap. We chose this for its ability to handle a large number of markers and dynamic data smoothly using WebGL. It allows custom layers, styling, and animation which are beneficial for our use-case (like animating bus movement or showing routes).
- **TypeScript** (optional but likely): We anticipate using TypeScript with React for better type safety and developer experience. This can catch errors early and document the shape of data we handle (like the structure of API responses).

Additionally, common React ecosystem tools will likely be used:
- **State management**: The plan is to use React’s built-in Context API or a state management library (like Redux or Zustand) to handle global state. Global state might include things like the list of vehicles, the selected route or stop filters, user’s map view (current zoom/bounds), etc. Given the app isn’t extremely complex in state, Context + Hooks may suffice.
- **React Query or SWR**: We might use a data-fetching library like React Query to manage API calls, caching, and updates. This is very handy for polling or real-time updates as it can refetch data on interval or when certain conditions are met, and keeps a cache to avoid unnecessary calls.
- **Build tooling**: Likely Create React App or Vite for initial setup, configured to integrate Tailwind (which requires PostCSS) and possibly to load MapLibre’s CSS, etc. The build pipeline will produce an optimized bundle for production.

## Application Structure

The UI will be organized into components corresponding to different parts of the interface. A possible breakdown:
- `<MapView>`: The core component that renders the MapLibre map. It will initialize the map, load a basemap style (perhaps an OpenStreetMap style or HSL’s base map tiles【27†L40-L47】), and add layers/markers for vehicles and other data.
- `<VehicleMarker>`: A component or layer representation for vehicles. We might not use individual React components for each marker (as thousands of DOM elements would be slow); instead we use MapLibre’s API to draw points. This could be done by converting vehicle data to a GeoJSON source and using a symbol layer, or by programmatically adding Marker objects. The strategy will be to let MapLibre handle marker rendering in bulk via its WebGL layer for efficiency.
- `<Sidebar>` or `<Controls>`: UI for controlling the view – e.g., a list of routes to filter by, a search box to find a stop or route, legend for marker colors, etc.
- `<RouteList>` / `<RouteItem>`: If the UI lists routes (with maybe current alerts or how many vehicles, etc.), components for those.
- `<StopInfo>`: A pop-up or side panel that shows details when a user selects a stop (like next departures and their delays).
- `<VehicleInfoPopup>`: If a vehicle marker is clicked, perhaps a small popup showing its line, destination, delay, etc.
- `<Header>` and `<Footer>`: Basic branding or title, plus maybe a last updated timestamp or link to data source credits (we should credit HSL open data, etc., in the UI).

The app’s state includes:
- Selected route filter (could be “All routes” or a specific route).
- Selected stop or vehicle (if any, for details).
- Map viewport (center, zoom) which we track to possibly only show relevant vehicles.
- The vehicles data itself (which updates frequently).
- Static data like list of routes, stops (for search) – these can be loaded once at startup.

**Data Flow in the App:**
1. On app load, fetch static data needed (e.g., list of all routes with names and IDs, maybe a list of stops if doing search – though thousands of stops might be heavy to load all at once, might rely on API search instead).
2. Initialize the MapLibre map with a base map. Possibly use an open tile source, or if HSL’s map API is open, their tile server could provide nicely styled transit map tiles.
3. Fetch current vehicle positions from the backend API. This could be done via a GET request to `/vehicles` endpoint. The response will be a list of vehicles with their coords, route, maybe delay, etc.
4. Plot these vehicles on the map:
   - Convert vehicle list to a GeoJSON `FeatureCollection` with Point features and properties. Use MapLibre’s `map.addSource({...})` with type geojson. Then define a layer (`map.addLayer({ id: 'vehicles', type: 'symbol', source: 'vehicles', ... })`).
   - Use an icon (e.g., a bus icon or colored circle) for the symbol. We can use data-driven styling: e.g., color the icon based on delay (green if on time, orange if moderate delay, red if very late).
   - Alternatively, use the Marker API for simplicity (MapLibre’s Mapbox API compatibility allows `new mapboxgl.Marker()` per vehicle). This is easier to implement but can be slower with many markers.
   - We will likely try the vector layer approach for performance.
5. Set up updates: Because vehicles move, we need to update the map periodically:
   - **Polling approach:** Use `setInterval` or React Query’s refetch interval to call the `/vehicles` API every N seconds (for HSL, a 10-15 second interval might be fine, though HSL feed is 1 sec, such frequent polling might overload API; if we want near-real-time, maybe 5 seconds is a compromise).
   - On each update, merge the new data: simplest is to replace the entire vehicles source with the new GeoJSON. MapLibre can diff it internally or re-draw all points. With WebGL, drawing a few thousand points is fine.
   - The map view can smoothly animate markers if desired (Mapbox GL has an API for updating source data which by default will just move them to new positions without animation; we can implement a tween for nicer movement if needed).
   - The polling interval can be tuned. If the backend ever supports a WebSocket or Server-Sent Events for pushes, the frontend could switch to that for truly instant updates.
   - Also, if using MQTT directly from the browser were possible (HSL’s broker supports WebSocket connections as listed【47†L73-L81】 via mqtt.digitransit.fi in some cases), one could have the frontend subscribe to MQTT and update vehicles client-side. However, decoding and security (CORS, needing an API key for some brokers) make that complex. The simpler architecture is to use our backend API as the single data source for the web.
6. Interaction:
   - Clicking a vehicle marker: We can set up an event on the map layer (`map.on('click', 'vehicles', (e) => { ... })`). That can retrieve the feature (vehicle data). We then display a small popup at that location with info (route, destination, current delay, etc.). We can use MapLibre’s Popup for this or a custom React component overlay.
   - Filter by route: Suppose the UI has a dropdown or list of routes. If the user selects one (e.g., Route 550), we update a filter in the map layer: MapLibre allows filtering features by properties. Our vehicle GeoJSON features have a property like `route_id` or `route_short_name`. We can apply `map.setFilter('vehicles', ['==', ['get', 'route_short_name'], '550'])`. This will only show those markers. Simultaneously, we might call the API with a filter param (e.g., `/vehicles?route=550`) to reduce data, but since filtering on the client is easy, we might just get all and filter clientside.
   - Searching for a stop: We could implement a search bar where a user types a stop name. We’d likely call a `/stops?query=<name>` API to get matches (since loading all stops to client for fuzzy search is heavy). Once a stop is selected, we can:
     - Highlight that stop on the map (perhaps add a marker or a pulse animation).
     - Center map to that stop.
     - Show upcoming departures: The frontend can call `/stops/{stop_id}/departures` to get next departures and their status. That could be shown in a panel.
   - Real-time updates affecting UI: When new data arrives, the UI should update any open popup or panel if relevant (e.g., if we have a vehicle popup open showing “5 min late”, after next update it might become “4 min late” or “6 min late”; we should update that in real-time).
   - We may use React state to keep track of selected vehicle and feed it updated data from the polling response (e.g., find that vehicle in the list and update the popup component’s props).

## Rendering and Performance Strategy

**Map Rendering:**
- Using MapLibre GL (WebGL) means the map and markers are rendered on the GPU, allowing thousands of points to be rendered smoothly. This is superior to using plain HTML markers for each vehicle, especially as the number grows.
- If we have a very large number of vehicles (say, over 1000), we might consider clustering or reducing detail when zoomed out. For example, at a city-wide zoom, showing individual 2000 points could be cluttered. We might cluster them (MapLibre can cluster GeoJSON points) to show like “100 buses in view” clusters, which then break apart as you zoom in.
- Initially, we might skip clustering if performance is acceptable and opt for showing all vehicles. But we will set sensible limits, e.g., limit the map view to region of interest to avoid showing vehicles outside area if we had multiple cities loaded.
- We will also define different icon styles or colors for different vehicle types (if we have trams, trains, etc., or differentiate bus vs tram by icon, as HSL route types indicate mode).
- Tailwind will help style UI elements (buttons, lists) but not directly map markers; map markers styling is done through MapLibre style specification (we can include a small SVG icon or font glyph for the marker).

**Frequent Data Updates:**
- Because data updates often, we must ensure applying updates is efficient:
  - Replacing the entire GeoJSON source is a single operation from the map’s perspective and should be efficient. The diff will likely just move points mostly.
  - React components themselves should not re-render unnecessarily. For example, we won’t represent each vehicle as an individual React component that re-renders on each update (that would be 1000s of component updates). Instead, all vehicles are in one MapLibre layer. We let MapLibre handle the heavy lifting in a single go.
  - UI components like lists or tables (if any) should use keys and only re-render minimal parts. E.g., if we showed a list of routes with average delay, only update the one that changed.
- Using an optimized state library or React’s own batching will help. If using Redux or Context, ensure the state slice for vehicles is handled carefully (maybe store as an object map by id to update easily, etc.).
- We should also consider memory leaks or buildup: each interval refetch should cancel or overwrite previous (React Query handles this nicely).
- If WebGL performance becomes an issue (less likely on modern hardware for a few thousand points), we might consider simplifying marker icons or reducing refresh rate slightly.

**Caching and Offline:**
- The frontend can cache some things:
  - API responses for static data (like routes list, stops info) can be cached in memory (and even localStorage if we want to persist across sessions).
  - Map tile caching: Browsers automatically cache tile images. Also, if we use vector tiles, the library caches in-memory. If building a PWA, we could pre-cache certain assets or tiles.
  - Real-time data itself is always changing, so not cacheable in the traditional sense, but the short-term state is kept in memory.
- Offline usage is not a primary goal (since you need internet to get real-time data), but the app should handle loss of connection gracefully (e.g., if API calls fail, show a notification like “Disconnected” and keep showing last known data, perhaps).

**Responsive Design:**
- Tailwind will help in making the UI responsive (mobile vs desktop). The map will naturally fill the screen. On mobile, maybe the sidebar becomes a collapsible panel, etc.
- Performance on mobile: MapLibre on WebGL works on modern smartphones but can be heavier. We might reduce the number of markers (maybe always cluster on mobile for performance, for example).
- Also, on mobile network, we may want to use less frequent updates to avoid data costs. Possibly allow user to adjust refresh rate or auto-adjust if performance issues.

**Accessibility & UX:**
- Provide clear indicators of delay (like color or maybe numeric labels on markers if zoomed in enough).
- Possibly a legend: e.g., green dot = on time (delay < 2 min), yellow = slight delay, red = major delay. Tailwind can help style these consistently.
- When clicking a route filter, highlight that route’s vehicles and maybe deemphasize others (could hide others or make them semi-transparent).
- If showing route lines: We can use GTFS shapes to draw the route path on the map for the selected route, so user sees the route alignment. Shapes can be loaded from the backend (maybe an endpoint like `/routes/{id}/shape` returns GeoJSON). We’d then add a line layer to MapLibre for it. This helps in context.
- If time permits, a nice feature: animate a vehicle along the route between known stops or positions. But that might be overkill; focusing on live positions is enough.

**Integration with Backend API:**
- All data displayed is fetched from our FastAPI backend. The endpoints likely used by the frontend:
  - `GET /routes` to get list of routes (id, short name, long name, mode, etc.) for populating a filter list.
  - `GET /vehicles` to get all current vehicles (with coordinates and associated info). Or `GET /vehicles?route=X` if filtering server-side.
  - `GET /stops/{id}/departures` when user clicks a stop to show upcoming times (with delays).
  - Possibly `GET /routes/{id}/stops` to show route’s stops on map or list.
  - Possibly `GET /routes/{id}/vehicles` as an alternative to filter vehicles by route. (Either do that or client filter.)
  - `GET /stops/search?query=foo` if we implement search.
  - Websocket at `/ws` (if implemented for live feed) – if so, the frontend would open it and handle incoming messages to update vehicle state. (This is a potential future improvement; for now, polling is simpler.)
- The API calls will use fetch or a library. With React Query, for example:
  ```js
  useQuery(['vehicles', routeFilter], fetchVehicles, { refetchInterval: 10000 });
  ```
  This would fetch every 10s and update state.
- We must also handle error states (if API is down or returns 500). The UI should alert the user and maybe retry. Possibly show an overlay like “Unable to fetch data. Retrying…” on network issues.

## Caching and Performance Strategies

To reiterate some strategies, with emphasis on performance and caching:
- **Memoization:** Use `React.memo` for components that depend on props that rarely change. For instance, if we have a component that renders the list of routes in the sidebar, and only the “selected route” prop changes often, we memoize to prevent re-render of the entire list every time vehicles update.
- **Avoid expensive computations in render:** e.g., calculating which vehicles are in view. Instead, we can leverage MapLibre’s built-in view filtering (it won’t draw points outside view anyway) or explicit filters if needed.
- **Throttling updates:** If an API update comes every 5 seconds, the UI can apply it immediately. If that proves too jarring or heavy, we could throttle to, say, update the map markers every 10 seconds while retrieving data every 5 (taking the latest every other time). But likely not needed.
- **Using Web Workers:** If we needed to handle very heavy computations (like filtering thousands of points or decoding protobuf in JS), we could offload to a web worker to keep the UI thread free. At this stage, our operations are straightforward (just updating the map source with new JSON), which MapLibre handles internally likely in a web worker anyway (it does parsing off main thread for big data).
- **Progressive loading:** If the app needed to load lots of static data (like thousands of stops for search suggestions), we might load them on demand or in chunks. For example, only load stop data when user focuses the search bar (and then perhaps fetch stops around their area or use an API to search by name prefix). This prevents slowing initial load.
- **Persistent caching:** Optionally, we could cache static data in `localStorage` or IndexedDB. For example, once we fetch the routes list the first time, store it. On next app load, show cached list immediately (so user can see routes even if network is slow), then refresh in background. Same for stops if needed.
- **Tailwind JIT**: Tailwind CSS with JIT compilation will only generate the CSS classes we actually use, which keeps the CSS bundle small, aiding performance.

## User Interface and Experience

**Map Interaction:**
- Users can pan and zoom the map freely. As they do, we might want to update which vehicles are shown. If we have all vehicles loaded, no need to change the data source—MapLibre will simply not draw those far away. But for performance, we might still consider only loading vehicles in a bounding box. However, given moderate number of vehicles, it's fine to load all and let client filter, especially since we want to see off-screen ones when panning quickly.
- If focusing on one route, possibly draw that route’s polyline and highlight those vehicles, while others are greyed out or hidden.
- Clicking on the map background could clear selection (closing any popups).

**Theme and Styling:**
- Tailwind makes it easy to implement a dark mode or color scheme. Considering maps often have dark backgrounds (depending on tile style), we might choose a style that works (Mapbox Dark or a custom style).
- UI elements (sidebar, popups) should contrast well. Tailwind’s default or custom color palette will be used to encode status:
  - Green for on-time, Yellow for slight delay, Red for late, etc. These can be used for text or small indicators. On the map markers themselves, using colored icons or halos can encode the same.
- The design should also accommodate localization if needed (the system could be used in Finnish/English etc., though initially English for dev).

**Planned Features:**
While initial version focuses on vehicles and delays, the frontend architecture leaves room for:
- **Real-time route timetables:** Click a route to see all its vehicles and maybe a timeline of their deviations.
- **Playback mode:** Because we store historical data, a feature could allow selecting a past time and “replaying” vehicle movement. The UI could have a slider to move through time and update positions accordingly (this requires API support to query historical positions).
- **Alerts integration:** If GTFS-Realtime Service Alerts were integrated, the UI might show alert icons on routes or stops.
- **User location / nearby stops:** If allowed, show user’s GPS location on map and highlight nearest stops or vehicles.

The architecture with React makes these additions possible by adding new state slices and components.

## Deployment of Frontend

Though details in Deployment doc, note that the frontend can be built as static files and served either by a simple web server or directly by something like GitHub Pages if it’s client-side only. In a Docker context, we might serve the built app via an Nginx container or have the backend serve the static files (FastAPI can be configured to do so). We must ensure correct API URL config (maybe relative paths so if hosted together it just works).

During development, we run `npm start` which proxies API requests to the backend (using something like a proxy setting for `/api` to `http://localhost:8000`). In production, likely both frontend and backend are hosted under the same domain (e.g., backend at `/api/*` and frontend files at `/`). We’ll handle CORS in development (FastAPI will allow localhost:3000).

## Conclusion

The frontend architecture of Bussikartta is designed to provide a **smooth, real-time, and user-friendly** experience. By leveraging React’s component model and MapLibre’s powerful map rendering, we can efficiently display live transit data. Our strategies ensure that the frequent updates are handled gracefully and that the app remains responsive even with a large number of data points. The use of Tailwind and modern React patterns will speed up development and make it easier for developers to maintain the UI.

As development progresses, this document can be updated with specifics (like component file structure, any performance tuning done, etc.). New developers should now have a clear understanding of how the frontend is planned to function and interact with the backend API to bring the Bussikartta project to life in the browser.




> **Updated by system audit on 2025-06-18 19:10 UTC.**


## 🔄 Status and Notes

- MapLibre GL and OpenStreetMap tile sources confirmed as working.
- React polling loop fetches `/vehicles` endpoint correctly.

## 🧼 Cleanup Notes

- Component `OverviewMap.tsx` exists but unused — can be removed unless kept for future mini-map.
- Marker rendering logic is stable but previously allowed stale markers to persist. This was addressed.

