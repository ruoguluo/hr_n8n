#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import json
from datetime import datetime

# Configuration
PORT = 8002
HTML_DIRECTORY = "html"

# MySQL数据库配置
DB_CONFIG = {
    'host': '107.182.26.178',
    'database': 'hr_jd_system',
    'user': 'root',
    'password': 'secret-2025',  # 请根据实际情况修改密码
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

app = Flask(__name__)
CORS(app)  # 允许跨域请求

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

def init_database():
    """初始化数据库表"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # 创建数据库（如果不存在）
            cursor.execute("CREATE DATABASE IF NOT EXISTS hr_jd_system")
            cursor.execute("USE hr_jd_system")
            
            # 创建company_registration表（一个公司可以有多个JD）
            create_company_table_query = """
            CREATE TABLE IF NOT EXISTS company_registration (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_id VARCHAR(255) UNIQUE NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                website VARCHAR(500) NOT NULL,
                contact_person VARCHAR(255) NOT NULL,
                contact_number VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_company_table_query)
            
            # 创建position_information表（JD表，关联到公司）
            create_table_query = """
            CREATE TABLE IF NOT EXISTS position_information (
                id INT AUTO_INCREMENT PRIMARY KEY,
                jd_id VARCHAR(255) UNIQUE NOT NULL,
                company_id VARCHAR(255) NOT NULL,
                job_title VARCHAR(255) NOT NULL,
                location VARCHAR(500) NOT NULL,
                team_structure TEXT,
                position_type ENUM('new', 'replacement') NOT NULL,
                new_reason TEXT,
                reason_leave TEXT,
                background_last TEXT,
                compliments_concerns TEXT,
                hiring_when VARCHAR(255),
                hiring_problems TEXT,
                emergency_level ENUM('low', 'medium', 'high', 'critical'),
                interview_rounds TEXT,
                compensation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES company_registration(company_id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_table_query)
            
            # 创建company_registration表索引
            company_indexes = [
                "CREATE INDEX idx_company_id ON company_registration(company_id)",
                "CREATE INDEX idx_company_name ON company_registration(company_name)",
                "CREATE INDEX idx_company_created_at ON company_registration(created_at)"
            ]
            
            for index_query in company_indexes:
                try:
                    cursor.execute(index_query)
                except Error as e:
                    if "Duplicate key name" not in str(e) and "already exists" not in str(e):
                        print(f"创建公司表索引错误: {e}")
            
            # 创建position_information表索引
            position_indexes = [
                "CREATE INDEX idx_jd_id ON position_information(jd_id)",
                "CREATE INDEX idx_position_company_id ON position_information(company_id)",
                "CREATE INDEX idx_position_type ON position_information(position_type)",
                "CREATE INDEX idx_emergency_level ON position_information(emergency_level)",
                "CREATE INDEX idx_position_created_at ON position_information(created_at)"
            ]
            
            for index_query in position_indexes:
                try:
                    cursor.execute(index_query)
                except Error as e:
                    if "Duplicate key name" not in str(e) and "already exists" not in str(e):
                        print(f"创建职位表索引错误: {e}")
            
            connection.commit()
            print("数据库表初始化成功")
            
    except Error as e:
        print(f"数据库初始化错误: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/')
def index():
    """提供主页"""
    return send_from_directory(HTML_DIRECTORY, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """提供静态文件"""
    return send_from_directory(HTML_DIRECTORY, filename)

@app.route('/api/position-info', methods=['POST'])
def save_position_info():
    """保存Position Information表单数据到MySQL数据库"""
    try:
        # 获取表单数据
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '没有接收到数据'}), 400
        
        # 验证必填字段
        required_fields = ['company_id', 'location', 'position_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
        
        # 连接数据库
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败'}), 500
        
        cursor = connection.cursor()
        
        # 生成jd_id（使用时间戳+JD前缀）
        import time
        timestamp = str(int(time.time()))
        jd_id = f"JD_{timestamp}"
        
        # 插入数据
        insert_query = """
        INSERT INTO position_information (
            jd_id, company_id, job_title, location, team_structure, position_type, new_reason,
            reason_leave, background_last, compliments_concerns, hiring_when,
            hiring_problems, emergency_level, interview_rounds, compensation
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            jd_id,
            data.get('company_id'),
            data.get('job_title'),
            data.get('location'),
            data.get('team_structure', ''),
            data.get('position_type'),
            data.get('new_reason', ''),
            data.get('reason_leave', ''),
            data.get('background_last', ''),
            data.get('compliments_concerns', ''),
            data.get('hiring_when', ''),
            data.get('hiring_problems', ''),
            data.get('emergency_level', ''),
            data.get('interview_rounds', ''),
            data.get('compensation', '')
        )
        
        cursor.execute(insert_query, values)
        connection.commit()
        
        # 获取插入的记录ID
        position_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Position Information保存成功',
            'jd_id': jd_id,
            'position_id': position_id
        }), 200
        
    except Error as e:
        print(f"数据库操作错误: {e}")
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/position-info/<company_id>', methods=['GET'])
def get_position_info(company_id):
    """根据company_id获取Position Information数据"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM position_information WHERE company_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (company_id,))
        
        results = cursor.fetchall()
        
        # 转换datetime对象为字符串
        for result in results:
            if result.get('created_at'):
                result['created_at'] = result['created_at'].isoformat()
            if result.get('updated_at'):
                result['updated_at'] = result['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'data': results
        }), 200
        
    except Error as e:
        print(f"数据库查询错误: {e}")
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/company-registration', methods=['POST'])
def save_company_registration():
    """保存Company Registration表单数据到MySQL数据库"""
    try:
        # 获取表单数据
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '没有接收到数据'}), 400
        
        # 验证必填字段
        required_fields = ['company_name', 'website', 'contact_person', 'contact_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
        
        # 连接数据库
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败'}), 500
        
        cursor = connection.cursor()
        
        # 生成company_id（使用时间戳+公司名称前缀）
        import time
        import hashlib
        timestamp = str(int(time.time()))
        company_prefix = data.get('company_name', '')[:3].upper()
        company_id = f"{company_prefix}_{timestamp}"
        
        # 插入数据
        insert_query = """
        INSERT INTO company_registration (
            company_id, company_name, website, contact_person, contact_number
        ) VALUES (%s, %s, %s, %s, %s)
        """
        
        values = (
            company_id,
            data.get('company_name'),
            data.get('website'),
            data.get('contact_person'),
            data.get('contact_number')
        )
        
        cursor.execute(insert_query, values)
        connection.commit()
        
        # 获取插入的记录ID
        registration_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Company Registration保存成功',
            'company_id': company_id,
            'registration_id': registration_id
        }), 200
        
    except Error as e:
        print(f"数据库操作错误: {e}")
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/company-registration/<company_id>', methods=['GET'])
def get_company_registration(company_id):
    """根据company_id获取Company Registration数据"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM company_registration WHERE company_id = %s"
        cursor.execute(query, (company_id,))
        
        result = cursor.fetchone()
        
        if result:
            # 转换datetime对象为字符串
            if result.get('created_at'):
                result['created_at'] = result['created_at'].isoformat()
            if result.get('updated_at'):
                result['updated_at'] = result['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Error as e:
        print(f"数据库查询错误: {e}")
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """获取所有公司列表"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM company_registration ORDER BY created_at DESC"
        cursor.execute(query)
        
        results = cursor.fetchall()
        
        # 转换datetime对象为字符串
        for result in results:
            if result.get('created_at'):
                result['created_at'] = result['created_at'].isoformat()
            if result.get('updated_at'):
                result['updated_at'] = result['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'data': results
        }), 200
        
    except Error as e:
        print(f"数据库查询错误: {e}")
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/jd/<jd_id>', methods=['GET'])
def get_jd_by_id(jd_id):
    """根据jd_id获取单个JD数据"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM position_information WHERE jd_id = %s"
        cursor.execute(query, (jd_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'message': 'JD不存在'}), 404
        
        # 转换datetime对象为字符串
        if result.get('created_at'):
            result['created_at'] = result['created_at'].isoformat()
        if result.get('updated_at'):
            result['updated_at'] = result['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Error as e:
        print(f"数据库查询错误: {e}")
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/jd-detail/<jd_id>', methods=['GET'])
def get_jd_detail(jd_id):
    """获取JD详细信息用于模态框显示"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': '数据库连接失败'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM position_information WHERE jd_id = %s"
        cursor.execute(query, (jd_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'error': 'JD不存在'}), 404
        
        # 转换datetime对象为字符串
        if result.get('created_at'):
            result['created_at'] = result['created_at'].isoformat()
        if result.get('updated_at'):
            result['updated_at'] = result['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'jd': result
        }), 200
        
    except Error as e:
        print(f"数据库查询错误: {e}")
        return jsonify({'success': False, 'error': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/jd/<jd_id>', methods=['DELETE'])
def delete_jd(jd_id):
    """删除指定的JD"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': '数据库连接失败'}), 500
        
        cursor = connection.cursor()
        
        # 首先检查JD是否存在
        check_query = "SELECT jd_id FROM position_information WHERE jd_id = %s"
        cursor.execute(check_query, (jd_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'message': 'JD不存在'}), 404
        
        # 删除JD
        delete_query = "DELETE FROM position_information WHERE jd_id = %s"
        cursor.execute(delete_query, (jd_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            return jsonify({
                'success': True,
                'message': 'JD删除成功'
            }), 200
        else:
            return jsonify({'success': False, 'message': 'JD删除失败'}), 500
        
    except Error as e:
        print(f"数据库操作错误: {e}")
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    # 切换到项目目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 检查html目录是否存在
    if not os.path.exists(HTML_DIRECTORY):
        print(f"错误: 目录 '{HTML_DIRECTORY}' 不存在!")
        return
    
    # 初始化数据库
    print("正在初始化数据库...")
    init_database()
    
    # 启动Flask应用
    print(f"从 '{HTML_DIRECTORY}' 目录提供HTML文件")
    print(f"服务器运行在 http://localhost:{PORT}/")
    print("按 Ctrl+C 停止服务器")
    
    app.run(host='0.0.0.0', port=PORT, debug=True)

if __name__ == "__main__":
    main()