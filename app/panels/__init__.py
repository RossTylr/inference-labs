"""The panels of page 1, one file per lens (D-27).

Each panel file holds ORDER, the slice that built it, which sets where it appears on the page; SOURCE, the
library function that computes everything it shows from lens 03's walk-through casualty; and render(st, walk),
which lays that out. The entry file finds the panels here, so adding a lens adds a file and changes nothing else.
"""
import importlib
import pkgutil


def discovered() -> list:
    """Every panel module in this folder, in page order."""
    modules = [importlib.import_module(f"{__name__}.{m.name}") for m in pkgutil.iter_modules(__path__)]
    return sorted(modules, key=lambda m: m.ORDER)
