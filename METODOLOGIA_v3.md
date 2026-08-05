# Metodología v3 — presupuesto anual de 365 días

**Fecha:** agosto de 2026
**Sustituye a:** `README.md` §3.4 (taxonomía de feriados), §4 (fórmulas) y §5 (supuestos).
El resto del README —procedencia de datos, códigos de confianza, fuentes— sigue vigente.

| | v2 | v3 |
|---|---|---|
| Script | `scripts/modelo_completo.py` | `scripts/modelo_v3.py` |
| Dashboard | `descanso-latam-2026.html` | `dashboard-tiempo-de-trabajo-2026.html` |
| Marco | ranking de «días liberados» | reparto cerrado de los 365 días |
| Entradas por país | 8 | 6 |
| Verificaciones internas | 4 | 5 (incluye el cierre en 365) |

---

## 1. Debilidades detectadas en v2

### 1.1 La métrica principal no medía lo que decía medir — **estructural**

v2 ordenaba países por `vacaciones + feriados`. Ese agregado ocupa entre el 5 % y el 10 % del año.
Ordenar por él y concluir «este país descansa más» supone implícitamente que todo lo demás es
igual entre países.

La correlación entre ese agregado y el porcentaje del año efectivamente trabajado es
**r = +0,01**. Es decir: el indicador que ordenaba la infografía **no contiene información**
sobre cuánto trabaja la gente en el año. No es una imprecisión de grado — es un indicador
ortogonal al fenómeno que dice describir.

La causa es que el bloque con más peso quedaba fuera del modelo. Dispersión entre los once países:

| Bloque | Rango entre países |
|---|---|
| Descanso semanal | **52,1 días** ← no estaba en el modelo |
| Vacaciones | 15,7 días |
| Feriados | 6,9 días |

La estructura de la semana explica un rango **3,3 veces mayor** que las vacaciones.

### 1.2 Cinco países tenían una jornada diaria legalmente imposible — **error de consistencia**

v2 fijaba a mano los días laborables por semana (`dsl`). Al cruzarlos con la jornada semanal, el
cociente `jornada ÷ dsl` superaba el tope diario legal en cinco de los once países:

| País | jornada | dsl v2 | h/día implícita | tope legal | Norma |
|---|---|---|---|---|---|
| Panamá | 48 | 5,5 | **8,73** | 8 | CT art. 31 |
| Brasil | 44 | 5,0 | **8,80** | 8 | CLT art. 58 |
| Argentina | 48 | 5,0 | **9,60** | 9 | Ley 11.544 art. 1 |
| Uruguay | 48 | 5,5 | **8,73** | 8 | Ley 5.350 |
| Paraguay | 48 | 5,0 | **9,60** | 8 | CL art. 194 |

El par (jornada semanal máxima, días por semana) era internamente contradictorio: describía
trabajadores que agotan el tope semanal violando el tope diario.

### 1.3 La conversión de días hábiles a calendario no era reversible — **bug**

`vac_en_calendario` usaba un factor fijo `7/5` mientras `vac_en_laborables` usaba `dsl/7`.
Las dos funciones asumían semanas distintas para el mismo país:

| País | dsl | 7/5 (v2) | 7/dsl (correcto) | Error | Ida y vuelta |
|---|---|---|---|---|---|
| Uruguay | 5,5 | 28,0 | 25,5 | +2,5 | 20 → 28 → **22** |
| Honduras | 5,5 | 14,0 | 12,7 | +1,3 | 10 → 14 → **11** |
| México | 6,0 | 16,8 | 14,0 | +2,8 | 12 → 16,8 → **14,4** |

Convertir hábiles → calendario → laborables no devolvía el valor original.

### 1.4 La taxonomía de feriados era precisión sin exactitud — **coste/beneficio negativo**

Clasificar cada feriado en fijo / trasladable / litúrgico era la entrada `[C]` más frágil: una
taxonomía construida por el autor, sin fuente que la publique, para once calendarios nacionales.

Lo que compraba, frente a la ambigüedad que ya arrastraba el conteo base:

| País | Corrección de la taxonomía | Ambigüedad del conteo | Ratio |
|---|---|---|---|
| Perú | +0,29 días | ±2,57 días | **8,9×** |
| Panamá | +1,07 días | ±1,57 días | 1,5× |
| Uruguay | +1,71 días | ±0,79 días | 0,5× |

En Perú, la taxonomía refinaba en **0,3 días** un número cuya base era incierta en **2,6 días**.
Corrección media en los once países: 1,4 días. Es refinar un dígito que el dato de partida no tiene.

### 1.5 El índice porcentual tenía denominador endógeno — **ya declarado en v2**

`pct_anio_laboral_descanso = descanso / (dsl × 52)` es algebraicamente idéntico a
`horas_descanso / horas_contractuales`: la jornada aparece en numerador y denominador y **se
cancela**. El índice no distinguía entre trabajar 40 h o 48 h semanales.

El síntoma: Ecuador quedaba 9.º de 11 pese a ser el país con menos horas trabajadas de la muestra.
v2 documentaba el problema pero mantenía el índice como opción seleccionable. Un índice cuyo
síntoma es invertir el caso más claro no se acompaña de una advertencia: se retira.

### 1.6 Doble conteo feriado–vacaciones — **omisión**

Si la ley expresa las vacaciones en días **calendario**, un feriado que cae dentro del período
queda absorbido: no libera un día de trabajo adicional. v2 lo sumaba dos veces. Afecta
exactamente a los cinco países de régimen calendario/corridos —Perú, Panamá, Brasil, Ecuador,
Argentina— que son los que encabezaban el ranking. En Perú el sobreconteo era de 1,1 días.

### 1.7 Longitud de barra invertida — **error de visualización**

Para las métricas «menos es mejor», v2 calculaba el ancho como
`w = 100 − ((v−min)/(max−min)) × 62`. Consecuencias: la barra **más larga** correspondía al valor
**menor**, y la escala arrancaba en 38 % en vez de cero. La longitud contradecía el número impreso
al lado: Ecuador con 1.907 h tenía barra al 100 % y México con 2.349 h barra al 38 %.

### 1.8 La vista inicial era la métrica menos defendible

El dashboard abría con `cur="bruto"`, la métrica que su propia descripción calificaba de «menos
defendible». Lo primero que veía un lector era el número incorrecto.

---

## 2. Metodología v3

### 2.1 Principio: un presupuesto cerrado

Los 365 días del año se reparten en **cuatro bloques mutuamente excluyentes y exhaustivos**:

```
trabajo  +  descanso semanal  +  vacaciones  +  feriados  =  365
```

Ninguna cifra puede crecer sin que otra decrezca. No hay residuo, no hay doble conteo, y el cierre
en 365 es una **verificación automática** que v2 no podía hacer porque su marco no era exhaustivo.

Esto resuelve de raíz el problema de unidades incompatibles que el propio trabajo denunciaba: no
hay que elegir entre días calendario y días hábiles, porque todo aterriza en una sola partición
del año.

### 2.2 Fórmulas

```
d               = máx(5 ; ceil_medio(jornada_semanal / tope_diario_legal))
descanso_semanal = 365 × (7 − d) / 7
potenciales      = 365 × d / 7

vacaciones  = V                    si la ley las expresa en días hábiles
            = V × d/7              si las expresa en días calendario o corridos

feriados_br = F × d/7
solape      = 0                              si la unidad es hábiles
            = feriados_br × (vacaciones / potenciales)   si es calendario o corridos
feriados    = feriados_br − solape

trabajo     = potenciales − vacaciones − feriados
horas       = trabajo × (jornada_semanal / d)
```

Indicadores derivados: `% del año = bloque / 365`, `% de vigilia = horas / 5.840`
(5.840 = 365 días × 16 h despierto), `días libres = 365 − trabajo`,
`días de trabajo por semana = trabajo / 52,14`.

### 2.3 Por qué cada decisión

**`d` derivado, no supuesto.** Si la jornada semanal máxima es *J* y el tope diario es *T*,
repartir *J* en menos de *J/T* días obliga a superar *T*. El número de días deja de ser una
opinión sobre costumbres laborales y pasa a ser una consecuencia de dos cifras `[A]` verificables.
El piso de 5 recoge que ningún código de la muestra contempla una semana ordinaria más corta
(Chile lo dice expresamente: CT art. 28, «no menos de cinco días»).

**Feriados sin taxonomía.** `F × d/7` es la esperanza de que un feriado caiga en día laborable si
su fecha no está correlacionada con el día de la semana. Pierde la corrección de los feriados
trasladados por ley —Colombia es el caso más afectado— pero elimina once clasificaciones no
auditables. Bajo el marco de 365 días el coste es menor de lo que era: un feriado vale 0,27 puntos
porcentuales del año, mientras que la brecha Perú–Chile es de 11,4 puntos.

**Vacaciones en días de trabajo liberados.** Los fines de semana que caen dentro de un período
vacacional ya están contados en el bloque de descanso semanal: el trabajador los habría tenido
libres igual. Atribuirlos a «vacaciones» los contaría dos veces. Esta separación es lo que permite
comparar los 30 días calendario de Perú con los 15 hábiles de Chile.

**Solape solo en régimen calendario.** Es una distinción legal, no un ajuste ad hoc. Las
legislaciones que cuentan en días **hábiles** ya excluyen los feriados del cómputo — CST art. 187
en Colombia, CT art. 69 en Chile — de modo que un feriado dentro del período no consume día de
vacaciones. Las que cuentan en días **calendario** lo absorben; Ecuador lo dice expresamente
(CT art. 69: «incluidos los días no laborables»).

**Año de 365 días, no 52 semanas.** v2 mezclaba `jornada × 52` (= 364 días) con una vigilia
calculada sobre 8.760 h (= 365 días). v3 usa 365 en todo, y las 5.840 h de vigilia son
exactamente 365 × 16.

### 2.4 Qué métrica usar para qué

| | Robustez frente al supuesto `d` | Interpretabilidad |
|---|---|---|
| **Horas trabajadas al año** | **Invariante** (≤1,5 % entre escenarios) | media |
| **% del año trabajado** | sensible (hasta 14 puntos) | alta |

Para un país con vacaciones en días calendario la invariancia es exacta:

```
horas = (365·d/7 − V·d/7 − F·d/7 + solape) × (J/d)
      = J·(365 − V − F)/7 + F·V·J/(7·365)
```

La `d` se cancela por completo. Por eso el dashboard presenta las **horas anuales** como cifra
comparable principal y el **porcentaje del año** como lectura intuitiva, siempre con el escenario
declarado y conmutable.

---

## 3. Verificaciones automáticas

`python3 scripts/modelo_v3.py` imprime seis comprobaciones. Estado actual: **las seis pasan.**

| # | Comprueba | Resultado |
|---|---|---|
| V1 | Los cuatro bloques suman 365 días | desvío máx. 0,100 d (redondeo a 1 decimal) |
| V2 | Los cuatro porcentajes suman 100 | desvío máx. 0,100 pp |
| V3 | horas = días × horas/día | desvío máx. 1,10 h |
| V4 | Ninguna jornada diaria supera el tope legal | 11/11 (v2: 6/11) |
| V5 | Las horas anuales son invariantes al escenario | máx. 1,45 % (Uruguay) |
| V6 | Sueño + trabajo + traslado + libre suman 8.760 h | desvío máx. 1,0 h (8 países) |

El dashboard replica el modelo en JavaScript; se verificó que ambas implementaciones producen
cifras idénticas, y que el presupuesto cierra con error de 5,7 × 10⁻¹⁴ días en las 12
combinaciones de escenario × antigüedad. La versión JavaScript del reparto horario cierra en
8.760 h con desviación 0,0000 h exacto (sin el redondeo a enteros que aplica la salida de consola
de Python).

---

## 4. Resultados principales

Escenario legal, trabajador de 1 año de antigüedad:

| # | País | Trabajo | Sem. | Vac. | Fer. | % vigilia | Horas | Días libres |
|---|---|---|---|---|---|---|---|---|
| 1 | México | 294,9 | 52,1 | 12,0 | 6,0 | 40,4 % | 2.359 | 70,1 |
| 2 | Paraguay | 290,6 | 52,1 | 12,0 | 10,3 | 39,8 % | 2.325 | 74,4 |
| 3 | Argentina | 263,7 | 78,2 | 11,0 | 12,1 | 39,4 % | 2.301 | 101,3 |
| 4 | Uruguay | 280,0 | 52,1 | 20,0 | 12,9 | 38,4 % | 2.240 | 85,0 |
| 5 | Panamá | 277,7 | 52,1 | 25,7 | 9,4 | 38,0 % | 2.222 | 87,3 |
| 6 | **Perú** | **274,6** | 52,1 | 25,7 | 12,6 | **37,6 %** | **2.196** | **90,4** |
| 7 | Honduras | 268,1 | 78,2 | 10,0 | 8,6 | 36,7 % | 2.145 | 96,9 |
| 8 | Brasil | 256,0 | 78,2 | 23,6 | 7,2 | 35,1 % | 2.048 | 109,0 |
| 9 | Chile | 233,6 | 104,3 | 15,0 | 12,1 | 33,6 % | 1.962 | 131,4 |
| 10 | Colombia | 232,9 | 104,3 | 15,0 | 12,9 | 33,5 % | 1.956 | 132,1 |
| 11 | Ecuador | 241,8 | 104,3 | 10,7 | 8,2 | 33,1 % | 1.934 | 123,2 |

Ordenada por % de vigilia (§4ter) en vez de por % del año en días — el orden cambia levemente
respecto a la primera versión de esta tabla (Argentina y Honduras suben, Ecuador baja) porque las
dos métricas pesan `d` de forma distinta, exactamente el punto que motivó el retiro del % en días.

**El vuelco.** Perú pasa del 1.º puesto en «días de vacaciones + feriados» al **7.º en días libres
al año** y al **6.º en horas trabajadas**. México hace el recorrido inverso: del 11.º al 1.º.

**Robustez.** Perú queda **6.º de 11 en horas anuales bajo los tres escenarios** de semana laboral.
La conclusión —que el 1.º puesto del ranking original no describe el tiempo libre— no depende del
supuesto más débil del modelo.

**Correlaciones.** jornada semanal ~ horas/año: **r = +0,94**. días/semana ~ % del año en días:
**r = +0,95**. vacaciones + feriados ~ % de vigilia trabajando: **r = −0,04** (§4ter; era +0,01
con la métrica retirada).

---

## 4bis. Capa de traslado (añadida en agosto de 2026)

**Deliberadamente fuera del presupuesto de 365 días.** El presupuesto modela **derechos legales**;
el traslado es **conducta observada**, medida con otro instrumento y en otras unidades. Meterlo
dentro repetiría exactamente el error que este trabajo denuncia. Vive en su propia sección, como
la capa de horas efectivas.

**Fuentes `[B]`.** Métrica: minutos diarios de desplazamiento **ida y vuelta** al trabajo.
Seis países vienen de la OIT, *Tiempo de trabajo y bienestar en América Latina*, Informes Técnicos
Cono Sur n.º 56 (marzo de 2026), Gráfico 2 — elaborado con microdatos de las encuestas nacionales
de uso del tiempo. Perú y Brasil no están en ese informe y vienen de otro procesamiento de la
misma clase de instrumento (ver más abajo).

| País | min/día | Año | h traslado/año | h comprometidas/año | % vigilia | traslado ÷ vacaciones | Fuente |
|---|---|---|---|---|---|---|---|
| México | 69 | 2019 | 339 | 2.698 | 46,2 % | 3,5× | OIT · EUT |
| Argentina | 77 | 2021 | 338 | 2.640 | 45,2 % | 3,5× | OIT · EUT |
| **Perú** | **80** | **2024** | **366** | **2.563** | **43,9 %** | **1,8×** | **ENUT · BCRP–USIL** |
| Uruguay | 56 | 2022 | 261 | 2.501 | 42,8 % | 1,6× | OIT · EUT |
| Paraguay | 36 | 2016 | 174 | 2.499 | 42,8 % | 1,8× | OIT · EUT |
| **Brasil** | **58** | **2019** | **247** | **2.295** | **39,3 %** | **1,3×** | **PNS · IBGE** |
| Colombia | 86 | 2021 | 334 | 2.290 | 39,2 % | 2,7× | OIT · EUT |
| Chile | 74 | 2023 | 288 | 2.250 | 38,5 % | 2,3× | OIT · EUT |

Fórmula: `horas_traslado = días_de_trabajo × minutos / 60`. Se multiplica por los días
efectivamente trabajados —no por 365— porque no se viaja al trabajo en vacaciones ni en feriados;
así la capa es coherente con el presupuesto sin formar parte de él.

**Hallazgo 1.** En los ocho países con dato, **el traslado consume más horas al año que las
vacaciones legales**, entre 1,3× y 3,5×. Añade de 3,0 a 6,3 puntos de la vida despierta. El debate
sobre quién descansa más se libra sobre una variable más pequeña que el trayecto diario que nadie
contabiliza.

**Hallazgo 2 — reordenamiento.** Sumar el traslado mueve el ranking: **Perú sube del 5.º al 3.º
puesto**, Argentina del 3.º al 2.º, Paraguay baja del 2.º al 5.º y Chile del 7.º al 8.º. Con
366 h/año, Perú tiene el **traslado absoluto más alto** de los ocho. Brasil, con el factor más
bajo (1,3×), no cambia de posición.

**Desigualdad interna.** *Chile (EUT 2023):* transporte público 105 min/día (33,9 % de los
trabajadores) frente a auto propio 63 min (42,4 %) — 66 minutos diarios de diferencia con la misma
jornada legal. *Perú (ENUT 2024):* promedio nacional 80 min, Lima Metropolitana 102 min, periferia
de Lima y Callao más de 180 min. Los promedios nacionales esconden esto.

### El dato de Brasil: procedencia

**Fuente `[B]`:** Pesquisa Nacional de Saúde (PNS) 2019, IBGE — encuesta nacional de salud con
módulo de traslado, sobre la población ocupada que se desplaza a su trabajo. Reporta **4,8
horas/semana ida y vuelta** (4,9 h en zona urbana, 3,5 h en zona rural). Convertido a diario
dividiendo entre 5 días —la misma convención que usa el propio informe de la OIT para pasar de
semanal a diario en otros datos brasileños de esta serie—: **58 minutos/día**.

*Verificación cruzada:* un procesamiento más antiguo de la PNAD (~2012, vía IPEA) estimó 30,2
minutos **de ida** a nivel nacional, que implica ~60 min ida y vuelta — muy cerca de los 58 min
de la PNS 2019. Dos fuentes independientes convergen.

### Por qué Panamá, Ecuador y Honduras siguen sin dato

Se buscó activamente un dato comparable para los cuatro países que faltaban (incluido Brasil, ya
incorporado arriba). Para los otros tres, la búsqueda encontró algo pero no calificó, por tres
motivos distintos — vale la pena distinguirlos en vez de agruparlos como «no se encontró nada»:

- **Panamá:** dos fuentes candidatas, y **las dos se descartan**.
  1. La cifra publicada de 52 minutos (Panamá Ciudad, CAF RED 2017, Daude y otros) es una encuesta
     de **movilidad urbana de una sola ciudad**, no una encuesta nacional de uso del tiempo como
     las otras ocho. Usarla mezclaría el mismo problema de unidades incompatibles que este trabajo
     corrige. Tampoco se pudo confirmar si mide solo ida o ida y vuelta.
  2. Panamá **sí tiene** una Encuesta de Uso del Tiempo (INEC, **octubre de 2011**) —la lista el
     repositorio de la CEPAL y no figuraba en versiones previas de este documento— pero falla por
     dos motivos independientes, ambos verificados en el propio informe del INEC
     (`inec.gob.pa/archivos/p5151comentarios_eut.pdf`):
     - **Cobertura urbana, no nacional.** «La Encuesta de Uso del Tiempo se realizó por primera vez
       en Panamá, en el mes de octubre de 2011, *en todas las áreas urbanas del país*». El dominio
       de estudio declarado es «Nacional **Urbano**», sobre 3.720 viviendas. Mismo defecto que la
       cifra de CAF.
     - **Excluye el traslado por diseño.** Los tres cuadros de resultados llevan al pie la nota
       literal **«No incluye traslados»** sobre la categoría *Trabajo*. No existe ninguna categoría
       de transporte, desplazamiento o viaje en el instrumento. Es decir, la encuesta **no puede**
       producir un dato de traslado ni siquiera para el ámbito urbano.

  Conclusión: el hueco de Panamá no es por falta de búsqueda, sino porque **ninguna fuente
  panameña mide la variable**. Es un caso distinto del de Ecuador (que la mide pero no la aísla).
- **Ecuador:** el problema **no es la antigüedad, es el diseño del instrumento.** El repositorio de
  la CEPAL registra para Ecuador una Encuesta Específica de Uso del Tiempo (**EUT 2012**) y, además,
  módulos de uso del tiempo dentro de la ENEMDU en **2005, 2007, 2010, 2012 y 2015-2017** — es
  decir, sí existen mediciones posteriores a 2012. Pero ninguna aísla la variable: la EUT 2012 mide
  «trabajo y traslado» como **una sola categoría** (43–50 h/semana), y la cifra de la ENEMDU combina
  el traslado al trabajo **y** al estudio. Un módulo más reciente con el mismo diseño no resuelve
  nada: por muchas ediciones que se añadan, la pregunta no separa lo que hace falta.
- **Honduras:** es el registro **más pobre de los once**. El repositorio de la CEPAL le asigna una
  sola entrada, **2009**, y no es una encuesta sino un «**set de preguntas** en la Encuesta
  Permanente de Hogares de Propósitos Múltiples (EPHPM)». Hay indicios de una repetición en 2014,
  pero **con la pregunta agregada** en vez de desagregada — es decir, el instrumento evolucionó en
  la dirección contraria a la que haría falta. Esos sets de preguntas se diseñaron para cuantificar
  trabajo doméstico no remunerado, no traslado. Y el Observatorio de Movilidad Urbana de la CAF
  —que cubre 29 áreas metropolitanas en 12 países— no incluye Tegucigalpa ni San Pedro Sula, así que
  tampoco hay salida por la vía urbana.

**Por qué no existe ninguna ruta que llegue a los once.** Las tres ausencias tienen causas
distintas —Panamá no mide la variable, Ecuador la mide sin aislarla, Honduras no tiene instrumento—
y por eso ninguna solución única las cubre. Bajar el estándar a encuestas de movilidad urbana
metropolitana recuperaría Ecuador (Quito, Guayaquil) y Panamá (los 52 min de CAF), pero **seguiría
dejando fuera a Honduras**, y además haría incomparables esas tres cifras con las ocho actuales, que
son nacionales. Se pasaría de «8 países medidos igual» a «8 nacionales + 2 urbanos + 1 hueco»: peor
que el estado actual, y con el mismo defecto de unidades incompatibles que denuncia §1.1. **Se
mantienen los ocho.**

### Por qué el dato de Paraguay es de 2016 y no puede actualizarse

Comprobado contra el **repositorio de uso del tiempo de América Latina y el Caribe** de la CEPAL,
edición de **noviembre de 2025**: Paraguay aparece con **una sola entrada, 2016, Encuesta sobre el
Uso del Tiempo (EUT)**. Fue la primera encuesta de uso del tiempo del país —levantada por la DGEEC
(hoy INE) en octubre-noviembre de 2016, 4.272 hogares, personas de 14 años o más, con apoyo
metodológico de la División de Asuntos de Género de la CEPAL— y **no ha tenido segunda edición**.

La Encuesta Permanente de Hogares Continua (EPHC) del INE sigue vigente en 2026 y es trimestral,
pero es un instrumento de **mercado laboral** sin módulo de uso del tiempo: no mide traslado. Usarla
para «actualizar» los 36 minutos sería exactamente la mezcla de instrumentos que denuncia §1.1.

**Conclusión:** los 36 min/día de Paraguay no son un dato viejo por descuido del informe de la OIT
ni de este trabajo — son la frontera de lo que existe. Es, además, el dato más antiguo de los ocho
y por eso el dashboard marca su año en ámbar. Si el INE de Paraguay levanta una segunda EUT, esta
es la primera cifra que habría que sustituir.

*Movimiento a vigilar:* el mismo repositorio de la CEPAL registra a **Brasil en «pilotaje de módulos
de uso del tiempo» 2024–2025**. Si esos módulos se consolidan, sustituirían la cifra brasileña
actual (PNS 2019 convertida de semanal a diaria), que es la que más procesamiento propio arrastra.

### Años de referencia: nota de consistencia

Los años que usa el modelo son **Argentina 2021, Colombia 2021, México 2019, Uruguay 2022,
Chile 2023, Paraguay 2016** (más Perú 2024 y Brasil 2019, de otras fuentes). Una versión anterior
del pie de fuentes del dashboard citaba «DANE 2022» e «INE-MIDES Uruguay 2024», en contradicción
con los datos efectivamente usados aquí y en el propio dashboard. Se corrigió el pie para que
coincida con la tabla de arriba; el repositorio de la CEPAL respalda 2021 para Colombia.
**Pendiente de confirmación final contra el Gráfico 2 del informe de la OIT n.º 56.**

### El dato de Perú: procedencia y descarte

Se usa el promedio nacional del estudio de **N. Céspedes (BCRP–USIL, 2025)** sobre microdatos de la
**ENUT 2024 del INEI**: 1,33 h/día = **80 min**, tras subir un 57 % desde las 0,84 h de 2010. Es la
misma clase de instrumento —encuesta nacional de uso del tiempo— que la OIT usa para los otros
seis, procesado por otro equipo.

*Que la cifra es ida y vuelta se deduce de la aritmética del propio estudio:* calcula 32.400 horas
de vida en traslado como «tiempo de traslado diario × 240 días laborales × 45 años»; para los
distritos periféricos (3 h/día) da 3 × 240 × 45 = 32.400 exacto. Si midiera solo la ida no
cuadraría. **Validación externa independiente:** la Encuesta CAF 2016 estimó 40 minutos por
trayecto para el trabajador latinoamericano promedio — los mismos 80 min diarios.

*Se descarta* el «107 minutos **semanales**» que circuló en la nota de prensa de la ENUT: tomado
literalmente daría a Perú el traslado más corto de la región, por debajo de Paraguay, y es
incompatible con la propia serie 2010–2024 del INEI. Queda registrado para que un auditor no
repita el camino.

**Limitaciones declaradas.** El informe de la OIT advierte que «debido a diferencias metodológicas,
los datos no son estrictamente comparables entre países»; las cifras de Perú y Brasil añaden
además un procesamiento distinto al de las otras seis, aunque de la misma clase de instrumento.
Años de referencia de 2016 a 2024. Cobertura: 8 de 11 países — faltan Panamá, Ecuador y Honduras,
por los motivos documentados arriba. Fuerte heterogeneidad interna: Argentina registra 94 min en
el Gran Buenos Aires frente a 61 en el resto. Referencia de países de altos ingresos: ~25 min/día.
Úsese como orden de magnitud, no como ranking fino.

---

## 4ter. Retiro del % del año en días y presupuesto horario completo (agosto 2026)

### Por qué se retiró el % del año en días

El dashboard usaba `% del año trabajado = días de trabajo ÷ 365` como indicador porcentual
principal. Se probó su sensibilidad al supuesto de `d` (días laborables por semana) con el mismo
método de la sección 3, y falló la propia prueba de robustez del modelo:

| Métrica | Rango promedio entre escenarios | Rango máximo |
|---|---|---|
| % del año en días | **7,9 puntos** | 14,0 puntos (México, 66,8–80,8 %) |
| Horas trabajadas al año | 0,3 % | 1,4 % (Uruguay) |
| % de vigilia trabajando (horas ÷ 5.840) | **0,12 puntos** | 0,55 puntos (Uruguay) |

La causa es algebraica, no empírica: `horas = trabajo(d) × jornada/d` cancela `d` casi por
completo (sección 2.4), así que cualquier cociente con denominador **externo y fijo** —horas
totales, horas de vigilia— hereda esa invariancia. `% del año en días`, en cambio, divide un
numerador sensible a `d` (`trabajo`, en días) entre una constante (365) que no absorbe nada: el
`d` pasa directo. Es el mismo tipo de fallo, con el signo invertido, que llevó a retirar el
índice `horas / (jornada×52)` de v2 (§1.5): ahí la jornada se cancelaba y el índice quedaba ciego
a 40 h frente a 48 h; aquí es `d` el que no se cancela y el índice queda sobreexpuesto a él.

**Consecuencia práctica.** El % del año en días dejó de mostrarse en cualquier sección del
dashboard —hero, tiles, correlación, dispersión por jornada, tabla, panel de robustez—. Los días
en sí (recuentos, no porcentajes) se mantienen donde son la unidad natural del dato legal
(vacaciones, feriados, el presupuesto de 365 días de la sección 02, el ranking de la sección 01,
que es la comparación que el propio dashboard usa para *ilustrar* el problema, no una afirmación
de robustez). Lo que se retiró es el **cociente** días/365 como estadístico resumen, no la unidad
día.

**Efecto sobre la sección 01.** La correlación «vacaciones + feriados» vs. tiempo trabajado se
recalculó sobre `% de vigilia` en vez de `% del año`. El resultado no cambia de sentido —sigue
siendo nula al año 1 (r = −0,04 en vez de +0,01) y sigue volviéndose moderada-fuerte a partir de
los 5 años por el mismo mecanismo de confusión (regímenes escalonados concentrados en países de
seis días) documentado en la sección de robustez del dashboard—; si acaso, el resultado es más
nítido con la base robusta.

### El día completo: sueño + trabajo + traslado + libre = 8.760 h

Nueva sección del dashboard (07) que extiende el presupuesto de días (sección 02) y la capa de
traslado (sección 06) con la pieza que faltaba —el sueño— para repartir las 24 horas del año
completo, no solo los días de trabajo.

```
horas_sueño   = 8 h/día × 365           — constante [C], igual para los 11 países
horas_libre   = 8.760 − sueño − trabajo − traslado
```

**Cobertura: 8 de 11 países** — los mismos con dato de traslado (sección 06). Mostrar «libre» sin
restar un traslado real trataría un dato no medido como cero; es el mismo criterio de no imputar
que rige el resto del modelo.

**El toggle sueño-o-no.** El lector elige si el sueño cuenta como tiempo libre:

```
% comprometido, base vigilia = (horas + h_traslado) / 5.840 × 100     — el sueño queda fuera del universo
% comprometido, base año     = (horas + h_traslado) / 8.760 × 100     — el sueño cuenta, pero no como "libre"
```

A diferencia del selector de escenario de `d` (que puede reordenar países — sección 3), este
toggle es una transformación afín: resta la misma constante (2.920 h) a los 11 países por igual,
así que **nunca cambia el orden**, solo el nivel. Es una elección de interpretación —¿el sueño es
«tuyo» o es tiempo que no administras?— no un supuesto que pueda invalidar una comparación. Por
eso se deja a elección del lector en vez de fijarlo de antemano, algo que **no** sería seguro
hacer con el escenario de `d`.

**Verificación.** El cierre exacto en 8.760 h (V6, sección 3) y el hecho de que el gráfico siempre
muestra las cuatro franjas —el sueño nunca se esconde dentro de «libre»— son las dos garantías de
que esta capa no repite el error de ocultar una variable dentro de un supuesto implícito.

---

## 5. Limitaciones que siguen abiertas

1. ~~Tres conteos de feriados en conflicto~~ — **resuelto en agosto de 2026** (README §3.3):
   Perú 16 (verificación del autor), Panamá 12 (Código de Trabajo art. 49 + Ley 291/2022),
   Uruguay 15 (5 no laborables + 10 laborables, reconstruido fecha por fecha). Las tres cifras
   confirman el valor que ya usaba el modelo — no hubo que cambiar ningún número.
2. **Se pierde la corrección por feriados trasladados.** Colombia mueve ~12 feriados a lunes por
   Ley Emiliani y v3 no lo recoge. Sustituir la esperanza por el calendario 2026 día a día
   resolvería esto y el punto anterior a la vez.
3. **Esto mide derechos, no conducta.** El presupuesto de 365 días (sección 02) y sus derivados
   suponen que el trabajador toma todas sus vacaciones y todos los feriados y trabaja la jornada
   máxima. Las secciones 05 (horas efectivas, 4 de 11 países) y 06 (traslado, 8 de 11) son
   contrapeso empírico, pero de otros instrumentos y otros años de referencia — no se integran al
   presupuesto legal, precisamente para no mezclar derecho con conducta observada.
4. **`d` sigue siendo un mínimo legal, no una observación.** Una empresa puede repartir la jornada
   en más días de los que exige el tope. La derivación acota el supuesto; no lo elimina.
5. **Uruguay tiene jornada dual** (48 h industria, 44 h comercio y servicios); se usa el techo
   de 48 h, lo que subestima su descanso relativo en servicios.
6. **Informalidad excluida por decisión de alcance.** En varios de estos países el empleo formal
   es minoritario.
7. **El promedio regional de la serie temporal es simple, no ponderado** por población ocupada.

---

## 6. Estado de los archivos

| Archivo | Estado |
|---|---|
| `dashboard-tiempo-de-trabajo-2026.html` | **vigente** |
| `scripts/modelo_v3.py` | **vigente** — genera los CSV |
| `datos/dataset_maestro.csv` | **vigente** (v3) |
| `datos/presupuesto_anual.csv` | **vigente** (v3) — 44 filas |
| `datos/sensibilidad_dsl.csv` | **vigente** (v3) |
| `datos/jornada_serie_2023_2030.csv` | **vigente** |
| `descanso-latam-2026.html` | histórico (v2) |
| `scripts/modelo_completo.py` | histórico (v2) — **no ejecutar**: sobrescribiría `dataset_maestro.csv` con el esquema antiguo |
| `datos/resultados_por_antiguedad.csv` | **obsoleto** — salida de v2, incoherente con el resto |
| `scripts/01_modelo_inicial.py`, `02_modelo_antiguedad.py` | históricos |
