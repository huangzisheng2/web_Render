"""
调试测试文件 - 用于排查用户模式和调试模式AI分析结果不一致的问题

访问地址：
- GET /api/test/debug-info?birth_date=2000-01-01&hour=12&gender=male
  返回：用户模式和调试模式的完整数据对比
"""

import os
import sys
from pathlib import Path

# 添加命理模块路径
BASE_DIR = Path(__file__).parent
BAZI_DIR = BASE_DIR / "bazi_modules"
sys.path.insert(0, str(BAZI_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from services.bazi_service_web import BaziAnalysisServiceWeb

app = FastAPI(title="调试测试 API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bazi_service = BaziAnalysisServiceWeb()


@app.get("/api/test/debug-info")
def debug_info(
    name: str = "测试用户",
    year: int = 2000,
    month: int = 1,
    day: int = 1,
    hour: int = 12,
    minute: int = 0,
    gender: str = "male",
    province: str = "北京",
    city: str = "北京"
):
    """
    调试接口：返回用户模式和调试模式的完整数据对比
    """
    birth_data = {
        "name": name,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "gender": gender,
        "province": province,
        "city": city,
    }
    
    # 1. 执行基础分析（获取完整数据）
    full_result = bazi_service.analyze_basic(birth_data)
    
    # 2. 提取构建AI提示词所需的数据
    bazi_data = full_result.get("bazi", {})
    analysis_data = full_result.get("raw_data", {})
    user_info = {
        "name": full_result.get("user_info", {}).get("name", "匿名"),
        "gender": "male" if full_result.get("user_info", {}).get("gender") == "男" else "female",
    }
    
    # 3. 构建AI提示词（关键！）
    ai_prompt = bazi_service._build_ai_prompt(bazi_data, analysis_data, user_info)
    
    # 4. 执行AI分析
    ai_report = bazi_service.analyze_ai(full_result["report_id"], full_result)
    
    return {
        "success": True,
        "input_data": birth_data,
        
        # ===== 关键数据：用于排查AI分析差异 =====
        "debug_data": {
            # 四柱数据
            "bazi": bazi_data,
            
            # 原始分析数据（用户模式下这个数据不会返回给前端）
            "raw_data": analysis_data,
            
            # AI提示词（关键！两种模式必须使用相同的提示词）
            "ai_prompt": ai_prompt,
            
            # AI生成的报告
            "ai_report": ai_report,
        },
        
        # ===== 用户模式实际返回的数据 =====
        "user_mode_response": {
            "ai_report": ai_report,
            # 注意：用户模式下不会返回 raw_data, bazi, user_info 等
        },
        
        # ===== 调试模式返回的数据 =====
        "debug_mode_response": {
            "report_id": full_result["report_id"],
            "user_info": full_result.get("user_info", {}),
            "bazi": bazi_data,
            "analysis": full_result.get("analysis", {}),
            "raw_data": analysis_data,
            "ai_prompt": ai_prompt,
            # 注意：调试模式下 ai_report 需要前端手动调用 /api/analyze-ai 获取
        },
        
        # ===== 差异对比 =====
        "comparison": {
            "user_mode_data_keys": ["ai_report"],
            "debug_mode_data_keys": ["report_id", "user_info", "bazi", "analysis", "raw_data", "ai_prompt"],
            "ai_analysis_source": "两种模式都使用相同的 analyze_ai() 方法和 _build_ai_prompt() 方法",
            "potential_issue": "如果结果不同，可能是因为：\n1. 提示词构建时使用了不同的数据\n2. AI API 调用参数不同\n3. 时间戳或随机因素",
        }
    }


@app.get("/api/test/compare-modes")
def compare_modes(
    name: str = "测试用户",
    year: int = 2000,
    month: int = 1,
    day: int = 1,
    hour: int = 12,
    minute: int = 0,
    gender: str = "male",
    province: str = "北京",
    city: str = "北京"
):
    """
    对比接口：直接对比两种模式的AI分析结果
    """
    birth_data = {
        "name": name,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "gender": gender,
        "province": province,
        "city": city,
    }
    
    # 模拟用户模式：后端直接执行AI分析
    full_result = bazi_service.analyze_basic(birth_data)
    user_mode_report = bazi_service.analyze_ai(full_result["report_id"], full_result)
    
    # 模拟调试模式：前端传递 basic_result 给 /api/analyze-ai
    # 注意：调试模式下前端传递的 basic_result 包含 raw_data
    debug_mode_report = bazi_service.analyze_ai(full_result["report_id"], full_result)
    
    return {
        "success": True,
        "input": birth_data,
        "comparison": {
            "user_mode_report": user_mode_report,
            "debug_mode_report": debug_mode_report,
            "are_identical": user_mode_report == debug_mode_report,
            "user_mode_length": len(user_mode_report),
            "debug_mode_length": len(debug_mode_report),
        },
        "note": "如果 are_identical 为 false，说明两次AI调用结果不同（可能是AI的随机性）"
    }


@app.get("/api/test/raw-data-structure")
def raw_data_structure():
    """
    返回 raw_data 的数据结构说明
    """
    return {
        "success": True,
        "description": "raw_data 是AI分析所需的核心数据，包含以下关键字段",
        "structure": {
            "第一论级_月令与格局": {
                "description": "八字基础信息",
                "key_fields": ["日主", "月令", "身强身弱", "主要格局", "十神"]
            },
            "第二论级_地支关系": {
                "description": "地支刑冲合害关系",
                "key_fields": ["地支关系"]
            },
            "第三论级_天干关系": {
                "description": "天干生克制化关系",
                "key_fields": ["天干关系"]
            },
            "第四论级_天干与地支的关系": {
                "description": "干支组合关系",
                "key_fields": ["干支关系"]
            },
            "第五论级_定喜忌": {
                "description": "喜用神分析",
                "key_fields": ["用神", "喜神", "忌神"]
            },
            "第五论级_辅助信息": {
                "description": "神煞等辅助信息",
                "key_fields": ["神煞", "纳音", "十二长生"]
            },
            "第六论级_大运流年": {
                "description": "大运流年分析",
                "key_fields": ["大运表", "当前大运", "岁运分析"]
            },
            "格局综合判定": {
                "description": "综合格局判定",
                "key_fields": ["主格局", "五行能量分析", "十神能量分析"]
            },
            "基础信息综合分析": {
                "description": "基础信息汇总",
                "key_fields": ["日元", "日支", "月令", "五行旺相", "调候用神"]
            },
        },
        "usage_in_ai": "这些数据被 _build_ai_prompt() 方法用于构建AI分析的提示词"
    }


if __name__ == "__main__":
    import uvicorn
    print("启动调试服务器...")
    print("访问地址：")
    print("  http://localhost:8001/api/test/debug-info")
    print("  http://localhost:8001/api/test/compare-modes")
    print("  http://localhost:8001/api/test/raw-data-structure")
    uvicorn.run(app, host="0.0.0.0", port=8001)
