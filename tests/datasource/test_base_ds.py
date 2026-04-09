import pytest
from unittest.mock import Mock
from unittest.mock import patch
from mktxp.datasource.base_ds import BaseDSProcessor
from mktxp.cli.config.config import MKTXPConfigKeys
from mktxp.datasource.interface_ds import BaseInterfaceDataSource, BridgeVlanMetricsDataSource

@pytest.mark.parametrize(
    "custom_labels_input, should_have_metadata, expected_custom_labels",
    [
        # Test case 1: Custom labels provided as a string
        (
            'dc:london, service=prod',
            True,
            {'dc': 'london', 'service': 'prod'}
        ),
        # Test case 2: No custom labels provided
        (
            None,
            False,
            None
        ),
        # Test case 3: Custom labels provided as a list
        (
            ['dc:london', 'service=prod', 'rack:a1'],
            True,
            {'dc': 'london', 'service': 'prod', 'rack': 'a1'}
        ),
    ]
)
def test_trimmed_records(custom_labels_input, should_have_metadata, expected_custom_labels):
    """
    Tests that the trimmed_records method correctly handles various custom label inputs.
    """
    mock_router_entry = Mock()
    mock_router_entry.config_entry.custom_labels = custom_labels_input
    mock_router_entry.router_id = {'routerboard_name': 'r1', 'routerboard_address': '1.1.1.1'}
    
    router_records = [{'metric1': 'value1'}]
    metric_labels = ['metric1']

    processed_records = BaseDSProcessor.trimmed_records(
        mock_router_entry,
        router_records=router_records,
        metric_labels=metric_labels
    )

    assert len(processed_records) == 1
    record = processed_records[0]

    if should_have_metadata:
        assert MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID in record
        custom_labels = record[MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID]
        assert custom_labels == expected_custom_labels
    else:
        assert MKTXPConfigKeys.CUSTOM_LABELS_METADATA_ID not in record

    assert record['metric1'] == 'value1'
    assert record['routerboard_name'] == 'r1'


@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        # Valid string inputs
        ('dc:london, rack:a1, service:prod', {'dc': 'london', 'rack': 'a1', 'service': 'prod'}),
        ('dc=london, rack=a1, service=prod', {'dc': 'london', 'rack': 'a1', 'service': 'prod'}),
        ('dc:london, rack=a1, service:prod', {'dc': 'london', 'rack': 'a1', 'service': 'prod'}),
        ('  dc : london  ,  rack = a1  ,   service : prod  ', {'dc': 'london', 'rack': 'a1', 'service': 'prod'}),

        # Valid list/tuple inputs
        (['dc:london', 'rack=a1', 'service:prod'], {'dc': 'london', 'rack': 'a1', 'service': 'prod'}),
        (['  dc : london  ', '  rack = a1  ', '   service : prod  '], {'dc': 'london', 'rack': 'a1', 'service': 'prod'}),
        (('dc:london', 'rack=a1', 'service:prod'), {'dc': 'london', 'rack': 'a1', 'service': 'prod'}),

        # Edge cases and invalid inputs
        ('', {}),
        (None, {}),
        ('    ', {}),
        ([], {}),
        (['dc:london', 'invalid_entry', 'rack:a1'], {'dc': 'london', 'rack': 'a1'}),
        (['dc:london', 123, 'rack:a1'], {'dc': 'london', 'rack': 'a1'}),
        ({'dc': 'london'}, {}),
        (123, {}),
        (True, {}),
    ]
)
def test_parse_custom_labels(test_input, expected_output):
    """
    Tests the _parse_custom_labels method with various valid and invalid inputs.
    """
    # Create a mock router_entry for the method call
    mock_router_entry = Mock()
    mock_router_entry.router_name = "TestRouter"
    
    assert BaseDSProcessor._parse_custom_labels(test_input, mock_router_entry) == expected_output

def test_parse_custom_labels_with_warning(capsys):
    """
    Tests that a warning is printed for malformed custom labels.
    """
    test_input = 'dc:london, invalid_entry, rack:a1'
    expected_output = {'dc': 'london', 'rack': 'a1'}
    
    # Create a mock router_entry for the method call
    mock_router_entry = Mock()
    mock_router_entry.router_name = "TestRouter"
    
    # Mock config_handler to enable verbose mode so warnings are printed
    from unittest.mock import patch
    with patch('mktxp.datasource.base_ds.config_handler') as mock_config_handler:
        mock_config_handler.system_entry.verbose_mode = True
        assert BaseDSProcessor._parse_custom_labels(test_input, mock_router_entry) == expected_output
        
    captured = capsys.readouterr()
    assert "Warning: Configuration for TestRouter contains a malformed custom label ' invalid_entry'. It should be in 'key:value' or 'key=value' format. Ignoring." in captured.out

def test_parse_custom_labels_with_none_string():
    """
    Tests that the string 'None' is handled correctly.
    """
    # Create a mock router_entry for the method call
    mock_router_entry = Mock()
    mock_router_entry.router_name = "TestRouter"

    assert BaseDSProcessor._parse_custom_labels('None', mock_router_entry) == {}

def test_bridge_vlan_metric_records():
    """
    Tests that BridgeVlanMetricsDataSource correctly fetches, flattens,
    and formats bridge VLAN records.
    """
    mock_router_entry = Mock()
    mock_resource = Mock()

    # Mock the API chain: router_entry -> api_connection -> router_api() -> get_resource()
    mock_router_entry.api_connection.router_api.return_value.get_resource.return_value = mock_resource

    # Define raw MikroTik API return data
    mock_resource.call.return_value = [
        {
            'bridge': 'bridge-local',
            'vlan-ids': '10',
            'current-tagged': 'sfp-sfpplus1',
            'current-untagged': 'ether1'
        }
    ]

    # Patch the BaseDSProcessor.trimmed_records method to capture what is passed to it
    with patch('mktxp.datasource.base_ds.BaseDSProcessor.trimmed_records') as mock_trimmed:

        BridgeVlanMetricsDataSource.metric_records(mock_router_entry)

        # Ensure the API was called with the correct proplist
        mock_resource.call.assert_called_once_with('print', {'proplist': 'bridge,vlan-ids,current-tagged,current-untagged'})

        # Inspect the records sent to the final processor
        args, kwargs = mock_trimmed.call_args
        processed_records = kwargs['router_records']

        assert len(processed_records) == 1
        record = processed_records[0]

        # Verify your custom formatting logic
        assert record['name'] == 'bridge-local-vlan-10'
        assert record['bridge'] == 'bridge-local'
        assert record['vlan_ids'] == '10'
        assert record['current_tagged'] == 'sfp-sfpplus1'
        assert record['current_untagged'] == 'ether1'

def test_bridge_vlan_metric_records_exception(capsys):
    """
    Tests that exceptions in the BridgeVlanMetricsDataSource are caught and logged.
    """
    mock_router_entry = Mock()
    # Force an exception when calling the API
    mock_router_entry.api_connection.router_api.side_effect = Exception("Connection Timeout")

    result = BridgeVlanMetricsDataSource.metric_records(mock_router_entry)

    assert result is None
    captured = capsys.readouterr()
    assert "Error in BridgeVlanMetricsDataSource: Connection Timeout" in captured.out
