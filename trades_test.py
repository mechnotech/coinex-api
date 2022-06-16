from trades import get_amount


def test_get_amount():
    assert get_amount() > 100
