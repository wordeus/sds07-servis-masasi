"""Mimari kural testleri (NFR-16, FR-09; Hafta 3).

Katman yönü: views -> services -> models. Kurallar kaynak kod üzerinde (Python AST)
denetlenir; böylece kural yalnız belgede kalmaz, her test koşusunda doğrulanır.
"""

import ast
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

APP = Path(settings.BASE_DIR) / "servicedesk"
ACCESS_MIXINS = {"LoginRequiredMixin", "PermissionRequiredMixin"}


def _modules(package: str) -> list[Path]:
    return sorted((APP / package).glob("*.py"))


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imported_names(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.append("." * node.level + (node.module or ""))
    return names


class LayeringTests(SimpleTestCase):
    def test_layers_follow_dependency_rules(self):
        """TC-ARCH-01: Görünümler model yöneticilerine (.objects) doğrudan erişmez; services katmanı views, şablon ve HTTP modüllerini içe aktarmaz; models katmanı services ve views'i içe aktarmaz."""
        violations: list[str] = []
        for path in _modules("views"):
            for node in ast.walk(_tree(path)):
                if isinstance(node, ast.Attribute) and node.attr in {"objects", "_default_manager"}:
                    violations.append(f"views/{path.name}:{node.lineno} doğrudan model sorgusu")
        for path in _modules("services"):
            for name in _imported_names(_tree(path)):
                if "views" in name or name.startswith(("django.http", "django.shortcuts", "django.template")):
                    violations.append(f"services/{path.name}: yasak içe aktarma {name}")
        for path in _modules("models"):
            for name in _imported_names(_tree(path)):
                if "services" in name or "views" in name:
                    violations.append(f"models/{path.name}: yasak içe aktarma {name}")
        self.assertEqual(violations, [])
        for package in ("views", "services", "models"):
            with self.subTest(package=package):
                self.assertTrue(any(p.name != "__init__.py" for p in _modules(package)), f"{package}/ boş")

    def test_every_view_class_checks_access(self):
        """TC-ARCH-02: views/ paketindeki her görünüm sınıfı oturum veya izin denetimi içerir (LoginRequiredMixin veya PermissionRequiredMixin)."""
        unchecked: list[str] = []
        found = 0
        for path in _modules("views"):
            for node in ast.walk(_tree(path)):
                if isinstance(node, ast.ClassDef) and node.name.endswith("View"):
                    found += 1
                    bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in node.bases}
                    if not bases & ACCESS_MIXINS:
                        unchecked.append(f"views/{path.name}:{node.lineno} {node.name}")
        self.assertGreaterEqual(found, 8)
        self.assertEqual(unchecked, [])
