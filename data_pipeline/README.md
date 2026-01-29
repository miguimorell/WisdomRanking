Pipeline de datos (prototipo)

Qué hace
- Toma el CSV real de población por edad y genera el JSON que usa la app.

Entrada (ya disponible)
- assets/data/population-by-age-group.csv
- assets/data/deaths-by-age-group.csv

Salida
- assets/data/age_distribution.json

Uso
- Ejecuta build_age_distribution.py con Python 3.
- Por defecto usa la fila más reciente de "World".

Notas
- Si existe el CSV de muertes, añade deaths_by_age al JSON.
