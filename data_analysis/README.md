Análisis visual (aislado)

Qué es
- Script para ver distribución de población y muertes por edad.
- También puede mostrar un heatmap con tasa de muerte (muertes / población).
- La tasa usa población aproximada por rangos de muertes (0-9, 10-19, ...).

Requisitos
- Python 3
- pandas
- matplotlib

Archivos de entrada
- assets/data/population-by-age-group.csv
- assets/data/deaths-by-age-group.csv

Uso
- Ejecuta plot_mortality_trends.py
- Modo por defecto: barras
- Modo tasa (último año): --mode rate-bars
- Modo heatmap: --mode heatmap
- Modo 3D: --mode surface
- Modo comparación población: --mode compare-pop --year 2023
- Modo comparación tasas: --mode compare-rate --year 2023
- Puedes añadir un sufijo al nombre: --output-suffix aligned
- Para guardar sin ventana: --no-show

Salida
- Los plots se guardan en assets/Results
