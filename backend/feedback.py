"""
用户反馈模块 - 匿名反馈收集与存储
数据存储在 Render 提供的 PostgreSQL 数据库中
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL 数据库连接配置
# 从环境变量读取，如果不存在则使用默认值（仅用于开发测试）
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://web_render_feedback_user:1oht9JHK8Mcx4jE5m0p2TxlA13TDacT3@dpg-d7ed6skvikkc73en0hm0-a/web_render_feedback"
)


def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise


def init_feedback_table():
    """初始化反馈表 - 如果不存在则创建"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 创建反馈表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_feedback (
            id SERIAL PRIMARY KEY,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            feedback_text TEXT,
            experience_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_agent TEXT,
            ip_address INET
        );
        """
        
        # 创建索引
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON user_feedback(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_feedback_rating ON user_feedback(rating);
        """
        
        cursor.execute(create_table_sql)
        cursor.execute(create_index_sql)
        conn.commit()
        
        logger.info("反馈表初始化成功")
        return True
        
    except Exception as e:
        logger.error(f"初始化反馈表失败: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def submit_feedback(
    rating: int,
    feedback_text: Optional[str] = None,
    experience_type: Optional[str] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    提交用户反馈
    
    Args:
        rating: 评分 (1-5星)
        feedback_text: 反馈文字内容
        experience_type: 体验类型（如：界面设计、分析内容、整体体验等）
        user_agent: 用户浏览器信息
        ip_address: 用户IP地址（仅用于防止滥用，不关联个人身份）
    
    Returns:
        包含提交结果的字典
    """
    # 验证评分
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return {
            "success": False,
            "error": "评分必须是1-5之间的整数"
        }
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        insert_sql = """
        INSERT INTO user_feedback (rating, feedback_text, experience_type, user_agent, ip_address)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, created_at;
        """
        
        cursor.execute(insert_sql, (
            rating,
            feedback_text if feedback_text else None,
            experience_type if experience_type else None,
            user_agent if user_agent else None,
            ip_address if ip_address else None
        ))
        
        result = cursor.fetchone()
        conn.commit()
        
        logger.info(f"反馈提交成功，ID: {result['id']}")
        
        return {
            "success": True,
            "message": "感谢您的反馈！",
            "feedback_id": result["id"],
            "created_at": result["created_at"].isoformat() if result["created_at"] else None
        }
        
    except Exception as e:
        logger.error(f"提交反馈失败: {str(e)}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "error": f"提交失败，请稍后重试: {str(e)}"
        }
    finally:
        if conn:
            conn.close()


def get_feedback_stats() -> Dict[str, Any]:
    """获取反馈统计信息（用于管理后台）"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 统计各评分数量
        stats_sql = """
        SELECT 
            rating,
            COUNT(*) as count,
            AVG(rating) as avg_rating
        FROM user_feedback
        GROUP BY rating
        ORDER BY rating;
        """
        
        cursor.execute(stats_sql)
        stats = cursor.fetchall()
        
        # 总反馈数
        cursor.execute("SELECT COUNT(*) as total FROM user_feedback;")
        total_result = cursor.fetchone()
        
        return {
            "success": True,
            "total_feedback": total_result["total"] if total_result else 0,
            "rating_distribution": [
                {"rating": row["rating"], "count": row["count"]} 
                for row in stats
            ],
            "average_rating": round(float(stats[0]["avg_rating"]), 2) if stats else 0
        }
        
    except Exception as e:
        logger.error(f"获取反馈统计失败: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        if conn:
            conn.close()


# 初始化表（在模块导入时执行）
init_feedback_table()
