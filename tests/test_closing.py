"""Tests for Report Generation functions."""
# Standard Python Libraries
import types

# cisagov Libraries
from pca_report_library.customer.closing import deltas


def test_deltas_returns_generator():
    """Test generator type is returned."""
    in_val = [1, 2, 3, 4]
    result = deltas(in_val)
    assert isinstance(result, types.GeneratorType)
