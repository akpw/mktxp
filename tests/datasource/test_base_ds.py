import pytest
from unittest.mock import Mock
from mktxp.datasource.base_ds import BaseDSProcessor
from mktxp.cli.config.config import MKTXPConfigKeys

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

