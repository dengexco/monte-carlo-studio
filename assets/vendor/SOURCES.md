# Third party assets

The DengeX stylesheets were retrieved from the following public URLs on 2026-10-19 at the user's request:

- https://dengex.com/build/assets/app-Bol-Fz0i.css → dengex-app.css
- https://dengex.com/build/assets/marketing-BDgYp26K.css → dengex-marketing.css

They are used locally without modification. The application uses the original `dx-lead-form` rules and adds application-specific overrides in `assets/app.css`. No DengeX analytics, scripts, forms or remote requests are included. No ownership or license to redistribute DengeX styles is claimed.

`plotly.min.js` is bundled from the installed Plotly Python package. Its embedded license header is retained. Plotly.js is distributed under the MIT license.

## UI TripleD integration

Source: https://github.com/moumen-soliman/uitripled (MIT, copyright 2026 uitripled).
License preserved in `UITRIPLED-LICENSE.md`.
Adapted components in `frontend/components.jsx`:
- `packages/components/react-baseui/src/components/native/native-tabs-baseui.tsx`: Base UI controlled tabs and Motion shared-layout pill. Panels are hosted by the existing simulation UI so switching preserves Plotly state.
- `packages/components/react-shadcn/src/components/native/native-magnetic-shadcnui.tsx`: spring-based magnetic pointer movement, adapted to the creator credit and reduced-motion preference.

The dashboard layout and styling are custom. DengeX assets remain archived in this directory but are no longer loaded. React, React DOM, Framer Motion and Base UI are bundled locally in `assets/components.js`; dependency versions are locked in `package-lock.json` and license notices are retained in the bundle. No remote scripts are required at runtime.
