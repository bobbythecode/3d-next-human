import sys

from service.bootstrap import qt_imported


def test_qt_not_imported_by_unit_surface():
    from service.http_api import health_payload
    from service.modifier_request import HumanModifierRequest

    HumanModifierRequest.parse({"gender": 0.5})
    health_payload()
    assert qt_imported() is False
    assert "PyQt5" not in sys.modules
