# -*- coding: utf-8 -*-
"""
TCL表格比对系统 - 网络连接管理模块
负责客户端与服务器的通信、配置管理、模式切换
"""

import os
import json
import requests
from datetime import datetime

class NetworkManager:
    """网络连接管理器"""

    def __init__(self):
        # 配置文件在 data/ 目录
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'network_config.json')
        self.server_url = ''
        self.is_server_mode = False
        self.client_id = ''
        self.server_password = ''
        self.auto_connect = False  # 是否开机自动连接
        self.timeout = 10  # 请求超时时间（秒）

        self.load_config()

    def load_config(self):
        """加载网络配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.server_url = config.get('server_url', '')
                    self.is_server_mode = config.get('is_server_mode', False)
                    self.client_id = config.get('client_id', self._generate_client_id())
                    self.server_password = config.get('server_password', '')
                    self.auto_connect = config.get('auto_connect', False)
            except UnicodeDecodeError:
                # 旧版本可能用GBK编码，尝试GBK读取后用UTF-8重新保存
                try:
                    with open(self.config_file, 'r', encoding='gbk') as f:
                        config = json.load(f)
                        self.server_url = config.get('server_url', '')
                        self.is_server_mode = config.get('is_server_mode', False)
                        self.client_id = config.get('client_id', self._generate_client_id())
                        self.server_password = config.get('server_password', '')
                        self.auto_connect = config.get('auto_connect', False)
                    self.save_config()
                except Exception:
                    self.client_id = self._generate_client_id()
            except Exception:
                self.client_id = self._generate_client_id()
        else:
            self.client_id = self._generate_client_id()
            self.save_config()

    def save_config(self):
        """保存网络配置"""
        config = {
            'server_url': self.server_url,
            'is_server_mode': self.is_server_mode,
            'client_id': self.client_id,
            'server_password': self.server_password,
            'auto_connect': self.auto_connect,
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] 保存网络配置失败: {e}")

    def _generate_client_id(self):
        """生成唯一的客户端ID"""
        import platform
        import uuid
        hostname = platform.node()
        unique_id = str(uuid.uuid4())[:8]
        return f"{hostname}_{unique_id}"

    def _get_headers(self):
        """获取请求头（包含客户端ID和认证信息）"""
        headers = {'X-Client-ID': self.client_id}
        if self.server_password:
            headers['X-Auth-Token'] = self.server_password
        return headers

    def set_server_mode(self, server_url, is_enabled=True, password='', auto_connect=None):
        """
        设置服务器模式

        Args:
            server_url: 服务器地址 (例如: http://192.168.1.100:5000)
            is_enabled: 是否启用服务器模式
            password: 连接密码
            auto_connect: 是否开机自动连接（None表示不修改）
        """
        self.server_url = server_url.rstrip('/')
        self.is_server_mode = is_enabled
        if password:
            self.server_password = password
        if auto_connect is not None:
            self.auto_connect = auto_connect
        self.save_config()

        if is_enabled:
            print(f"[OK] 已切换到服务器模式: {self.server_url}")
        else:
            print("[OK] 已切换到本地模式")

    def test_connection(self):
        """
        测试与服务器的连接

        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.server_url or not self.is_server_mode:
            return False, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/health"
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                return True, f"连接成功 - 服务器版本: {data.get('version', 'unknown')}"
            else:
                return False, f"服务器返回错误: HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "无法连接到服务器，请检查：\n1. 服务器是否启动\n2. IP地址和端口是否正确\n3. 防火墙设置"
        except requests.exceptions.Timeout:
            return False, "连接超时，请检查网络"
        except Exception as e:
            return False, f"连接错误: {str(e)}"

    # ==================== 数据库管理 API ====================

    def save_db_data(self, headers, data):
        """保存数据库数据到服务器"""
        if not self.is_server_mode:
            return None, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/db/data"
            response = requests.post(
                url,
                json={'headers': headers, 'data': data},
                headers=self._get_headers(),
                timeout=self.timeout
            )

            result = response.json()
            if result.get('success'):
                return True, result.get('message', '保存成功')
            else:
                return False, result.get('error', '保存失败')
        except Exception as e:
            return False, f"网络错误: {str(e)}"

    def load_db_data(self):
        """从服务器加载数据库数据"""
        if not self.is_server_mode:
            return None, None, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/db/data"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )

            result = response.json()
            if result.get('success'):
                return result.get('headers', []), result.get('data', []), None
            else:
                return None, None, result.get('error', '加载失败')
        except Exception as e:
            return None, None, f"网络错误: {str(e)}"

    def delete_db_data(self, item_ids=None):
        """删除数据库数据"""
        if not self.is_server_mode:
            return False, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/db/data"
            data = {'ids': item_ids} if item_ids else {}
            response = requests.delete(
                url,
                json=data,
                headers=self._get_headers(),
                timeout=self.timeout
            )

            result = response.json()
            if result.get('success'):
                return True, result.get('message', '删除成功')
            else:
                return False, result.get('error', '删除失败')
        except Exception as e:
            return False, f"网络错误: {str(e)}"

    # ==================== 批量导入 API ====================

    def save_batch_import_data(self, headers, data):
        """保存批量导入数据到服务器"""
        if not self.is_server_mode:
            return None, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/batch/data"
            response = requests.post(
                url,
                json={'headers': headers, 'data': data},
                headers=self._get_headers(),
                timeout=self.timeout
            )

            result = response.json()
            if result.get('success'):
                return True, result.get('message', '保存成功')
            else:
                return False, result.get('error', '保存失败')
        except Exception as e:
            return False, f"网络错误: {str(e)}"

    def load_batch_import_data(self):
        """从服务器加载批量导入数据"""
        if not self.is_server_mode:
            return None, None, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/batch/data"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )

            result = response.json()
            if result.get('success'):
                return result.get('headers', []), result.get('data', []), None
            else:
                return None, None, result.get('error', '加载失败')
        except Exception as e:
            return None, None, f"网络错误: {str(e)}"

    def delete_batch_import_items(self, indices=None):
        """删除批量导入的指定项"""
        if not self.is_server_mode:
            return False, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/batch/data"
            data = {'indices': indices} if indices else {}
            response = requests.delete(
                url,
                json=data,
                headers=self._get_headers(),
                timeout=self.timeout
            )

            result = response.json()
            if result.get('success'):
                return True, result.get('message', '删除成功')
            else:
                return False, result.get('error', '删除失败')
        except Exception as e:
            return False, f"网络错误: {str(e)}"

    # ==================== 配置 API ====================

    def save_config_to_server(self, key, value):
        """保存配置到服务器"""
        if not self.is_server_mode:
            return False, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/config/{key}"
            response = requests.post(
                url,
                json={'value': value},
                headers=self._get_headers(),
                timeout=self.timeout
            )

            result = response.json()
            return result.get('success', False), result.get('error', '操作完成')
        except Exception as e:
            return False, f"网络错误: {str(e)}"

    def load_config_from_server(self, key, default=None):
        """从服务器加载配置"""
        if not self.is_server_mode:
            return default, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/config/{key}"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )

            result = response.json()
            if result.get('success'):
                return result.get('value'), None
            else:
                return default, result.get('error', '加载失败')
        except Exception as e:
            return default, f"网络错误: {str(e)}"

    # ==================== 服务器信息 ====================

    def get_server_stats(self):
        """获取服务器统计信息"""
        if not self.is_server_mode:
            return None, "未启用服务器模式"

        try:
            url = f"{self.server_url}/api/stats"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            return response.json(), None
        except Exception as e:
            return None, f"网络错误: {str(e)}"

    def check_server_changes(self):
        """
        检查服务器数据是否有变更（轻量级，不拉取完整数据）

        Returns:
            tuple: (changed: bool, error: str|None)
        """
        if not self.is_server_mode or not self.server_url:
            return False, None

        try:
            url = f"{self.server_url}/api/sync/check"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json(), None
            return None, f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return None, "连接失败"
        except requests.exceptions.Timeout:
            return None, "连接超时"
        except Exception as e:
            return None, str(e)

    def get_local_ip(self):
        """获取本机IP地址（用于显示给用户）"""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"


# 全局单例
network_manager = NetworkManager()


# 测试代码
if __name__ == "__main__":
    nm = NetworkManager()

    print("=" * 60)
    print("网络管理器测试")
    print("=" * 60)

    print(f"\n客户端ID: {nm.client_id}")
    print(f"本机IP: {nm.get_local_ip()}")
    print(f"当前模式: {'服务器模式' if nm.is_server_mode else '本地模式'}")
    print(f"服务器地址: {nm.server_url or '(未设置)'}")

    print("\n测试连接功能...")
    success, msg = nm.test_connection()
    print(f"连接结果: {msg}")

    print("\n[OK] 网络管理器初始化完成")
