# Plan: Arreglar el pipeline de CI — descombinator-pro

## Diagnóstico (ya verificado localmente)

Cloné el repo y reproduje los pasos de `.github/workflows/ci.yml` uno por uno:

| Step del CI             | Resultado local           |
|-------------------------|---------------------------|
| `ruff check .`          | ✅ Pasa                   |
| `ruff format --check .` | ✅ Pasa                   |
| `pytest tests/ --cov=app --cov=engine ...` | ❌ **`collected 0 items`** |
| `mypy .`              | `continue-on-error: true` (no bloquea) |

**Causa raíz:** `tests/` solo contiene `__init__.py`, `conftest.py` (fixtures) y una carpeta `fixtures/` vacía. No existe ningún archivo `test_*.py`. Pytest sale con código de error 5 ("no tests ran"), y aunque no fuera así, `pyproject.toml` exige:

```toml
[tool.coverage.report]
fail_under = 85
```

0% de cobertura también rompería el gate.

**Causa secundaria (contexto, no bloquea el fallo actual):** `app/` y `engine/` son módulos vacíos — solo tienen `__init__.py` de un renglón. Es decir, el proyecto está en fase de esqueleto: todavía no hay lógica que testear. Esto cambia el enfoque del plan.

**Riesgo latente (no ha fallado aún, pero fallará en cuanto existan tests de UI):** el workflow corre en `ubuntu-latest` sin display. `pytest-qt` con `qt_api = "pyside6"` necesita un display virtual (`xvfb` o `QT_QPA_PLATFORM=offscreen`), y el workflow no lo configura.

---

## Objetivo del agente

No se trata solo de "hacer pasar el CI en verde" — hay que decidir conscientemente entre dos caminos, porque el proyecto aún no tiene código de negocio implementado:

### Opción A — Desbloquear el pipeline ahora, cobertura real después (recomendado si el equipo va a seguir implementando código en los próximos días/semanas)

### Opción B — Implementar código + tests en el mismo PR (recomendado solo si ya hay una feature concreta lista para escribir)

El agente debe elegir la opción según el estado real del trabajo pendiente, pero por defecto debe seguir la **Opción A** para no bloquear al equipo con un gate de cobertura irreal en un proyecto que aún no tiene código.

---

## Tareas — Opción A (desbloqueo inmediato)

1. **Bajar temporalmente el gate de cobertura** en `pyproject.toml`:

   ```toml
   [tool.coverage.report]
   fail_under = 0   # TODO: subir a 85 cuando exista implementación real (ver issue #XX)
   ```

   Documentar con un comentario y, si es posible, abrir un issue/ticket para revertirlo.

2. **Añadir al menos un test "smoke" real** para que pytest no falle por "no tests collected", por ejemplo:

   ```python
   # tests/test_smoke.py
   """Sanity checks that the package imports cleanly."""


   def test_app_package_imports() -> None:
       import app  # noqa: F401


   def test_engine_package_imports() -> None:
       import engine  # noqa: F401
   ```

3. **Arreglar el riesgo de PySide6 en headless CI** antes de que se añadan tests de UI. Editar `.github/workflows/ci.yml`:

   ```yaml
       - name: Pytest
         env:
           QT_QPA_PLATFORM: offscreen
         run: pytest tests/ --cov=app --cov=engine --cov-report=xml --cov-report=term-missing
   ```

   (Alternativa más robusta si offscreen da problemas con algún widget: instalar `xvfb` y correr con `xvfb-run -a pytest ...`.)

4. **Verificar localmente antes de hacer push**:

   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ruff check .
   ruff format --check .
   pytest tests/ --cov=app --cov=engine --cov-report=xml --cov-report=term-missing
   mypy .
   ```

5. Hacer commit y push, y confirmar que el run de GitHub Actions se pone en verde.

---

## Tareas — Opción B (si ya hay features implementadas para testear)

1. Implementar el módulo correspondiente dentro de `app/` o `engine/` (respetando los "Module Boundaries" descritos en `AGENTS.md`: `app/` no debe llamar directamente a `engine/`, solo vía `services/`).
2. Escribir tests unitarios junto con el código, usando los markers ya definidos en `pyproject.toml` (`unit`, `integration`, `ui`, `slow`).
3. Ejecutar `pytest --cov=app --cov=engine --cov-report=term-missing` localmente y revisar qué líneas faltan por cubrir antes de subir el PR.
4. Solo entonces mantener `fail_under = 85` sin bajarlo.
5. Igual que en la Opción A, asegurar `QT_QPA_PLATFORM=offscreen` en el workflow si se añaden tests con `pytest-qt`.

---

## Checklist final antes de cerrar el PR

- [ ] `ruff check .` sin errores
- [ ] `ruff format --check .` sin errores
- [ ] `pytest tests/` recolecta y pasa al menos un test real
- [ ] Cobertura reportada coincide con el `fail_under` configurado (o se documentó por qué se bajó temporalmente)
- [ ] Workflow de CI actualizado con `QT_QPA_PLATFORM=offscreen` (o `xvfb-run`)
- [ ] Run de GitHub Actions en verde en la rama del PR
