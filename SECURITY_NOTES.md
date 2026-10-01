# Security baseline – anonymous access

2026-10-01

- Anonymous `GET /recipes` → 200 OK, returned all recipes including one with `"is_public": false` ("Secret family hot sauce").
- Anonymous `PATCH /recipes/1` → 200 OK, changed title to "Hacked by anonymous".
- Anonymous `DELETE /recipes/2` → 200/204, recipe id 2 no longer appears in `GET /recipes` results.
