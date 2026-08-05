# Descanso remunerado en Latinoamérica 2026 — documentación de auditoría

Reanálisis de una infografía de circulación pública que rankeaba a once países
latinoamericanos por "días de descanso remunerado". El trabajo corrige errores de dato,
normaliza unidades incompatibles e incorpora variables que la pieza original omitía.

**Fecha de elaboración:** julio–agosto de 2026
**Estado:** las cifras derivadas son **estimaciones metodológicas**, no valores oficiales.

> ## ⚠ Este README documenta el modelo **v2**, superado en agosto de 2026
>
> El modelo pasó a un **presupuesto cerrado de 365 días**. Lee primero
> **[`METODOLOGIA_v3.md`](METODOLOGIA_v3.md)**, que **sustituye** a las secciones
> **§3.4** (taxonomía de feriados), **§3.5** (`dsl` asignado a mano), **§4** (fórmulas) y
> **§5** (supuestos) de este documento. §3.4 y §3.5 ya no tienen tabla propia: quedaron
> reducidas a una nota que explica por qué se retiraron y remite a la metodología vigente.
>
> Sigue vigente todo lo demás: procedencia de los datos (§3.1–3.3, §3.6–3.7), códigos de
> confianza (§2), limitaciones de alcance (§6) y fuentes (§8).
>
> Cambios de fondo: se eliminó la clasificación de feriados en fijos/trasladables/litúrgicos;
> los días laborables por semana pasaron de supuesto `[C]` a derivación del tope diario legal;
> se corrigieron un error de conversión hábiles↔calendario, un doble conteo feriado–vacaciones
> y cinco países cuya jornada diaria implícita superaba su propio tope legal.
>
> **No ejecutes `scripts/modelo_completo.py`**: sobrescribiría `datos/dataset_maestro.csv`
> con el esquema antiguo. El script vigente es `scripts/modelo_v3.py`.

---

## 1. Contenido de la carpeta

```
Politicas_laborales/
├── README.md                          este archivo
├── descanso-latam-2026.html           infografía interactiva (abrir en navegador)
├── datos/
│   ├── dataset_maestro.csv            entradas del modelo, una fila por país
│   ├── resultados_por_antiguedad.csv  44 filas (11 países × 4 tramos)
│   └── jornada_serie_2023_2030.csv    serie temporal de jornada legal
└── scripts/
    ├── modelo_completo.py             ← reproduce TODAS las cifras derivadas
    ├── 01_modelo_inicial.py           versión 1 (histórico, superada)
    └── 02_modelo_antiguedad.py        versión 2 (histórico, superada)
```

Para reproducir: `python3 scripts/modelo_completo.py`. No requiere dependencias externas.
Imprime verificaciones internas y regenera los tres CSV.

---

## 2. Cómo leer los códigos de confianza

Cada dato de entrada lleva una etiqueta. **Si vas a auditar, empieza por los [C].**

| Código | Significado | Riesgo |
|---|---|---|
| **[A]** | Verificado en fuente primaria: texto de ley, publicación oficial o documento OIT | Bajo |
| **[B]** | Verificado en prensa especializada con al menos dos coincidencias independientes | Medio |
| **[C]** | Clasificación o supuesto **del autor del modelo**, no tomado de ninguna fuente | **Alto** |
| **[?]** | Fuentes consultadas **se contradicen** y el conflicto no se resolvió | **Alto** |

> **Nota de honestidad.** La primera versión de este README sobreestimó la confianza de los
> conteos de feriados (§3.3). Cinco venían de la infografía auditada, no de verificación
> propia. Se corrigió en agosto de 2026 y apareció un error de dato en Brasil. Si encuentras
> otras etiquetas optimistas, asúmelas como sospechosas hasta comprobarlas.

---

## 3. Procedencia de cada dato

### 3.1 Vacaciones legales mínimas y escalas por antigüedad — [A]

| País | 1 año | 5 años | 10 años | 20 años | Unidad | Norma |
|---|---|---|---|---|---|---|
| Perú | 30 | 30 | 30 | 30 | calendario | Ley 27735 — régimen plano |
| Panamá | 30 | 30 | 30 | 30 | calendario | Código de Trabajo — plano |
| Brasil | 30 | 30 | 30 | 30 | corridos | CLT — plano (se reduce por faltas) |
| Colombia | 15 | 15 | 15 | 15 | hábiles | CST — plano |
| Chile | 15 | 15 | 15 | 18 | hábiles | Art. 68 CT — feriado progresivo: +1 día por cada 3 años sobre 10 de cotizaciones |
| Argentina | 14 | 21 | 28 | 35 | corridos | Art. 150 LCT — 4 tramos |
| Uruguay | 20 | 21 | 22 | 25 | hábiles | Ley 12.590 — +1 día cada 4 años tras el 5.º |
| Ecuador | 15 | 15 | 20 | 30 | calendario | Art. 69 CT — +1 día por año tras el 5.º, tope 30 |
| Paraguay | 12 | 18 | 30 | 30 | hábiles | 3 tramos: <5, 5–10, >10 años |
| Honduras | 10 | 20 | 20 | 20 | hábiles | 10/12/15/20 días según 1/2/3/4+ años |
| México | 12 | 20 | 22 | 26 | hábiles | Art. 76 LFT tras reforma "Vacaciones Dignas" (1 ene 2023) |

**Advertencia sobre los años frontera.** Los valores corresponden al *tramo legal* en que cae
el trabajador, no a un cálculo día a día. Las redacciones difieren ("hasta 5 años" vs.
"más de 5 y hasta 10"), por lo que en el aniversario exacto puede haber uno o dos días de
diferencia respecto a lo que muestra el modelo. **No usar para liquidaciones individuales.**

**Error corregido respecto a la infografía original:** clasificaba los 12 días de México como
*calendario*. El art. 76 de la LFT los define como **hábiles**. La diferencia es de ~5 días
de calendario.

### 3.2 Jornada máxima legal semanal — [A]

Vigente a **julio de 2026** (no la ley marco, sino el escalón en vigor a esa fecha):

| País | h/sem 2026 | Nota |
|---|---|---|
| Ecuador | 40 | Art. 47 CT — único que ya cumple la recomendación OIT |
| Colombia | 42 | Ley 2101 de 2021, escalón final el **15 de julio de 2026** |
| Chile | 42 | Ley 21.561 ("40 horas"), escalón vigente desde el **26 de abril de 2026** |
| Brasil, Honduras | 44 | |
| Perú, Panamá, Argentina, Uruguay, Paraguay, México | 48 | |

**Errores corregidos respecto a la infografía original:** citaba el *Panorama Laboral OIT 2023*
como fuente para datos rotulados 2026. Entre esa publicación y julio de 2026 ocurrieron tres
reformas de jornada (Chile, Colombia, y la reforma constitucional mexicana con gradualidad
2027–2030) que la pieza no recoge.

**Serie 2023–2030** en `datos/jornada_serie_2023_2030.csv`:
Colombia 47→46→44→42 (jul. de cada año); Chile 45→44 (abr. 2024) →42 (abr. 2026) →40 (abr. 2028);
México 48 hasta 2026, luego 46 (2027), 44 (2028), 42 (2029), 40 (2030).
**Ocho de los once países no registran un solo cambio en toda la serie.**

### 3.3 Feriados nacionales 2026 — **confianza DESIGUAL, revisar por país**

> **Corrección de integridad (agosto 2026).** Una versión previa de este README etiquetaba
> todos estos conteos como `[B] verificado en prensa con al menos dos coincidencias`.
> **Eso era falso.** Cinco de los once (Brasil, Panamá, Uruguay, Paraguay, Honduras) se
> arrastraron de la infografía original sin verificación independiente — es decir, de la
> misma pieza que este trabajo audita. Al verificarlos apareció **un error de dato**.
> La tabla siguiente refleja el estado real tras la verificación.

| País | Valor usado | Confianza | Estado |
|---|---|---|---|
| Brasil | **10** | **[A]** | **CORREGIDO — era 12.** Portaria MGI n.º 11.460, DOU 30 dic. 2025: son 10 feriados nacionales. Carnaval es *ponto facultativo*, no feriado |
| Paraguay | 12 | [A] | Verificado — Ley 7544 (incluye Jura de la Constitución desde 2026) |
| México | 7 | [A] | Art. 74 LFT — días de descanso obligatorio |
| Colombia | 18 | [B] | Consistente en varias fuentes |
| Chile | 17 | [B] | Consistente en varias fuentes |
| Argentina | 16 | [B] | Consistente (inamovibles + trasladables) |
| Ecuador | 12 | [B] | Calendario del Ministerio de Turismo |
| Honduras | 11 | [B] | Verificado tras la auditoría |
| **Perú** | 16 | **[A]** | **RESUELTO** — verificado por el autor contra fuente propia (ago. 2026) |
| **Panamá** | 12 | **[A]** | **RESUELTO** — Código de Trabajo art. 49 + Ley 291 de 2022 |
| **Uruguay** | 15 | **[B]** | **RESUELTO por reconstrucción** — 5 no laborables + 10 laborables, fecha por fecha |

**Origen de los conflictos.** No era error de las fuentes: los países clasifican los feriados de
formas distintas. Uruguay separa *no laborables* (descanso obligatorio) de *laborables*
(a criterio del empleador); Panamá distingue feriados nacionales de días de duelo y de fiesta
nacional; Perú separa feriados de *días no laborables* del sector público. La pregunta
"¿cuántos feriados tiene el país X?" no tiene una respuesta única sin fijar antes qué cuenta
como feriado — que es, en pequeño, el mismo problema de unidades que denuncia todo este trabajo.

**Cómo se resolvieron los tres casos (agosto 2026).**

- **Perú — 16.** El autor lo verificó de forma independiente. Descarta la fuente minoritaria
  que decía 13; no requirió investigación adicional de este trabajo.

- **Panamá — 12.** El art. 49 del Código de Trabajo fija 11 fechas de descanso obligatorio:
  1 y 9 de enero, martes de carnaval, viernes santo, 1.º de mayo, 3 y 5 de noviembre,
  10 y 28 de noviembre, 8 y 25 de diciembre. La **Ley 291 de 2022** añadió el 20 de diciembre
  como Día de Duelo Nacional (invasión de EE. UU. de 1989), elevando el total a **12**. Es la
  suma exacta de las dos normas, no una elección de clasificación. Verificado además contra
  cobertura de prensa específica de 2026 (La Estrella, Telemetro), que coincide en 12.
  El 15 de agosto (fundación de la Ciudad de Panamá) y el 5 de noviembre a veces se reportan
  como "fiesta nacional" no obligatoria en vez de feriado — de ahí las cifras de 13-14 que
  circulan y que citan el art. 49 sin la actualización de 2022.

- **Uruguay — 15.** Ninguna ley única lista las 15 fechas: son **5 "no laborables"** fijas por
  el art. 18 de la Ley 12.590 (1.º de enero, 1.º de mayo, 18 de julio, 25 de agosto,
  25 de diciembre — confirmado en la página oficial del MTSS) más **10 "laborables"** fijadas
  por normas dispersas (6 de enero, lunes y martes de carnaval, jueves y viernes santo,
  19 de abril, 18 de mayo, 19 de junio, 12 de octubre, 2 de noviembre). Se reconstruyó
  fecha por fecha y coincide con dos fuentes de prensa que hacen el mismo desglose completo.
  Las cifras de 14 o 16 que circulan vienen de tratar la Semana de Turismo como un solo bloque
  (14) o de contar su inicio y cierre como fechas adicionales en vez de las dos fechas que
  realmente se pagan —jueves y viernes santo— (16).

Las tres cifras coinciden con las que ya usaba el modelo: esta verificación sube su nivel de
confianza, no cambia ningún número del dashboard.

**Impacto de la corrección de Brasil (12 → 10 feriados, 1 → 2 litúrgicos):**

| | Antes | Después |
|---|---|---|
| Feriados efectivos | 8,9 | **7,7** |
| Descanso en días laborables | 30,3 | **29,1** |
| Horas trabajadas al año | 2.021 | **2.032** |

Brasil baja una posición en el ranking de descanso. No altera las conclusiones estructurales
del análisis, pero **sí altera la cifra de Brasil**.

**Discrepancia adicional:** la infografía original asigna **19** feriados a Colombia; las
fuentes consultadas reportan **18**. El modelo usa 18.

**Inconsistencia interna declarada:** la fuente que reporta 18 feriados colombianos indica
**11** trasladados por Ley Emiliani; el modelo usa **12**. Diferencia no resuelta, de bajo
impacto (±0,3 días laborables), pero registrada.

### 3.4 Clasificación de feriados en tres tipos — **retirada del modelo (agosto 2026)**

Este README documentaba aquí una taxonomía propia (fijo / trasladable / litúrgico) para
ponderar cada feriado según su probabilidad de caer en día laborable. **No se usa desde
`modelo_v3.py`.** Se retiró porque era coste/beneficio negativo: en Perú corregía apenas
**0,3 días** sobre un conteo cuya propia base tenía **±2,6 días** de incertidumbre — refinar
un dígito que el dato de partida no tiene. Corrección media en los once países: 1,4 días.

La fórmula vigente trata todos los feriados por igual —`F × d/7`, la esperanza de que un
feriado caiga en día laborable— sin distinguir tipo. Detalle completo, con la tabla de
corrección por país y las dos correcciones de error que motivaron el retiro, en
`METODOLOGIA_v3.md` §1.4.

### 3.5 Días laborables por semana (`dsl`) — **retirada del modelo (agosto 2026)**

Este README documentaba aquí una tabla de asignación manual por país (5,0 para Brasil,
Colombia, Chile, Argentina, Ecuador y Paraguay; 5,5 para Panamá, Uruguay y Honduras; 6,0 para
Perú y México) — un supuesto `[C]`, no un dato observado. **No se usa desde `modelo_v3.py`.**
Se retiró porque era internamente contradictorio: cruzado con la jornada semanal, el cociente
superaba el tope diario legal en cinco de los once países (Panamá y Uruguay 8,73 h/día sobre
un tope de 8; Brasil 8,80 h sobre 8; Argentina 9,60 h sobre 9; Paraguay 9,60 h sobre 8) —
combinaciones legalmente imposibles.

El modelo vigente **deriva** `d` en vez de asignarlo:
`d = máx(5 ; jornada_semanal ÷ tope_diario_legal)`, redondeado hacia arriba en pasos de 0,5.
Con esa regla, los once países cumplen siempre su propio tope legal. Detalle completo, con la
tabla de las cinco combinaciones imposibles, en `METODOLOGIA_v3.md` §1.2.

### 3.6 Horas efectivamente trabajadas por asalariados — [A]

**Fuente primaria:** OIT, nota técnica *"¿Cuántas horas se trabajan en América Latina y el
Caribe? Indicadores del tiempo de trabajo y su organización"*, Sonia Gontero, 30 de octubre de
2025. Datos ILOSTAT recopilados en octubre de 2025, año de referencia **2023**.
DOI: 10.54394/ZSZI3837

| País | h/sem | |
|---|---|---|
| Colombia | 46,6 | valor más alto de América Latina |
| Honduras | ~45,0 | la fuente dice "alrededor de 45" |
| Argentina | 37,0 | valor más bajo de la región |
| Uruguay | 37,0 | |
| **Otros 7** | **sin dato** | **no imputado** |
| Ref. América Latina | 42,0 | promedio de asalariados |
| Ref. OCDE altos ingresos | 34,6 | 19 países |

La nota reporta el indicador de asalariados **solo para los países en los extremos de la
distribución**. Los siete restantes quedan vacíos deliberadamente. Rellenarlos con el promedio
regional de 42 h aparentaría completitud a costa de inventar observaciones.

**Por qué "asalariados" y no "personas ocupadas":** el recorte excluye al trabajo por cuenta
propia, donde se concentra la informalidad, y reduce la influencia de jornadas extremas. Es la
mejor aproximación disponible al empleo formal en datos armonizados — **pero no lo aísla:
existen asalariados informales.** La OIT no desagrega por formalidad en esta serie.

### 3.7 Caso Perú: horas por formalidad — [B], **no comparable**

**Fuente:** INEI, Encuesta Permanente de Empleo Nacional (EPEN), procesada y difundida por
ComexPerú (datos 2023).

| Segmento | h/sem |
|---|---|
| Microempresa **formal** | 50,3 — **por encima** del tope legal de 48 h |
| Microempresa **informal** | 40,6 |
| Brecha agregada formal vs. informal | +7,4 |
| Gran empresa (brecha) | +2,4 |

**Hallazgo que contradice la intuición dominante:** en Perú el trabajador **formal** trabaja
*más* horas que el informal. La lectura de ComexPerú es que la formalidad encarece al
trabajador y la empresa compensa extrayendo más horas por puesto. Consecuencia para este
trabajo: restringir el análisis al sector formal **no** sesga el resultado a favor del descanso;
en Perú lo sesga en contra.

También contradice una afirmación de la nota OIT ("en todos los países las horas efectivas de
los asalariados son inferiores a la jornada legal"): cierto en el agregado, falso en el
segmento de microempresa formal peruana. La agregación escondía el caso.

**Por qué no entra en el gráfico comparativo:** distinto instrumento (EPEN vs. ILOSTAT),
distinto período de referencia y distinta definición operativa de "formal". Además, 50,3 h
corresponde a **microempresa formal**, no al agregado del sector formal: tratarlo como promedio
nacional sería un salto de segmento a agregado.

**Nota de rastreo:** la serie del BCRP titulada *"Promedio de Horas de Trabajo"* (BCRPData,
CD10245DA) **no** es la fuente correcta — corresponde a braceros arroceros, 1931–1944.

---

## 4. Fórmulas

Todas implementadas en `scripts/modelo_completo.py`.

### 4.1 Vacaciones → días laborables liberados
```
si unidad = hábiles      →  vac_laborables = vac
si unidad = calendario   →  vac_laborables = vac × (dsl / 7)
```
Las vacaciones en días calendario consumen fines de semana que el trabajador
habría descansado igual; las expresadas en hábiles no.

### 4.2 Vacaciones → días calendario equivalentes
```
si unidad = hábiles      →  vac_calendario = vac × 7 / 5
si unidad = calendario   →  vac_calendario = vac
```

### 4.3 Feriados → días laborables (esperanza matemática)
```
feriados_efectivos = (trasladables + litúrgicos) × 1 + fecha_fija × (dsl / 7)
```

### 4.4 Descanso total
```
descanso_dias_laborables = vac_laborables + feriados_efectivos
```

### 4.5 Horas anuales
```
horas_dia       = jornada_semanal / dsl
horas_descanso  = descanso_dias_laborables × horas_dia
horas_teoricas  = jornada_semanal × 52
horas_trabajadas = horas_teoricas − horas_descanso
```

### 4.6 Índices porcentuales
```
pct_anio_laboral_descanso = descanso_dias_laborables / (dsl × 52) × 100
pct_vigilia_trabajando    = horas_trabajadas / 5840 × 100
```

> **Propiedad algebraica crítica del primer índice.** Es idéntico a
> `horas_descanso / horas_teoricas`, porque:
> ```
> (tot × jor/dsl) / (jor × 52)  =  tot / (dsl × 52)
> ```
> **La jornada se cancela.** El índice NO distingue entre trabajar 40 h o 48 h semanales.
> El script incluye una verificación automática que comprueba esta identidad.
>
> Síntoma clínico: **Ecuador queda 9.º de 11 (8,3%) pese a ser el país con menos horas
> trabajadas al año de toda la muestra.** No es un error del dato: es el problema del
> denominador endógeno — quien trabaja poco tiene un denominador pequeño que castiga su
> numerador.
>
> El segundo índice corrige esto usando un denominador **externo e idéntico para todos**
> (horas de vigilia). Con él, Ecuador pasa a primero (32,7%) y México a último (40,2%).
> **Los dos índices deben leerse juntos; ninguno sustituye al otro.**

---

## 5. Supuestos

| # | Supuesto | Impacto si es falso |
|---|---|---|
| S1 | `dsl` (días laborables/semana) es 5, 5,5 o 6 según país | Alto — afecta todas las cifras derivadas de ese país |
| S2 | Los feriados litúrgicos y de carnaval nunca caen en fin de semana | Bajo — es cierto por construcción del calendario |
| S3 | Los feriados de fecha fija se distribuyen uniformemente en la semana | Medio — cierto a largo plazo, no en un año concreto |
| S4 | 8 h diarias de sueño → 5.840 h de vigilia anuales | Bajo para el orden, alto para el nivel absoluto |
| S5 | 52 semanas por año | Despreciable |
| S6 | El trabajador toma todas sus vacaciones y todos los feriados | **Alto** — ver §6 |

---

## 6. Limitaciones y advertencias

**6.1 — Esto mide derechos, no experiencia.** Todo el análisis legal describe lo que la norma
garantiza. No captura cumplimiento efectivo, y no puede hacerlo.

**6.2 — La esperanza de feriados no es el calendario 2026.** Los de fecha fija se ponderan por
`dsl/7`, no por el día real en que caen. Margen aproximado **±1 día laborable**. Sustituir la
esperanza por el calendario real de 2026 eliminaría este margen; es trabajo mecánico pendiente.

**6.3 — Asimetría temporal en la brecha ley–práctica.** Las horas efectivas son de **2023** y
la jornada legal de **julio de 2026**. La brecha de Colombia (+4,6 h) mide la distancia entre
una norma nueva y una conducta medida *antes* de su entrada en vigor. **No es incumplimiento
comprobado.**

**6.4 — Un promedio bajo de horas efectivas no equivale a bienestar.** Puede reflejar
parcialidad involuntaria o subempleo. Rankear por esa variable premiaría al subempleo. Por eso
se presenta como contexto y no como ranking.

**6.5 — Jornadas duales no capturadas.** Uruguay tiene 48 h en actividad industrial y 44 h en
comercio y servicios; el modelo usa el techo de 48 h, lo que **subestima** su descanso relativo
en el sector servicios.

**6.6 — El promedio regional de la serie temporal es simple, no ponderado.** Es la media de
once legislaciones, no de once poblaciones ocupadas. Ponderado por fuerza laboral, Brasil y
México dominarían y la trayectoria sería distinta.

**6.7 — Informalidad excluida por decisión del usuario.** El análisis se restringe al empleo
formal. Es una decisión deliberada, no un descuido — pero significa que las cifras describen a
una minoría de la población ocupada en varios de estos países.

**6.8 — "Número de feriados" no es una magnitud unívoca.** Perú, Panamá y Uruguay tienen ya sus
16, 12 y 15 feriados verificados (§3.3, agosto 2026), pero eso no los hace comparables entre sí:
cada país clasifica de forma distinta feriados, días no laborables y días de descanso
obligatorio, y el número usado adopta el criterio de cada legislación, no un estándar común.
Cualquier ranking que sume feriados entre países arrastra esta ambigüedad de fondo, incluido este.

**6.9 — Lo que deliberadamente NO se grafica en la serie temporal.**
*Feriados:* su número varía por accidente de calendario, no por política — una serie invitaría
a leer tendencia donde hay aritmética del año.
*Vacaciones:* el único cambio relevante (México, "Vacaciones Dignas") entró en vigor el 1 de
enero de 2023, justo en el borde de la ventana; una línea 2023–2026 la mostraría plana.
*Horas efectivas:* ILOSTAT armonizado llega a 2023; cualquier punto posterior sería
extrapolación.

---

## 7. Errores detectados en la infografía original

1. **México** — los 12 días se rotulan *calendario*; el art. 76 LFT los define como **hábiles**.
2. **Chile** — la jornada bajó a **42 h** el 26 de abril de 2026, no 45 h.
3. **Colombia** — la jornada bajó a **42 h** el 15 de julio de 2026.
4. **Inconsistencia interna** — Colombia figura con 34 días rankeada *por encima* de Chile y
   Uruguay, que muestran 35.
5. **Fuente desactualizada** — cita el *Panorama Laboral OIT 2023* para datos rotulados 2026,
   con al menos tres reformas de jornada ocurridas después.
6. **Unidades incompatibles sumadas** — días calendario, corridos y hábiles en una sola columna.
7. **Feriados tratados como equivalentes** — ignora que uno trasladado a lunes vale más que uno
   fijo que puede caer en domingo.
8. **Brasil con 12 feriados** — el calendario oficial 2026 (Portaria MGI n.º 11.460) registra
   **10** feriados nacionales. Carnaval es *ponto facultativo*, no feriado.
   *(Este error se replicó en la primera versión del presente análisis antes de detectarse.)*
9. **Sesgo del "primer año"** — mostrar solo el primer año favorece sistemáticamente a los
   países de régimen plano (Perú, Panamá, Brasil, Colombia) y castiga a los escalonados. Al
   pasar a 10 años, **Paraguay salta del 8.º al 1.º puesto** y Argentina del 7.º al 5.º.

---

## 8. Fuentes consultadas

**Auditado en agosto de 2026: se revisaron todas las fuentes en uso; ninguna resultó huérfana.**
Cada cita de este README, de `METODOLOGIA_v3.md` y del pie del dashboard se cruzó contra esta
lista. No se encontró ninguna fuente listada aquí que ya no esté citada en algún lugar del
proyecto — si eliminas una entrada de esta tabla, elimina primero su cita en el dashboard o en
`METODOLOGIA_v3.md`, o quedará un enlace roto de referencia.

**Cómo leer la columna Rigor.** No mide si el *dato* citado es correcto — eso ya lo cubren los
códigos `[A]`/`[B]`/`[C]`/`[?]` de la §2. Mide el tipo de fuente en sí, para que puedas decidir
cuánto peso darle si alguna vez entra en conflicto con otra:

| Rigor | Significa |
|---|---|
| **Alta** | Texto legal, boletín de instituto nacional de estadística/banco central, o informe técnico de organismo internacional/multilateral. Fuente primaria. |
| **Media-alta** | Prensa con desk económico o legal propio y estándares editoriales establecidos (agencias, diarios de referencia regional). Secundaria pero fiable; cita datos oficiales sin reprocesarlos. |
| **Media** | Prensa generalista de un solo país, gremio empresarial con interés en el tema, o medio pequeño sin desk especializado. Usar como apoyo, no como única fuente. |
| **Baja / verificar** | Blog corporativo o agregador sin proceso editorial visible. En este proyecto, al menos una (Lenox HR) mostró una inconsistencia interna real — ver nota. |

### Primarias

| Fuente | Usada para | Rigor | Nota |
|---|---|---|---|
| OIT / Sonia Gontero (30 oct. 2025), *¿Cuántas horas se trabajan en América Latina y el Caribe?* — [Nota técnica](https://www.ilo.org/sites/default/files/2025-11/NOTA%20TECNICASG_NOV2025%20ESP.pdf), DOI 10.54394/ZSZI3837 | Horas efectivas §3.6, base del hero y las secciones 04-05 del dashboard | **Alta** | Informe técnico OIT, datos ILOSTAT 2023 |
| [OIT, *Tiempo de trabajo y bienestar en América Latina*, Informes Técnicos Cono Sur n.º 56](https://www.ilo.org/sites/default/files/2026-03/IT56-Tiempo-trabajo-bienestar-Am%C3%A9rica-Latina_v3.pdf) (marzo 2026) | Capa de traslado, sección 06 del dashboard, 6 de 8 países | **Alta** | Informe técnico OIT con microdatos de encuestas nacionales de uso del tiempo |
| Portal oficial de feriados — [argentina.gob.ar](https://www.argentina.gob.ar/jefatura/feriados-nacionales-2026) | Feriados Argentina 2026 | **Alta** | Gobierno nacional |
| Portal oficial de feriados — [gob.pe](https://www.gob.pe/feriados) | Feriados Perú, referencia general | **Alta** | Gobierno nacional |
| Textos legales citados en §3.1 y §3.2 (Ley 27735 Perú, CLT Brasil, Ley 2101 Colombia, Ley 21.561 Chile, etc.) | Vacaciones y jornada legal de los 11 países | **Alta** | Norma primaria por país |

### Reformas de jornada y verificación cruzada

| Fuente | Usada para | Rigor | Nota |
|---|---|---|---|
| [Thomson Reuters Chile — guía Ley 21.561](https://www.thomsonreuters.cl/es-cl/soluciones-juridicas/biblioteca-contenido-legal/reduccion-de-jornada-laboral-en-chile-guia-hacia-las-42-horas-en-20261) | Escalón de la Ley 40 horas Chile | **Alta** | Contenido legal profesional, cita el texto de la ley directamente |
| [Infobae Colombia (15 jul. 2026) — jornada a 42 h](https://www.infobae.com/colombia/2026/07/15/jornada-laboral-en-colombia-bajo-a-42-horas-semanales-como-quedo-la-carga-laboral-con-respecto-a-otros-paises-de-la-region/) | Fecha exacta del escalón colombiano | **Media-alta** | Medio digital de referencia regional, desk económico propio |
| [El Imparcial (17 jul. 2026) — jornadas laborales en América Latina](https://www.elimparcial.com/mexico/2026/07/17/asi-quedan-las-jornadas-laborales-en-america-latina-con-colombia-en-42-horas-chile-rumbo-a-40-y-mexico-a-la-espera-de-iniciar-su-reduccion-gradual/) | Panorama comparado de jornadas 2026 | **Media** | Diario mexicano generalista; cifras cruzadas contra fuente primaria de cada país |
| [Bloomberg Línea — reducción de jornada en América Latina](https://www.bloomberglinea.com/economia/latinoamerica-avanza-en-la-reduccion-de-la-jornada-laboral-en-que-paises-se-trabaja-menos/) | Comparativos regionales de jornada | **Alta** | Desk económico especializado, estándar editorial de Bloomberg |
| [Infobae (7 jul. 2024) — días corridos vs. hábiles](https://www.infobae.com/america/mundo/2024/07/07/cantidad-de-dias-corridos-o-habiles-como-son-las-vacaciones-en-el-mundo/) | Contraste de regímenes de vacaciones | **Media-alta** | Mismo medio que arriba |

### Conteos de feriados 2026 (verificación de agosto 2026)

| País | Fuente | Rigor | Nota |
|---|---|---|---|
| Brasil | [Portaria MGI n.º 11.460, DOU 30 dic. 2025](https://www.gov.br/gestao/pt-br/assuntos/noticias/2025/dezembro/confira-o-calendario-oficial-de-feriados-nacionais-e-pontos-facultativos-em-2026) | **Alta** | Diario Oficial de la Unión — texto legal primario |
| Paraguay | Ley 7544 · [abc.com.py](https://www.abc.com.py/nacionales/2025/11/13/estos-son-los-feriados-para-el-2026/) | **Alta** (ley) / **Media-alta** (medio) | ABC Color es el diario de mayor tirada de Paraguay |
| Perú | [peru21.pe](https://peru21.pe/peru/estos-son-los-16-feriados-nacionales-del-2026/) + verificación directa del autor | **Media** (medio) — **Alta** (verificación) | Peru21 es un tabloide de servicio, no de investigación; la cifra queda sostenida por la verificación propia del autor, no por el medio |
| Panamá | Código de Trabajo art. 49; Ley 291 de 2022 · [La Estrella](https://www.laestrella.com.pa/panama/nacional/calendario-oficial-de-dias-festivos-en-panama-para-2026-NM18273259), [Telemetro](https://www.telemetro.com/nacionales/calendario-feriados-panama-2026-todos-los-dias-festivos-y-no-laborables-n6062135) | **Alta** (ley) / **Media-alta** (medios) | Los dos diarios panameños de mayor trayectoria; la cifra queda anclada al texto legal, no solo a la prensa |
| Uruguay | Ley 12.590 art. 18 · [MTSS](https://www.gub.uy/ministerio-trabajo-seguridad-social/institucional/derecho-laboral-uruguayo/feriados), [El Observador](https://www.elobservador.com.uy/nacional/estos-son-todos-los-feriados-2026-uruguay-que-dias-se-corren-y-cuales-se-mantienen-su-fecha-original-n6024895), [Lenox HR](https://www.lenoxhr.com/feriados-uruguay) | **Alta** (ley y MTSS) / **Media-alta** (El Observador) / **Baja** (Lenox HR) | Lenox HR es un blog corporativo de RR. HH.: su propia tabla se contradice (llama "no laborable" a la Semana de Turismo y omite el 18 de mayo). Se usó solo tras contrastarla contra el MTSS y El Observador — nunca como fuente única |

### Tiempo de traslado

| Fuente | Usada para | Rigor | Nota |
|---|---|---|---|
| Pesquisa Nacional de Saúde (PNS) 2019, IBGE — vía [Jovem Pan](https://jovempan.com.br/noticias/brasileiro-gasta-quase-5-horas-semanais-para-ir-ao-trabalho-pandemia-pode-mudar-essa-logistica/) | Traslado Brasil, sección 06 | **Alta** (encuesta) / **Media-alta** (medio) | IBGE es el instituto nacional de estadística; Jovem Pan es un medio brasileño grande y establecido |
| [CAF RED 2017, "Crecimiento urbano y acceso a oportunidades"](https://scioteca.caf.com/handle/123456789/1090) (Daude y otros) | Referencia regional de 40 min/trayecto | **Alta** | Publicación institucional de CAF (banco de desarrollo), autores identificados |
| [Síntesis de Resultados II ENUT 2023, INE Chile](https://www.ine.gob.cl/docs/default-source/uso-del-tiempo-tiempo-libre/publicaciones-y-anuarios/ii-enut/sintesis-de-resultados-ii-enut-2023.pdf) | Traslado por medio de transporte, Chile | **Alta** | Instituto nacional de estadística, publicación oficial |

### Caso Perú

| Fuente | Usada para | Rigor | Nota |
|---|---|---|---|
| INEI, [Encuesta Permanente de Empleo Nacional (EPEN)](https://m.inei.gob.pe/media/MenuRecursivo/boletines/epen-nacional-ivt2023.pdf), procesada por [ComexPerú, *Semanario*](https://www.comexperu.org.pe/articulo/trabajadores-formales-trabajan-mas-que-informales-por-costos-laborales) — datos 2023 | Horas por formalidad §3.7 | **Alta** (INEI) / **Media** (ComexPerú) | ComexPerú es un gremio empresarial: su análisis de los datos INEI es técnicamente sólido y las cifras se verificaron exactas, pero su interpretación puede llevar un sesgo pro-empresarial — se usó el dato, no la lectura editorial completa |
| [N. Céspedes (BCRP–USIL, 2025), "El muy prolongado viaje al trabajo en Perú", Documento de Trabajo n.º 009-2025](https://www.bcrp.gob.pe/docs/Publicaciones/Documentos-de-Trabajo/2025/documento-de-trabajo-009-2025.pdf) | Traslado Perú, sección 06 | **Alta** | Documento de trabajo del banco central, afiliación académica identificable. **Corrección (ago. 2026):** el resto del proyecto lo citaba como "2026" — la cobertura de prensa es de febrero de 2026, pero el documento del BCRP está archivado en su serie **2025**. Se corrigió el año en `METODOLOGIA_v3.md` y en el dashboard para que coincida con la fuente primaria |
| [BCRPData, «Promedio de Horas de Trabajo» (CD10245DA)](https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/CD10245DA/html) — **descartada** | — (corresponde a braceros arroceros, 1931–1944) | **Alta** (la serie) | La serie del BCRP es fiable en sí misma; el error habría sido nuestro, al usarla para lo que no mide. Se descarta el uso, no la fuente |

---

## 9. Trabajo pendiente sugerido

1. **Sustituir la esperanza de feriados por el calendario 2026 día a día** para los once países.
   Elimina la limitación 6.2 por completo.
2. ~~Resolver los tres conteos en conflicto (Perú, Panamá, Uruguay — §3.3)~~ — **hecho en
   agosto de 2026**, ver §3.3. Las tres cifras confirmaron el valor que ya usaba el modelo.
3. ~~Validar la clasificación [C] de feriados (§3.4) contra los decretos nacionales~~ —
   **ya no aplica**: la clasificación se retiró del modelo en agosto de 2026 (§3.4),
   no solo quedó sin validar.
4. **Actualizar horas efectivas** cuando ILOSTAT publique 2024–2025, y cerrar los siete vacíos.
5. **Ponderar el promedio regional** por población ocupada (§6.6).
6. **Buscar el corte formal/informal en fuentes nacionales** del resto de países (DANE, INE
   Chile, IBGE, INEGI). Daría el criterio de formalidad en los once, a costa de perder
   comparabilidad entre instrumentos — decisión a tomar conscientemente.
