import pytest
from unittest.mock import Mock
from mktxp.datasource.package_ds import PackageMetricsDataSource

class TestPackageMetricsDataSource:

    @pytest.fixture
    def mock_router_entry(self):
        router_entry = Mock()
        router_entry.router_name = 'test_router'
        router_entry.config_entry.hostname = '192.168.1.1'

        # Setup API mock chain: router_entry.api_connection.router_api().get_resource('/system/package').get()
        api_conn = Mock()
        router_api = Mock()
        resource = Mock()

        router_api.get_resource.return_value = resource
        api_conn.router_api.return_value = router_api
        router_entry.api_connection = api_conn

        return router_entry, resource

    def test_is_package_installed_v6_style(self, mock_router_entry):
        """Test with RouterOS v6 style where disabled flag is present."""
        router_entry, resource = mock_router_entry
        resource.get.return_value = [
            {'name': 'system'},
            {'name': 'container'},
        ]

        assert PackageMetricsDataSource.is_package_installed(router_entry, 'container') is True
        assert PackageMetricsDataSource.is_package_installed(router_entry, 'dummy') is False
        resource.get.assert_called_with(disabled='false')

    def test_is_package_installed_routeros7_style(self, mock_router_entry):
        """Test with RouterOS v7 records returned by recent package API."""
        router_entry, resource = mock_router_entry
        resource.get.return_value = [
            {'name': 'routeros', 'version': '7.22.2'},
            {'name': 'wifi-qcom', 'version': '7.22.2'},
            {'name': 'container', 'version': '7.22.2'},
        ]

        assert PackageMetricsDataSource.is_package_installed(router_entry, 'container') is True
        assert PackageMetricsDataSource.is_package_installed(router_entry, 'wifi-qcom') is True
        assert PackageMetricsDataSource.is_package_installed(router_entry, 'wireless') is False
        resource.get.assert_called_with(disabled='false')

    def test_is_package_installed_can_include_disabled_packages(self, mock_router_entry):
        router_entry, resource = mock_router_entry
        resource.get.return_value = [
            {'name': 'routeros'},
            {'name': 'wireless'},
        ]

        assert PackageMetricsDataSource.is_package_installed(router_entry, 'wireless', enabled_only=False) is True
        resource.get.assert_called_with()

    def test_is_package_installed_api_error(self, mock_router_entry):
        """Test API error handling."""
        router_entry, resource = mock_router_entry
        resource.get.side_effect = Exception("API connection failed")

        assert PackageMetricsDataSource.is_package_installed(router_entry, 'container') is False
