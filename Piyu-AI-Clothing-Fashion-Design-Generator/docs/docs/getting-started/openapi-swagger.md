---
sidebar_position: 6
title: OpenAPI & Postman
description: Swagger / OpenAPI snapshot and Postman collection for upstream media providers integrated in Piyu
keywords:
  - OpenAPI
  - Swagger
  - Postman
  - Seedance
  - Seedream
  - Kling
  - Pruna
  - Grok
  - Ideogram
---

# OpenAPI & Postman

For **provider-level** debugging, Piyu includes:

| Asset | Path |
|---|---|
| OpenAPI 3 / Swagger snapshot | [`openapi/piyu-media.openapi.yaml`](https://github.com/piyu/piyu/blob/main/openapi/piyu-media.openapi.yaml) |
| Postman collection | [`postman/piyu-media.postman_collection.json`](https://github.com/piyu/piyu/blob/main/postman/piyu-media.postman_collection.json) |

These describe **upstream** HTTP APIs (BytePlus Seedance/Seedream, Kling Video, Luma Ray 3.2, xAI Grok Imagine, Ideogram, Pruna predictions, …).

The **source of truth for calling models from apps** remains:

1. `piyu` CLI  
2. MCP tools  
3. Python adapters under `tryon.api`

## View in Swagger / Redoc

```bash
npx @redocly/cli preview-docs openapi/piyu-media.openapi.yaml
# or import the YAML into https://editor.swagger.io /
```

## Postman

File → Import → select `postman/piyu-media.postman_collection.json`, then set collection variables (`ARK_API_KEY`, `PRUNA_API_KEY`, …).

## Legacy FastAPI demo docs

`api_server.py` still exposes its own `/docs` Swagger UI for the older VTON demo endpoint. Prefer CLI/MCP for the full model set.

More detail: [`openapi/README.md`](https://github.com/piyu/piyu/blob/main/openapi/README.md).
