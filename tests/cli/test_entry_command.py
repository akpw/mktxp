import pytest
from unittest.mock import Mock, patch, MagicMock
from routeros_exporter.cli.dispatch import RouterOSExporterDispatcher


class TestEntryCommand:
    """测试 entry 命令的功能"""
    
    @patch('routeros_exporter.cli.dispatch.config_handler')
    @patch('builtins.print')
    def test_create_new_entry_success(self, mock_print, mock_config_handler):
        """测试成功创建新的配置条目"""
        # 设置 mock
        mock_config_handler.registered_entry.return_value = None
        mock_config = MagicMock()
        mock_config.comments = {}
        mock_config_handler.config = mock_config
        mock_config_handler.usr_conf_data_path = '/test/path/routeros_exporter.conf'

        # 创建 dispatcher
        dispatcher = RouterOSExporterDispatcher()

        # 准备参数
        args = {
            'entry_name': 'TestRouter',
            'hostname': '192.168.1.1',
            'port': 8728,
            'username': 'admin',
            'password': 'test123'
        }

        # 执行创建
        dispatcher.create_entry(args)

        # 验证配置已创建 - 检查 __setitem__ 调用
        mock_config.__setitem__.assert_called()
        # 验证成功消息
        mock_print.assert_any_call('成功创建配置条目 [TestRouter]')
        # 验证 write 方法被调用
        mock_config.write.assert_called_once()
    
    @patch('routeros_exporter.cli.dispatch.config_handler')
    @patch('builtins.print')
    def test_create_entry_already_exists(self, mock_print, mock_config_handler):
        """测试创建已存在的配置条目时的错误处理"""
        # 设置 mock - 条目已存在
        mock_config_handler.registered_entry.return_value = {'hostname': '192.168.1.1'}
        
        # 创建 dispatcher
        dispatcher = RouterOSExporterDispatcher()
        
        # 准备参数
        args = {
            'entry_name': 'ExistingRouter',
            'hostname': '192.168.1.2'
        }
        
        # 执行创建
        dispatcher.create_entry(args)
        
        # 验证错误消息
        mock_print.assert_any_call('错误: 配置条目 [ExistingRouter] 已存在')
        mock_print.assert_any_call('使用 "routeros_exporter edit" 命令编辑现有条目')
    
    @patch('routeros_exporter.cli.dispatch.config_handler')
    @patch('builtins.print')
    def test_create_entry_minimal_params(self, mock_print, mock_config_handler):
        """测试只使用必需参数创建配置条目"""
        # 设置 mock
        mock_config_handler.registered_entry.return_value = None
        mock_config = MagicMock()
        mock_config.comments = {}
        mock_config_handler.config = mock_config
        mock_config_handler.usr_conf_data_path = '/test/path/routeros_exporter.conf'

        # 创建 dispatcher
        dispatcher = RouterOSExporterDispatcher()

        # 准备参数 - 只有名称
        args = {
            'entry_name': 'MinimalRouter'
        }

        # 执行创建
        dispatcher.create_entry(args)

        # 验证配置已创建
        mock_config.__setitem__.assert_called()
        # 验证成功消息
        mock_print.assert_any_call('成功创建配置条目 [MinimalRouter]')
        # 验证 write 方法被调用
        mock_config.write.assert_called_once()
    
    @patch('routeros_exporter.cli.dispatch.config_handler')
    def test_create_entry_with_comments(self, mock_config_handler):
        """测试创建配置条目时添加注释"""
        # 设置 mock
        mock_config_handler.registered_entry.return_value = None
        mock_config = MagicMock()
        mock_config.comments = {}
        mock_config_handler.config = mock_config
        mock_config_handler.usr_conf_data_path = '/test/path/routeros_exporter.conf'

        # 创建 dispatcher
        dispatcher = RouterOSExporterDispatcher()

        # 准备参数
        args = {
            'entry_name': 'CommentedRouter',
            'hostname': '192.168.1.1'
        }

        # 执行创建
        dispatcher.create_entry(args)

        # 验证注释已添加
        assert 'CommentedRouter' in mock_config.comments
        comments = mock_config.comments['CommentedRouter']
        assert any('RouterOS device configuration' in comment for comment in comments)

