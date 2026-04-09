import pytest
from mktxp.cli.config.config import MKTXPConfigKeys, ConfigEntry

def test_bridge_vlan_key_registration():
    """
    Verifies FE_BRIDGE_VLAN_KEY is defined and correctly categorized.
    """
    # Verify the constant is defined
    assert hasattr(MKTXPConfigKeys, 'FE_BRIDGE_VLAN_KEY')
    assert MKTXPConfigKeys.FE_BRIDGE_VLAN_KEY == "bridge_vlan"

    # Verify it is in the list of keys that default to 'No' (False)
    assert MKTXPConfigKeys.FE_BRIDGE_VLAN_KEY in MKTXPConfigKeys.BOOLEAN_KEYS_NO

def test_config_entry_bridge_vlan_attribute():
    """
    Tests that a ConfigEntry instance can hold the bridge_vlan attribute.
    """
    config = ConfigEntry()

    # Manually setting the attribute to simulate how the handler populates it
    config.bridge_vlan = True
    assert config.bridge_vlan is True

    config.bridge_vlan = False
    assert config.bridge_vlan is False

def test_bridge_vlan_presence_in_boolean_keys():
    """
    Ensures that bridge_vlan is not accidentally added to BOOLEAN_KEYS_YES.
    """
    assert MKTXPConfigKeys.FE_BRIDGE_VLAN_KEY not in MKTXPConfigKeys.BOOLEAN_KEYS_YES
