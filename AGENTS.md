# AGENTS.md

## Comandos

- Ejecutar siempre desde la raíz del repo (los imports son `modelo.*`, `calculos.*`, `salidas.*`):
  `.venv/bin/python main.py`
- Sin entorno gráfico: `MPLBACKEND=Agg .venv/bin/python main.py`
- Tests: `.venv/bin/python -m pytest -q`. Cubren unidades, transformaciones, reacciones, solicitaciones, validación y salidas. Un archivo puntual: `.venv/bin/python -m pytest tests/test_solicitaciones.py -q`.
- `tests/conftest.py` fuerza el backend `Agg` de matplotlib; los tests no abren ventanas.
- No hay `requirements.txt`, `pyproject.toml` ni CI. El entorno es `.venv` (Python 3.14) con numpy, sympy, matplotlib y pytest.

## Alcance real

- `especificaciones.md` describe el objetivo completo (fatiga, dimensionamiento, geometría, materiales), pero **no está implementado**. Hoy solo existen modelo de cargas, reacciones, solicitaciones simbólicas y diagramas.
- `main.py` es un ejemplo ejecutable, no un entrypoint de librería; para probar un caso, editar sus datos.

## Unidades y modelo

- Las entradas de los `crear(...)` están en **mm/in, N/lbf y N·mm/lbf·in**. Internamente todo se guarda en **m, N y N·m**.
- Construir los objetos con `Clase.crear(...)`; llamar al constructor directamente exige unidades SI.
- En `CargaDistribuida.crear`, `q` se ingresa en **N/mm** (SI) o **lbf/in** (inglés); internamente queda en N/m.
- `posicion` es el centro del apoyo/elemento y `ancho` su ancho total, medidos desde el extremo izquierdo. X es longitudinal, Y vertical, Z horizontal.
- El eje exige exactamente 2 apoyos y exactamente 1 con `fijo_axial=True`.
- `eje.validar()` acumula todos los errores y lanza un único `ValueError`; `calcular_solicitaciones` ya lo invoca.

## Arquitectura

- `modelo/`: dataclasses y validación. Sin cálculos ni impresión.
- `calculos/transformaciones.py`: convierte cargas a `Accion` equivalente sobre el eje central (SI).
- `calculos/reacciones.py`: resuelve los dos apoyos; solo advierte si hay `Mx` externo desbalanceado, porque los apoyos no lo absorben.
- `calculos/solicitaciones.py`: genera expresiones sympy `Piecewise` por tramos. `ResultadoSolicitaciones.evaluar(nombre, x)` recibe **x en metros** y devuelve SI. Las resultantes `VR` y `MR` se evalúan con `hypot` de sus componentes: no reemplazar por el `sqrt` expandido, que puede dar un radicando negativo por redondeo en apoyos.
- `salidas/`: conversión a unidades de usuario, informes y gráficos. Mantener la conversión de unidades acá, no en el núcleo de cálculo.
- `generar_diagramas` llama siempre a `plt.show()`. `generar_diagramas_eje(..., mostrar=True)` devuelve `(fig_3d, fig_2d)`; usar `mostrar=False` para guardar o incrustar.
- Ninguna función guarda figuras en disco; usar `fig.savefig(...)` si se necesitan archivos.

## Convenciones

- Identificadores, docstrings, mensajes de error y salida en español.
- Indentación de **2 espacios** en todo el repo; no reformatear a 4.
- Usar «solicitaciones» para las funciones internas V, M, N y T. Reservar «esfuerzos» para tensiones/fatiga, que todavía no están implementados.
