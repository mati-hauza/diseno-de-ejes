# ESPECIFICACIONES TÉCNICAS v2
# Programa de análisis y verificación de ejes contra fatiga y fluencia

**Asignatura:** Mecanismos y Elementos de Máquinas
**Lenguaje:** Python
**Bibliografía principal:** Budynas, R. G. y Nisbett, J. K. *Diseño en ingeniería mecánica de Shigley*, décima edición.
**Bibliografía complementaria:** Pilkey, W. D. *Peterson's Stress Concentration Factors*, segunda edición.

---

# 0. DECISIONES CERRADAS DE ESTA VERSIÓN

Estas decisiones corrigen las ambigüedades de la versión anterior. El agente no debe reinterpretarlas.

1. **El eje siempre gira.** No se analizan ejes fijos. Todo esfuerzo de flexión producido por cargas transversales es completamente alternante en un punto material de la superficie.
2. **Los factores teóricos \(K_t\) no se usan directamente para calcular tensiones.** Se usan solamente para obtener los factores de fatiga \(K_f\). Tanto la verificación de fatiga como la de fluencia usan \(K_f\), \(K_{fs}\), siguiendo el procedimiento de ejes de Shigley (ecuaciones 7-5 y 7-6 para fatiga, y 7-15 y 7-16 para fluencia). No se calcula un segundo juego de tensiones con \(K_t\).
3. **Las chavetas se dimensionan primero**, porque su longitud define la geometría del chavetero y, por lo tanto, el concentrador de esfuerzos.
4. **No se permite el solape de concentradores de esfuerzos.** La única excepción son varios chaveteros pertenecientes al mismo elemento, que comparten la misma zona axial por diseño.
5. **Si \(\sum M_x \neq 0\), el programa lanza un error y se detiene.** Los apoyos no absorben torque.
6. **En los chaveteros hay dos radios distintos:**
   - \(r_e=a/2\): radio del extremo semicircular del chavetero visto desde arriba. Es geometría, no entra en Peterson.
   - \(r_f\): radio del filo de fondo del chavetero. Es el \(r\) que usa Peterson y es una entrada opcional del usuario.
7. **Si no se conoce \(r_f\), se usan los valores iniciales de la tabla 7-1 de Shigley.** Si se conoce pero no cumple el rango de Peterson, se emite una advertencia y se vuelve a la tabla 7-1.
8. **El factor de efectos diversos de Marin se llama \(k_{f,marin}\).** No debe confundirse con \(K_f\).
9. **Los factores de Marin fuera de rango son error**, no advertencia. El programa no extrapola.
10. **El informe se muestra por consola.** No se genera PDF en esta versión.
11. **La última salida del programa son las gráficas de factor de seguridad.** No se imprime nada después de ellas.
12. **La cantidad de chaveteros de un elemento multiplica los \(K_t\)** y luego se recalculan los \(K_f\). Es una aproximación académica y debe advertirse.
13. **Todas las cargas son constantes en el tiempo.** No hay valores mínimos y máximos, ni casos de carga, ni parámetro de ciclo. La alternancia proviene exclusivamente de la rotación del eje.
14. **Cada concentrador genera siempre tres \(K_t\)** (\(K_{t,N}\), \(K_{t,B}\), \(K_{ts}\)) y **tres \(K_f\)** (\(K_{f,N}\), \(K_{f,B}\), \(K_{fs}\)). No se admiten concentradores con uno o dos factores.
15. **El usuario no ingresa ángulos de chaveta.** Solo indica a qué elemento corresponde la chaveta. La cantidad \(m\) y la distribución angular las define el programa.
16. **Los ejes de las gráficas son fijos:** A-15-7, A-15-8 y A-15-9 usan \(r/d\) con curvas \(D/d\); A-15-16 y A-15-17 usan \(a/t\) con curvas \(r/t\). Peterson Chart 5.1 y 5.2 usan \(r_f/d\). No se reinterpretan.

---

# 1. OBJETIVO

Desarrollar un programa académico en Python que permita analizar y verificar el diseño de ejes macizos de sección circular, fabricados en acero, sometidos a cargas axiales, flexión y torsión.

El usuario introduce la geometría del eje, sus elementos montados, apoyos, concentradores, material, cargas, factor de seguridad mínimo y cantidad de divisiones de la malla.

El programa debe:

1. Validar la coherencia geométrica y mecánica de los datos.
2. Dimensionar las chavetas y determinar la geometría de los chaveteros.
3. Calcular los factores teóricos \(K_t\) y los factores de fatiga \(K_f\) de todos los concentradores.
4. Calcular las reacciones en los apoyos.
5. Calcular las ocho solicitaciones internas a lo largo del eje.
6. Calcular los esfuerzos nominales y corregidos, separando componentes medias y alternantes.
7. Calcular los Von Mises alternante, medio y máximo.
8. Verificar fatiga por Goodman modificado y fluencia por Von Mises.
9. Calcular los factores de seguridad en todos los puntos de evaluación.
10. Generar un informe completo del procedimiento para los puntos críticos.
11. Generar las gráficas de solicitaciones y de factores de seguridad.

El programa **no dimensiona automáticamente los diámetros del eje**. El usuario propone la geometría y el programa la verifica. Sí dimensiona automáticamente las chavetas.

---

# 2. ALCANCE Y LIMITACIONES

## 2.1. Geometría incluida

- Ejes macizos de sección circular.
- Tramos cilíndricos de diámetro constante.
- Escalonamientos con radio de redondeo.
- Chaveteros para chavetas cuadradas, fresados de extremo semicircular.
- Ranuras para anillos de retención, con geometría opcional.

## 2.2. Materiales

- Acero para el eje.
- Material para cada chaveta.
- Material para el cubo de cada elemento con chaveta.
- Se permite que distintos elementos tengan distintos materiales de cubo.

## 2.3. Cargas incluidas

- Fuerzas puntuales cartesianas.
- Fuerzas radiales y tangenciales.
- Momentos puntuales.
- Cargas distribuidas uniformes por intervalo.
- Todas las cargas son constantes en el tiempo. La alternancia proviene únicamente de la rotación del eje.

## 2.4. Criterios de falla

- Fatiga: Goodman modificado.
- Fluencia: Von Mises.

La arquitectura debe permitir agregar otros criterios de fatiga sin modificar los módulos mecánicos.

## 2.5. Fuera de alcance

- Deflexiones y pendientes.
- Velocidades críticas.
- Vibraciones.
- Pandeo.
- Fatiga multiaxial no proporcional.
- Elementos finitos.
- Ejes huecos.
- Materiales distintos del acero para el eje.
- Dimensionamiento automático de diámetros.
- Torque absorbido por los apoyos.
- Chaveteros de extremo abierto.
- Correcciones de proximidad entre concentradores.

## 2.6. Hipótesis de fatiga

- Todas las cargas son constantes en el tiempo.
- El eje siempre gira.
- La flexión de un eje giratorio sometido a cargas transversales constantes produce esfuerzo completamente alternante: \(M_a=M_R\), \(M_m=0\).
- El torque constante y la carga axial constante producen componentes medias: \(T_a=0\), \(T_m=T\), \(N_a=0\), \(N_m=N\).
- No existen componentes alternantes de torque ni de carga axial.
- No se analiza fatiga multiaxial no proporcional.

---

# 3. CONVENCIONES Y UNIDADES

## 3.1. Coordenadas

- \(X\): eje longitudinal del eje.
- \(Y\): vertical.
- \(Z\): horizontal transversal.
- El ángulo \(\theta\) se mide desde \(+Y\) hacia \(+Z\).
- Los ángulos de entrada y salida se expresan en grados.

## 3.2. Unidades de entrada y salida

| Magnitud | SI | Inglés |
|---|---|---|
| Longitud | mm | in |
| Fuerza | N | lbf |
| Momento | N·mm | lbf·in |
| Carga distribuida | N/mm | lbf/in |
| Esfuerzo | MPa | ksi |
| Temperatura | °C | °F |
| Velocidad angular | rpm | rpm |

## 3.3. Unidades internas

Todo cálculo interno se realiza en SI coherente:

- Longitud: m.
- Fuerza: N.
- Momento: N·m.
- Esfuerzo: Pa.
- Temperatura: °C.
- Ángulo: radianes.

Las conversiones se hacen al ingresar y al mostrar resultados. Los módulos de cálculo no reciben ni devuelven unidades de usuario.

## 3.4. Nomenclatura

| Símbolo | Significado |
|---|---|
| \(K_{t,N}\) | Factor teórico de concentración para carga axial |
| \(K_{t,B}\) | Factor teórico de concentración para flexión |
| \(K_{ts}\) | Factor teórico de concentración para torsión |
| \(K_{f,N}\) | Factor de fatiga para carga axial |
| \(K_{f,B}\) | Factor de fatiga para flexión |
| \(K_{fs}\) | Factor de fatiga para torsión |
| \(q\) | Sensibilidad a la entalla para esfuerzo normal |
| \(q_s\) | Sensibilidad a la entalla para esfuerzo cortante |
| \(S_e'\) | Límite de fatiga de la probeta |
| \(S_e\) | Límite de fatiga corregido |
| \(k_a\) | Factor de acabado superficial |
| \(k_b\) | Factor de tamaño |
| \(k_c\) | Factor de carga |
| \(k_d\) | Factor de temperatura |
| \(k_e\) | Factor de confiabilidad |
| \(k_{f,marin}\) | Factor de efectos diversos |
| \(n_f\) | Factor de seguridad a fatiga |
| \(n_y\) | Factor de seguridad contra fluencia |
| \(n_{min}\) | Factor de seguridad mínimo requerido |
| \(n_{chaveta}\) | Factor de seguridad exigido a la chaveta; por defecto \(n_{min}\) |

---

# 4. MODELO DE DATOS DE ENTRADA

## 4.1. Eje

| Campo | Tipo | Descripción |
|---|---|---|
| `longitud` | float | Longitud total \(L>0\) |
| `sistema` | enum | `SI` o `INGLES` |
| `material` | Material | Material del eje |
| `n_min` | float | Factor de seguridad mínimo \(>0\) |
| `n_div` | int | Cantidad de divisiones de la malla, por defecto 1000 |
| `tramos` | lista | Tramos cilíndricos |
| `escalonamientos` | lista | Escalonamientos |
| `apoyos` | lista | Apoyos |
| `elementos` | lista | Elementos montados |
| `ranuras` | lista | Ranuras para anillos de retención |
| `cargas` | lista | Fuerzas puntuales |
| `momentos` | lista | Momentos puntuales |
| `cargas_distribuidas` | lista | Cargas distribuidas |

El eje **siempre gira**. No existe el campo `gira`.

## 4.2. Tramo

| Campo | Descripción |
|---|---|
| `x_inicio` | Posición inicial del tramo |
| `x_fin` | Posición final del tramo |
| `d` | Diámetro del tramo |

Reglas:

- Al menos un tramo.
- Cada tramo debe tener longitud positiva.
- Los tramos deben estar ordenados y cubrir exactamente \([0,L]\).
- No puede haber espacios ni superposiciones.
- Todos los diámetros deben ser positivos.
- Si dos tramos adyacentes tienen el mismo diámetro, se pueden unir; si el usuario los deja separados, se aceptan pero no generan escalonamiento.
- Todo cambio de diámetro entre tramos adyacentes debe estar definido por un escalonamiento.

## 4.3. Escalonamiento

| Campo | Descripción |
|---|---|
| `x_s` | Posición longitudinal del escalonamiento |
| `r` | Radio de redondeo del filete |

Los diámetros \(D\) (mayor) y \(d\) (menor) no se informan: se deducen de los dos tramos adyacentes a \(x_s\), como \(D=\max(d_{izq},d_{der})\) y \(d=\min(d_{izq},d_{der})\).

Reglas:

- \(r>0\).
- \(x_s\) debe coincidir con el límite entre dos tramos adyacentes.
- Los dos tramos adyacentes deben tener diámetros distintos; de lo contrario no hay escalonamiento.
- Con \(D\) y \(d\) deducidos, \(D>d>0\) y \(r \leq (D-d)/2\).
- El filete se talla sobre el lado del diámetro menor. El tramo menor debe tener longitud suficiente para contener el radio \(r\).
- Si un tramo tiene filetes en sus dos extremos, la suma de los radios de los filetes que invaden ese tramo no puede superar su longitud.
- \(D/d\) y \(r/d\) deben estar dentro del dominio de las tablas de Shigley. No se extrapola.
- No puede haber un escalonamiento dentro de un elemento, ranura, chavetero o apoyo.
- Un escalonamiento puede coincidir con el borde de un apoyo, pero se emite una advertencia.

## 4.4. Apoyo

| Campo | Descripción |
|---|---|
| `nombre` | Identificador único |
| `posicion` | Centro del apoyo |
| `ancho` | Ancho total del apoyo |
| `fijo_axial` | Verdadero para el apoyo que absorbe carga axial |

Reglas:

- Exactamente dos apoyos.
- Exactamente uno con `fijo_axial=True`.
- Ancho positivo.
- Cada apoyo debe estar completamente dentro del eje: `inicio >= 0` y `fin <= L`.
- Los apoyos no pueden superponerse.
- Los centros de los apoyos no pueden coincidir.
- Ningún apoyo absorbe momento flector ni torque.
- La reacción se aplica en el centro del apoyo.
- Un apoyo no puede superponerse con un elemento.
- Un apoyo no puede contener estrictamente un escalonamiento, ranura o chavetero. Si un escalonamiento coincide exactamente con el borde del apoyo, se permite con advertencia.

## 4.5. Elemento montado

| Campo | Descripción |
|---|---|
| `nombre` | Identificador |
| `posicion` | Centro longitudinal \(x_e\) |
| `ancho` | Ancho \(L_e>0\) |
| `masa` | Opcional, kg (SI) o lb (inglés) |
| `usa_chaveta` | Verdadero si lleva chaveta |
| `a` | Lado de la chaveta cuadrada |
| `material_chaveta` | Material de la chaveta |
| `material_cubo` | Material del cubo |
| `r_f` | Radio del filo de fondo del chavetero, opcional |
| `n_chaveta` | Factor de seguridad para la chaveta, opcional, por defecto `n_min` |
| `cargas` | Cargas asociadas al elemento |
| `momentos` | Momentos asociados al elemento |

Reglas:

- El elemento debe estar completamente contenido en un solo tramo de diámetro constante.
- Si tiene chaveta, no puede estar al ras de \(x=0\) ni de \(x=L\), porque el chavetero quedaría abierto.
- No puede superponerse con otro elemento ni con un apoyo.
- Si `masa` se informa, se agrega una fuerza vertical \(W=mg\) en \(x_e\), con \(g=9.81\ \mathrm{m/s^2}\), en dirección \(-Y\).
- Si `usa_chaveta=True`, \(a>0\), `material_chaveta` y `material_cubo` son obligatorios, y \(S_{y,chaveta}\), \(S_{y,cubo}\) deben ser positivas.
- Si se informa \(n_{chaveta}\), debe ser positivo; si no, se usa \(n_{min}\).
- Si se informa \(r_f\), debe ser positivo.
- Se recomienda \(a\approx d/4\). Si \(a/d<0.2\) o \(a/d>0.3\), se emite una advertencia.
- Si \(S_{y,chaveta}\geq S_{y,eje}\), se emite una advertencia.
- Las cargas y momentos asociados deben estar dentro del intervalo del elemento.

## 4.6. Chaveta y chavetero

La chaveta es cuadrada:

\[
b=h=a
\]

Profundidad de alojamiento:

\[
t_{eje}=\frac{a}{2},\qquad t_{cubo}=\frac{a}{2}
\]

La chaveta se dimensiona en la Etapa 1. El chavetero resultante tiene:

- Cantidad \(m\).
- Lado \(a\).
- Longitud individual \(l\).
- Longitud total del chavetero \(L_k=l\).
- Centro \(x_e\).
- Intervalo axial \([x_e-l/2,\;x_e+l/2]\).
- Radio del extremo semicircular \(r_e=a/2\).
- Radio del filo de fondo \(r_f\) opcional.
- Profundidad en el eje \(a/2\).
- Profundidad en el cubo \(a/2\).

Los \(m\) chaveteros de un mismo elemento comparten el mismo centro y la misma longitud. Se suponen distribuidos uniformemente alrededor de la circunferencia. **El usuario no ingresa ningún ángulo de chaveta.**

El diámetro nominal usado para tensiones es el diámetro bruto del tramo \(d\). No se descuenta el chavetero. Esta es una aproximación que debe informarse.

## 4.7. Ranura para anillo de retención

| Campo | Descripción |
|---|---|
| `posicion` | Centro longitudinal \(x_r\) |
| `ancho` | Ancho \(a\) |
| `profundidad` | Profundidad radial \(t\) |
| `radio` | Radio del filo de fondo \(r\) |

La geometría es opcional. Si el usuario la informa, deben estar los tres valores. Si no la informa, se usan los valores iniciales de la tabla 7-1 de Shigley y la ranura se trata como un concentrador puntual en \(x_r\).

Con geometría:

\[
d_r=D_{local}-2t
\]

Reglas:

- \(a>0\), \(0<t<D_{local}/2\), \(0<r\leq a/2\).
- El intervalo \([x_r-a/2,\;x_r+a/2]\) debe estar completamente contenido en un solo tramo.
- La ranura no puede coincidir con un escalonamiento.
- La ranura no puede superponerse con un elemento, apoyo, chavetero u otra ranura.
- \(d_r>0\).

Sin geometría:

- Solo se requiere \(x_r\).
- Se usan \(K_{t,N}=K_{t,B}=5\), \(K_{ts}=3\), \(q=q_s=1\).
- Se advierte que se usaron valores iniciales.

## 4.8. Material del eje y factores de Marin

| Campo | Descripción |
|---|---|
| `nombre` | Identificador |
| `Sut` | Resistencia última a la tracción, en unidades de usuario |
| `Sy` | Resistencia a la fluencia, en unidades de usuario |
| `acabado` | Acabado superficial: `esmerilado`, `maquinado`, `laminado_caliente` o `forja` |
| `temperatura` | Temperatura de funcionamiento, en °C (SI) o °F (inglés) |
| `confiabilidad` | Confiabilidad requerida como fracción, \(0.50\leq R\leq0.999999\) |
| `k_f_marin` | Factor de efectos diversos, opcional, por defecto 1 |

Reglas:

- \(S_{ut}>0\), \(S_y>0\), \(S_{ut}>S_y\). Internamente se convierten a Pa.
- `acabado` debe ser uno de los cuatro valores admitidos.
- `temperatura` se convierte internamente a °C y debe estar dentro de \(20\)–\(600\) °C, que es el rango de la tabla 6-5.
- `confiabilidad` se ingresa como fracción, no como porcentaje. Debe estar entre \(0.50\) y \(0.999999\). Internamente se usa tal cual, sin multiplicar por 100.
- \(k_{f,marin}>0\) y finito. No debe confundirse con \(K_f\).
- Los módulos \(E\), \(G\) y la densidad no son necesarios para esta versión. Si se informan, se almacenan pero no se usan en los cálculos.

## 4.9. Cargas

### 4.9.1. Cargas constantes

Todas las cargas que define el usuario son constantes en el tiempo. No existen valores mínimos y máximos, ni parámetros de ciclo, ni casos de carga. Cada fuerza o momento tiene un único valor.

La única fuente de alternancia es la rotación del eje:

- La flexión producida por cargas transversales constantes es completamente alternante en un punto material de la superficie: \(M_a=M_R\), \(M_m=0\).
- El torque constante es medio: \(T_a=0\), \(T_m=T\).
- La carga axial constante es media: \(N_a=0\), \(N_m=N\).

No se admiten cargas variables, pulsantes, completamente invertidas ni periódicas en esta versión. Si el usuario intenta introducirlas, el programa debe rechazar la entrada.

### 4.9.2. Fuerza puntual cartesiana

| Campo | Descripción |
|---|---|
| `nombre` | Identificador |
| `posicion` | Posición longitudinal \(x\) |
| `Fx` | Componente axial |
| `Fy` | Componente vertical |
| `Fz` | Componente horizontal |
| `radio_aplicacion` | Opcional, radio de aplicación |
| `angulo_aplicacion` | Opcional, ángulo de aplicación en grados |

Si `radio_aplicacion=0`, la fuerza se aplica sobre el eje central. Si es mayor que cero, el punto de aplicación es:

\[
r_y=r\cos\theta,\qquad r_z=r\sin\theta
\]

y los momentos equivalentes son:

\[
M_x=r_yF_z-r_zF_y
\]

\[
M_y=r_zF_x
\]

\[
M_z=-r_yF_x
\]

Si `radio_aplicacion>0` y no se informa `angulo_aplicacion`, se adopta \(\theta=0\), es decir, el punto de aplicación sobre \(+Y\).

### 4.9.3. Fuerza radial y tangencial

| Campo | Descripción |
|---|---|
| `nombre` | Identificador |
| `posicion` | Posición longitudinal \(x\) |
| `radio_aplicacion` | Radio \(r_c>0\) |
| `angulo` | Ángulo \(\theta\) en grados |
| `F_radial` | Fuerza radial |
| `F_tangencial` | Fuerza tangencial |
| `F_axial` | Fuerza axial opcional |

Transformación:

\[
F_y=F_r\cos\theta-F_t\sin\theta
\]

\[
F_z=F_r\sin\theta+F_t\cos\theta
\]

\[
F_x=F_a
\]

El torque generado por la fuerza tangencial es:

\[
T=F_t\,r_c
\]

La orientación angular se mide desde \(+Y\) hacia \(+Z\).

### 4.9.4. Momento puntual

| Campo | Descripción |
|---|---|
| `nombre` | Identificador |
| `posicion` | Posición longitudinal \(x\) |
| `Mx` | Torque |
| `My` | Momento flector respecto a \(Y\) |
| `Mz` | Momento flector respecto a \(Z\) |

### 4.9.5. Carga distribuida

| Campo | Descripción |
|---|---|
| `nombre` | Identificador |
| `x_inicio` | Inicio del intervalo |
| `x_fin` | Fin del intervalo |
| `qx` | Intensidad axial |
| `qy` | Intensidad vertical |
| `qz` | Intensidad horizontal |

Reglas:

- \(x_{inicio}<x_{fin}\).
- El intervalo debe estar dentro de \([0,L]\).
- En esta versión las intensidades son constantes. No se admiten cargas distribuidas variables.
- La carga se aplica sobre el eje central y no genera torque ni momentos por excentricidad.

### 4.9.6. Equilibrio torsional

Antes de calcular reacciones se comprueba:

\[
\sum M_x=0
\]

Si no se cumple, se lanza un `ValueError` con el valor del torque desbalanceado y se detiene el programa. No se continúa con una advertencia.

---

# 5. VALIDACIÓN

La validación se ejecuta antes de cualquier cálculo. Se acumulan todos los errores y se lanza un único `ValueError` con la lista completa. Las advertencias no detienen el programa.

## 5.1. Tolerancias

- Geometría: \(1\times10^{-9}\max(L,1)\).
- Equilibrio de fuerzas: \(1\times10^{-8}\max(1,\sum|F|)\).
- Equilibrio de momentos: \(1\times10^{-8}\max(1,\sum|M|,L\sum|F|)\).
- Interpolaciones: no se extrapola; si el valor está fuera del dominio, es error.

## 5.2. Geometría

- \(L>0\) y finita.
- Al menos un tramo.
- Tramos ordenados, contiguos y cubriendo \([0,L]\).
- Diámetros positivos y finitos.
- Escalonamientos en límites de tramos, entre tramos de diámetros distintos.
- \(D\) y \(d\) se deducen de los tramos adyacentes: \(D>d>0\), \(r>0\), \(r\leq(D-d)/2\).
- Radios compatibles con la longitud de los tramos.
- Relaciones \(D/d\) y \(r/d\) dentro de las tablas.
- Sin concentradores solapados.

## 5.3. Apoyos

- Exactamente dos.
- Exactamente uno fijo axial.
- Nombres únicos.
- Anchos positivos.
- Dentro del eje.
- Sin superposición entre apoyos.
- Sin superposición con elementos.
- Sin concentradores ocultos dentro del apoyo.

## 5.4. Elementos

- Dentro del eje.
- Ancho positivo.
- Completamente contenidos en un solo tramo.
- Sin superposición entre elementos.
- Sin superposición con apoyos.
- Si tiene chaveta, no al ras de los extremos.
- Cargas y momentos asociados dentro del elemento.
- Si tiene chaveta: \(a>0\), materiales válidos, \(a<d\).
- La longitud del chavetero no excede \(0.9L_e\).
- El chavetero no contiene escalonamientos, ranuras, apoyos ni chaveteros de otros elementos.
- Si se emite advertencia por \(l>1.5d\), se informa como buena práctica.
- Cada extremo del chavetero está al menos a \(d/10\) del filete de un escalonamiento.

## 5.5. Ranuras

- Posición dentro del eje.
- Si se informa geometría, están los tres valores y son positivos.
- \(d_r>0\).
- Intervalo dentro de un solo tramo.
- Sin superposición con escalonamientos, chaveteros, elementos, apoyos u otras ranuras.

## 5.6. Cargas

- Posiciones dentro del eje.
- Valores finitos.
- Radio de aplicación no negativo.
- Cargas distribuidas con intervalo válido.
- Todas las cargas deben ser constantes. No se admiten valores mínimos/máximos ni casos de carga.

## 5.7. Material

- \(S_{ut}>0\), \(S_y>0\), \(S_{ut}>S_y\).
- Acabado válido.
- Temperatura dentro del rango.
- Confiabilidad dentro del rango.
- \(k_{f,marin}>0\).
- Materiales de chaveta y cubo positivos.
- Advertencia si \(S_{y,chaveta}\geq S_{y,eje}\).

## 5.8. Torque

- \(\sum M_x=0\). Si no, error y detención.

## 5.9. Residuos de equilibrio

Después de calcular reacciones se verifican los seis residuos:

\[
\sum F_x,\quad \sum F_y,\quad \sum F_z,\quad
\sum M_x,\quad \sum M_y,\quad \sum M_z
\]

Si algún residuo supera la tolerancia, se lanza un error con el residuo y las reacciones calculadas.

---

# 6. ORDEN DE EJECUCIÓN

El programa debe respetar este orden:

1. Validar entradas.
2. Dimensionar chavetas y generar chaveteros.
3. Calcular concentradores de esfuerzos.
4. Calcular reacciones.
5. Calcular solicitaciones.
6. Discretizar el eje y construir el conjunto de puntos de evaluación.
7. Calcular esfuerzos nominales, corregidos y Von Mises en todos los puntos.
8. Calcular \(S_e\).
9. Aplicar los criterios de falla.
10. Calcular factores de seguridad locales y globales.
11. Generar el informe.
12. Generar las gráficas de solicitaciones.
13. Generar las gráficas de factores de seguridad.
14. No imprimir nada después de las gráficas de seguridad.

Pseudocódigo:

```text
eje.validar()
chavetas = dimensionar_chavetas(eje)
concentradores = calcular_concentradores(eje, chavetas)
acciones = construir_acciones(eje)
reacciones = calcular_reacciones(eje, acciones)
solicitaciones = calcular_solicitaciones(eje, acciones, reacciones)
puntos = discretizar(eje, solicitaciones, concentradores)
para cada punto:
    esfuerzos[punto] = calcular_esfuerzos(punto, solicitaciones, concentradores, material)
    Se[punto] = calcular_Se(punto, material)
    factores[punto] = aplicar_criterios(esfuerzos[punto], Se[punto], material)
informe(eje, chavetas, concentradores, reacciones, solicitaciones, puntos, factores)
graficar_solicitaciones(...)
graficar_factores_seguridad(...)
```

---

# 7. ETAPA 1: DIMENSIONAMIENTO DE CHAVETAS

Esta etapa se ejecuta antes de calcular los concentradores.

En todas las fórmulas de esta etapa, el factor de seguridad exigido es \(n_{chaveta}\). Si el elemento no informa `n_chaveta`, se usa \(n_{chaveta}=n_{min}\).

## 7.1. Torque transmitido por el elemento

Para cada elemento con `usa_chaveta=True`, se suman algebraicamente los torques externos aplicados dentro de su intervalo axial:

\[
T_e=\left|\sum_{x_i\in[x_e-L_e/2,\;x_e+L_e/2]} M_{x,i}\right|
\]

Incluye:

- Momentos \(M_x\) aplicados directamente.
- Torques generados por fuerzas tangenciales: \(M_x=r_cF_t\).
- Torques generados por fuerzas cartesianas excéntricas: \(M_x=r_yF_z-r_zF_y\).

Si \(T_e=0\):

- No se genera chavetero.
- Se adopta \(m=1\), \(l=0\).
- Se emite una advertencia: el elemento no transmite torque, por lo que no se dimensiona chaveta.

## 7.2. Geometría de la chaveta

\[
b=h=a
\]

\[
t_{eje}=t_{cubo}=\frac{a}{2}
\]

Recomendación:

\[
a\approx\frac{d}{4}
\]

No es obligatoria. Se advierte si \(a/d<0.2\) o \(a/d>0.3\).

## 7.3. Fuerza tangencial

\[
F_t=\frac{2T_e}{d}
\]

donde \(d\) es el diámetro local del elemento.

## 7.4. Verificación por cortante

Área resistente:

\[
A_c=al
\]

Esfuerzo cortante:

\[
\tau_c=\frac{F_t}{al}
\]

Resistencia al cortante:

\[
S_{sy}=0.577\,S_{y,chaveta}
\]

Factor de seguridad:

\[
n_c=\frac{S_{sy}}{\tau_c}
\]

Longitud mínima requerida:

\[
l_c=\frac{2T_e\,n_{chaveta}}{0.577\,d\,a\,S_{y,chaveta}}
\]

## 7.5. Verificación por aplastamiento

Área proyectada:

\[
A_p=\frac{a}{2}l
\]

Esfuerzo de aplastamiento:

\[
\sigma_p=\frac{F_t}{(a/2)l}
\]

Resistencia de contacto:

\[
S_{y,contacto}=\min\left(S_{y,chaveta},S_{y,eje},S_{y,cubo}\right)
\]

Factor de seguridad:

\[
n_p=\frac{S_{y,contacto}}{\sigma_p}
\]

Longitud mínima requerida:

\[
l_p=\frac{4T_e\,n_{chaveta}}{d\,a\,S_{y,contacto}}
\]

## 7.6. Longitud necesaria de una chaveta

\[
l_{req,1}=\max(l_c,l_p)
\]

## 7.7. Longitud máxima admisible

La única cota dura es la fracción del elemento:

\[
l_{max}=0.9L_e
\]

Además, si \(l>1.5d\), se emite una advertencia de buena práctica, porque una chaveta muy larga tiene reparto de carga no uniforme. No se fuerza por ello un aumento de \(m\); solo se advierte.

## 7.8. Cantidad de chavetas

\[
m=\left\lceil\frac{l_{req,1}}{l_{max}}\right\rceil
\]

con \(m\geq1\).

Si \(m\) resulta menor que 1 por \(l_{req,1}=0\), se usa \(m=1\) y \(l=0\).

Se supone reparto uniforme:

\[
T_i=\frac{T_e}{m}
\]

Se repiten las verificaciones con \(T_i\):

\[
l_{c,m}=\frac{2T_i\,n_{chaveta}}{0.577\,d\,a\,S_{y,chaveta}}
\]

\[
l_{p,m}=\frac{4T_i\,n_{chaveta}}{d\,a\,S_{y,contacto}}
\]

\[
l=\max(l_{c,m},l_{p,m})
\]

Se comprueba \(l\leq l_{max}\). Si no se cumple por redondeo numérico, se incrementa \(m\) en 1 y se repite.

## 7.9. Geometría final del chavetero

Para cada elemento se registra:

- Cantidad \(m\).
- Lado \(a\).
- Longitud individual \(l\).
- Longitud del chavetero \(L_k=l\).
- Profundidad del alojamiento \(a/2\).
- Radio del extremo \(r_e=a/2\).
- Radio del filo de fondo \(r_f\) (opcional).
- Centro \(x_e\).
- Intervalo \([x_e-l/2,\;x_e+l/2]\).

Los \(m\) chaveteros tienen el mismo centro y la misma longitud. Se suponen equiespaciados angularmente; el usuario no ingresa ángulos.

## 7.10. Informe de chavetas

Para cada elemento con chaveta se muestra:

1. Torque transmitido \(T_e\).
2. Diámetro local.
3. Lado \(a\).
4. Material de chaveta y cubo.
5. Fuerza tangencial \(F_t\).
6. Área de cortante.
7. Esfuerzo cortante.
8. Resistencia al cortante.
9. Factor de seguridad por cortante.
10. Área proyectada.
11. Esfuerzo de aplastamiento.
12. Resistencia de contacto.
13. Factor de seguridad por aplastamiento.
14. Longitud requerida.
15. Longitud máxima.
16. Cantidad \(m\).
17. Longitud final \(l\).
18. Geometría del chavetero.
19. Factor de seguridad exigido \(n_{chaveta}\).

Se muestran todas las sustituciones numéricas.

---

# 8. ETAPA 2: CONCENTRADORES DE ESFUERZOS

Para cada concentrador se calculan siempre tres factores teóricos:

\[
K_{t,N},\quad K_{t,B},\quad K_{ts}
\]

y tres factores de fatiga:

\[
K_{f,N},\quad K_{f,B},\quad K_{fs}
\]

## 8.1. Sensibilidad a la entalla

\[
q=\frac{1}{1+\sqrt{a/r}}
\]

\[
q_s=\frac{1}{1+\sqrt{a_s/r}}
\]

Las relaciones de Neuber para acero son:

\[
\sqrt a=0.246-3.08(10^{-3})S_{ut}+1.51(10^{-5})S_{ut}^2-2.67(10^{-8})S_{ut}^3
\]

\[
\sqrt{a_s}=0.190-2.51(10^{-3})S_{ut}+1.35(10^{-5})S_{ut}^2-2.67(10^{-8})S_{ut}^3
\]

con \(S_{ut}\) en kpsi, \(\sqrt a\) y \(\sqrt{a_s}\) en \(\sqrt{\mathrm{in}}\), y \(r\) en pulgadas.

Conversiones:

\[
S_{ut}[\mathrm{kpsi}]=\frac{S_{ut}[\mathrm{Pa}]}{6.894757\times10^6}
\]

\[
r[\mathrm{in}]=\frac{r[\mathrm{m}]}{0.0254}
\]

Si \(\sqrt a\) o \(\sqrt{a_s}\) resultan no positivos, el programa lanza un error indicando que \(S_{ut}\) está fuera del rango de validez de Neuber. No se sustituye silenciosamente.

Factores de fatiga:

\[
K_{f,N}=1+q(K_{t,N}-1)
\]

\[
K_{f,B}=1+q(K_{t,B}-1)
\]

\[
K_{fs}=1+q_s(K_{ts}-1)
\]

`q` se usa para axial y flexión. `q_s` se usa para torsión.

## 8.2. Escalonamientos

Geometría obligatoria:

- \(x_s\).
- \(r\).

Los diámetros \(D\) y \(d\) se deducen de los dos tramos adyacentes a \(x_s\):
\(D=\max(d_{izq},d_{der})\) y \(d=\min(d_{izq},d_{der})\). El escalonamiento solo
existe si esos diámetros son distintos.

Relaciones:

\[
\frac{D}{d},\qquad\frac{r}{d}
\]

Factores y ejes reales de cada figura:

| Factor | Figura de Shigley | Eje horizontal | Curvas | Rango de la figura |
|---|---|---|---|---|
| \(K_{t,N}\) | A-15-7 | \(r/d\) | \(D/d=1.02,\ 1.05,\ 1.10,\ 1.50\) | \(r/d\approx0.02\)–\(0.30\) |
| \(K_{ts}\) | A-15-8 | \(r/d\) | \(D/d=1.09,\ 1.20,\ 1.33,\ 2\) | \(r/d\approx0.02\)–\(0.30\) |
| \(K_{t,B}\) | A-15-9 | \(r/d\) | \(D/d=1.02,\ 1.05,\ 1.10,\ 1.50,\ 3\) | \(r/d\approx0.02\)–\(0.30\) |

Las curvas se cargan desde una tabla digitalizada. La interpolación es bilineal lineal en \(r/d\) y \(D/d\). No se extrapola. Si \(r/d\) o \(D/d\) quedan fuera del rango de la figura, se lanza un error indicando el valor y el rango admitido.

Luego:

\[
K_{f,N}=1+q(K_{t,N}-1)
\]

\[
K_{f,B}=1+q(K_{t,B}-1)
\]

\[
K_{fs}=1+q_s(K_{ts}-1)
\]

El escalonamiento se evalúa en \(x_s\). El factor se aplica del lado del diámetro menor. Del lado del diámetro mayor se usa \(K_f=1\).

## 8.3. Ranuras para anillos de retención

### Con geometría informada

Se calculan:

\[
d_r=D_{local}-2t
\]

y las relaciones que usan las figuras A-15-16 y A-15-17:

\[
\frac{a}{t},\qquad\frac{r}{t}
\]

donde \(a\) es el ancho axial de la ranura, \(t\) es su profundidad radial y \(r\) es el radio del filo de fondo. El eje horizontal de ambas figuras es \(a/t\). Las curvas son de \(r/t\). La figura A-15-16 cubre \(r/t=0.03\)–\(1.00\); la figura A-15-17 cubre \(r/t=0.03\)–\(0.20\). No se extrapola.

Factores:

\[
K_{t,N}=K_{t,B}=\text{figura A-15-16}
\]

\[
K_{ts}=\text{figura A-15-17}
\]

La figura A-15-16 se usa para tensión y flexión, y entrega un único valor para ambas. La figura A-15-17 se usa para torsión. Interpolación bilineal en \(a/t\) y \(r/t\); sin extrapolación. Si \(a/t\) o \(r/t\) quedan fuera del rango de la figura, se lanza un error.

Luego se calculan \(q\), \(q_s\) con \(r\) y los \(K_f\).

### Sin geometría informada

\[
K_{t,N}=K_{t,B}=5,\qquad K_{ts}=3
\]

\[
q=q_s=1
\]

\[
K_{f,N}=5,\qquad K_{f,B}=5,\qquad K_{fs}=3
\]

Se advierte que se usaron valores iniciales de la tabla 7-1.

### Aplicación

- Con geometría: la ranura está activa en \([x_r-a/2,\;x_r+a/2]\), con diámetro \(d_r\).
- Sin geometría: la ranura está activa en \(x_r\), con diámetro local \(D_{local}\).

## 8.4. Chaveteros

### Radios

- \(r_e=a/2\): radio del extremo semicircular del chavetero en planta.
- \(r_f\): radio del filo de fondo. Es el que usa Peterson.

### Con \(r_f\) informado y dentro del rango

Se usa Peterson, segunda edición:

- Chart 5.1, página 408, para flexión.
- Chart 5.2, página 409, para torsión.

Para flexión:

\[
K_{t,B,A}=1.6
\]

\[
K_{t,B,B}=1.426+0.1643\left(\frac{0.1}{r_f/d}\right)-0.0019\left(\frac{0.1}{r_f/d}\right)^2
\]

\[
K_{t,B}=\max(K_{t,B,A},K_{t,B,B})
\]

Para torsión:

\[
K_{ts,A}=1.7
\]

\[
K_{ts,B}=1.953+0.1434\left(\frac{0.1}{r_f/d}\right)-0.0021\left(\frac{0.1}{r_f/d}\right)^2
\]

\[
K_{ts}=\max(K_{ts,A},K_{ts,B})
\]

Para carga axial, Peterson no da un factor específico. Se adopta:

\[
K_{t,N}=K_{t,B}
\]

con advertencia explícita de que es una aproximación académica.

Hipótesis geométricas de las gráficas de Peterson:

- Chart 5.1: \(b=d/4\), \(t=d/8\), \(\alpha=10^\circ\), \(h/d=0.125\).
- Chart 5.2: \(b=d/4\), \(t=d/8\), flancos del chavetero a \(50^\circ\).

Estos ángulos son parte de la geometría normalizada de la gráfica y **no son entradas del usuario**. El usuario solo indica a qué elemento corresponde la chaveta. Se supone que la chaveta es cuadrada con \(a\approx d/4\), coherente con \(b=d/4\). Si \(a/d\) se aparta mucho de \(0.25\), se advierte que los valores de Peterson son aproximados.

La línea de trazos de Chart 5.2 corresponde a valores aproximados en el extremo de la chaveta cuando el torque se transmite por una longitud de \(2.5d\). Se usa la curva continua, que es la condición conservadora.

Rangos:

- Flexión: \(0.005\leq r_f/d\leq0.04\).
- Torsión: \(0.005\leq r_f/d\leq0.07\).

Como se necesitan ambos, para usar Peterson se exige:

\[
0.005\leq\frac{r_f}{d}\leq0.04
\]

Luego:

\[
K_{f,N}=1+q(K_{t,N}-1)
\]

\[
K_{f,B}=1+q(K_{t,B}-1)
\]

\[
K_{fs}=1+q_s(K_{ts}-1)
\]

con \(q\) y \(q_s\) calculados con \(r_f\).

### Sin \(r_f\) o fuera de rango

Se usan los valores iniciales de la tabla 7-1 de Shigley:

\[
K_{t,N}=2.14,\qquad K_{t,B}=2.14,\qquad K_{ts}=3.0
\]

Para \(q\) y \(q_s\) se adopta:

\[
\frac{r_f}{d}=0.02
\]

Se calculan \(K_f\) con esos valores. Se advierte:

- Se usaron valores iniciales.
- No se usaron las gráficas de Peterson.
- Si el usuario informó \(r_f\) pero quedó fuera del rango, se indica el valor y el rango admitido.

### Varios chaveteros en el mismo elemento

Si \(m>1\):

\[
K_{t,N,ef}=mK_{t,N}
\]

\[
K_{t,B,ef}=mK_{t,B}
\]

\[
K_{ts,ef}=mK_{ts}
\]

\[
K_{f,N,ef}=1+q(K_{t,N,ef}-1)
\]

\[
K_{f,B,ef}=1+q(K_{t,B,ef}-1)
\]

\[
K_{fs,ef}=1+q_s(K_{ts,ef}-1)
\]

Se advierte que la multiplicación por \(m\) es una aproximación académica y que no se encontró una relación publicada para varios chaveteros simultáneos.

### Aplicación

El chavetero está activo en \([x_e-l/2,\;x_e+l/2]\), pero solo si \(l>0\). Si \(l=0\), no existe concentrador de chavetero y se usan \(K_f=1\). Se usa el diámetro bruto \(d\). No se descuenta la profundidad del chavetero. Se informa esta aproximación.

En rigor, la concentración de chaveteros es máxima en los extremos y en los filos laterales. El modelo 1D aplica el mismo \(K_f\) en todo el intervalo del chavetero. Esto es conservador y debe informarse.

## 8.5. Prohibición de solape

La validación garantiza que, salvo los múltiples chaveteros de un mismo elemento, no hay dos concentradores activos en la misma posición. Por eso no se define una regla de superposición. Si por un error de datos aparecen dos concentradores activos en el mismo punto, se lanza un error.

Además, el extremo de un chavetero debe quedar al menos a \(d/10\) del filete de un escalonamiento. Esta separación evita que ambos concentradores se combinen. Si no se cumple, se lanza un error. La regla proviene de Shigley, sección 7-7.

## 8.6. Resumen por concentrador

Para cada concentrador se almacena y muestra:

- Tipo.
- Posición o intervalo.
- Geometría.
- Relaciones geométricas.
- Figura o tabla usada.
- Método de interpolación.
- \(K_{t,N}\), \(K_{t,B}\), \(K_{ts}\).
- \(q\), \(q_s\).
- \(K_{f,N}\), \(K_{f,B}\), \(K_{fs}\).
- Radio usado.
- Fuente: gráfica de Shigley, tabla 7-1, Peterson o aproximación académica.
- Advertencias.

---

# 9. ETAPA 3: REACCIONES EN LOS APOYOS

## 9.1. Incógnitas

Existen cinco componentes de reacción:

- \(R_{x}\) en el apoyo fijo axial.
- \(R_{Ay}\), \(R_{Az}\) en el apoyo A.
- \(R_{By}\), \(R_{Bz}\) en el apoyo B.

No hay momentos de reacción ni torque de reacción.

## 9.2. Equilibrio

Para el cálculo global, cada carga distribuida se reemplaza por su resultante aplicada en el centro de su intervalo.

Con las cargas constantes:

\[
\sum F_x=0,\qquad \sum F_y=0,\qquad \sum F_z=0
\]

\[
\sum M_x=0,\qquad \sum M_y=0,\qquad \sum M_z=0
\]

La reacción axial se asigna únicamente al apoyo fijo:

\[
R_x=-\sum F_x
\]

Las reacciones radiales se resuelven en los planos \(XY\) y \(XZ\):

\[
R_{Ay}+R_{By}=-\sum F_y
\]

\[
x_A R_{Ay}+x_B R_{By}=-\sum M_z
\]

\[
R_{Az}+R_{Bz}=-\sum F_z
\]

\[
x_A R_{Az}+x_B R_{Bz}=\sum M_y
\]

donde los momentos externos incluyen los momentos de las fuerzas respecto al origen.

## 9.3. Verificación

Se calculan los seis residuos y se comparan con las tolerancias. Si alguno falla, se lanza un error.

## 9.4. Informe de reacciones

Se muestra:

1. Esquema textual del cuerpo libre: posiciones de apoyos, cargas y momentos.
2. Ecuaciones de equilibrio.
3. Sustitución numérica de cada fuerza y momento.
4. Reacciones.
5. Verificación de los seis residuos.

---

# 10. ETAPA 4: SOLICITACIONES INTERNAS

## 10.1. Las ocho funciones

| Función | Descripción |
|---|---|
| \(N(x)\) | Fuerza axial |
| \(V_y(x)\) | Fuerza cortante en Y |
| \(V_z(x)\) | Fuerza cortante en Z |
| \(V_R(x)\) | Fuerza cortante resultante |
| \(M_y(x)\) | Momento flector respecto a Y |
| \(M_z(x)\) | Momento flector respecto a Z |
| \(M_R(x)\) | Momento flector resultante |
| \(T(x)\) | Momento torsor |

Resultantes:

\[
V_R(x)=\sqrt{V_y(x)^2+V_z(x)^2}
\]

\[
M_R(x)=\sqrt{M_y(x)^2+M_z(x)^2}
\]

## 10.2. Convenio de signos

Se usa el equilibrio del segmento izquierdo. Para una sección en \(x\), con acciones externas en \(x_i<x\):

\[
N(x)=-\sum F_{x,i}-\int_0^x q_x(s)\,ds
\]

\[
V_y(x)=-\sum F_{y,i}-\int_0^x q_y(s)\,ds
\]

\[
V_z(x)=-\sum F_{z,i}-\int_0^x q_z(s)\,ds
\]

\[
M_y(x)=-\sum M_{y,i}-\sum (x-x_i)F_{z,i}-\int_0^x (x-s)q_z(s)\,ds
\]

\[
M_z(x)=-\sum M_{z,i}+\sum (x-x_i)F_{y,i}+\int_0^x (x-s)q_y(s)\,ds
\]

\[
T(x)=-\sum M_{x,i}
\]

Las reacciones se incluyen como acciones externas.

## 10.3. Discontinuidades

- Una fuerza concentrada produce un salto en \(V_y\), \(V_z\), \(V_R\) y \(N\).
- Un momento concentrado produce un salto en \(M_y\), \(M_z\), \(M_R\).
- Un torque concentrado produce un salto en \(T\).
- Una carga distribuida introduce términos lineales y cuadráticos en su intervalo.
- En \(x=x_i\), la acción se incluye para \(x\geq x_i\) y se excluye para \(x<x_i\).

El programa debe evaluar ambos lados:

\[
x^-,\qquad x^+
\]

## 10.4. Expresiones por tramos

Se construyen expresiones `Piecewise` agrupadas por función, no por tramo. El informe muestra:

\[
N(x)=\begin{cases}N_1(x),&0\leq x<x_1\\N_2(x),&x_1\leq x<x_2\\\vdots\end{cases}
\]

y lo mismo para las otras siete funciones.

## 10.5. Cálculo para cargas constantes

Las ocho funciones se calculan una sola vez. No hay estados de carga ni valores mínimos y máximos. La alternancia de la flexión proviene de la rotación del eje, no de la variación temporal de las cargas.

---

# 11. ETAPA 5: DISCRETIZACIÓN Y PUNTOS DE EVALUACIÓN

## 11.1. Malla uniforme

\[
N_{div}\geq1
\]

\[
\Delta x=\frac{L}{N_{div}}
\]

\[
x_i=i\Delta x,\qquad i=0,1,\ldots,N_{div}
\]

La malla incluye exactamente \(0\) y \(L\).

## 11.2. Puntos críticos

Se agregan:

1. Extremos de cada tramo.
2. Posiciones de escalonamientos, con lados \(x^-\) y \(x^+\).
3. Posiciones de apoyos, con lados \(x^-\) y \(x^+\).
4. Posiciones de fuerzas y momentos, con lados \(x^-\) y \(x^+\).
5. Extremos de cargas distribuidas, con lados \(x^-\) y \(x^+\).
6. Extremos de chaveteros, con lados \(x^-\) y \(x^+\).
7. Centros de chaveteros.
8. Extremos de ranuras, con lados \(x^-\) y \(x^+\).
9. Centros de ranuras.
10. Puntos interiores donde alguna solicitación tenga máximo o mínimo.
11. Mínimos locales de los factores de seguridad dentro de cada intervalo continuo.

## 11.3. Extremos interiores de solicitaciones

Dentro de cada intervalo continuo:

- \(V_y\), \(V_z\), \(N\), \(T\): extremos en los bordes o donde su derivada se anule.
- \(M_y\): derivada \(V_z\). Extremos donde \(V_z=0\).
- \(M_z\): derivada \(-V_y\). Extremos donde \(V_y=0\).
- \(M_R\): extremos donde \(M_yV_z-M_zV_y=0\).
- \(V_R\): extremos donde \(V_yq_y+V_zq_z=0\).

Se resuelven las raíces dentro de cada intervalo y se agregan las que pertenezcan al intervalo.

## 11.4. Mínimos locales de factores de seguridad

Después de calcular los factores de seguridad en la malla y en los puntos críticos, se busca el mínimo local dentro de cada intervalo continuo con un método de optimización acotada (por ejemplo, búsqueda dorada). Se agrega el minimizador a los puntos de evaluación. La tolerancia es \(10^{-6}L\).

## 11.5. Puntos duplicados y lados

- Se eliminan duplicados exactos de misma posición y mismo lado.
- Se conservan \(x^-\) y \(x^+\) cuando hay discontinuidad.
- Los puntos se ordenan por \(x\) y luego por lado.
- Cada punto almacena: \(x\), lado, tramo, diámetro, concentrador activo, tipo de discontinuidad.

## 11.6. Diámetro local

- Dentro de un tramo: \(d\) del tramo.
- En un escalonamiento: \(d\) del tramo izquierdo para \(x^-\), \(d\) del tramo derecho para \(x^+\).
- Dentro de una ranura: \(d_r=D-2t\).
- En el borde de una ranura: \(d_r\) del lado interior, \(D\) del lado exterior.
- Dentro de un chavetero: diámetro bruto \(d\) del tramo.
- En el borde de un chavetero: el concentrador está activo del lado interior y no está activo del lado exterior.

## 11.7. Concentrador activo

- Escalonamiento: activo solamente en \(x_s\), del lado del diámetro menor.
- Ranura: activa en \([x_r-a/2,\;x_r+a/2]\), con \(d_r\).
- Chavetero: activo en \([x_e-l/2,\;x_e+l/2]\), con \(d\).
- Sin concentrador: \(K_{f,N}=K_{f,B}=K_{fs}=1\).
- Varios chaveteros del mismo elemento: se usa el concentrador efectivo con \(m\).

La validación garantiza que no hay dos tipos distintos activos en el mismo punto.

---

# 12. ETAPA 6: ESFUERZOS NOMINALES

Para cada punto de evaluación se determina \(d\) y se calculan:

\[
A=\frac{\pi d^2}{4}
\]

\[
I=\frac{\pi d^4}{64}
\]

\[
J=\frac{\pi d^4}{32}
\]

\[
c=\frac{d}{2}
\]

## 12.1. Momento flector alternante y medio

Como el eje siempre gira y las cargas son constantes:

\[
M_a=M_R
\]

\[
M_m=0
\]

## 12.2. Carga axial alternante y media

Como la carga axial es constante:

\[
N_a=0
\]

\[
N_m=N(x)
\]

\(N_m\) conserva signo.

## 12.3. Torque alternante y medio

Como el torque es constante:

\[
T_a=0
\]

\[
T_m=T(x)
\]

\(T_m\) conserva signo.

## 12.4. Componentes nominales

Esfuerzo normal axial:

\[
\sigma_{N,a}=\frac{4N_a}{\pi d^2}
\]

\[
\sigma_{N,m}=\frac{4N_m}{\pi d^2}
\]

Esfuerzo normal por flexión:

\[
\sigma_{B,a}=\frac{32M_a}{\pi d^3}
\]

\[
\sigma_{B,m}=0
\]

Esfuerzo cortante por torsión:

\[
\tau_{T,a}=\frac{16T_a}{\pi d^3}
\]

\[
\tau_{T,m}=\frac{16T_m}{\pi d^3}
\]

## 12.5. Signos

- \(\sigma_{B,a}\) es una magnitud positiva: la flexión giratoria es completamente alternante.
- \(\sigma_{N,m}\) conserva el signo de la carga axial media.
- \(\tau_{T,m}\) conserva el signo del torque medio.
- Para el Von Mises las componentes se elevan al cuadrado, por lo que el signo de \(\sigma_{B,a}\) no se usa.
- Para fluencia se evalúan los dos extremos del ciclo normal.

---

# 13. ETAPA 7: ESFUERZOS CORREGIDOS

## 13.1. Factores activos

En cada punto se usan los factores del concentrador activo. Si no hay concentrador:

\[
K_{f,N}=K_{f,B}=K_{fs}=1
\]

## 13.2. Esfuerzos corregidos

\[
\sigma_a=K_{f,B}\sigma_{B,a}+K_{f,N}\sigma_{N,a}
\]

\[
\sigma_m=K_{f,B}\sigma_{B,m}+K_{f,N}\sigma_{N,m}
\]

\[
\tau_a=K_{fs}\tau_{T,a}
\]

\[
\tau_m=K_{fs}\tau_{T,m}
\]

Como \(\sigma_{B,m}=0\):

\[
\sigma_m=K_{f,N}\sigma_{N,m}
\]

## 13.3. Aclaración sobre \(K_t\) y \(K_f\)

Los factores \(K_t\) son teóricos y elásticos. Los factores \(K_f\) son los que se usan para estimar la tensión local en el procedimiento de ejes de Shigley.

**Tanto la fatiga como la fluencia usan \(K_f\), \(K_{f,N}\), \(K_{f,B}\) y \(K_{fs}\).** No se calcula un segundo juego de tensiones con \(K_t\). \(K_t\) se muestra en el informe y se usa solamente para obtener \(K_f\).

Esto coincide con las ecuaciones (7-3) a (7-6) y (7-15) de Shigley.

Se aplican \(K_f\) y \(K_{fs}\) también a las componentes medias. Shigley señala que, para materiales dúctiles, a veces se omiten en la media por la capacidad de fluencia local. Aplicarlos es conservador y así se adopta en este programa.

---

# 14. ETAPA 8: VON MISES ALTERNANTE Y MEDIO

## 14.1. Von Mises alternante

\[
\sigma'_a=
\sqrt{
\left(
K_{f,B}\sigma_{B,a}
+
\frac{K_{f,N}\sigma_{N,a}}{0.85}
\right)^2
+
3\left(K_{fs}\tau_{T,a}\right)^2
}
\]

El divisor \(0.85\) es la corrección de Shigley para carga axial alternante. No es un factor de concentración.

## 14.2. Von Mises medio

\[
\sigma'_m=
\sqrt{
\left(
K_{f,B}\sigma_{B,m}
+
K_{f,N}\sigma_{N,m}
\right)^2
+
3\left(K_{fs}\tau_{T,m}\right)^2
}
\]

## 14.3. Observaciones

- El divisor \(0.85\) no se aplica a la componente media.
- El divisor \(0.85\) no se aplica a la verificación de fluencia.
- \(\sigma'_m\) es no negativo. Si la carga axial media es compresiva, el signo se pierde al elevar al cuadrado. Esto es conservador y debe indicarse.
- El programa evalúa ambos lados de la sección cuando corresponda y conserva la condición más desfavorable.

---

# 15. ETAPA 9: LÍMITE DE FATIGA CORREGIDO

## 15.1. Límite de la probeta

\[
S_e'=0.5S_{ut}
\]

para \(S_{ut}\leq1400\) MPa.

Para \(S_{ut}>1400\) MPa:

\[
S_e'=700\ \text{MPa}
\]

Si \(S_e'\leq0\), se lanza un error.

## 15.2. Factores de Marin

\[
S_e=k_a\,k_b\,k_c\,k_d\,k_e\,k_{f,marin}\,S_e'
\]

### Acabado superficial \(k_a\)

\[
k_a=a\,S_{ut}^{b}
\]

Se usa la tabla 6-2 de Shigley. Internamente se usa la columna SI, con \(S_{ut}\) en MPa:

| Acabado superficial | \(a\) para \(S_{ut}\) en MPa | \(b\) |
|---|---:|---:|
| Esmerilado | 1.58 | -0.085 |
| Maquinado o laminado en frío | 4.51 | -0.265 |
| Laminado en caliente | 57.7 | -0.718 |
| Como sale de la forja | 272 | -0.995 |

La columna inglesa de la tabla original, con \(S_{ut}\) en kpsi, es:

| Acabado superficial | \(a\) para \(S_{ut}\) en kpsi | \(b\) |
|---|---:|---:|
| Esmerilado | 1.34 | -0.085 |
| Maquinado o laminado en frío | 2.70 | -0.265 |
| Laminado en caliente | 14.4 | -0.718 |
| Como sale de la forja | 39.9 | -0.995 |

El programa convierte \(S_{ut}\) a MPa y usa la tabla SI. La tabla 6-2 no declara por sí misma un rango de \(S_{ut}\); el ajuste se usa para todo \(S_{ut}>0\). Si se reemplaza la tabla por otra que declare un rango válido, se respeta y se lanza un error fuera de él.

### Tamaño \(k_b\)

Para el eje giratorio, con \(d\) en mm:

\[
k_b=1.24\,d^{-0.107}
\]

para \(2.79\leq d\leq51\) mm.

\[
k_b=1.51\,d^{-0.157}
\]

para \(51<d\leq254\) mm.

Las expresiones equivalentes en pulgadas son:

\[
k_b=0.879\,d^{-0.107}
\]

para \(0.11\leq d\leq2\) in.

\[
k_b=0.91\,d^{-0.157}
\]

para \(2<d\leq10\) in.

Como internamente todo está en SI, se usan las expresiones en mm. Si \(d<2.79\) mm o \(d>254\) mm, se lanza un error. No se extrapola.

### Carga \(k_c\)

Para la combinación de flexión, torsión y carga axial resuelta con Von Mises, se adopta:

\[
k_c=1
\]

Los valores \(0.85\) para axial pura y \(0.59\) para torsión pura que aparecen en la tabla de Shigley no se aplican a este caso combinado. La corrección de carga axial alternante se realiza con el divisor \(0.85\) de la ecuación de Von Mises alternante, no con \(k_c\).

### Temperatura \(k_d\)

\[
k_d=\frac{S_T}{S_{RT}}
\]

se obtiene de la tabla 6-5 de Shigley. Internamente se usa la columna en °C:

| Temperatura [°C] | \(k_d\) |
|---:|---:|
| 20 | 1.000 |
| 50 | 1.010 |
| 100 | 1.020 |
| 150 | 1.025 |
| 200 | 1.020 |
| 250 | 1.000 |
| 300 | 0.975 |
| 350 | 0.943 |
| 400 | 0.900 |
| 450 | 0.843 |
| 500 | 0.768 |
| 550 | 0.672 |
| 600 | 0.549 |

La tabla original en °F es:

| Temperatura [°F] | \(k_d\) |
|---:|---:|
| 70 | 1.000 |
| 100 | 1.008 |
| 200 | 1.020 |
| 300 | 1.024 |
| 400 | 1.018 |
| 500 | 0.995 |
| 600 | 0.963 |
| 700 | 0.927 |
| 800 | 0.872 |
| 900 | 0.797 |
| 1000 | 0.698 |
| 1100 | 0.567 |

Si el usuario ingresa °F, se convierte a °C y se usa la tabla en °C. Se interpola linealmente en temperatura. Si la temperatura está fuera de \(20\)–\(600\) °C, se lanza un error.

### Confiabilidad \(k_e\)

La confiabilidad se ingresa como fracción \(R\), con \(0.50\leq R\leq0.999999\). Se usa la tabla 6-4 de Shigley:

| Confiabilidad [%] | \(R\) | \(k_e\) |
|---:|---:|---:|
| 50 | 0.50 | 1.000 |
| 90 | 0.90 | 0.897 |
| 95 | 0.95 | 0.868 |
| 99 | 0.99 | 0.814 |
| 99.9 | 0.999 | 0.753 |
| 99.99 | 0.9999 | 0.702 |
| 99.999 | 0.99999 | 0.659 |
| 99.9999 | 0.999999 | 0.620 |

Se interpola linealmente en \(R\). Si \(R\) está fuera del rango, se lanza un error. La interpolación lineal en \(R\) es una aproximación; la tabla solo define los valores listados y el informe lo indica.

### Efectos diversos \(k_{f,marin}\)

\[
k_{f,marin}
\]

es una entrada opcional del usuario, con valor inicial 1. Debe ser positivo y finito. No debe confundirse con \(K_f\).

## 15.3. Cálculo por sección

\(S_e\) se calcula para cada punto de evaluación porque \(k_b\) depende del diámetro local. Los demás factores son constantes para el material.

## 15.4. Informe

Se muestran por separado:

- \(S_e'\).
- \(k_a\) con \(a\), \(b\), \(S_{ut}\).
- \(k_b\) con \(d\).
- \(k_c\).
- \(k_d\).
- \(k_e\).
- \(k_{f,marin}\).
- \(S_e\).

---

# 16. ETAPA 10: CRITERIOS DE FATIGA

## 16.1. Interfaz de criterio

Cada criterio de fatiga es una función independiente:

```text
factor_seguridad(sigma_a, sigma_m, Se, Sut, Sy) -> n
```

El programa mantiene un registro de criterios. Agregar un criterio nuevo consiste en agregar su función y registrarla. No se modifican geometría, chavetas, concentradores, reacciones, solicitaciones, esfuerzos, discretización ni Marin.

## 16.2. Goodman modificado

\[
\frac{1}{n_f}=\frac{\sigma'_a}{S_e}+\frac{\sigma'_m}{S_{ut}}
\]

\[
n_f=\frac{1}{\frac{\sigma'_a}{S_e}+\frac{\sigma'_m}{S_{ut}}}
\]

Si el denominador es cero, \(n_f=\infty\).

Si \(S_e\leq0\) o \(S_{ut}\leq0\), el punto es no verificable y se informa como error, nunca como aprobado.

## 16.3. Criterios futuros

La misma interfaz permite agregar:

**Gerber:**

\[
\frac{\sigma'_a}{S_e}+\left(\frac{\sigma'_m}{S_{ut}}\right)^2=\frac{1}{n}
\]

**Soderberg:**

\[
\frac{\sigma'_a}{S_e}+\frac{\sigma'_m}{S_y}=\frac{1}{n}
\]

**ASME elíptico:**

\[
\left(\frac{n\sigma'_a}{S_e}\right)^2+\left(\frac{n\sigma'_m}{S_y}\right)^2=1
\]

No son obligatorios en esta versión.

## 16.4. Criterio de fluencia como criterio registrado

La fluencia se implementa como otro criterio del mismo registro, para que genere su propia gráfica y participe del mínimo general. Recibe \(\sigma'_{max}\) y \(S_y\).

---

# 17. ETAPA 11: VERIFICACIÓN CONTRA FLUENCIA

Se usa el procedimiento de Shigley para ejes. Se usan \(K_{f,N}\), \(K_{f,B}\) y \(K_{fs}\). **No se usan \(K_t\) directamente.**

## 17.1. Esfuerzo normal máximo

Sean:

\[
S_B=K_{f,B}\sigma_{B,a}
\]

\[
S_{Nm}=K_{f,N}\sigma_{N,m}
\]

\[
S_{Na}=K_{f,N}\sigma_{N,a}
\]

Se evalúan los dos extremos del ciclo normal:

\[
\sigma_{x,1}=S_B+S_{Nm}+S_{Na}
\]

\[
\sigma_{x,2}=-S_B+S_{Nm}-S_{Na}
\]

Se toma el de mayor valor absoluto:

\[
\sigma_{x,max}=\max\left(|\sigma_{x,1}|,|\sigma_{x,2}|\right)
\]

El signo se conserva para el informe. Para el Von Mises se eleva al cuadrado.

No se usa el divisor \(0.85\).

## 17.2. Esfuerzo cortante máximo

\[
\tau_{x,max}=K_{fs}\left(|\tau_{T,m}|+\tau_{T,a}\right)
\]

## 17.3. Von Mises máximo

\[
\sigma'_{max}=\sqrt{\sigma_{x,max}^2+3\tau_{x,max}^2}
\]

También se muestra la estimación conservadora de Shigley:

\[
\sigma'_{max,cons}=\sigma'_a+\sigma'_m
\]

El informe distingue entre el máximo del ciclo proporcional y la estimación conservadora.

## 17.4. Factor de seguridad

\[
n_y=\frac{S_y}{\sigma'_{max}}
\]

Si \(\sigma'_{max}=0\), \(n_y=\infty\).

Condición de aceptación:

\[
n_y\geq n_{min}
\]

---

# 18. ETAPA 12: FACTOR DE SEGURIDAD GENERAL

Para cada punto:

\[
n_{local}(x)=\min\left(n_f(x),n_y(x),\ldots\right)
\]

incluyendo todos los criterios registrados.

Para el eje:

\[
n_{eje}=\min_{x\in[0,L]}n_{local}(x)
\]

Se identifica:

- Valor mínimo.
- Posición.
- Criterio que gobierna.
- Si cumple \(n_{eje}\geq n_{min}\).

Además, se verifica cada chaveta:

\[
n_c\geq n_{chaveta}
\]

\[
n_p\geq n_{chaveta}
\]

El eje se considera aceptado solamente si se cumplen todas las verificaciones del eje y de las chavetas.

Si algún punto es no verificable, el resultado general es **no verificable**, nunca aprobado.

---

# 19. INFORME DE CÁLCULO

El informe se muestra por consola, en español, con texto claro y tablas cuando sea útil. No se imprimen los cálculos de los 1000 puntos de la malla. Se imprimen completos los cálculos de todos los puntos críticos.

En todos los apartados, cada magnitud se presenta con su fórmula, la sustitución numérica y el resultado en las unidades del usuario. Esto incluye chavetas, concentradores, reacciones, solicitaciones, esfuerzos, Marin y criterios de falla.

## 19.1. Orden del informe

1. Resumen de entradas.
2. Validaciones y advertencias.
3. Dimensionamiento de chavetas.
4. Concentradores de esfuerzos.
5. Reacciones.
6. Solicitaciones internas.
7. Procedimiento detallado en cada punto crítico.
8. Resumen final.

## 19.2. Resumen de entradas

Incluye:

- Longitud.
- Tramos y diámetros.
- Escalonamientos.
- Apoyos.
- Elementos.
- Chavetas.
- Ranuras.
- Material y propiedades.
- Cargas y momentos.
- \(n_{min}\).
- \(N_{div}\).

## 19.3. Validaciones

Se muestra cada comprobación y su resultado. Los errores se distinguen de las advertencias.

## 19.4. Chavetas

Se muestra lo indicado en la sección 7.10, para cada elemento.

## 19.5. Concentradores

Se muestra lo indicado en la sección 8.6, para cada concentrador.

## 19.6. Reacciones

Se muestra lo indicado en la sección 9.4.

## 19.7. Solicitaciones

Se muestran las ocho funciones por tramos, agrupadas por función:

\[
N,\ V_y,\ V_z,\ V_R,\ M_y,\ M_z,\ M_R,\ T
\]

Se muestran los valores en todos los puntos críticos.

## 19.8. Punto crítico

Para cada punto crítico se muestra un apartado con:

### A. Identificación geométrica

- Posición \(x\).
- Lado \(x^-\) o \(x^+\).
- Tramo.
- Diámetro local.
- Tipo de discontinuidad.
- Radio de redondeo.
- Concentrador activo.

### B. Solicitaciones

- \(N\), \(V_y\), \(V_z\), \(V_R\).
- \(M_y\), \(M_z\), \(M_R\), \(T\).
- Valores medios y alternantes usados: \(M_a=M_R\), \(M_m=0\), \(N_a=0\), \(N_m=N\), \(T_a=0\), \(T_m=T\).

### C. Factores de concentración

- \(K_{t,N}\), \(K_{t,B}\), \(K_{ts}\).
- \(q\), \(q_s\).
- \(K_{f,N}\), \(K_{f,B}\), \(K_{fs}\).
- Fuente y advertencias.
- Aclaración de que \(K_t\) se muestra como resultado intermedio y que los esfuerzos usan \(K_f\).

### D. Esfuerzos nominales

- \(\sigma_{N,a}\), \(\sigma_{N,m}\).
- \(\sigma_{B,a}\), \(\sigma_{B,m}\).
- \(\tau_{T,a}\), \(\tau_{T,m}\).

### E. Esfuerzos corregidos

- \(\sigma_a\), \(\sigma_m\), \(\tau_a\), \(\tau_m\).

### F. Von Mises

- \(\sigma'_a\) con sustitución.
- \(\sigma'_m\) con sustitución.

### G. Resistencia a fatiga

- \(S_e'\).
- \(k_a\), \(k_b\), \(k_c\), \(k_d\), \(k_e\), \(k_{f,marin}\).
- \(S_e\).

### H. Factor de seguridad a fatiga

- Sustitución de Goodman modificado.
- \(n_f\).

### I. Fluencia

- \(\sigma_{x,max}\).
- \(\tau_{x,max}\).
- \(\sigma'_{max}\).
- \(\sigma'_{max,cons}\).
- \(n_y\).

### J. Resultado de la sección

- \(n_f\).
- \(n_y\).
- Criterio gobernante.
- Cumplimiento o incumplimiento.

## 19.9. Resumen final

Incluye:

- Mínimo \(n_f\) y posición.
- Mínimo \(n_y\) y posición.
- \(n_{eje}\) y posición crítica.
- Criterio que gobierna.
- Cumplimiento de \(n_{min}\).
- Resultado de cada chaveta.
- Lista de advertencias y aproximaciones.

---

# 20. GRÁFICAS

## 20.1. Gráficas de solicitaciones

Se generan las ocho funciones en una grilla de 2 filas por 4 columnas. Cada gráfica muestra:

- Posición longitudinal \(x\).
- Valor de la solicitación.
- Longitud del eje.
- Posición de apoyos.
- Posición de elementos.
- Escalonamientos.
- Chaveteros.
- Ranuras.
- Valores relevantes.

## 20.2. Gráficas de factores de seguridad

Se genera una gráfica independiente por cada criterio registrado. Inicialmente:

1. Goodman modificado: \(n_f(x)\).
2. Fluencia: \(n_y(x)\).

Cada gráfica muestra:

- Eje horizontal: \(x\).
- Eje vertical: factor de seguridad.
- Curva del criterio.
- Línea horizontal \(n_{min}\).
- Mínimo y posición.
- Concentradores existentes.
- Puntos de la malla y puntos críticos.

## 20.3. Discontinuidades

Los saltos se representan sin conectar valores de lados distintos. Se usan segmentos separados o `NaN`.

## 20.4. Valores infinitos

Si un factor es infinito:

- Se conserva el valor exacto en los datos.
- Para la gráfica se limita a un valor máximo legible.
- Se anota “∞” o el valor exacto.

## 20.5. Orden final

Las gráficas de factores de seguridad son la última salida. No se imprime ni se muestra nada después.

---

# 21. ARQUITECTURA

## 21.1. Módulos

| Módulo | Responsabilidad |
|---|---|
| `modelo/` | Dataclasses y validación estructural |
| `modelo/tramo.py` | Tramos |
| `modelo/escalonamiento.py` | Escalonamientos |
| `modelo/apoyo.py` | Apoyos |
| `modelo/elemento.py` | Elementos y chavetas |
| `modelo/ranura.py` | Ranuras |
| `modelo/carga.py` | Fuerzas y cargas distribuidas |
| `modelo/momento.py` | Momentos |
| `modelo/material.py` | Material y datos de Marin |
| `calculos/geometria.py` | Diámetro local, intervalos, lados |
| `calculos/validacion.py` | Validaciones |
| `calculos/chavetas.py` | Dimensionamiento de chavetas |
| `calculos/concentradores.py` | \(K_t\), \(q\), \(K_f\) |
| `calculos/reacciones.py` | Reacciones |
| `calculos/solicitaciones.py` | Ocho funciones |
| `calculos/discretizacion.py` | Malla y puntos críticos |
| `calculos/esfuerzos.py` | Esfuerzos nominales y corregidos |
| `calculos/marin.py` | \(S_e\) |
| `calculos/criterios.py` | Registro de criterios |
| `calculos/fatiga.py` | Goodman |
| `calculos/fluencia.py` | Von Mises máximo |
| `datos/` | Tablas digitalizadas |
| `datos/concentradores.py` | Curvas de Shigley A-15-7/8/9/16/17 |
| `datos/marin.py` | Tablas 6-2, 6-4 y 6-5 |
| `salidas/informe.py` | Informe por consola |
| `salidas/diagramas_solicitaciones.py` | 8 diagramas |
| `salidas/diagramas_seguridad.py` | Gráficas de factores |

## 21.2. Separación de responsabilidades

- `modelo/`: datos y validación estructural. Sin cálculos mecánicos.
- `calculos/`: cálculos en SI. Sin impresión.
- `salidas/`: conversión a unidades de usuario, texto y gráficas.
- `datos/`: tablas y coeficientes. Sin lógica de cálculo.

## 21.3. Reutilización

- Los concentradores se calculan una vez.
- Las reacciones se calculan una vez.
- Las solicitaciones se calculan una vez.
- Los esfuerzos se calculan una vez por punto.
- Los criterios usan los esfuerzos ya calculados.
- Las gráficas usan los arrays almacenados.

## 21.4. Estilo

- Identificadores, docstrings, mensajes y salida en español.
- Indentación de 2 espacios.
- Sin reformatear a 4 espacios.
- Usar «solicitaciones» para \(N,V,M,T\).
- Reservar «esfuerzos» para tensiones.

---

# 22. MANEJO DE ERRORES NUMÉRICOS

El programa debe controlar:

- Divisiones entre cero.
- Diámetros inválidos.
- Raíces no definidas.
- Interpolaciones fuera de rango.
- Factores no finitos.
- Resistencias inválidas.
- Funciones discontinuas.
- Puntos duplicados o mal ordenados.
- Torque desbalanceado.
- Residuos de equilibrio fuera de tolerancia.

Reglas:

- No se sustituye silenciosamente un cálculo inválido por un valor arbitrario.
- Si un punto no se puede calcular, se marca como **no verificable**.
- Un resultado no verificable nunca se considera aprobado.
- Los errores de entrada se acumulan y se informan juntos.
- Los errores de cálculo se lanzan con un mensaje que indique la magnitud, la posición y el valor.

---

# 23. DATOS EXTERNOS REQUERIDOS

El agente debe cargar estos datos desde `datos/`. No debe inventar valores.

## 23.1. Figuras de Shigley para escalonamientos

- A-15-7: \(K_{t,N}\), eje \(r/d\), curvas \(D/d\).
- A-15-8: \(K_{ts}\), eje \(r/d\), curvas \(D/d\).
- A-15-9: \(K_{t,B}\), eje \(r/d\), curvas \(D/d\).

Formato:

```python
TABLA_HOMBROS = {
  "A-15-7": {
    "variable_x": "r/d",
    "variable_curva": "D/d",
    "x_min": 0.02,
    "x_max": 0.30,
    "curvas": {
      1.02: [(0.02, ...), (0.03, ...), (0.05, ...), (0.10, ...), (0.20, ...), (0.30, ...)],
      1.05: [...],
      ...
    }
  },
  ...
}
```

Los valores entre paréntesis son puntos de la curva digitalizada y **deben leerse de la figura entregada**. No se copian de este ejemplo. Cada curva debe estar ordenada por `r/d` y declarar `x_min` y `x_max`. La interpolación es bilineal lineal en \(r/d\) dentro de cada curva y lineal en \(D/d\) entre curvas. Si \(D/d\) o \(r/d\) están fuera del rango, error.

Rangos de las figuras:

| Figura | Curvas \(D/d\) disponibles |
|---|---|
| A-15-7 | 1.02, 1.05, 1.10, 1.50 |
| A-15-8 | 1.09, 1.20, 1.33, 2 |
| A-15-9 | 1.02, 1.05, 1.10, 1.50, 3 |

## 23.2. Figuras de Shigley para ranuras

- A-15-16: \(K_{t,N}=K_{t,B}\), eje \(a/t\), curvas \(r/t\).
- A-15-17: \(K_{ts}\), eje \(a/t\), curvas \(r/t\).

Requisitos de la tabla:

- `variable_x = "a/t"`, con \(0.5\leq a/t\leq6.0\).
- `variable_curva = "r/t"`.
- A-15-16: curvas \(r/t=0.03,\ 0.04,\ 0.05,\ 0.07,\ 0.10,\ 0.15,\ 0.20,\ 0.40,\ 0.60,\ 1.00\).
- A-15-17: curvas \(r/t=0.03,\ 0.04,\ 0.06,\ 0.10,\ 0.20\).
- Las curvas inferiores no existen para \(a/t\) pequeños. Por ejemplo, la curva \(r/t=1.00\) de A-15-16 comienza recién en \(a/t\approx0.65\), y la curva \(r/t=0.20\) de A-15-17 comienza en \(a/t\approx1.0\). Cada curva debe declarar su propio intervalo válido de \(a/t\).
- Fuera del dominio declarado por cada curva, error. No se interpola hacia una región sin curva.

## 23.3. Tabla 7-1 de Shigley

Valores iniciales:

| Concentrador | \(K_{t,N}\) | \(K_{t,B}\) | \(K_{ts}\) | \(q\) | \(q_s\) |
|---|---|---|---|---|---|
| Chavetero | 2.14 | 2.14 | 3.0 | calcular con \(r_f/d=0.02\) | calcular con \(r_f/d=0.02\) |
| Ranura | 5 | 5 | 3 | 1 | 1 |

## 23.4. Tablas de Marin

Los valores exactos ya están transcriptos en la sección 15.2 y provienen de los archivos entregados:

- `recursos/Marin_Ka.png`: tabla 6-2, acabado superficial, con \(a\) y \(b\) en kpsi y en MPa.
- `recursos/Marin_Kb.png`: ecuación (6-20), tamaño, en pulgadas y en mm.
- `recursos/Marin_Kc.png`: factor de carga \(k_c\).
- `recursos/Marin_Kd.png`: tabla de temperatura, con columnas en °C y en °F.
- `recursos/Marin_Ke.png`: tabla de confiabilidad, con \(z_a\) y \(k_e\).

El módulo `datos/marin.py` debe contener estas tablas tal como están en la sección 15.2. No se inventan valores ni se extrapola fuera de los rangos declarados.

## 23.5. Figuras y fórmulas de concentradores

Los archivos entregados son:

- `recursos/FiguraA-15-7.png`, `FiguraA-15-8.png`, `FiguraA-15-9.png`: hombros.
- `recursos/FiguraA-15-16.png`, `FiguraA-15-17.png`: ranuras.
- `recursos/Chart5.1.png`, `Chart5.2.png`: chaveteros.

La digitalización de las curvas debe hacerse en `datos/concentradores.py`. Las fórmulas de Peterson para chaveteros ya están cerradas en la sección 8.4 y no requieren digitalizar las gráficas.

## 23.6. Fórmulas de Peterson para chaveteros

No requieren tabla. Están en la sección 8.4.

---

# 24. CRITERIOS DE ACEPTACIÓN

El programa cumple cuando:

1. Permite definir un eje con tramos de distintos diámetros.
2. Valida geometría, apoyos, elementos, ranuras, chavetas, cargas y material.
3. Dimensiona chavetas por cortante y aplastamiento.
4. Determina cantidad y longitud de chavetas.
5. Genera la geometría de los chaveteros.
6. Calcula \(K_{t,N}\), \(K_{t,B}\), \(K_{ts}\) para todos los concentradores.
7. Calcula \(q\), \(q_s\), \(K_{f,N}\), \(K_{f,B}\), \(K_{fs}\).
8. Calcula reacciones y verifica equilibrio.
9. Calcula las ocho solicitaciones.
10. Discretiza el eje y agrega puntos críticos.
11. Calcula esfuerzos nominales y corregidos.
12. Calcula Von Mises alternante y medio.
13. Calcula \(S_e\) con Marin.
14. Calcula \(n_f\) por Goodman y \(n_y\) por fluencia.
15. Identifica el mínimo y su posición.
16. Genera el informe completo para todos los puntos críticos.
17. Genera las ocho gráficas de solicitaciones.
18. Genera una gráfica de factor de seguridad por criterio.
19. Permite agregar criterios sin modificar los módulos mecánicos.
20. No imprime nada después de las gráficas de seguridad.

---

# 25. REFERENCIAS ESPECÍFICAS

| Procedimiento | Referencia |
|---|---|
| Esfuerzo axial | Shigley, capítulo 3, sección 3-9 |
| Esfuerzo de flexión | Shigley, capítulo 3, sección 3-10 |
| Esfuerzo de torsión | Shigley, capítulo 3, sección 3-12 |
| Sensibilidad a la entalla \(q\), \(q_s\) | Shigley, ecuaciones (6-32), (6-33) y (6-34) |
| Constantes de Neuber \(\sqrt a\), \(\sqrt{a_s}\) | Shigley, ecuaciones (6-35a) y (6-35b), figura 6-21 |
| \(K_{t,N}\) en hombros | Shigley, figura A-15-7, eje \(r/d\), curvas \(D/d\) |
| \(K_{ts}\) en hombros | Shigley, figura A-15-8, eje \(r/d\), curvas \(D/d\) |
| \(K_{t,B}\) en hombros | Shigley, figura A-15-9, eje \(r/d\), curvas \(D/d\) |
| \(K_{t,N}=K_{t,B}\) en ranuras | Shigley, figura A-15-16, eje \(a/t\), curvas \(r/t\) (Peterson, 3.ª ed., p. 115) |
| \(K_{ts}\) en ranuras | Shigley, figura A-15-17, eje \(a/t\), curvas \(r/t\) (Peterson, 3.ª ed., p. 133) |
| Estimaciones iniciales | Shigley, tabla 7-1 |
| Chaveteros por flexión | Peterson, 2.ª ed., Chart 5.1, p. 408 |
| Chaveteros por torsión | Peterson, 2.ª ed., Chart 5.2, p. 409 |
| Geometría de chavetas | Shigley, sección 7-7, tabla 7-6 |
| Resistencia de chavetas | Shigley, ejemplo 7-6 |
| Límite de fatiga | Shigley, sección 6-7 |
| Factores de Marin | Shigley, sección 6-9, tablas 6-2, 6-4 y 6-5 |
| Goodman modificado | Shigley, ecuación (6-46) |
| Combinación axial, flexión y torsión | Shigley, ecuaciones (6-55) y (6-56) |
| Esfuerzos alternante y medio en ejes | Shigley, ecuaciones (7-3), (7-4), (7-5) y (7-6) |
| Fluencia en ejes | Shigley, ecuaciones (7-15) y (7-16) |
| Confiabilidad \(k_e\) | Shigley, tabla 6-4 |
| Temperatura \(k_d\) | Shigley, tabla 6-5 |
| Acabado superficial \(k_a\) | Shigley, tabla 6-2 |
