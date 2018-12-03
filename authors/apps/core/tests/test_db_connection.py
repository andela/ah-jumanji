import pytest
from django.db import connection


@pytest.mark.django_db
class TestDatabaseConnection:
    """Test cases -for db connection"""
    db_connection = connection

    def test_db_is_connected(self):
        """
        asserts that a database cursor can be opened
        :return:
        """
        cursor = self.db_connection.cursor()
        assert cursor.closed is False

    def test_db_vendor_is_postgres(self):
        """Verify the databases vendors name"""
        assert self.db_connection.vendor == "postgresql"
