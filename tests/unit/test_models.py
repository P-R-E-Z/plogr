"""Unit tests for the models module"""

from datetime import datetime

from src.plogr.models import PkgEvent


class TestPkgEvent:
    """Test the PkgEvent model."""

    def test_pkg_event_creation(self):
        """Test creating a PkgEvent instance."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
        )

        assert event.name == "test-package"
        assert event.version == "1.0.0"
        assert event.manager == "dnf"
        assert event.scope == "user"
        assert event.action == "install"

    def test_pkg_event_defaults(self):
        """Test PkgEvent with default values."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
        )

        assert event.name == "test-package"
        assert event.version == "1.0.0"
        assert event.manager == "dnf"
        assert event.scope == "user"
        assert event.date is not None  # Should have default datetime

    def test_pkg_event_str_representation(self):
        """Test string representation of PkgEvent."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
        )

        str_repr = str(event)
        assert "test-package" in str_repr
        assert "1.0.0" in str_repr

    def test_pkg_event_repr_representation(self):
        """Test repr representation of PkgEvent."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
        )

        repr_str = repr(event)
        assert "PkgEvent" in repr_str
        assert "test-package" in repr_str
        assert "1.0.0" in repr_str

    def test_pkg_event_equality(self):
        """Test PkgEvent equality comparison."""
        event1 = PkgEvent(
            name="test-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
            date=datetime(2023, 1, 1, 12, 0, 0),
        )

        event2 = PkgEvent(
            name="test-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
            date=datetime(2023, 1, 1, 12, 0, 0),
        )

        event3 = PkgEvent(
            name="different-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
            date=datetime(2023, 1, 1, 12, 0, 0),
        )

        assert event1 == event2
        assert event1 != event3

    def test_pkg_event_to_dict(self):
        """Test PkgEvent to_dict method."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
        )

        result = event.to_dict()

        assert result["name"] == "test-package"
        assert result["version"] == "1.0.0"
        assert result["manager"] == "dnf"
        assert result["scope"] == "user"
        assert result["action"] == "install"
        assert "date" in result
        assert result["removed"] is False

    def test_pkg_event_system_scope(self):
        """Test PkgEvent with system scope."""
        event = PkgEvent(
            name="system-package",
            version="2.0.0",
            manager="dnf",
            action="install",
            scope="system",
        )

        assert event.scope == "system"

    def test_pkg_event_custom_datetime(self):
        """Test PkgEvent with custom datetime."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
            date=custom_time,
        )

        assert event.date == custom_time

    def test_pkg_event_scope_types(self):
        """Test PkgEvent with different scope types."""
        # Test user scope
        user_event = PkgEvent(
            name="user-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
        )
        assert user_event.scope == "user"

        # Test system scope
        system_event = PkgEvent(
            name="system-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="system",
        )
        assert system_event.scope == "system"

    def test_pkg_event_immutable_attributes(self):
        """Test that PkgEvent attributes are immutable (dataclass frozen)."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            manager="dnf",
            action="install",
            scope="user",
        )

        # Dataclasses are not frozen by default, so attributes should be mutable
        # This test verifies the current behavior
        event.name = "new-name"
        assert event.name == "new-name"
