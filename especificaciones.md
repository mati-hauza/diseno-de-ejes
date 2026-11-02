# PROGRAMA PARA EL ANÁLISIS Y DISEÑO DE EJES
## Especificación funcional y técnica — Versión 1.0

**Objetivo:** desarrollar un programa en Python que permita modelar, analizar y dimensionar ejes mecánicos, siguiendo los fundamentos y procedimientos de diseño de ejes presentados en *Diseño en ingeniería mecánica*, de Shigley.

El programa debe ser modular, extensible y educativo. No debe limitarse a entregar resultados finales: debe mostrar las acciones, ecuaciones, iteraciones, factores y comprobaciones que conducen al diseño.

---

# 1. ALCANCE GENERAL

## 1.1. Funciones principales

El programa tendrá las siguientes capacidades:

1. Definir un eje y su sistema de unidades.
2. Definir dos apoyos.
3. Definir elementos montados sobre el eje.
4. Definir cargas puntuales y distribuidas.
5. Definir concentradores de esfuerzos.
6. Definir el material del eje.
7. Calcular las reacciones en los apoyos.
8. Calcular las solicitaciones internas.
9. Obtener las funciones y diagramas de fuerzas, momentos y torque.
10. Calcular los diámetros ideales necesarios para cumplir un factor de seguridad.
11. Construir una geometría de eje escalonada.
12. Comprobar las concentraciones de esfuerzos.
13. Ajustar iterativamente los diámetros cuando sea necesario.
14. Normalizar los diámetros.
15. Verificar el diseño final.
16. Presentar gráficas, ecuaciones, tablas y resultados intermedios.

## 1.2. Limitaciones iniciales

La primera versión tendrá las siguientes restricciones:

- Ejes circulares macizos.
- Materiales de acero.
- Exactamente dos apoyos.
- Uno de los dos apoyos será fijo axialmente y el otro permitirá desplazamiento axial.
- Cargas estáticas en el espacio.
- Eje considerado horizontal.
- Se supondrá que el eje gira.
- La geometría del eje será escalonada.
- Los escalonamientos aumentarán de diámetro desde los extremos hacia la zona central.
- El dimensionamiento se realizará considerando fatiga y fluencia.
- Se permitirá obtener un diseño automático o verificar un diseño introducido manualmente.

No se implementarán inicialmente ejes huecos, materiales distintos del acero, análisis dinámico de cargas, vibraciones, velocidad crítica ni deformaciones como criterios de dimensionamiento.

Estas funciones podrán incorporarse posteriormente sin modificar la estructura fundamental del programa.

---

# 2. CONVENCIONES GENERALES

## 2.1. Sistema de coordenadas

El sistema de coordenadas será:

- X: dirección longitudinal del eje.
- Y: dirección vertical.
- Z: dirección transversal horizontal.

Se utilizará un sistema de mano derecha:

\[
\vec X\times\vec Y=\vec Z
\]

El eje se extenderá desde \(x=0\) hasta \(x=L\).

Se considerará que la gravedad actúa en dirección negativa de Y:

\[
\vec g=(0,-g,0)
\]

## 2.2. Sistemas de unidades

El usuario podrá elegir entre:

- Sistema Internacional (SI).
- Sistema inglés (US).

Las entradas y salidas se presentarán en el sistema seleccionado.

Para evitar errores de conversión, el programa trabajará internamente con unidades SI coherentes:

- Longitud: m.
- Fuerza: N.
- Momento: N·m.
- Esfuerzo: Pa.
- Módulo de elasticidad: Pa.
- Densidad: kg/m³.

En la presentación se podrán utilizar unidades de ingeniería más cómodas:

| Magnitud | SI | Inglés |
|---|---|---|
| Longitud | mm | in |
| Fuerza | N | lbf |
| Momento | N·mm | lbf·in |
| Esfuerzo | MPa | ksi |
| Módulo elástico | GPa | ksi |
| Densidad | kg/m³ | lb/in³ |

Todas las conversiones se realizarán en los límites de entrada y salida. No se mezclarán unidades dentro de los cálculos.

---

# 3. MODELO DEL EJE

## 3.1. Definición

El eje tendrá:

- Nombre opcional.
- Longitud total.
- Sistema de unidades.
- Dos apoyos.
- Una colección de elementos montados.
- Una colección de cargas independientes.
- Una colección de concentradores independientes.
- Una colección de secciones geométricas.
- Un material.
- Una configuración de diseño.

La longitud debe ser positiva.

## 3.2. Apoyos

Existirán exactamente dos apoyos.

Cada apoyo tendrá:

- Nombre.
- Posición longitudinal.
- Ancho.
- Condición axial.

La posición representa el centro del apoyo.

Por lo tanto, sus límites serán:

\[
x_{\text{inicio}}=x_c-\frac{w}{2}
\]

\[
x_{\text{final}}=x_c+\frac{w}{2}
\]

Uno de los apoyos deberá tener:

\[
\text{fijo\_axial}=\text{True}
\]

El otro deberá tener:

\[
\text{fijo\_axial}=\text{False}
\]

### Modelo mecánico de los apoyos

Los apoyos se considerarán ideales:

- Ambos pueden producir reacciones en Y.
- Ambos pueden producir reacciones en Z.
- Solamente el apoyo fijo puede producir reacción axial en X.
- Ninguno puede resistir momentos flectores.
- Ninguno puede proporcionar un momento torsor de reacción.

Las reacciones radiales se considerarán aplicadas en el centro longitudinal del apoyo.

El ancho del apoyo se utilizará en la geometría y en las comprobaciones de montaje, pero no para distribuir la reacción radial.

No se modelarán inicialmente apoyos empotrados ni rodamientos capaces de transmitir momentos.

---

# 4. ELEMENTOS MONTADOS SOBRE EL EJE

## 4.1. Definición de un elemento

Los elementos podrán representar:

- Engranajes.
- Poleas.
- Piñones.
- Acoplamientos.
- Ruedas.
- Otros componentes montados sobre el eje.

Cada elemento tendrá:

- Nombre.
- Posición longitudinal.
- Ancho.
- Masa opcional.
- Cargas asociadas.
- Concentradores asociados.
- Información de retención axial.

La posición representará el centro longitudinal del elemento.

Sus límites físicos serán:

\[
x_{\text{inicio}}=x_c-\frac{w}{2}
\]

\[
x_{\text{final}}=x_c+\frac{w}{2}
\]

No se introducirá inicialmente un diámetro de montaje.

El diámetro correspondiente al asiento será calculado por el programa.

## 4.2. Masa de los elementos

La masa podrá introducirse opcionalmente.

Si se proporciona, el programa calculará automáticamente su peso:

\[
W=mg
\]

El peso se considerará aplicado en el centro del elemento y dirigido hacia \(-Y\).

## 4.3. Retención axial

Un elemento montado sobre el eje debe tener una forma de retención axial.

En esta primera versión se utilizará principalmente el siguiente mecanismo:

- Escalonamiento en el lado interior.
- Ranura y anillo de retención en el lado exterior.

El anillo tendrá un ancho que se añadirá al espacio axial ocupado por el conjunto.

La ausencia de una retención necesaria deberá generar una advertencia o un error de validación, según la configuración del elemento.

---

# 5. MODELO GEOMÉTRICO DEL EJE

## 5.1. Secciones cilíndricas

El eje final estará compuesto por secciones cilíndricas de diámetro constante, conectadas mediante escalonamientos.

Cada sección tendrá:

- Posición inicial.
- Posición final.
- Longitud.
- Diámetro.
- Elemento o apoyo asociado, si corresponde.
- Concentradores asociados.

Las secciones no se limitarán a las zonas ocupadas por elementos y apoyos. También existirán secciones correspondientes a los espacios libres entre ellos y a los extremos del eje.

La geometría final será una sucesión de secciones con diferentes diámetros.

## 5.2. Orientación de los escalonamientos

Se establecerá como regla constructiva que los diámetros aumenten desde los extremos hacia el centro geométrico del eje.

El centro geométrico será:

\[
x_c=\frac{L}{2}
\]

Para los elementos ubicados a la izquierda del centro:

- El escalonamiento de apoyo estará en el lado derecho del elemento.
- La retención axial estará en el lado izquierdo.

Para los elementos ubicados a la derecha:

- El escalonamiento de apoyo estará en el lado izquierdo.
- La retención axial estará en el lado derecho.

Un elemento cuyo centro coincida exactamente con el centro del eje necesitará una orientación definida explícitamente.

## 5.3. Anillos de retención

Los anillos ocuparán un ancho axial adicional.

Para un elemento situado a la izquierda del centro:

\[
x_{\text{anillo}}=
\left[
x_{\text{inicio}}-w_{\text{anillo}},
x_{\text{inicio}}
\right]
\]

Para un elemento situado a la derecha:

\[
x_{\text{anillo}}=
\left[
x_{\text{final}},
x_{\text{final}}+w_{\text{anillo}}
\right]
\]

El anillo se ubicará en el extremo opuesto al escalonamiento que soporta el elemento.

La ranura correspondiente será un concentrador geométrico.

## 5.4. Validaciones geométricas

El programa deberá comprobar:

- Ningún elemento debe salir de los límites del eje.
- Ningún apoyo debe salir de los límites del eje.
- No deben existir superposiciones no permitidas.
- Debe existir espacio suficiente para los anillos.
- Debe existir espacio suficiente para los escalonamientos y radios de redondeo.
- Ningún elemento deberá quedar al ras de un extremo.
- Todas las longitudes deben ser positivas.
- Los escalonamientos deben respetar la orientación constructiva.
- No deben superponerse ranuras, redondeos u otros concentradores.

Cuando la geometría no sea viable, el programa no deberá producir silenciosamente un diseño inválido. Deberá informar cuál es el conflicto y dónde ocurre.

---

# 6. MODELO DE CARGAS

El programa permitirá introducir cargas asociadas a elementos y cargas independientes.

Todas las cargas se expresarán respecto del sistema de coordenadas global.

## 6.1. Fuerzas puntuales

Se podrán introducir:

### Fuerza axial

\[
\vec F=(F_x,0,0)
\]

Actúa longitudinalmente.

### Fuerzas radiales

\[
\vec F=(0,F_y,F_z)
\]

Actúan en el plano transversal.

Podrán introducirse directamente mediante componentes cartesianas o mediante magnitud y dirección.

### Fuerza tangencial

Se permitirá introducir:

- Magnitud.
- Radio de aplicación.
- Dirección o ángulo.
- Posición longitudinal.

El momento torsor generado será:

\[
T_x=(\vec r\times\vec F)_x
\]

Para una fuerza perfectamente tangencial:

\[
|T_x|=F_t r
\]

El signo dependerá de la dirección de giro.

## 6.2. Momentos puntuales

Se podrán introducir momentos aplicados directamente alrededor de los tres ejes:

\[
\vec M=(M_x,M_y,M_z)
\]

Su interpretación será:

- \(M_x\): momento torsor.
- \(M_y\): momento flector respecto de Y.
- \(M_z\): momento flector respecto de Z.

Esto permitirá introducir momentos que no procedan de una fuerza tangencial.

## 6.3. Posición de aplicación

Una carga podrá aplicarse:

- En el centro del elemento al que pertenece.
- En otra posición longitudinal especificada.
- En una posición independiente de cualquier elemento.

El programa validará que las posiciones estén dentro de los límites del eje.

## 6.4. Cargas distribuidas

Se podrán introducir cargas distribuidas sobre un intervalo:

\[
x\in[a,b]
\]

En la primera versión se admitirán:

- Distribución uniforme.
- Distribución linealmente variable.

Se permitirán componentes distribuidas en X, Y y Z:

\[
\vec q(x)=
(q_x(x),q_y(x),q_z(x))
\]

Las unidades serán fuerza por unidad de longitud.

El programa calculará sus resultantes y momentos equivalentes para obtener las reacciones y las solicitaciones internas.

Se mantendrá el intervalo original de aplicación para construir correctamente los diagramas.

No se implementarán inicialmente distribuciones arbitrarias definidas por el usuario mediante funciones Python.

## 6.5. Peso propio del eje

El peso propio podrá activarse o desactivarse.

Cuando esté activado, el programa calculará una carga distribuida dependiente de la geometría y del material:

\[
q_g(x)=-\rho A(x)g
\]

Para un eje circular macizo:

\[
A(x)=\frac{\pi d(x)^2}{4}
\]

La carga tendrá dirección negativa de Y.

Como el diámetro todavía es desconocido durante el dimensionamiento inicial, el peso propio se incorporará mediante un proceso iterativo:

1. Calcular un diseño inicial sin peso propio del eje.
2. Obtener una geometría preliminar.
3. Calcular el peso propio de esa geometría.
4. Recalcular reacciones y diagramas.
5. Volver a dimensionar.
6. Repetir hasta alcanzar convergencia.

El peso de los elementos montados se incorporará independientemente mediante sus masas.

---

# 7. CÁLCULO DE REACCIONES

El programa calculará las reacciones utilizando las ecuaciones de equilibrio estático.

Se resolverán separadamente los planos correspondientes a Y y Z, además de la condición de equilibrio axial.

## 7.1. Equilibrio de fuerzas

\[
\sum F_x=0
\]

\[
\sum F_y=0
\]

\[
\sum F_z=0
\]

## 7.2. Equilibrio de momentos

\[
\sum M_x=0
\]

\[
\sum M_y=0
\]

\[
\sum M_z=0
\]

Se considerarán:

- Cargas puntuales.
- Cargas distribuidas.
- Momentos aplicados.
- Peso propio del eje, cuando esté activado.
- Peso de los elementos.
- Posiciones reales de los apoyos.

## 7.3. Resultados

Se mostrarán las reacciones:

\[
R_{Ax},R_{Ay},R_{Az}
\]

\[
R_{Bx},R_{By},R_{Bz}
\]

El apoyo móvil axial tendrá:

\[
R_{Ax}=0
\]

o:

\[
R_{Bx}=0
\]

según cuál sea el apoyo fijo.

Se mostrarán también los residuos de las ecuaciones de equilibrio.

Si las cargas aplicadas generan un momento torsor externo resultante distinto de cero, el programa informará que el sistema no está equilibrado torsionalmente. Los apoyos ideales no proporcionarán una reacción torsional artificial.

---

# 8. SOLICITACIONES INTERNAS Y DIAGRAMAS

## 8.1. Magnitudes internas

El programa calculará:

- Fuerza axial \(N(x)\).
- Fuerza cortante \(V_y(x)\).
- Fuerza cortante \(V_z(x)\).
- Momento torsor \(T_x(x)\).
- Momento flector \(M_y(x)\).
- Momento flector \(M_z(x)\).

También podrá calcular la magnitud del momento flector resultante:

\[
M_f(x)=\sqrt{M_y(x)^2+M_z(x)^2}
\]

## 8.2. Convención de signos

Para que las funciones y diagramas sean coherentes, se establecerá una única convención.

Las solicitaciones internas en una sección serán las acciones que equilibran las cargas externas situadas a la izquierda del corte.

De esta forma:

\[
\vec F_{\text{int}}(x)=
-\sum \vec F_{\text{ext,izquierda}}
\]

Los momentos internos se calcularán tomando momentos respecto de la sección de corte:

\[
\vec M_{\text{int}}(x)=
-\sum
\left[
(\vec r_i-\vec r_x)\times\vec F_i
+\vec M_i
\right]
\]

Las cargas distribuidas se integrarán sobre el intervalo correspondiente.

Esta definición será la referencia para todas las funciones, cálculos y gráficas. No se cambiarán signos de forma independiente en diferentes módulos.

## 8.3. Funciones por tramos

Las funciones se representarán por tramos.

Cada discontinuidad deberá generar los intervalos correspondientes.

Se considerarán especialmente:

- Posiciones de fuerzas puntuales.
- Posiciones de momentos aplicados.
- Inicio y final de cargas distribuidas.
- Posiciones de las reacciones.
- Extremos del eje.

Las funciones deberán poder evaluarse en cualquier posición válida.

## 8.4. Diagramas

Se generarán:

- Diagrama de fuerza axial.
- Diagramas de fuerzas cortantes en Y y Z.
- Diagrama de momento torsor.
- Diagramas de momentos flectores en Y y Z.
- Diagrama del momento flector resultante.

Las gráficas deberán respetar exactamente las funciones matemáticas y sus convenciones de signo.

En los puntos de discontinuidad se representarán correctamente los límites por izquierda y derecha.

---

# 9. LOCALIZACIÓN DE PUNTOS CRÍTICOS

No se dimensionará únicamente en los concentradores.

El programa evaluará:

1. Una discretización configurable a lo largo del eje.
2. Los extremos de cada tramo.
3. Las posiciones de cargas puntuales.
4. Las posiciones de discontinuidad.
5. Los puntos de aplicación de momentos.
6. Las posiciones de todos los concentradores.
7. Las raíces de las derivadas de los diagramas cuando puedan determinarse analíticamente.

Esto permitirá detectar máximos de solicitaciones que no coincidan con un concentrador ni con un punto de la malla.

En discontinuidades se evaluarán ambos lados:

\[
x^-,\quad x^+
\]

La discretización será configurable, pero nunca sustituirá la evaluación obligatoria de los puntos especiales.

---

# 10. MATERIAL

## 10.1. Tipos de material

La primera versión aceptará exclusivamente aceros.

Se permitirá seleccionar un material de una biblioteca interna o introducir sus propiedades manualmente.

## 10.2. Propiedades

El material incluirá:

- Resistencia última a la tracción \(S_{ut}\).
- Límite de fluencia \(S_y\).
- Módulo de elasticidad \(E\).
- Módulo de rigidez \(G\).
- Densidad \(\rho\).

Podrán añadirse propiedades adicionales cuando sean necesarias.

## 10.3. Límite de resistencia a la fatiga de probeta

El usuario no introducirá directamente \(S'_e\).

Se calculará mediante las aproximaciones de Shigley para aceros:

En SI:

\[
S'_e=
\begin{cases}
0.5S_{ut},&S_{ut}\leq1400\text{ MPa}\\
700\text{ MPa},&S_{ut}>1400\text{ MPa}
\end{cases}
\]

En sistema inglés:

\[
S'_e=
\begin{cases}
0.5S_{ut},&S_{ut}\leq200\text{ ksi}\\
100\text{ ksi},&S_{ut}>200\text{ ksi}
\end{cases}
\]

Las unidades se manejarán internamente en SI.

## 10.4. Factores de Marin

El límite de resistencia a la fatiga del elemento se calculará mediante:

\[
S_e=k_a k_b k_c k_d k_e k_f S'_e
\]

Se implementarán los factores:

- \(k_a\): acabado superficial.
- \(k_b\): tamaño.
- \(k_c\): tipo de carga.
- \(k_d\): temperatura.
- \(k_e\): confiabilidad.
- \(k_f\): efectos diversos.

Los factores dependerán de la configuración del diseño.

El factor de tamaño se recalculará cuando cambie el diámetro.

Las ecuaciones y rangos de validez se documentarán en el código y deberán corresponder a las relaciones adoptadas de Shigley.

Para evitar confusiones de nomenclatura, los factores de Marin se distinguirán de los factores de concentración de esfuerzos.

---

# 11. CONCENTRADORES DE ESFUERZOS

## 11.1. Tipos iniciales

Se implementarán:

1. Escalonamientos con radio de redondeo.
2. Chaveteros.
3. Ranuras para anillos de retención.

Se dejará preparada la estructura para incorporar otros tipos posteriormente.

## 11.2. Propiedades de un concentrador

Cada concentrador incluirá:

- Tipo.
- Posición.
- Dimensiones geométricas.
- Diámetros de referencia, cuando corresponda.
- Radio de redondeo, cuando corresponda.
- Método de cálculo.
- Factores resultantes.

Podrá pertenecer a un elemento, a un apoyo o existir independientemente.

## 11.3. Concentración teórica

Se calcularán los factores teóricos:

\[
K_t
\]

\[
K_{ts}
\]

Según el tipo de solicitación y la geometría.

En los escalonamientos:

\[
K_t=f\left(\frac{D}{d},\frac{r}{d}\right)
\]

\[
K_{ts}=f\left(\frac{D}{d},\frac{r}{d}\right)
\]

Los valores se obtendrán mediante las ecuaciones, tablas o gráficas correspondientes de Shigley.

Cuando se utilicen tablas o gráficas discretas, se permitirá interpolar dentro de sus intervalos válidos. No se extrapolarán valores silenciosamente.

## 11.4. Sensibilidad a la entalla

Para fatiga se calcularán los factores:

\[
K_f=1+q(K_t-1)
\]

\[
K_{fs}=1+q_s(K_{ts}-1)
\]

Donde \(q\) y \(q_s\) representan la sensibilidad a la entalla.

Se calcularán a partir del material y de la geometría de la entalla, de acuerdo con el método seleccionado de Shigley.

Se distinguirán los factores de concentración para esfuerzos normales y cortantes.

## 11.5. Concentradores superpuestos

No se multiplicarán factores de concentración de manera arbitraria.

En la primera versión, dos concentradores cuyos campos geométricos se superpongan no podrán tratarse como independientes sin un método de combinación justificado.

Si existe una superposición no admitida, el programa informará del conflicto.

---

# 12. CÁLCULO DE ESFUERZOS

La sección será circular maciza.

Sus propiedades geométricas serán:

\[
A=\frac{\pi d^2}{4}
\]

\[
I=\frac{\pi d^4}{64}
\]

\[
J=\frac{\pi d^4}{32}
\]

## 12.1. Esfuerzo axial

\[
\sigma_N=\frac{N}{A}
\]

## 12.2. Esfuerzo de flexión

\[
\sigma_b=\frac{M_f c}{I}
\]

Para una sección circular:

\[
\sigma_b=\frac{32M_f}{\pi d^3}
\]

## 12.3. Esfuerzo cortante torsional

\[
\tau_t=\frac{Tc}{J}
\]

Para una sección circular:

\[
\tau_t=\frac{16T}{\pi d^3}
\]

Las concentraciones correspondientes se aplicarán según la geometría y el tipo de esfuerzo.

En la primera versión, el diseño por fatiga considerará los esfuerzos normales producidos por carga axial y flexión, además de los esfuerzos cortantes producidos por torsión.

Las fuerzas cortantes transversales se utilizarán para calcular los diagramas y momentos flectores. No se incluirá inicialmente su distribución local de esfuerzo en el criterio de fatiga de la superficie del eje.

---

# 13. FATIGA Y FLUENCIA

## 13.1. Suposición de funcionamiento

Se supondrá que el eje gira y que las cargas son constantes en el espacio.

Por lo tanto:

- La flexión producida por cargas transversales será completamente alternante en un punto material de la superficie.
- La carga axial constante producirá esfuerzo normal medio.
- El torque constante producirá esfuerzo cortante medio.

Para la primera versión no se modelarán espectros de carga, fases arbitrarias, impactos ni ciclos variables introducidos por el usuario.

## 13.2. Esfuerzos alternantes y medios

Los esfuerzos normales y cortantes se separarán en componentes alternantes y medias.

A partir de ellos se calcularán:

\[
\sigma'_a=
\sqrt{\sigma_a^2+3\tau_a^2}
\]

\[
\sigma'_m=
\sqrt{\sigma_m^2+3\tau_m^2}
\]

Estas magnitudes serán las equivalentes de Von Mises para los componentes alternante y medio.

No se supondrá que los esfuerzos medios sean cero.

## 13.3. Criterios de fatiga

Se implementarán como criterios independientes:

### Goodman modificado

\[
\frac{1}{n_G}=
\frac{\sigma'_a}{S_e}
+
\frac{\sigma'_m}{S_{ut}}
\]

### Soderberg

\[
\frac{1}{n_S}=
\frac{\sigma'_a}{S_e}
+
\frac{\sigma'_m}{S_y}
\]

### Gerber

Se resolverá la ecuación:

\[
\left(\frac{n\sigma'_m}{S_{ut}}\right)^2
+
\frac{n\sigma'_a}{S_e}
=1
\]

Se tomará la raíz positiva físicamente válida.

Los criterios se podrán activar o desactivar independientemente.

## 13.4. Fluencia

Se calculará el esfuerzo equivalente máximo instantáneo.

Para la hipótesis de carga estática espacial sobre eje giratorio:

\[
\sigma_{VM,\max}=
\sqrt{
\left(|\sigma_m|+\sigma_a\right)^2
+
3\tau_m^2
}
\]

En esta primera versión, el torque y la carga axial constantes se consideran medios, mientras que la flexión alternante determina la variación cíclica.

El factor de seguridad a fluencia será:

\[
n_y=\frac{S_y}{\sigma_{VM,\max}}
\]

## 13.5. Factor de seguridad de diseño

El programa obtendrá todos los factores de seguridad activos.

El factor global será:

\[
n_{\min}=\min(n_1,n_2,\ldots,n_y)
\]

El diseño será válido cuando:

\[
n_{\min}\geq n_{\text{objetivo}}
\]

No se exigirá que todos los factores de seguridad sean iguales al objetivo.

Bastará con que ninguno quede por debajo de él.

---

# 14. DIMENSIONAMIENTO DEL DIÁMETRO IDEAL

Esta etapa determinará el diámetro mínimo necesario en cada posición antes de construir la geometría escalonada.

## 14.1. Discretización

Se utilizará una discretización configurable del eje.

Además de los puntos de la malla, se incluirán todos los puntos especiales definidos anteriormente.

El objetivo es obtener el diámetro requerido a lo largo de todo el eje, no solamente en los concentradores.

## 14.2. Cálculo en un punto

Para cada posición:

1. Obtener las solicitaciones internas.
2. Identificar los concentradores presentes.
3. Determinar sus factores de concentración.
4. Proponer un diámetro inicial.
5. Calcular las propiedades geométricas.
6. Calcular los esfuerzos.
7. Calcular los factores de Marin.
8. Calcular los factores de seguridad.
9. Comparar con el factor objetivo.
10. Ajustar el diámetro hasta cumplir.

El diámetro ideal será:

\[
d_{\text{ideal}}(x)
\]

Será el menor diámetro que satisfaga todos los criterios activos para esa posición.

En los puntos sin concentradores:

\[
K_t=K_{ts}=K_f=K_{fs}=1
\]

En los puntos con chaveteros y ranuras se aplicarán sus respectivos factores.

Los escalonamientos se tratarán en una etapa posterior, porque todavía no se conocen sus dos diámetros definitivos.

## 14.3. Resolución numérica

Como el factor de tamaño depende del diámetro, no se podrá calcular el diámetro requerido mediante una única sustitución directa.

Se utilizará un método iterativo de búsqueda numérica.

El resultado deberá cumplir:

\[
n_{\min}(d,x)\geq n_{\text{objetivo}}
\]

y un diámetro ligeramente menor deberá dejar de cumplir, dentro de la tolerancia numérica establecida.

## 14.4. Resultado preliminar

Se obtendrá una curva de diámetro ideal en función de X.

Esta curva representa una envolvente de resistencia requerida.

No representa todavía el perfil físico definitivo del eje.

---

# 15. ASIGNACIÓN DE DIÁMETROS A LAS SECCIONES

Después de calcular los diámetros ideales, se determinará el diámetro preliminar de cada sección geométrica.

Para la sección \(i\):

\[
d_{i,0}=
\max_{x\in \text{sección }i}
d_{\text{ideal}}(x)
\]

Esto asegura que el diámetro inicial de cada sección sea suficiente para todos los puntos que contiene.

El programa no utilizará el diámetro de un solo punto representativo.

También deberá considerar los puntos especiales y los límites de sección.

El resultado será una colección de diámetros preliminares:

\[
d_{1,0},d_{2,0},\ldots,d_{m,0}
\]

---

# 16. CUMPLIMIENTO DE LAS RELACIONES GEOMÉTRICAS

## 16.1. Relación entre diámetros

Para cada escalonamiento se definirán:

- \(D\): diámetro mayor.
- \(d\): diámetro menor.

La relación mínima de diseño será:

\[
\frac{D}{d}\geq C_D
\]

Donde \(C_D\) será un parámetro configurable.

Es importante distinguir esta condición geométrica de la verificación de esfuerzos.

Cumplir la relación no garantiza que el escalonamiento sea resistente.

## 16.2. Propagación de diámetros hacia el centro

Para los tramos del lado izquierdo se recorrerán las secciones desde el extremo izquierdo hacia el centro.

Cuando una sección interior no cumpla:

\[
d_{\text{interior}}\geq C_Dd_{\text{exterior}}
\]

se aumentará su diámetro hasta cumplir la condición.

En el lado derecho se realizará el mismo procedimiento recorriendo desde el extremo derecho hacia el centro.

Si existe una sección central compartida, deberá satisfacer las condiciones provenientes de ambos lados.

En esta etapa nunca se reducirá un diámetro preliminar.

Este procedimiento es determinista y permite propagar los aumentos hacia la zona central sin modificar innecesariamente las secciones exteriores.

## 16.3. Radio de redondeo

Se utilizará una relación mínima:

\[
\frac{r}{d}\geq C_r
\]

El radio inicial será:

\[
r=C_rd
\]

salvo que se especifique un radio mayor.

Se comprobará que el radio sea geométricamente viable y no interfiera con otras secciones, ranuras o elementos.

Los factores de concentración del escalonamiento se calcularán utilizando los valores geométricos reales.

---

# 17. VERIFICACIÓN DE ESCALONAMIENTOS

Una vez obtenidos los diámetros preliminares corregidos, se calcularán los factores de concentración correspondientes a cada escalonamiento.

Para cada escalonamiento se conocerán:

\[
D,\quad d,\quad r
\]

Con ellos se obtendrán:

\[
K_t,\quad K_{ts},\quad K_f,\quad K_{fs}
\]

Se evaluarán los esfuerzos en la zona crítica del escalonamiento, considerando el diámetro menor y los factores de concentración correspondientes.

Se comprobarán todos los criterios de fatiga y fluencia.

El programa deberá revisar ambos lados de las transiciones cuando las condiciones locales lo requieran.

---

# 18. CORRECCIÓN ITERATIVA DEL DISEÑO

Esta etapa debe ser estable y reproducible.

No se aumentarán diámetros arbitrariamente según cuál escalonamiento falle.

## 18.1. Escalamiento global inicial

Se partirá de la geometría que cumple los diámetros preliminares y las relaciones geométricas.

Se definirá un multiplicador:

\[
\lambda\geq1
\]

Y se calcularán:

\[
d_i(\lambda)=\lambda d_{i,0}
\]

Los radios de redondeo definidos mediante relaciones geométricas también se actualizarán:

\[
r_j(\lambda)=\lambda r_{j,0}
\]

De esta manera se conservan las relaciones \(D/d\) y \(r/d\) de los escalonamientos.

Los factores geométricos se recalcularán si alguna dimensión relativa cambia, por ejemplo en concentradores definidos mediante dimensiones absolutas.

## 18.2. Búsqueda del multiplicador

Se buscará el menor multiplicador que permita cumplir:

\[
n_{\min}(\lambda)\geq n_{\text{objetivo}}
\]

Se utilizará una búsqueda acotada:

1. Iniciar con \(\lambda=1\).
2. Verificar todos los puntos y concentradores.
3. Aumentar \(\lambda\) hasta encontrar una geometría que cumpla.
4. Una vez encontrado un intervalo válido, aplicar bisección.
5. Detenerse cuando se alcance la tolerancia establecida.

Esta solución no pretende minimizar el volumen del eje. Es un procedimiento inicial conservador y reproducible que evita correcciones locales desordenadas.

Si las restricciones geométricas impiden obtener una solución válida, el programa deberá informar que el diseño no es viable bajo las condiciones introducidas.

## 18.3. Verificación general

Después de cada modificación:

- Se recalcularán las propiedades de las secciones.
- Se recalcularán los factores de Marin.
- Se recalcularán los factores de concentración.
- Se recalcularán los esfuerzos.
- Se recalcularán todos los factores de seguridad.

No bastará con comprobar solamente el escalonamiento que produjo el fallo.

Los cambios en una sección pueden afectar los dos escalonamientos que la delimitan.

---

# 19. NORMALIZACIÓN DE DIÁMETROS

Una vez cumplido el factor de seguridad, se normalizarán los diámetros.

## 19.1. Sistema Internacional

Se permitirá utilizar series de números preferidos, como:

- R5.
- R10.
- R20.

La serie seleccionada será configurable.

La primera configuración recomendada será R10.

## 19.2. Sistema inglés

Se utilizarán diámetros normalizados en pulgadas.

Se permitirá definir series de incrementos fraccionarios, por ejemplo:

- 1/16 in.
- 1/8 in.
- 1/4 in.

Los incrementos utilizados dependerán del rango de diámetros.

## 19.3. Regla de redondeo

Siempre se redondeará hacia arriba.

Nunca se seleccionará el diámetro más cercano si este es inferior al requerido.

Después de normalizar:

1. Se comprobarán nuevamente las relaciones entre diámetros.
2. Si una relación deja de cumplirse, se aumentará el diámetro interior correspondiente.
3. Se recalcularán las concentraciones.
4. Se recalcularán los esfuerzos.
5. Se recalcularán todos los factores de seguridad.

El diseño normalizado será válido únicamente si supera todas las comprobaciones.

---

# 20. PESO PROPIO Y RECÁLCULO FINAL

Si el peso propio está activado, el diseño y su peso se encuentran relacionados.

Por ello, después de obtener una geometría normalizada:

1. Calcular el peso real del eje.
2. Actualizar la carga distribuida.
3. Recalcular las reacciones.
4. Recalcular las solicitaciones.
5. Recalcular el dimensionamiento y la verificación.
6. Repetir hasta convergencia.

Se establecerán tolerancias para considerar convergentes las iteraciones.

Si se alcanza el máximo de iteraciones sin converger, se informará del problema y no se presentará el resultado como diseño verificado.

---

# 21. DISEÑO MANUAL Y VERIFICACIÓN

El programa tendrá dos modos de trabajo.

## 21.1. Dimensionamiento automático

El programa calculará los diámetros requeridos, construirá la geometría escalonada, normalizará los diámetros y verificará el resultado.

## 21.2. Verificación de un diseño propuesto

El usuario podrá introducir manualmente:

- Diámetros.
- Posiciones de los escalonamientos.
- Radios de redondeo.
- Geometría de los concentradores.

El programa no modificará automáticamente los diámetros.

Calculará todas las solicitaciones, esfuerzos y factores de seguridad, indicando las zonas que cumplen y las que no.

---

# 22. RESULTADOS Y PRESENTACIÓN

El programa deberá mostrar los resultados de forma organizada.

## 22.1. Resumen del sistema

- Longitud del eje.
- Sistema de unidades.
- Apoyos.
- Elementos.
- Material.
- Configuración de diseño.

## 22.2. Reacciones

Mostrar las reacciones de cada apoyo y los residuos de equilibrio.

## 22.3. Ecuaciones

Mostrar las funciones por tramos de:

- Fuerza axial.
- Fuerzas cortantes.
- Momentos flectores.
- Momento torsor.

La presentación será por magnitud, no agrupando primero los tramos y después las magnitudes.

## 22.4. Gráficas 2D

Mostrar los diagramas correspondientes a las solicitaciones internas.

Las gráficas deberán tener:

- Ejes correctamente identificados.
- Unidades.
- Signos.
- Límites de discontinuidad.
- Posiciones de apoyos.
- Posiciones de elementos.
- Posiciones de cargas importantes.

## 22.5. Gráfica 3D

Mostrar el eje con:

- Secciones.
- Escalonamientos.
- Apoyos.
- Elementos.
- Concentradores.
- Fuerzas.
- Reacciones.
- Momentos.

Las fuerzas deberán originarse en la coordenada real de aplicación y seguir su dirección correcta.

Los colores de elementos y apoyos deberán ser consistentes.

## 22.6. Dimensionamiento

Mostrar:

- Diámetro ideal en función de X.
- Diámetros preliminares por sección.
- Correcciones geométricas.
- Diámetros finales.
- Diámetros normalizados.

## 22.7. Tabla de puntos críticos

Para cada punto importante se presentará:

- Posición.
- Tipo de sección.
- Diámetro local.
- Solicitaciones internas.
- Concentradores presentes.
- Factores \(K_t\), \(K_{ts}\), \(K_f\), \(K_{fs}\).
- Esfuerzos alternantes.
- Esfuerzos medios.
- Límite de fatiga corregido.
- Factores de seguridad.
- Criterio que controla el diseño.

## 22.8. Registro de iteraciones

Se mostrará cómo evolucionó el diseño:

- Diámetros preliminares.
- Correcciones de relaciones geométricas.
- Multiplicador aplicado.
- Cambios producidos por normalización.
- Factores de seguridad de cada etapa.

El usuario deberá poder comprender por qué aumentó el diámetro de una sección.

---

# 23. VALIDACIONES Y ERRORES

El programa deberá detectar, entre otros:

- Longitudes negativas o nulas.
- Posiciones fuera del eje.
- Apoyos superpuestos.
- Más o menos de dos apoyos.
- Ausencia de un apoyo fijo axial.
- Ambos apoyos fijos axialmente.
- Elementos superpuestos.
- Espacio insuficiente para anillos.
- Espacio insuficiente para escalonamientos.
- Radios de redondeo inviables.
- Concentradores superpuestos.
- Cargas fuera del eje.
- Material con propiedades incompletas.
- Datos de material incoherentes.
- Imposibilidad de obtener equilibrio estático.
- Desequilibrio torsional.
- Factores de concentración fuera de sus rangos válidos.
- Imposibilidad de cumplir el factor de seguridad.
- Ausencia de convergencia.
- Diámetros normalizados insuficientes.

Los errores deberán indicar la causa y, cuando sea posible, la posición donde ocurren.

---

# 24. ARQUITECTURA DEL PROGRAMA

Se mantendrá una separación clara entre el modelo, los cálculos y las salidas.

La organización lógica será:

## modelo/

Contendrá las clases y estructuras de datos:

- Sistema de unidades.
- Eje.
- Apoyo.
- Elemento.
- Carga puntual.
- Carga distribuida.
- Acción equivalente.
- Material.
- Concentrador.
- Sección geométrica.
- Configuración de diseño.

## calculos/

Contendrá funciones matemáticas independientes:

- Conversiones de unidades.
- Integración de cargas distribuidas.
- Cálculo de reacciones.
- Cálculo de solicitaciones.
- Construcción de funciones por tramos.
- Localización de puntos críticos.
- Cálculo de esfuerzos.
- Factores de Marin.
- Concentraciones de esfuerzos.
- Criterios de falla.
- Dimensionamiento preliminar.
- Construcción geométrica.
- Corrección iterativa.
- Normalización.
- Verificación final.

## salidas/

Contendrá:

- Impresión de resultados.
- Presentación de ecuaciones.
- Gráficas 2D.
- Gráfica 3D.
- Tablas.
- Resúmenes de diseño.
- Exportación de resultados.

Los módulos de cálculo no deberán depender de las gráficas ni de la presentación de resultados.

Las funciones matemáticas deberán ser comprobables independientemente.

---

# 25. PRUEBAS OBLIGATORIAS

Antes de incorporar el dimensionamiento, se deberán crear pruebas que garanticen la corrección del análisis mecánico.

## 25.1. Reacciones

Probar:

- Viga simplemente apoyada con carga puntual central.
- Carga puntual fuera del centro.
- Carga distribuida uniforme.
- Carga distribuida triangular o lineal.
- Cargas en ambos planos.
- Apoyos que no estén en los extremos.

## 25.2. Solicitaciones

Verificar manualmente:

- Fuerza cortante.
- Momento flector.
- Momento torsor.
- Fuerza axial.
- Momentos aplicados.
- Saltos y continuidad en las posiciones correspondientes.

## 25.3. Equivalencia de unidades

Un mismo problema introducido en SI y en sistema inglés deberá producir resultados físicamente equivalentes, una vez convertidas las unidades.

## 25.4. Concentradores

Probar casos con:

- Escalonamientos.
- Chaveteros.
- Ranuras de anillos.
- Diferentes relaciones \(D/d\).
- Diferentes radios \(r/d\).

## 25.5. Dimensionamiento

Verificar que:

- El diámetro calculado satisface el factor objetivo.
- Un diámetro inferior no lo satisface cuando corresponde.
- Los factores de Marin se actualizan al cambiar el diámetro.
- La geometría satisface las restricciones.
- La normalización no produce un diseño inseguro.

---

# 26. ORDEN DE DESARROLLO

El desarrollo se realizará siguiendo estrictamente este orden.

## ETAPA 1 — Auditoría y estabilización del análisis mecánico

1. Revisar el modelo actual.
2. Revisar las unidades.
3. Revisar las cargas puntuales.
4. Revisar las cargas distribuidas.
5. Revisar las reacciones.
6. Revisar los signos.
7. Revisar las funciones por tramos.
8. Revisar los diagramas.
9. Incorporar las pruebas analíticas.

**Condición para avanzar:** las reacciones y solicitaciones deben coincidir con los resultados mecánicos de referencia.

## ETAPA 2 — Consolidación del modelo geométrico

1. Formalizar las secciones.
2. Asociar elementos y apoyos a sus secciones.
3. Definir los escalonamientos.
4. Definir las posiciones de los anillos.
5. Incorporar las reglas de orientación.
6. Implementar las validaciones geométricas.

**Condición para avanzar:** el programa debe poder construir y validar una geometría escalonada coherente sin realizar todavía el dimensionamiento.

## ETAPA 3 — Materiales y propiedades

1. Implementar el modelo de acero.
2. Incorporar \(S_{ut}\), \(S_y\), \(E\), \(G\) y densidad.
3. Calcular \(S'_e\).
4. Implementar los factores de Marin.
5. Implementar sus dependencias con el diámetro.
6. Crear pruebas de las ecuaciones.

**Condición para avanzar:** se deben obtener correctamente las propiedades mecánicas y el límite de fatiga corregido.

## ETAPA 4 — Concentradores de esfuerzos

1. Crear la estructura general de concentradores.
2. Implementar escalonamientos.
3. Implementar chaveteros.
4. Implementar ranuras para anillos.
5. Calcular \(K_t\) y \(K_{ts}\).
6. Calcular \(q\) y \(q_s\).
7. Calcular \(K_f\) y \(K_{fs}\).
8. Validar rangos geométricos.

**Condición para avanzar:** cada concentrador debe calcular sus factores de forma reproducible y documentada.

## ETAPA 5 — Esfuerzos y criterios de falla

1. Calcular esfuerzos axiales.
2. Calcular esfuerzos de flexión.
3. Calcular esfuerzos torsionales.
4. Separar componentes alternantes y medias.
5. Implementar Von Mises alternante y medio.
6. Implementar Goodman.
7. Implementar Soderberg.
8. Implementar Gerber.
9. Implementar fluencia.
10. Obtener el factor de seguridad mínimo.

**Condición para avanzar:** deben verificarse casos de referencia y obtenerse factores de seguridad coherentes.

## ETAPA 6 — Diámetros ideales

1. Implementar la evaluación en una posición.
2. Implementar la búsqueda del diámetro mínimo.
3. Incorporar el factor de tamaño iterativo.
4. Evaluar todos los puntos de la discretización.
5. Incorporar los puntos especiales.
6. Encontrar los máximos relevantes.
7. Generar la curva de diámetro ideal.

**Condición para avanzar:** el programa debe obtener un diámetro requerido para cada punto evaluado y justificarlo mediante sus factores de seguridad.

## ETAPA 7 — Construcción de la geometría preliminar

1. Agrupar los puntos en secciones.
2. Obtener el máximo diámetro ideal por sección.
3. Comprobar las relaciones \(D/d\).
4. Propagar los aumentos hacia el centro.
5. Definir los radios de redondeo.
6. Validar la geometría.

**Condición para avanzar:** todas las secciones deben respetar sus diámetros mínimos y las reglas constructivas.

## ETAPA 8 — Verificación de escalonamientos

1. Calcular los factores de concentración.
2. Evaluar los esfuerzos en cada escalonamiento.
3. Calcular los factores de seguridad.
4. Identificar los puntos que no cumplen.
5. Aplicar la búsqueda del multiplicador geométrico.
6. Volver a verificar todas las secciones.
7. Registrar las iteraciones.

**Condición para avanzar:** todos los puntos críticos deben cumplir el factor objetivo.

## ETAPA 9 — Normalización

1. Seleccionar la serie de diámetros.
2. Redondear hacia arriba.
3. Volver a comprobar las relaciones geométricas.
4. Recalcular concentradores.
5. Recalcular esfuerzos.
6. Verificar nuevamente el factor de seguridad.

**Condición para avanzar:** el diseño normalizado debe continuar siendo seguro.

## ETAPA 10 — Peso propio y verificación final

1. Calcular el peso real del eje.
2. Incorporar su carga distribuida.
3. Recalcular reacciones.
4. Recalcular diagramas.
5. Recalcular el dimensionamiento.
6. Repetir hasta convergencia.
7. Realizar una verificación final completa.

**Condición para avanzar:** el diseño definitivo debe cumplir con todas las comprobaciones, incluyendo su peso propio cuando esté activado.

## ETAPA 11 — Presentación final

1. Organizar el resumen del sistema.
2. Presentar las ecuaciones.
3. Mejorar los diagramas 2D.
4. Mejorar la visualización 3D.
5. Mostrar la geometría definitiva.
6. Mostrar las tablas de factores de seguridad.
7. Mostrar el registro de iteraciones.
8. Preparar la exportación de resultados.

**Condición de finalización:** el usuario debe poder reconstruir y entender el procedimiento completo a partir de los resultados presentados.

---

# 27. FUNCIONES FUTURAS

No forman parte de la primera versión, pero el programa deberá diseñarse para poder incorporarlas posteriormente:

- Ejes huecos.
- Materiales distintos del acero.
- Cargas variables en el tiempo.
- Espectros de fatiga.
- Otros criterios de falla.
- Optimización del volumen o masa.
- Optimización libre de las proporciones geométricas.
- Verificación de deformaciones y pendientes.
- Ángulo de torsión.
- Velocidad crítica.
- Análisis de vibraciones.
- Diseño y verificación de chavetas.
- Verificación de rodamientos.
- Vida de rodamientos.
- Catálogos de componentes normalizados.
- Geometrías de eje más complejas.

---

# 28. PRINCIPIOS QUE DEBEN RESPETARSE DURANTE EL DESARROLLO

1. No introducir fórmulas sin definir sus convenciones y unidades.
2. No duplicar cálculos en diferentes módulos.
3. No mezclar el análisis mecánico con la visualización.
4. No aplicar factores de concentración sin conocer el tipo de geometría y solicitación.
5. No considerar que una relación geométrica satisfecha garantiza resistencia.
6. No considerar que el diámetro ideal representa automáticamente una geometría fabricable.
7. No modificar diámetros sin recalcular las secciones afectadas.
8. No presentar un resultado como válido si alguna comprobación obligatoria falla.
9. No ocultar iteraciones, aproximaciones ni advertencias.
10. Priorizar resultados verificables y físicamente coherentes antes que incorporar nuevas funcionalidades.

**Esta especificación será la referencia del desarrollo.** Cualquier cambio en el alcance o en las reglas de cálculo deberá incorporarse explícitamente a una nueva revisión del documento.