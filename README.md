# AdriaClimPlus Geoportal

AdriaClimPlus Geoportal is a web-based geoportal for exploring, visualizing and comparing marine and climate monitoring data for the Adriatic Sea. It is developed within the Interreg Italy-Croatia AdriaClim / AdriaClimPlus programme, co-funded by the European Union, in collaboration with ARPAE (the project is maintained under the `ARPA-SIMC` GitHub organization). The application combines an Angular single-page frontend with a Django/GIS backend for dataset ingestion, processing and delivery.

---

## Overview

The project is a full-stack, containerized application split into two independently deployable parts that live in the same repository:

- **Frontend** (`adriaclim-master/code/adria_project_frontend`): an Angular single-page application that renders an interactive Leaflet map, statistical graphs, dataset comparison tools and a public welcome/landing page.
- **Backend** (`adriaclim-master/code/adria_project_backend`): a Django + Django REST Framework application that stores dataset metadata in PostgreSQL/PostGIS, imports and processes scientific datasets (NetCDF, GDAL, geopandas, xarray), exposes JSON/GeoJSON endpoints consumed by the frontend, proxies WMS map overlays, and runs background/scheduled jobs with Celery and Redis.

The Angular app calls the Django backend over HTTP using a configurable base URL (`environment.backendUrl`), and both services are orchestrated together with Docker Compose behind an Nginx reverse proxy. Some data (time series) is fetched by the frontend directly from an external ERDDAP server rather than through the Django backend.

---

## Main Features

- Interactive Leaflet map with WMS and GeoJSON overlays, including a legacy map implementation (`geoportal-map`) and a current implementation (`geoportal-map-new`, `geoportal-map-new-menu`).
- Time-series and statistical graphs rendered with ECharts (`canvas-graph`, `canvas-graph-compare`).
- Dataset comparison between two datasets/points/polygons (`geoportal-compare-dialog`, `compareDatasets` API).
- Point/polygon coordinate selection on the map (`select-coords-dialog`).
- Color legend customization for map layers (`geoportal-color-dialog`).
- Guided, step-by-step tutorial overlay for the map, built with `driver.js`.
- Public welcome/landing page with links to the official AdriaClimPlus, AdriaClim and Climate Literacy Toolkit resources, and to the Interreg Italy-Croatia programme and EU co-funding notice.
- Backend dataset import and management (`Dataset` app: `initdatasets` management command, `dataset_manager.py`).
- Scheduled/background data downloads and statistics updates via Celery Beat (daily and weekly jobs defined in `AdriaProject/settings.py`).
- Integration with an external ERDDAP server for oceanographic time series.

---

## Technology Stack

### Frontend

- Angular ~15.1.0 (`@angular/core`, `@angular/router`, `@angular/forms`, `@angular/animations`, `@angular/cdk`)
- TypeScript ~4.9.4
- Angular Material ~15.1.5 and Angular Flex-Layout
- RxJS ~7.8.0
- Leaflet 1.9.3 via `@asymmetrik/ngx-leaflet`, plus `leaflet-polylinedecorator` and `leaflet-rotatedmarker`
- ECharts 5 via `ngx-echarts`
- `bootstrap-italia` 2.4 (Italian public-administration design system) and Bootstrap JS bundle
- `driver.js` (guided tutorial overlays)
- `jsts`, `lodash`, `moment`, `file-saver`
- Karma + Jasmine (unit tests), `@angular-eslint` / `@typescript-eslint` (linting)
- Node.js 18.15.0, npm, Angular CLI ~15.1.6

### Backend

- Python 3.9 (`python:3.9-bookworm` base image)
- Django 3.2.25, Django REST Framework 3.15.1
- `django-cors-headers`, `django-crispy-forms`, `django-redis`
- Celery 5.2.7 with Redis as broker and result backend; Celery Beat for scheduled tasks
- Hypercorn 0.16.0 (ASGI server; the project also exposes a standard WSGI entry point)
- GIS / scientific stack: GDAL 3.3.2, geopandas 0.14.4, shapely 2.0.4, xarray 2023.1.0, netCDF4 1.6.5, h5py 3.9.0, numpy, pandas, scipy, scikit-learn, folium, ipyleaflet
- PostgreSQL + PostGIS (`postgis/postgis:13-3.3` image), accessed via `django.contrib.gis`

### Infrastructure

- Docker and Docker Compose (services: `migrator`, `django`, `celery`, `celery-beat`, `angular`, `nginx`, `redis`, `db`)
- Nginx (separate dev and prod configurations)
- Jenkins (CI/CD pipeline, see `Jenkinsfile` at the repository root)

---

## Project Structure

```
adriaclim-geoportal/                   # Git repository root
├── Jenkinsfile                        # Jenkins CI/CD pipeline (build + SSH deploy)
├── LICENCE                            # GNU General Public License v3.0
├── README.md                          # This file
├── .gitignore, .gitattributes
├── .vscode/                           # Shared editor settings
└── adriaclim-master/                  # Application source and deployment configuration
    ├── README.md                      # Short legacy project notes
    ├── deploy_adria_portal.md         # Manual Jenkins/Docker deployment guide (Italian)
    ├── docker-compose.yml             # Multi-service orchestration
    ├── Dockerfile                     # Backend (Django) image
    ├── entrypoint.sh                  # Backend container entrypoint
    ├── requirements.txt                # Backend Python dependencies
    ├── .env                           # Local secrets (not committed, see Configuration)
    ├── nginx/                         # Nginx reverse-proxy configs (dev/prod) + Dockerfile
    └── code/
        ├── adria_project_frontend/    # Angular application — see "Frontend"
        └── adria_project_backend/     # Django application — see "Backend"
```

---

## Frontend

Path: `adriaclim-master/code/adria_project_frontend`

```
src/
├── main.ts, index.html, styles.scss, favicon.ico
├── environments/                      # environment.ts (dev) / environment.prod.ts (prod)
├── assets/
│   ├── configuration/                 # JSON content/config (e.g. welcomePage.json, infoModal.json)
│   ├── geojson/                       # Map overlay geometries
│   └── img/                           # Images used by the UI
└── app/
    ├── app.module.ts, app-routing.module.ts, app.component.*
    ├── modules/
    │   ├── pages/                     # Lazy-loaded module: welcome landing page (WelcomeComponent)
    │   └── services/angular-mat/      # Centralized Angular Material module imports
    ├── geoportal-map/                 # Legacy interactive map (+ color/compare/coordinates dialogs, graphs)
    ├── geoportal-map-new/             # Current interactive map implementation
    ├── geoportal-map-new-menu/        # Map variant with a redesigned side menu
    ├── demo-landing/                  # Alternative animated landing screen (not currently routed)
    ├── info-page/                     # Static info page
    ├── select-coords-dialog/          # Coordinate-picking dialog
    ├── services/                      # HttpService (backend API calls), SpinnerLoaderService
    ├── interfaces/                    # Shared TypeScript interfaces for map/dialog data
    ├── common-functions/              # Shared utility functions
    └── tutorial/                      # driver.js guided-tour step data
```

There is no `core`/`shared` module split in this codebase; feature areas sit as flat top-level folders under `src/app`, with only Angular Material configuration and routed pages grouped under `app/modules`.

### Routing

- `AppRoutingModule` (root): `''` lazy-loads `PagesModule`; `mapNewMenu` → `GeoportalMapNewMenuComponent`; `info` → `InfoPageComponent`. A legacy `map` route to `GeoportalMapComponent` exists in the source but is commented out.
- `PagesRoutingModule` (child of `PagesModule`): `''` → `WelcomeComponent`. `DemoLandingComponent` is present in the codebase but is not currently wired to any route.

---

## Backend

Path: `adriaclim-master/code/adria_project_backend`

- **`AdriaProject/`** — the Django project package: `settings.py`, root `urls.py`, `wsgi.py` and `asgi.py` entry points, `celery.py` (Celery app bootstrap), `tasks.py` (scheduled task functions), `context_processors.py` (injects `ERDDAP_URL` into templates), `logger_config.py`, and `views.py` (serves the server-rendered welcome page).
- **`Dataset/`** — the core domain app: models and migrations for datasets, the `initdatasets` management command and `dataset_manager.py` for dataset import, `geospatial_processing.py`, `external_wms.py` (WMS overlay proxying), `tasks.py` (Celery tasks for scheduled downloads), and `urls.py` (the app that currently exposes REST-style JSON endpoints, see below).
- **`Metadata/`** — models and a `metadata_manager.py` helper for dataset metadata. Its `urls.py` is registered in the root URLconf under `/metadata/` but currently defines no routes.
- **`Processing/`** — a library of stateless helper modules used by `Dataset`'s views: `time_processing.py`, `indicator_manager.py`, `compareStatistics.py`, `data_analysis.py`, `database_operations.py`, `functionTable.py`, `utils.py`. It defines no models and its `urls.py` (registered under `/Processing/`) currently has no routes.
- **`Utente/`** — user-related models, forms and views (add/modify user). Its `urls.py` (registered under `/utente/`) currently defines no routes; related pages are served through Django templates (`addUser.html`, `modify_user.html`, `administration.html`).
- **`templates/`** — server-rendered Django templates (`welcome.html`, `homepage.html`, `allDatasets.html`, `specificDataset.html`, `getData.html`, `addUser.html`, `modify_user.html`, `administration.html`, `wrongIdPassed.html`, `base.html`). These predate/run alongside the Angular SPA and are not part of it.
- **`static/`** — a separate, legacy static-assets folder (CSS/JS/images/GeoJSON) used only by the Django templates above, unrelated to the Angular app's `src/assets`.
- **`tests/`** — the backend automated test suite, documented in `tests/README.md` and `tests/TESTS_OVERVIEW.md` (see Troubleshooting/Coding Conventions).

### APIs

Only the `Dataset` app currently registers concrete routes (mounted under `/dataset/` in `AdriaProject/urls.py`):

`allDatasets/`, `getAllNodes/`, `getMetadataNew/`, `get_metadata_table/`, `getDataTableNew/`, `getOverlaysNew/<dataset_id>/`, `layers2DNew/`, `layers3DNew/<parameter>/`, `getDataPolygonNew/`, `getDataGraphicNewCanvas/`, `getDataVectorialNew/`, `updateStatistics/`, `compareDatasets/`, `check_task_status/`.

The root URLconf also mounts `/metadata/`, `/utente/`, `/Processing/` and `/admin/` (Django admin), and serves the welcome page at `/`. As noted above, the `Metadata`, `Processing` and `Utente` apps do not yet define their own URL patterns.

---

## Requirements

| Tool | Version | Source |
|---|---|---|
| Node.js | 18.15.0 | `Dockerfile.dev` / `Dockerfile.prod` (frontend) |
| npm | bundled with Node 18.15.0 | not separately pinned — TODO |
| Angular CLI | ~15.1.6 | `package.json` devDependency `@angular/cli` |
| TypeScript | ~4.9.4 | `package.json` devDependency |
| Python | 3.9 | root `Dockerfile` (`python:3.9-bookworm`) |
| PostgreSQL / PostGIS | 13-3.3 | `docker-compose.yml` `db` service (`postgis/postgis:13-3.3`) |
| Docker / Docker Compose | not pinned in-repo | required to run `docker-compose.yml` (`version: "3.9"`) |

TODO: no `engines` field is declared in `package.json`, so Node/npm compatibility outside the Docker images above is not formally enforced.

---

## Installation

```bash
git clone https://github.com/ARPA-SIMC/adriaclim-geoportal.git
cd adriaclim-geoportal/adriaclim-master
```

### Full stack (Docker Compose)

Create a `.env` file in `adriaclim-master/` defining `POSTGRES_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD` and `SECRET_KEY` (see Configuration), then:

```bash
docker compose up -d --build
```

This builds and starts `migrator` (runs `collectstatic`, `makemigrations`, `migrate`, `initdatasets` once), `django`, `celery`, `celery-beat`, `angular` (development server container), `nginx` (reverse proxy on port 8000), `redis` and `db` (PostgreSQL/PostGIS).

### Frontend only (against an already running backend)

```bash
cd code/adria_project_frontend
npm install
npm start
```

TODO: there is no documented procedure for running the Django backend directly on a host machine outside Docker; the required system libraries (GDAL, PostGIS client, PostgreSQL 15) are only defined inside the backend `Dockerfile`.

---

## Development

- **Frontend dev server**: `npm start` (equivalent to `ng serve --host 0.0.0.0`), served by default at `http://localhost:4200`, with Angular CLI live/hot reload enabled.
- **Backend dev server**: inside the `django` container, `python manage.py runserver 0.0.0.0:8000`, served at `http://localhost:8000/`.
- **Via Docker Compose**: Nginx (`nginx.dev.conf`) listens on `http://localhost:8000` and proxies `/` to the `angular` container and `/api`, `/dataset` to the `django` container, so the full stack can be exercised from a single port while the Angular container still hot-reloads.
- **Background jobs**: the `celery` and `celery-beat` containers process and schedule dataset-processing tasks; both require `redis` to be running.

---

## Build

### Frontend

```bash
npm run build
```

Equivalent to `ng build`, which defaults to the `production` configuration (`angular.json`). This replaces `environment.ts` with `environment.prod.ts` and outputs to `dist/adria-project-front/`. `Dockerfile.prod` performs this build in a multi-stage image and serves the result with `nginx:1.21-alpine` using `nginx.prod.conf`.

### Backend

Django has no separate compiled "build" step. On container start, `entrypoint.sh` runs `collectstatic`, `makemigrations`, `migrate` and `initdatasets` (the latter is allowed to fail/skip without stopping startup).

---

## Configuration

- **Frontend environments** — `src/environments/environment.ts` (development: `backendUrl: http://localhost:8000/`) and `environment.prod.ts` (production; `backendUrl` and `erddapUrl`). The production file is selected automatically by the `fileReplacements` entry in `angular.json` when building with the `production` configuration.
- **Backend environment file** — `adriaclim-master/.env`, loaded via `python-dotenv` in `AdriaProject/settings.py`. Declares (names only, values are secrets and must not be committed):
  - `POSTGRES_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — database credentials, also referenced from `docker-compose.yml`.
  - `SECRET_KEY` — Django secret key.
  - The repository's `.gitignore` (at the true repository root, one level above `adriaclim-master/`) excludes `.env` and virtual-environment directories from version control.
- **CI/CD secrets** — the Jenkins pipeline (`Jenkinsfile`) injects a `.env` file at deploy time from a Jenkins-managed credential (`adria-env`) rather than storing it in the repository.

---

## Architecture

- The Angular SPA calls the Django backend over HTTP through `HttpService` (`src/app/services/http.service.ts`), which prefixes every request with `environment.backendUrl`.
- In development, Nginx (`nginx.dev.conf`) fronts both services on port 8000: `/` is proxied to the Angular dev server (port 4200), while `/api` and `/dataset` are proxied to Django (port 8000 internally).
- In production, the Angular app is built statically (`Dockerfile.prod`) and served directly by Nginx (`nginx.prod.conf`), without a separate Angular container.
- Django persists dataset and metadata records in PostgreSQL/PostGIS (`django.contrib.gis`, `postgis` database engine) and uses Redis both as a cache backend and as the Celery broker/result backend.
- Long-running or scheduled work (bulk/seasonal data downloads, statistics updates) is offloaded to Celery workers (`celery` service) and scheduled by Celery Beat (`celery-beat` service, `CELERY_BEAT_SCHEDULE` in `settings.py`).
- The backend exposes a WSGI entry point (`AdriaProject/wsgi.py`, used by `docker-compose.yml`'s `runserver` command) and an ASGI entry point (`AdriaProject/asgi.py`); Hypercorn is included among the backend dependencies for ASGI-based deployment.
- Oceanographic time-series data can be fetched directly from an external ERDDAP server, both from the Angular app (`environment.erddapUrl`) and from the Django backend (`ERDDAP_URL` setting, injected into templates via `context_processors.py`).
- CORS/CSRF are configured permissively for development (`CORS_ORIGIN_ALLOW_ALL = True`) with an explicit `CSRF_TRUSTED_ORIGINS` allow-list that includes `http://localhost:4200` and the project's production domains.

---

## Coding Conventions

### Frontend

- Linting via `@angular-eslint` and `@typescript-eslint` recommended rule sets (`ng lint`).
- Component selector prefix `app` in kebab-case; directive selector prefix `app` in camelCase (`.eslintrc.json`).
- Default component stylesheet language is SCSS (`angular.json` schematics).
- `.editorconfig`: UTF-8, 2-space indentation, single quotes in `.ts` files, final newline inserted, trailing whitespace trimmed (Markdown files are exempted from the trailing-whitespace and line-length rules).
- `tsconfig.json` enables strict TypeScript checking (`strict`, `strictTemplates`, `noImplicitReturns`, `noFallthroughCasesInSwitch`, `noImplicitOverride`, `noPropertyAccessFromIndexSignature`).

### Backend

- One Django app per domain area (`Dataset`, `Metadata`, `Processing`, `Utente`), each with its own `models.py`, `views.py`, `urls.py` and `migrations/` where applicable.
- Scientific/processing logic is kept in dedicated modules (e.g. `dataset_manager.py`, `geospatial_processing.py`, `indicator_manager.py`) rather than directly in `views.py`.
- Automated tests live under `code/adria_project_backend/tests/` and are documented in `tests/README.md` (how to run them) and `tests/TESTS_OVERVIEW.md` (what each test covers); they run with Django's built-in `TestCase` and `unittest.mock`.

TODO: no Python linter/formatter configuration (e.g. flake8, black, pyproject.toml) was found in the repository.

---

## Troubleshooting

- **`npm install` fails or behaves inconsistently**: verify the local Node.js version matches the one used by the project (18.15.0, see `Dockerfile.dev`/`Dockerfile.prod`); a different Node major version can cause install or `ng build` failures.
- **`ng build` reports a bundle or component-style budget warning**: `angular.json` defines budgets (`initial`: 1 MB warning / 5 MB error; `anyComponentStyle`: 6 kB warning / 8 kB error). These are warnings, not build failures, unless the error threshold is exceeded.
- **Map styles or third-party CSS/JS missing in the browser**: Leaflet, `bootstrap-italia` and `driver.js` styles/scripts are wired in globally through the `styles`/`scripts` arrays in `angular.json`; re-run `npm install` if `node_modules` is missing or out of sync with `package-lock.json`.
- **CORS or CSRF errors when the Angular dev server calls the backend**: `settings.py` already whitelists `http://localhost:4200` in `CSRF_TRUSTED_ORIGINS` and enables `CORS_ORIGIN_ALLOW_ALL`; if requests still fail, check that the containers are on the same Docker network and that `environment.backendUrl` points to the correct host/port.
- **Scheduled/background tasks do not appear to run**: confirm the `redis` and `celery`/`celery-beat` containers are up (`docker compose ps`); Celery is configured to use `redis://redis:6379/0` as both broker and result backend.
- **Database or migration errors on startup**: the `migrator` service must complete successfully before `django`, `celery` and `celery-beat` start (`depends_on: service_completed_successfully` in `docker-compose.yml`); check the `migrator` container logs first.
- **Backend fails to build/run outside Docker**: the backend `Dockerfile` compiles against `libgdal-dev`, `gdal-bin` and PostgreSQL 15/PostGIS 3 system packages; installing `requirements.txt` (GDAL, geopandas, netCDF4, etc.) on a host without these system libraries will fail. Use the provided Docker image instead.

---

## Future Improvements

TODO — the following gaps were identified while writing this document and are not otherwise documented in the repository:

- Pin Node.js/npm versions in `package.json` (`engines` field) instead of relying only on Docker base images.
- Define concrete URL patterns for the `Metadata`, `Processing` and `Utente` Django apps, or remove their empty `urls.py` includes if they are not meant to expose routes.
- Add linting/formatting configuration for the Python backend.
- Clarify whether `demo-landing` (present in the frontend source but unrouted) and the legacy `map` route/`geoportal-map` component are still maintained or should be removed.
- Document a supported way to run the Django backend outside Docker, if one exists.
- Confirm and document the exact production `backendUrl` used for each deployment target (`environment.prod.ts` currently contains multiple candidate URLs, only one of which is active).

---

## License

This project is distributed under the GNU General Public License v3.0. See the `LICENCE` file at the repository root for the full text.
