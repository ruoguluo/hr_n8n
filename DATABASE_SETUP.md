# MySQL数据库设置说明

## 安装MySQL

### macOS用户:
```bash
# 使用Homebrew安装MySQL
brew install mysql

# 启动MySQL服务
brew services start mysql

# 设置root密码（可选）
mysql_secure_installation
```

### 其他系统:
请访问 https://dev.mysql.com/downloads/mysql/ 下载并安装MySQL

## 配置数据库

1. 连接到MySQL:
```bash
mysql -u root -p
```

2. 创建数据库:
```sql
CREATE DATABASE hr_jd_system;
USE hr_jd_system;
```

3. 运行数据库表创建脚本:
```bash
mysql -u root -p hr_jd_system < database_schema.sql
```

## 修改数据库配置

在 `server.py` 文件中修改数据库配置:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'hr_jd_system',
    'user': 'root',
    'password': 'your_password_here',  # 修改为你的MySQL密码
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}
```

## 测试连接

启动服务器后，如果看到"数据库表初始化成功"消息，说明连接正常。
如果看到连接错误，请检查:

1. MySQL服务是否正在运行
2. 用户名和密码是否正确
3. 数据库是否存在

## 注意事项

- 如果没有安装MySQL，应用仍然可以运行，但Position Information表单提交会失败
- 建议在生产环境中使用更安全的数据库配置
- 可以考虑使用环境变量来存储敏感的数据库配置信息