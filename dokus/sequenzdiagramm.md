## Sequenzdiagramm

```text
Entwickler        GitHub         GitHub Actions      Runner (Ubuntu)
    |               |                  |                   |
    | git push      |                  |                   |
    |-------------->|                  |                   |
    |               | Workflow startet |                   |
    |               |----------------->|                   |
    |               |                  | Code holen        |
    |               |                  |------------------>|
    |               |                  | Python installieren|
    |               |                  |------------------>|
    |               |                  | Tests ausführen   |
    |               |                  |------------------>|
    |               |                  | Ergebnis zurück   |
    |<--------------|                  |                   |
    | Ergebnis sehen|                  |                   |
```