import pytest


def test_version_exists():
    from pfn import __version__

    assert __version__ == "0.1.0.dev0"


def test_package_importable():
    import pfn

    assert pfn is not None
