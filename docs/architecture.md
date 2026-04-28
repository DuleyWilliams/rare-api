# Rare — System Architecture

Rare is a full-stack publishing platform. The frontend is a React SPA served at `localhost:3000`. It communicates with a Django REST Framework API at `localhost:8000` over HTTP using `fetch` with JSON payloads. The backend uses Django’s ORM to read and write a PostgreSQL database.

---

## Diagram

```mermaid
graph LR
    subgraph client ["React SPA — localhost:3000"]
        Router["ApplicationViews.js\nReact Router v6"]
        Components["src/components/\nper-resource UI"]
        Managers["src/managers/\nper-resource fetch wrappers"]
        APIConf["src/managers/api.js\nAPI constant · authHeader() helper"]
    end

    subgraph backend ["Django + DRF — localhost:8000"]
        URLRoot["rareproject/urls.py\nroot router"]
        URLApp["rareapi/urls.py\nall API routes"]
        Views["rareapi/views/\nfunction-based API views"]
        Serializers["rareapi/serializers/\nresponse shaping · some write validation"]
        Services["rareapi/services/\nadmin_actions logic"]
        Models["rareapi/models/\nDjango ORM models"]
    end

    DB[("PostgreSQL\nlocalhost:5432")]

    Router --> Components
    Components --> Managers
    Managers --> APIConf
    Managers -->|"fetch HTTP/JSON\nAuthorization: Token ..."| URLRoot
    URLRoot -->|"include()"| URLApp
    URLApp --> Views
    Views --> Serializers
    Views --> Services
    Views --> Models
    Models -->|"Django ORM"| DB