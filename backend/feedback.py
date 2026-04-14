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
        
        # 创建反馈表（新版：多维度评分）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_feedback (
            id SERIAL PRIMARY KEY,
            rating_overall INTEGER CHECK (rating_overall >= 1 AND rating_overall <= 5),
            rating_design INTEGER CHECK (rating_design >= 1 AND rating_design <= 5),
            rating_content INTEGER CHECK (rating_content >= 1 AND rating_content <= 5),
            rating_helpful INTEGER CHECK (rating_helpful >= 1 AND rating_helpful <= 5),
            feedback_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_agent TEXT,
            ip_address INET
        );
        """
        
        # 创建索引
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON user_feedback(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_feedback_overall ON user_feedback(rating_overall);
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
    rating_overall: Optional[int] = None,
    rating_design: Optional[int] = None,
    rating_content: Optional[int] = None,
    rating_helpful: Optional[int] = None,
    feedback_text: Optional[str] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    提交用户反馈（多维度评分版）
    
    Args:
        rating_overall: 整体体验评分 (1-5)
        rating_design: 设计美观评分 (1-5)
        rating_content: 分析内容评分 (1-5)
        rating_helpful: 是否有帮助评分 (1-5)
        feedback_text: 反馈文字内容
        user_agent: 用户浏览器信息
        ip_address: 用户IP地址（仅用于防止滥用，不关联个人身份）
    
    Returns:
        包含提交结果的字典
    """
    # 验证评分（至少有一个评分）
    ratings = [rating_overall, rating_design, rating_content, rating_helpful]
    if not any(r is not None and isinstance(r, int) and 1 <= r <= 5 for r in ratings):
        return {
            "success": False,
            "error": "请至少对一个维度进行评分（1-5分）"
        }
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        insert_sql = """
        INSERT INTO user_feedback (rating_overall, rating_design, rating_content, rating_helpful, feedback_text, user_agent, ip_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, created_at;
        """
        
        cursor.execute(insert_sql, (
            rating_overall,
            rating_design,
            rating_content,
            rating_helpful,
            feedback_text if feedback_text else None,
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
        
        # 总反馈数
        cursor.execute("SELECT COUNT(*) as total FROM user_feedback;")
        total_result = cursor.fetchone()
        total = total_result["total"] if total_result else 0
        
        # 各维度平均评分
        avg_sql = """
        SELECT 
            AVG(rating_overall) as avg_overall,
            AVG(rating_design) as avg_design,
            AVG(rating_content) as avg_content,
            AVG(rating_helpful) as avg_helpful
        FROM user_feedback;
        """
        cursor.execute(avg_sql)
        avg_result = cursor.fetchone()
        
        # 各维度评分分布
        dimensions = ['overall', 'design', 'content', 'helpful']
        distribution = {}
        
        for dim in dimensions:
            cursor.execute(f"""
                SELECT rating_{dim} as rating, COUNT(*) as count
                FROM user_feedback
                WHERE rating_{dim} IS NOT NULL
                GROUP BY rating_{dim}
                ORDER BY rating;
            """)
            distribution[dim] = [
                {"rating": row["rating"], "count": row["count"]} 
                for row in cursor.fetchall()
            ]
        
        return {
            "success": True,
            "total_feedback": total,
            "average_ratings": {
                "overall": round(float(avg_result["avg_overall"] or 0), 2),
                "design": round(float(avg_result["avg_design"] or 0), 2),
                "content": round(float(avg_result["avg_content"] or 0), 2),
                "helpful": round(float(avg_result["avg_helpful"] or 0), 2)
            },
            "rating_distribution": distribution
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


def get_admin_feedback_stats() -> Dict[str, Any]:
    """获取管理员反馈统计数据（包含最近评论）"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 总反馈数
        cursor.execute("SELECT COUNT(*) as total FROM user_feedback;")
        total = cursor.fetchone()["total"]
        
        # 计算综合平均评分（所有维度的平均值）
        avg_sql = """
        SELECT 
            AVG((COALESCE(rating_overall, 0) + COALESCE(rating_design, 0) + 
                 COALESCE(rating_content, 0) + COALESCE(rating_helpful, 0))::float / 
                NULLIF((rating_overall IS NOT NULL)::int + (rating_design IS NOT NULL)::int + 
                       (rating_content IS NOT NULL)::int + (rating_helpful IS NOT NULL)::int, 0)
            ) as avg_rating
        FROM user_feedback;
        """
        cursor.execute(avg_sql)
        avg_result = cursor.fetchone()
        avg_rating = round(float(avg_result["avg_rating"] or 0), 1)
        
        # 各星级评分数量（基于 overall 评分）
        cursor.execute("""
            SELECT rating_overall as rating, COUNT(*) as count
            FROM user_feedback
            WHERE rating_overall IS NOT NULL
            GROUP BY rating_overall
            ORDER BY rating;
        """)
        rating_dist = {str(row["rating"]): row["count"] for row in cursor.fetchall()}
        # 填充缺失的星级
        for i in range(1, 6):
            if str(i) not in rating_dist:
                rating_dist[str(i)] = 0
        
        # 最近20条文字评论
        cursor.execute("""
            SELECT 
                id,
                rating_overall,
                rating_design,
                rating_content,
                rating_helpful,
                feedback_text,
                created_at
            FROM user_feedback
            WHERE feedback_text IS NOT NULL AND feedback_text != ''
            ORDER BY created_at DESC
            LIMIT 20;
        """)
        comments = []
        for row in cursor.fetchall():
            comments.append({
                "id": row["id"],
                "ratings": {
                    "overall": row["rating_overall"],
                    "design": row["rating_design"],
                    "content": row["rating_content"],
                    "helpful": row["rating_helpful"]
                },
                "comment": row["feedback_text"],
                "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M:%S") if row["created_at"] else None
            })
        
        return {
            "success": True,
            "total": total,
            "avg_rating": avg_rating,
            "rating_distribution": rating_dist,
            "recent_comments": comments
        }
        
    except Exception as e:
        logger.error(f"获取管理员反馈统计失败: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        if conn:
            conn.close()


def export_feedback_to_csv() -> str:
    """导出所有反馈数据为CSV格式字符串"""
    import csv
    import io
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 获取所有反馈数据
        cursor.execute("""
            SELECT 
                id,
                rating_overall,
                rating_design,
                rating_content,
                rating_helpful,
                feedback_text,
                created_at,
                user_agent,
                ip_address
            FROM user_feedback
            ORDER BY created_at DESC;
        """)
        
        # 创建CSV字符串
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            'id', 'rating_overall', 'rating_design', 'rating_content', 'rating_helpful',
            'feedback_text', 'created_at', 'user_agent', 'ip_address'
        ])
        
        # 写入数据
        for row in cursor.fetchall():
            writer.writerow([
                row['id'],
                row['rating_overall'],
                row['rating_design'],
                row['rating_content'],
                row['rating_helpful'],
                row['feedback_text'] or '',
                row['created_at'].strftime("%Y-%m-%d %H:%M:%S") if row['created_at'] else '',
                row['user_agent'] or '',
                str(row['ip_address']) if row['ip_address'] else ''
            ])
        
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"导出反馈数据失败: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()


# 初始化表（在模块导入时执行）
init_feedback_table()
