# Tests für Feuerwehr-Sichtpruefer

## Übersicht

Dieses Verzeichnis enthält Unit-Tests für das Feuerwehr-Sichtpruefer-Projekt. Die Tests verwenden `pytest`, das Standard-Test-Framework für Python.

## Vergleich mit JUnit (Java)

| JUnit (Java) | pytest (Python) |
|--------------|-----------------|
| `@Test` Annotation | Funktionen mit `test_` Präfix |
| `@BeforeEach` | `@pytest.fixture` mit `autouse=True` |
| `@BeforeAll` | `@pytest.fixture(scope="class")` |
| `assertTrue()`, `assertEquals()` | `assert` (direkt) |
| `@Mock` (Mockito) | `unittest.mock.Mock` oder `pytest-mock` |
| `@ParameterizedTest` | `@pytest.mark.parametrize` |

## Test-Struktur

```
tests/
├── __init__.py
├── test_models_eigenschaft.py          # Tests für Eigenschaft-Modell
├── test_models_eigenschaftpruefung.py  # Tests für Eigenschaftspruefung-Modell
├── test_models_pruefanweisung.py      # Tests für Pruefanweisung-Modell
├── test_models_sichtpruefung.py        # Tests für Sichtpruefung-Modell
├── test_validators.py                  # Tests für Validatoren
├── test_state.py                       # Tests für AppState
└── test_managers.py                    # Tests für Manager-Klassen
```

## Tests ausführen

### Alle Tests ausführen
```bash
pytest
```

### Bestimmte Test-Datei ausführen
```bash
pytest tests/test_models_pruefanweisung.py
```

### Bestimmte Test-Funktion ausführen
```bash
pytest tests/test_models_pruefanweisung.py::TestPruefanweisung::test_pruefanweisung_initialisierung
```

### Mit ausführlicher Ausgabe
```bash
pytest -v
```

### Mit Coverage-Report
```bash
pytest --cov=src --cov-report=html
```

## Test-Patterns

### 1. Einfacher Test
```python
def test_eigenschaft_initialisierung(self):
    """Test: Eigenschaft wird korrekt initialisiert"""
    eigenschaft = Eigenschaft("Schutz", "Helm", [])
    assert eigenschaft.kategorie == "Schutz"
```

### 2. Test mit Fixtures (Setup)
```python
@pytest.fixture
def mock_ui(self):
    """Fixture: Erstellt ein Mock-UI-Objekt"""
    return MagicMock()

def test_something(self, mock_ui):
    # mock_ui wird automatisch übergeben
    pass
```

### 3. Test mit Mocking
```python
def test_with_mock(self, mocker):
    mock_function = mocker.patch('module.function')
    mock_function.return_value = "test"
    # ...
```

### 4. Test mit Exceptions
```python
def test_raises_exception(self):
    with pytest.raises(ValueError, match="nicht initialisiert"):
        function_that_raises()
```

## Best Practices

1. **Test-Namen**: Beschreibend und klar (z.B. `test_eigenschaft_initialisierung`)
2. **Arrange-Act-Assert**: Strukturiere Tests in drei Phasen
3. **Isolation**: Jeder Test sollte unabhängig sein
4. **Mocking**: Mocke externe Abhängigkeiten (UI, Dateisystem, etc.)
5. **Fixtures**: Verwende Fixtures für wiederkehrendes Setup

## Weitere Informationen

- [pytest Dokumentation](https://docs.pytest.org/)
- [unittest.mock Dokumentation](https://docs.python.org/3/library/unittest.mock.html)

