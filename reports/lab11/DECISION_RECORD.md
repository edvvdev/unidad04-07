# Decision record · LAB11 · Evaluación de impacto ético

Proyecto: `INF8239_U04_Gobernanza_DSS` · Unidad 04 · Fecha: 2026-11-02 · Caso: **sintético y didáctico**

## Decisión documentada: **LIMITAR**

No hay despliegue autónomo; se autoriza un piloto en modo **REVIEW** con revisión humana obligatoria
y el baseline sin modelo como camino operativo seguro. No se autoriza ningún uso fuera del alcance
aprobado.

## Estado del pipeline: **REVIEW**

Fallan tres puertas: `worst_group_recall` (0,6531 < 0,70), `recall_gap_pilot` (0,1376 > 0,10) e
`intersectional_support` (8 < 15). Las ocho puertas evaluadas, con su umbral y su resultado, están en
`reports/lab13/deployment_decision.json` y en la figura `reports/lab13/puertas_calidad.png`, que
genera `scripts/lab13_governance.py` desde `configs/governance.yml`.

## Escalamiento a STOP

Si la brecha de recall supera 0,15 o el recall del peor grupo baja de 0,60, el sistema se retira al
baseline sin modelo. Son umbrales de escalamiento declarados en `configs/governance.yml`
(`stop_recall_gap`, `stop_worst_group_recall`); con la evidencia actual no se dispara ninguno: el
estado es REVIEW, no STOP.

## Evidencia que sostiene la decisión

| Evidencia | Archivo | Hallazgo |
|---|---|---|
| Propósito, interesados y proporcionalidad | `student_inputs/lab11_impact.yml`, `student_inputs/stakeholders.csv` | Finalidad limitada a priorizar revisión; existe alternativa no predictiva (reparto rotativo por zona y severidad) y no hay decisión automatizada sobre personas |
| Registro de riesgos (9 riesgos) | `reports/lab11/risk_register_scored.csv` | Prioridad = probabilidad × impacto. Tres riesgos críticos: **R03** (brecha de recall entre grupos, prioridad 9), **R01** (falso positivo, 8) y **R02** (falso negativo, 8). R07 (presión para automatizar) queda con riesgo residual **alto** |
| Evidencia NIST AI RMF | `reports/lab11/rmf_summary.json` | **GOVERN**: responsable y política (dirección del programa). **MAP**: 9 riesgos documentados con control, responsable y evidencia. **MEASURE**: soporte de la auditoría del LAB12. **MANAGE**: condición de retiro y recurso de apelación documentados |
| Auditoría de equidad (LAB12) | `reports/lab12/logistic/fairness_by_group.csv`, `reports/lab12/logistic/global_metrics.json` | Brecha de recall **0,1376** entre grupos (G1 0,653 · G2 0,791) y de FPR 0,1250; la diferencia viene en parte de la tasa base de positivos (G2 63,9 % · G1 49,7 % en los datos completos; 72,9 % · 48,5 % en la prueba del corte temporal) |
| Soporte interseccional | `reports/lab12/logistic/fairness_intersectional.csv` | Ocho celdas con conteos de 8 a 35: soporte **insuficiente en tres celdas** —`G2 \| 45-59` (n=8), `G2 \| 18-29` (n=11) y `G2 \| 30-44` (n=14)—, marcadas por la columna `soporte_insuficiente` que calcula el propio script (umbral 15) |
| Comparación de alternativas | `reports/lab12/tree/global_metrics.json` | El árbol obtiene la misma utilidad global (recall 0,7174) con **brechas mayores** (recall 0,1813 · FPR 0,1683) y el doble de tamaño (7,90 KB frente a 3,56 KB): no se justifica |
| Decisión de despliegue | `reports/lab13/deployment_decision.json` | Estado **REVIEW**: fallan `worst_group_recall` (0,6531 < 0,70), `recall_gap_pilot` (0,1376 > 0,10) e `intersectional_support` (8 < 15); ningún umbral de escalamiento se dispara |

## Interpretación de los tres riesgos prioritarios

**R03 · Brecha de recall entre grupos (prioridad 9).** El grupo G1, que tiene la **menor** tasa base de
positivos (49,7 % frente a 63,9 % de G2), recibe además peor recall (0,653 frente a 0,791). Dos
lecturas son posibles y la evidencia disponible **no permite decidir entre ellas**: (a) el modelo
aprendió a priorizar señales proxy —zona y banda de edad— que correlacionan con el grupo, o (b) la
diferencia refleja la distinta prevalencia del target en cada grupo. Lo que sí puede afirmarse es que
**excluir el atributo sensible no elimina el sesgo indirecto** (riesgo R08). La brecha observada
requiere investigación; por sí sola no demuestra discriminación causal.

**R01 · Falso positivo (prioridad 8).** Con FPR global de 0,2794 y 0,375 en G2, el sistema puede
enviar verificación a casos sin riesgo y desplazar la atención de otros. El control vigente (umbral de
priorización más revisión humana de los 20 primeros) limita el daño, pero su eficacia **no está
verificada** porque no existe todavía un registro de decisiones con su justificación.

**R02 · Falso negativo (prioridad 8).** Es el daño priorizado: un caso con incidente probable que no
entra en la cola no recibe atención preventiva. Con recall de 0,653 en G1, el riesgo es
concreto. El control (cola secundaria por severidad reportada con revisión humana y muestreo de
casos no priorizados) depende de capacidad operativa que **no está medida**.

## Incertidumbre declarada

1. El caso es **sintético**: 640 registros que no representan personas, territorios ni estadísticas
   reales de República Dominicana. Ninguna métrica es evidencia sobre la población real.
2. Una sola partición temporal (corte 2026-09-24/25) y una sola semilla: **no hay intervalos de
   confianza** ni repetición que cuantifique la incertidumbre de las brechas.
3. El soporte interseccional es insuficiente en tres celdas (n=8, n=11 y n=14): esas cifras son
   indicativas, no concluyentes.
4. El **coste real** de un falso negativo y de un falso positivo en el programa no está cuantificado;
   sin ese dato, la tolerancia de brecha es un valor de trabajo, no una derivación.
5. El residuo de R07 (erosión de la supervisión humana) se mantiene **alto**: depende de la disciplina
   operativa, no del modelo.

## Responsable y condición de retiro

- **Responsable de la decisión:** Dirección del programa de prevención (rol *accountable* único). El
  equipo de datos mantiene el modelo y la evidencia, pero no aprueba su uso operativo.
- **Condiciones de retiro (obligatorias):** (1) brecha de recall entre grupos > 0,15 o recall del peor
  grupo < 0,60 en la auditoría trimestral, con retirada al baseline sin modelo; (2) fallo de una
  puerta de gobernanza sin resolver en la revisión; (3) el caso deja de ser sintético y documentado o
  entra un conjunto que no cumple el contrato de datos; (4) no se puede sostener la revisión humana
  con la capacidad disponible; (5) detección de un uso fuera del alcance aprobado.
- **Recurso de apelación:** registro de apelaciones con respuesta del responsable en plazo definido;
  su resultado se incorpora como evidencia de control al registro de riesgos.

## Lo que este registro NO afirma

No afirma que el sistema sea justo ni injusto, ni que la brecha observada sea discriminación causal,
ni que el piloto sea seguro: afirma que **con la evidencia disponible el despliegue autónomo no está
justificado** y que la vía defendible es un piloto con autoridad limitada, auditoría trimestral y
condiciones de retiro explícitas. El estado actual es REVIEW y el escalamiento a STOP está
documentado, no está activo.
