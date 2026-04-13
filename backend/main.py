"""
天赋性格测评系统 - FastAPI 后端
部署于 Render
"""

import os
import sys
from pathlib import Path

# 添加命理模块路径
BASE_DIR = Path(__file__).parent
BAZI_DIR = BASE_DIR / "bazi_modules"
sys.path.insert(0, str(BAZI_DIR))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import traceback

# 导入业务服务
from services.bazi_service_web import BaziAnalysisServiceWeb
from services.pdf_service import PDFService
from feedback import submit_feedback, get_feedback_stats

app = FastAPI(
    title="天赋性格测评系统 API",
    description="基于八字命理的天赋与性格分析 API",
    version="1.0.0"
)

# CORS 配置 - 允许 GitHub Pages 访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://huangzisheng2.github.io",
        "https://*.github.io",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

class AnalyzeRequest(BaseModel):
    name: str = Field(..., description="姓名", max_length=20)
    year: int = Field(..., ge=1900, le=2100, description="出生年")
    month: int = Field(..., ge=1, le=12, description="出生月")
    day: int = Field(..., ge=1, le=31, description="出生日")
    hour: Optional[int] = Field(None, ge=0, le=23, description="出生时(0-23)，可选")
    minute: int = Field(0, ge=0, le=59, description="出生分")
    gender: Literal["male", "female"] = Field(..., description="性别: male/female")
    province: str = Field(..., description="省份", max_length=50)
    city: str = Field(..., description="城市", max_length=50)


class AnalyzeResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class PDFDownloadResponse(BaseModel):
    success: bool
    download_url: Optional[str] = None
    error: Optional[str] = None


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="评分 1-5星")
    feedback_text: Optional[str] = Field(None, max_length=500, description="反馈文字内容")
    experience_type: Optional[str] = Field("overall", description="体验类型: overall/design/content/feature")


class FeedbackResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    feedback_id: Optional[int] = None
    error: Optional[str] = None


# ==================== 服务实例 ====================

bazi_service = BaziAnalysisServiceWeb()
pdf_service = PDFService()


# ==================== API 路由 ====================

@app.get("/")
def root():
    """健康检查"""
    return {"status": "ok", "service": "天赋性格测评系统 API"}


@app.get("/api/cities")
def get_cities():
    """获取支持的城市列表"""
    try:
        cities = bazi_service.get_cities()
        return {"success": True, "cities": cities}
    except Exception as e:
        return {"success": False, "error": str(e)}


"""
================================================================================
模式说明：

【用户模式】（不带 ?debug=true）
- 目的：保护用户隐私，只展示AI生成的报告文本
- 流程：填写信息 → 后端基础分析 → 后端AI分析 → 只返回 ai_report
- 返回数据：{ai_report: "..."}
- 前端：只显示AI报告 + PDF下载 + 反馈

【调试模式】（带 ?debug=true）
- 目的：开发者调试，查看完整命理数据
- 流程：填写信息 → 后端基础分析 → 返回完整数据 → 前端手动触发AI分析
- 返回数据：{user_info, bazi, analysis, raw_data, ...}
- 前端：显示完整命理图表 + AI报告 + 原始JSON

注意：
1. 用户模式绝不返回 raw_data、ai_prompt 等敏感计算数据
2. AI分析统一在后端完成，使用 _build_ai_prompt 构建提示词
3. 两种模式的AI分析逻辑必须保持一致
================================================================================
"""

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_bazi(request: AnalyzeRequest, http_request: Request):
    """
    八字分析主接口
    
    【用户模式】自动执行基础分析+AI分析，只返回 ai_report
    【调试模式】只执行基础分析，返回完整数据（含raw_data）
    """
    try:
        # 检测调试模式
        debug_mode = http_request.headers.get("X-Debug-Mode", "").lower() == "true"
        print(f"[DEBUG] 调试模式: {debug_mode}")
        
        # 转换为内部格式
        birth_data = {
            "name": request.name,
            "year": request.year,
            "month": request.month,
            "day": request.day,
            "hour": request.hour,
            "minute": request.minute,
            "gender": request.gender,
            "province": request.province,
            "city": request.city,
        }

        # 执行基础分析（计算命理数据）
        result = bazi_service.analyze_basic(birth_data)
        
        if debug_mode:
            # ========== 调试模式 ==========
            # 返回完整数据（含raw_data），不自动执行AI分析
            if "ai_prompt" in result:
                del result["ai_prompt"]
            print("[DEBUG] 调试模式，返回完整数据")
            
        else:
            # ========== 用户模式 ==========
            # 自动执行AI分析，只返回 ai_report
            print("[DEBUG] 用户模式，执行AI分析...")
            try:
                ai_report = bazi_service.analyze_ai(result["report_id"], result)
                # 只保留 ai_report，其他数据不返回（保护隐私）
                result = {
                    "ai_report": ai_report
                }
                print("[DEBUG] 用户模式，AI分析完成")
            except Exception as ai_error:
                print(f"[DEBUG] 用户模式AI分析失败: {ai_error}")
                result = {
                    "ai_report": "AI分析暂时不可用，请稍后重试"
                }

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"分析错误: {str(e)}\n{error_trace}")
        return {
            "success": False,
            "error": f"分析失败: {str(e)}"
        }


@app.post("/api/analyze-ai")
def analyze_ai_endpoint(request: dict):
    """
    AI 天赋分析接口
    
    接收基础分析结果，返回 AI 分析报告
    """
    try:
        report_id = request.get("report_id")
        basic_result = request.get("basic_result")
        
        if not report_id or not basic_result:
            return {
                "success": False,
                "error": "缺少 report_id 或 basic_result 参数"
            }
        
        # 执行 AI 分析
        ai_report = bazi_service.analyze_ai(report_id, basic_result)
        
        return {
            "success": True,
            "ai_report": ai_report
        }
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"AI 分析错误: {str(e)}\n{error_trace}")
        return {
            "success": False,
            "error": f"AI 分析失败: {str(e)}"
        }


@app.get("/api/download/{report_id}")
def download_report(report_id: str):
    """
    获取 PDF 报告下载链接
    
    report_id 为分析时返回的报告 ID
    """
    try:
        download_url = pdf_service.get_download_url(report_id)
        return {
            "success": True,
            "download_url": download_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"获取下载链接失败: {str(e)}"
        }


@app.post("/api/feedback", response_model=FeedbackResponse)
def submit_user_feedback(request: FeedbackRequest, http_request: Request):
    """
    提交用户反馈（完全匿名）
    
    用户可以对使用体验、外观设计、分析内容等进行评分和留言
    数据存储在 PostgreSQL 数据库中，不收集任何个人隐私信息
    """
    try:
        # 获取请求信息（仅用于防止滥用）
        user_agent = http_request.headers.get("user-agent")
        
        # 获取客户端IP（在Render环境中可能经过代理）
        forwarded_for = http_request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = http_request.client.host if http_request.client else None
        
        # 提交反馈
        result = submit_feedback(
            rating=request.rating,
            feedback_text=request.feedback_text,
            experience_type=request.experience_type,
            user_agent=user_agent,
            ip_address=client_ip
        )
        
        return result
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"提交反馈错误: {str(e)}\n{error_trace}")
        return {
            "success": False,
            "error": f"提交反馈失败: {str(e)}"
        }


@app.get("/api/feedback/stats")
def get_feedback_statistics():
    """
    获取反馈统计信息（管理用途）
    
    返回评分分布、平均评分等统计信息
    """
    try:
        stats = get_feedback_stats()
        return stats
    except Exception as e:
        return {
            "success": False,
            "error": f"获取统计失败: {str(e)}"
        }


# ==================== 调试测试接口 ====================

@app.post("/api/test/ai-analysis-debug")
def ai_analysis_debug(request: dict):
    """
    调试接口：对比用户模式和调试模式的AI分析过程
    
    返回：
    - 输入数据
    - AI提示词
    - AI分析结果
    """
    try:
        from fastapi.encoders import jsonable_encoder
        
        report_id = request.get("report_id", "test_report_id")
        basic_result = request.get("basic_result", {})
        
        # 提取数据（模拟 analyze_ai 方法的逻辑）
        bazi_data = basic_result.get("bazi", {})
        analysis_data = basic_result.get("raw_data", {})
        user_info = {
            "name": basic_result.get("user_info", {}).get("name", "匿名"),
            "gender": "male" if basic_result.get("user_info", {}).get("gender") == "男" else "female",
        }
        
        # 构建AI提示词
        ai_prompt = bazi_service._build_ai_prompt(bazi_data, analysis_data, user_info)
        
        # 检查关键数据是否存在
        debug_info = {
            "input_check": {
                "has_bazi": bool(bazi_data),
                "has_raw_data": bool(analysis_data),
                "has_user_info": bool(basic_result.get("user_info")),
                "bazi_keys": list(bazi_data.keys()) if bazi_data else [],
                "raw_data_keys": list(analysis_data.keys()) if analysis_data else [],
            },
            "ai_prompt_preview": ai_prompt[:500] + "..." if len(ai_prompt) > 500 else ai_prompt,
            "ai_prompt_length": len(ai_prompt),
        }
        
        # 执行AI分析
        ai_report = bazi_service.analyze_ai(report_id, basic_result)
        
        return {
            "success": True,
            "debug_info": debug_info,
            "ai_report": ai_report,
            "note": "如果 has_raw_data 为 false，说明 basic_result 中没有 raw_data，AI分析将缺少关键数据"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/api/test/check-mode-difference")
def check_mode_difference():
    """
    检查用户模式和调试模式的差异说明
    """
    return {
        "success": True,
        "mode_differences": {
            "user_mode": {
                "endpoint": "POST /api/analyze (without X-Debug-Mode header)",
                "flow": [
                    "1. Frontend: 发送出生信息",
                    "2. Backend: analyze_basic() 计算命理数据",
                    "3. Backend: analyze_ai() 执行AI分析（内部调用）",
                    "4. Backend: 返回 {ai_report}",
                ],
                "data_passed_to_ai": "完整的 result（包含 raw_data）",
                "data_returned_to_frontend": "仅 ai_report",
            },
            "debug_mode": {
                "endpoint": "POST /api/analyze (with X-Debug-Mode: true)",
                "flow": [
                    "1. Frontend: 发送出生信息",
                    "2. Backend: analyze_basic() 计算命理数据",
                    "3. Backend: 返回完整数据（含 raw_data）",
                    "4. Frontend: 用户点击'一键分析天赋'",
                    "5. Frontend: POST /api/analyze-ai {report_id, basic_result}",
                    "6. Backend: analyze_ai() 执行AI分析",
                    "7. Backend: 返回 {ai_report}",
                ],
                "data_passed_to_ai": "basic_result（包含 raw_data）",
                "data_returned_to_frontend": "完整数据 + ai_report",
            },
        },
        "potential_issue": "如果调试模式下 basic_result 被修改或截断，可能导致AI分析结果不同",
        "solution": "确保两种模式下传递给 analyze_ai() 的 basic_result 包含相同的 raw_data"
    }


# ==================== 启动 ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
