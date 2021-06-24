"""Tests for Report Generation functions."""
# Standard Python Libraries
import types

# cisagov Libraries
from pca_report_library.customer.closing import deltas, pairwise


def test_deltas_returns_generator():
    """Test generator type is returned."""
    in_val = [1, 2, 3, 4]
    result = deltas(in_val)
    assert isinstance(result, types.GeneratorType)


def test_pairwise_returns_zip():
    """Test zip type is returned."""
    in_val = [1, 2, 3, 4]
    result = pairwise(iter(in_val))
    assert isinstance(result, zip)
