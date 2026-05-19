from importlib import util
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def utr_sample():
    """Load the current single-file sample despite its dotted filename."""
    repo_root = Path(__file__).resolve().parents[1]
    sample_path = repo_root / "src" / "UTR_LAN_sample_1.0.0.py"
    spec = util.spec_from_file_location("utr_lan_sample", sample_path)
    assert spec is not None
    assert spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
