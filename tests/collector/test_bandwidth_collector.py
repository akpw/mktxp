import pytest
from unittest.mock import MagicMock, patch
from mktxp.collector.bandwidth_collector import BandwidthCollector
from mktxp.cli.config.config import config_handler
from types import SimpleNamespace

def test_bandwidth_collector_queue_leak_prevention():
    collector = BandwidthCollector()
    
    # Mock config to enable bandwidth
    with patch('mktxp.collector.bandwidth_collector.config_handler.system_entry', 
               SimpleNamespace(bandwidth=True, bandwidth_test_interval=0, bandwidth_test_dns_server='8.8.8.8', verbose_mode=False)):
        
        # Mock multiprocessing pool
        mock_pool = MagicMock()
        mock_job = MagicMock()
        mock_job.ready.return_value = False  # Simulate job is still running
        mock_pool.apply_async.return_value = mock_job
        
        with patch('mktxp.collector.bandwidth_collector.get_context') as mock_get_context:
            mock_get_context.return_value.Pool.return_value = mock_pool
            
            # First collect should spawn a job
            list(collector.collect())
            assert mock_pool.apply_async.call_count == 1
            
            # Second collect should skip spawning because the job isn't ready
            list(collector.collect())
            assert mock_pool.apply_async.call_count == 1
            
            # If we make the job ready, it should spawn a new job
            mock_job.ready.return_value = True
            list(collector.collect())
            assert mock_pool.apply_async.call_count == 2
