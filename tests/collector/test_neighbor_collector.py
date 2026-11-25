# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from mktxp.collector.neighbor_collector import NeighborCollector


@pytest.mark.parametrize("ipv4_enabled", [False, True])
def test_ipv6_neighbor_metrics_query_ndp_table(ipv4_enabled):
    # Documentation-only addresses and locally administered, synthetic MACs.
    ipv4 = Mock()
    ipv4.get.return_value = [
        {
            "address": "192.0.2.10",
            "interface": "bridge",
            "mac-address": "02:00:00:00:00:10",
            "identity": "switch",
        }
    ]
    ipv6 = Mock()
    ipv6.get.return_value = [
        {
            "address": "2001:db8::20",
            "interface": "bridge",
            "mac-address": "02:00:00:00:00:20",
            "status": "reachable",
            "comment": "client",
        }
    ]
    api = Mock()
    api.get_resource.side_effect = {
        "/ip/neighbor": ipv4,
        "/ipv6/neighbor": ipv6,
    }.__getitem__
    entry = SimpleNamespace(
        router_name="test-router",
        router_id={
            "routerboard_name": "test-router",
            "routerboard_address": "192.0.2.1",
        },
        config_entry=SimpleNamespace(
            neighbor=ipv4_enabled,
            ipv6_neighbor=True,
            custom_labels=None,
            hostname="192.0.2.1",
        ),
        api_connection=SimpleNamespace(router_api=lambda: api),
    )

    metrics = list(NeighborCollector.collect(entry))

    ipv6.get.assert_called_once_with(status="reachable")
    sample = metrics[-1].samples[0]
    assert sample.name == "mktxp_ipv6_neighbor_info"
    assert sample.labels["address"] == "2001:db8::20"
    assert sample.labels["mac_address"] == "02:00:00:00:00:20"
    assert sample.labels["status"] == "reachable"
    if ipv4_enabled:
        ipv4.get.assert_called_once_with()
        assert metrics[0].samples[0].name == "mktxp_neighbor_info"
        assert metrics[0].samples[0].labels["address"] == "192.0.2.10"
    else:
        ipv4.get.assert_not_called()
