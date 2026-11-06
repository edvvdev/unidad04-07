# Dataset Card · Riesgo territorial sintético (Unidad 04)

Proyecto: `INF8239_U04_Gobernanza_DSS` · Fecha: 2026-11-02

## Qué es este conjunto

Caso **sintético y didáctico** de riesgo territorial, generado con una semilla educativa fija para
practicar contratos de datos, evaluación temporal, auditoría de subgrupos y gobernanza.
**No contiene personas, lugares, tasas ni estadísticas oficiales de República Dominicana.**

## Procedencia y generación

| Campo | Valor |
|---|---|
| Origen | Generado sintéticamente por el profesor como parte del proyecto base (no es un dataset público) |
| Semilla | Fija y documentada por el profesor en el proyecto base |
| Fecha de recepción | 2026-11-02 (`~/Downloads/INF8239_U04_Gobernanza_DSS_Proyecto_Base_uv.zip`) |
| Ruta local | `data/territorial_risk_synthetic.csv` (versionado: es sintético y no contiene datos personales) |
| Filas × columnas | 640 × 9 |
| Periodo | 2026-01-01 a 2026-12-27 (fechas sintéticas) |

## Diccionario de datos

| Columna | Tipo | Significado | Uso | Momento de disponibilidad |
|---|---|---|---|---|
| `case_id` | texto | Identificador sintético del caso (`CASE-0001`…) | trazabilidad; **no entra al modelo** | conocido |
| `received_date` | fecha | Fecha sintética de recepción del reporte | **corte temporal**; no entra al modelo | conocido |
| `zone` | texto | Zona sintética (`Norte`, `Sur`, `Este`, `Oeste`; 155–164 casos cada una) | variable predictora | conocido |
| `protected_group` | texto | Grupo protegido sintético (`G1` 396 · `G2` 244) | **excluido del modelo**, solo auditoría | para auditoría |
| `age_band` | texto | Banda de edad sintética (`18-29`, `30-44`, `45-59`, `60+`) | variable predictora | conocido |
| `previous_incidents` | entero | Incidentes previos reportados | variable predictora | conocido |
| `infrastructure_score` | flotante | Índice sintético de infraestructura (0–1) | variable predictora | conocido |
| `exposure` | flotante | Exposición sintética (0–1) | variable predictora | conocido |
| `target` | entero | Resultado binario del caso (1 = incidente) | etiqueta | etiqueta |

**Columnas prohibidas por contrato:** `name`, `document_number`, `email`, `phone`. Cualquier columna
directa es rechazada antes de predecir (`src/inf8239_u04/data.py::validate_schema`, prueba
`tests/test_privacy.py`).

## Distribución y soporte

| Comprobación | Valor |
|---|---|
<!-- stats:inicio distribucion -->
| Target | 353 positivos (55,2 %) · 287 negativos (44,8 %): desbalance moderado, `accuracy` no basta |
| Grupos | G1 396 · G2 244 |
| Bandas de edad | 18-29: 148 · 30-44: 163 · 45-59: 150 · 60+: 179 |
| Zonas | Norte 155 · Oeste 157 · Sur 164 · Este 164 |
| Tasa de positivos por grupo (datos completos) | G1 49,7 % · **G2 63,9 %** |
| Tasa de positivos por grupo (prueba, 160 casos) | G1 48,5 % · **G2 72,9 %** |
<!-- stats:fin distribucion -->

La diferencia de prevalencia entre grupos es **el hecho central de la auditoría**: una brecha de recall
puede reflejar la distinta prevalencia del target y no una decisión discriminatoria del modelo.

## Corte temporal

El corte es **2026-09-24 / 2026-09-25**: entrenamiento 480 casos (hasta el 24 de septiembre) y prueba
160 casos (desde el 25). No se usa el futuro para evaluar el pasado, ni se mezclan periodos.

## Soporte mínimo en las celdas interseccionales

En la prueba, las ocho celdas `grupo | banda de edad` tienen entre **8 y 35 observaciones**. Las
cifras de `G2 | 45-59` (n=8) y `G2 | 18-29` (n=11) tienen soporte **insuficiente** y no deben
interpretarse como evidencia de brecha.

## Sesgos, población no cubierta y usos prohibidos

- **Sesgo por construcción:** el generador sintético no reproduce ninguna distribución real; las
  diferencias entre grupos son un artefacto del generador y sirven para practicar la auditoría, no
  para describir a grupo alguno.
- **Población no cubierta:** ninguna; el caso es sintético y no describe personas, zonas reales ni
  estadísticas de República Dominicana.
- **Usos prohibidos:** usar estos datos o el modelo para perfilamiento operativo, para inferir
  atributos de personas o grupos reales, para atribuir características a territorios reales o
  para cualquier decisión sobre personas.
- **Uso previsto:** únicamente la auditoría, la gobernanza y la práctica de contratos de datos.
