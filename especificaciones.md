Estas especificaciones no son las definitivas, pueden cambiar, todo sigue en desarrollo, es una vista general de como quiero el proyecto por ahora.

# 1. Objetivo y alcance

Desarrollar un programa en Python para diseñar ejes mecánicos, siguiendo el procedimiento de diseño de ejes de *Diseño en ingeniería mecánica*, de Shigley.

El programa deberá:
- Calcular reacciones, solicitaciones y diagramas.
- Dimensionar automáticamente los diámetros del eje.
- Considerar fatiga, fluencia y concentraciones de esfuerzos.
- Diseñar la geometría escalonada del eje.
- Considerar el peso propio del eje.
- Verificar diseños propuestos manualmente.
- Mostrar ecuaciones, resultados intermedios y justificaciones de los cálculos.

**Alcance inicial:** ejes circulares macizos de acero. No se considerarán ejes huecos ni otros materiales por ahora.

# 2. Sistemas de unidades

El usuario podrá seleccionar:
- Sistema Internacional (SI).
- Sistema inglés.

Internamente, los cálculos se realizarán en SI. Las entradas y salidas se convertirán al sistema seleccionado.

# 3. Definición del sistema

## 3.1. Eje
- Longitud total.
- Material.
- Sistema de unidades.

Sistema de coordenadas:
- X: dirección longitudinal del eje.
- Y: dirección vertical.
- Z: dirección transversal horizontal.

## 3.2. Apoyos
Se permitirán exactamente dos apoyos.

Cada apoyo tendrá:
- Nombre.
- Posición longitudinal, definida en su centro.
- Ancho.
- Identificación de si es el apoyo fijo axial.

El apoyo fijo absorbe las cargas axiales. El otro permite el desplazamiento axial.

Los apoyos no necesariamente estarán en los extremos del eje.

## 3.3. Elementos montados
Cada elemento tendrá:
- Nombre.
- Posición longitudinal, definida en su centro.
- Ancho.
- Cargas aplicadas.
- Concentradores de esfuerzos asociados, si corresponde.

Las cargas podrán ser:
- Fuerzas radiales.
- Fuerzas axiales.
- Fuerzas tangenciales.
- Momentos o torques aplicados directamente.
- Cargas distribuidas.

Para las fuerzas tangenciales se indicará el radio de aplicación, permitiendo calcular el torque:

\[
T=F_t r
\]

La masa de los elementos se introducirá como una carga aplicada sobre ellos. No se calculará automáticamente.

También podrán existir cargas y concentradores independientes de los elementos y apoyos.

# 4. Análisis de cargas y solicitaciones

Se calcularán las reacciones y las funciones de solicitación a lo largo del eje.

Se considerarán:
- Fuerza axial: \(F_x(x)\).
- Fuerza cortante vertical: \(V_y(x)\).
- Fuerza cortante horizontal: \(V_z(x)\).
- Momento flector respecto a Y: \(M_y(x)\).
- Momento flector respecto a Z: \(M_z(x)\).
- Momento torsor: \(T_x(x)\).

Se generarán los diagramas correspondientes.

Las cargas distribuidas podrán tener intensidad variable y actuar en cualquiera de las direcciones permitidas.

## 4.1. Peso propio del eje

El peso propio se incorporará como carga distribuida vertical.

Para cada sección:

\[
A(x)=\frac{\pi d(x)^2}{4}
\]

\[
w(x)=\rho g A(x)
\]

Donde:
- \(\rho\): densidad del material.
- \(g\): aceleración gravitacional.
- \(d(x)\): diámetro local.

Como el diámetro todavía es desconocido inicialmente, el peso propio se incorporará mediante iteraciones durante el dimensionamiento.

# 5. Materiales

Inicialmente se trabajará únicamente con aceros.

Propiedades necesarias:
- Resistencia última a la tensión: \(S_{ut}\).
- Límite de fluencia: \(S_y\).
- Módulo de elasticidad: \(E\).
- Módulo de rigidez: \(G\).
- Densidad: \(\rho\).

El límite de resistencia a la fatiga de probeta se calculará automáticamente a partir de \(S_{ut}\), según Shigley:

\[
S'_e=
\begin{cases}
0.5S_{ut}, & S_{ut}\leq 1400\text{ MPa}\\
700\text{ MPa}, & S_{ut}>1400\text{ MPa}
\end{cases}
\]

En el sistema inglés:

\[
S'_e=
\begin{cases}
0.5S_{ut}, & S_{ut}\leq 200\text{ ksi}\\
100\text{ ksi}, & S_{ut}>200\text{ ksi}
\end{cases}
\]

El límite de resistencia a la fatiga corregido será:

\[
S_e=k_a k_b k_c k_d k_e k_f S'_e
\]

Se utilizarán los factores de Marin correspondientes. Los factores que dependan del diámetro se recalcularán durante el dimensionamiento.

# 6. Concentradores de esfuerzos

Se podrán definir concentradores asociados a elementos, apoyos o independientemente.

Inicialmente se considerarán:
- Chaveteros.
- Ranuras para anillos de retención.
- Escalonamientos.
- Otros concentradores que se incorporen posteriormente.

Para cada concentrador se determinarán los factores teóricos:

\[
K_t,\qquad K_{ts}
\]

Y los factores efectivos de fatiga:

\[
K_f=1+q(K_t-1)
\]

\[
K_{fs}=1+q_s(K_{ts}-1)
\]

Donde \(q\) y \(q_s\) son las sensibilidades a la entalla.

Los factores dependerán de la geometría y del material. Se recalcularán cuando cambien los diámetros o radios.

En puntos sin concentradores:

\[
K_t=K_{ts}=K_f=K_{fs}=1
\]

# 7. Criterios de falla

Se implementarán como criterios independientes y seleccionables. El programa calculará el factor de seguridad de cada criterio y tomará el menor como factor de seguridad global.

## 7.1. Esfuerzos equivalentes

Se calcularán los esfuerzos alternantes y medios:

\[
\sigma'_a=\sqrt{\sigma_a^2+3\tau_a^2}
\]

\[
\sigma'_m=\sqrt{\sigma_m^2+3\tau_m^2}
\]

Los factores de concentración correspondientes se aplicarán a cada componente antes de calcular los equivalentes.

También se calculará el esfuerzo de Von Mises máximo instantáneo:

\[
\sigma_{VM,\max}
\]

Este se obtendrá evaluando el estado combinado de esfuerzos durante el ciclo de carga, no sumando directamente los equivalentes alternante y medio.

## 7.2. Goodman modificado

\[
\frac{1}{n_G}=
\frac{\sigma'_a}{S_e}
+
\frac{\sigma'_m}{S_{ut}}
\]

## 7.3. Soderberg

\[
\frac{1}{n_S}=
\frac{\sigma'_a}{S_e}
+
\frac{\sigma'_m}{S_y}
\]

## 7.4. Gerber

Se resolverá la ecuación:

\[
\left(\frac{\sigma'_m}{S_{ut}}\right)^2n_G^2
+
\frac{\sigma'_a}{S_e}n_G-1=0
\]

Se tomará la raíz positiva.

## 7.5. Fluencia

\[
n_y=\frac{S_y}{\sigma_{VM,\max}}
\]

## 7.6. Factor de seguridad global

\[
n_{\min}=\min(n_G,n_S,n_{Gerber},n_y,\ldots)
\]

El usuario establecerá el factor de seguridad objetivo. El diseño deberá cumplirlo en todos los puntos evaluados y para todos los criterios habilitados.

## 7.7. Comportamiento de las cargas

Para un eje giratorio sometido a cargas constantes en el espacio:
- La flexión produce esfuerzos normales completamente alternantes.
- El torque constante produce esfuerzos cortantes medios.
- La fuerza axial constante produce esfuerzos normales medios.

No se supondrá que todos los esfuerzos medios son cero.

Las cargas variables y ciclos más complejos podrán incorporarse posteriormente.

# 8. Geometría del eje: secciones y escalonamientos

La geometría se construirá a partir de los apoyos y elementos montados.

## 8.1. Secciones

Cada elemento y apoyo tendrá una sección propia del eje.

Entre secciones existirán escalonamientos. El diámetro será mayor hacia el centro del eje, siguiendo la disposición constructiva definida.

Cada elemento o apoyo se apoyará contra el escalonamiento de subida correspondiente:
- Si está a la izquierda, se apoya en el escalonamiento de su derecha.
- Si está a la derecha, se apoya en el escalonamiento de su izquierda.

El extremo opuesto podrá llevar un anillo de retención si se lo definió como concentrador de presión asociado al elemento.

La posición de los elementos y apoyos, sus anchos y los accesorios determinarán el espacio axial ocupado.

## 8.2. Anillos de retención

Los anillos se ubicarán en el extremo opuesto al escalonamiento que soporta el elemento.

Su ancho se sumará al espacio axial ocupado por el conjunto. No se confundirá el ancho físico del elemento con el espacio total requerido.

## 8.3. Validaciones geométricas

El programa verificará:
- Que existan exactamente dos apoyos.
- Que los elementos y apoyos no se superpongan indebidamente.
- Que no queden al ras de los extremos.
- Que haya espacio suficiente para los anillos.
- Que las longitudes sean positivas.
- Que los escalonamientos sean constructivamente viables.
- Que se respete la orientación de las subidas hacia el centro.

## 8.4. Relaciones geométricas

Se definirán:
- Relación mínima de diámetros: \(D/d\).
- Relación de radio de redondeo: \(r/d\).

Estas relaciones serán objetivos mínimos, no necesariamente valores exactos.

Para cada escalonamiento:

\[
D=\max(d_1,d_2)
\]

\[
d=\min(d_1,d_2)
\]

Se verificará que:

\[
\frac{D}{d}\geq C_D
\]

Y se utilizará la relación \(r/d\) definida para determinar el radio de redondeo.

En esta primera versión se mantendrán las relaciones objetivo como restricciones; no se optimizarán libremente.

# 9. Procedimiento de dimensionamiento

Esta es la parte central del programa.

## Etapa 1: dimensionamiento preliminar sin peso propio

1. Calcular reacciones y solicitaciones considerando las cargas externas, sin peso propio.
2. Discretizar el eje con un paso configurable.
3. Evaluar los esfuerzos y factores de seguridad en todos los puntos de la malla.
4. Evaluar también las posiciones especiales de los concentradores, aunque no coincidan con la malla.
5. No considerar todavía las concentraciones producidas por los escalonamientos.
6. Calcular el diámetro ideal mínimo requerido en cada punto.
7. Agrupar los puntos por sección geométrica.
8. Tomar el máximo diámetro ideal de cada sección.

Se obtendrán así los primeros diámetros preliminares:

\[
d_1^{(0)},d_2^{(0)},\ldots,d_n^{(0)}
\]

## Etapa 2: búsqueda del diámetro ideal

Para encontrar el diámetro mínimo que cumple el factor de seguridad objetivo se utilizará búsqueda binaria.

Para cada punto:

1. Establecer un intervalo de diámetros que contenga una solución.
2. Evaluar el factor de seguridad con el diámetro intermedio.
3. Si cumple el objetivo, reducir el límite superior.
4. Si no cumple, aumentar el límite inferior.
5. Repetir hasta alcanzar la tolerancia establecida.

Se buscará:

\[
d_{\text{ideal}}=
\min\{d:n_{\min}(d)\geq n_{\text{objetivo}}\}
\]

En cada evaluación se recalcularán los factores que dependan del diámetro, como los factores de Marin, esfuerzos, etc.

La búsqueda deberá disponer de límites, tolerancias y detección de casos sin solución.

## Etapa 3: iteraciones por peso propio

Con los diámetros preliminares:

1. Calcular el área y la masa de cada sección.
2. Obtener el peso distribuido del eje.
3. Incorporar ese peso a las cargas externas.
4. Recalcular reacciones y solicitaciones.
5. Volver a calcular los diámetros ideales.
6. Agrupar por secciones y obtener nuevos diámetros.
7. Actualizar la masa y repetir.

Se detendrá cuando los cambios relativos de los diámetros sean menores que una tolerancia establecida, o cuando se alcance el máximo de iteraciones.

## Etapa 4: ajuste de relaciones geométricas

Con los diámetros que ya consideran el peso propio:

1. Verificar las relaciones \(D/d\) entre secciones vecinas.
2. Ajustar los diámetros que no cumplan.
3. Considerar que modificar una sección afecta los escalonamientos de ambos lados.
4. Repetir las verificaciones geométricas hasta obtener una configuración válida.

Los ajustes deberán respetar los diámetros mínimos requeridos.

## Etapa 5: verificación de los escalonamientos

1. Calcular los factores \(K_t\), \(K_{ts}\), \(K_f\) y \(K_{fs}\) de cada escalonamiento.
2. Evaluar los esfuerzos y factores de seguridad en los hombros y posiciones correspondientes.
3. Si algún punto no cumple, modificar los diámetros o radios respetando las restricciones geométricas.
4. Recalcular los factores y verificar nuevamente.

Los cambios deberán propagarse a las secciones vecinas cuando corresponda.

## Etapa 6: realimentación del peso propio

Cualquier modificación geométrica actualizará la masa del eje.

Por tanto, si cambian los diámetros:
1. Recalcular la masa.
2. Actualizar el peso distribuido.
3. Recalcular reacciones y solicitaciones.
4. Redimensionar las secciones.
5. Volver a verificar relaciones geométricas, concentradores y factores de seguridad.

Este ciclo global se repetirá hasta que la geometría, las solicitaciones y las verificaciones sean consistentes.

## Etapa 7: normalización y verificación final

Una vez obtenido un diseño que cumple:

1. Normalizar los diámetros hacia arriba, nunca hacia abajo.
2. Para SI se podrán utilizar series preferidas ISO R5, R10 o R20.
3. Para el sistema inglés se utilizarán incrementos normalizados en pulgadas.
4. Recalcular masa y peso propio con los diámetros normalizados.
5. Recalcular todas las solicitaciones.
6. Verificar nuevamente todos los criterios de falla y restricciones geométricas.

El diseño solo se aceptará si sigue cumpliendo después de la normalización.

# 10. Evaluación de resultados

El programa mostrará:
- Reacciones y diagramas de solicitación.
- Ecuaciones de esfuerzos.
- Factores de concentración utilizados.
- Factores de Marin.
- Factores de seguridad por criterio y punto.
- Diámetros ideales y finales por sección.
- Masa y peso propio del eje.
- Iteraciones realizadas y convergencia.
- Relaciones geométricas y dimensiones de escalonamientos.
- Verificaciones y posibles incumplimientos.

Se mantendrán visualizaciones 2D y 3D del eje, sus apoyos, elementos, cargas y geometría final.

# 11. Funcionalidades posteriores

Una vez terminado y validado el dimensionamiento inicial, se podrán incorporar:
- Deformaciones y pendientes.
- Ángulo de torsión.
- Velocidades críticas.
- Diseño de chavetas por cortadura y aplastamiento.
- Selección y verificación de rodamientos por cargas equivalentes y vida.
- Otros concentradores, materiales y criterios de falla.
- Optimización geométrica del eje.

Estas funcionalidades no formarán parte de la primera etapa de implementación.