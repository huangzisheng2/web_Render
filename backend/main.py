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


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_bazi(request: AnalyzeRequest, http_request: Request):
    """
    八字分析主接口（仅基础分析，不含AI）

    接收用户出生信息，返回八字基础分析结果（四柱、六级论级等）
    AI分析请调用 /api/analyze-ai 接口
    
    调试模式：添加请求头 X-Debug-Mode: true 可获取完整命理数据
    """
    try:
        # 检查是否为调试模式
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

        # 执行基础分析（不含AI）
        result = bazi_service.analyze_basic(birth_data)
        
        # 如果不是调试模式，移除原始命理数据
        if not debug_mode:
            # 保存一份完整数据供AI分析使用，但返回时过滤掉
            full_data = result.get("raw_data", {})
            # 在调试模式下才会包含 _debug_full_data
            result["_debug_full_data"] = full_data if debug_mode else None
            # 用户模式下只保留必要信息
            if "raw_data" in result:
                del result["raw_data"]
            if "ai_prompt" in result:
                del result["ai_prompt"]
        else:
            # 调试模式：保留完整数据
            result["_debug_full_data"] = result.get("raw_data", {})

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
def analyze_ai_endpoint(request: dict, http_request: Request):
    """
    AI 天赋分析接口
    
    接收基础分析结果，返回 AI 分析报告
    
    调试模式：添加请求头 X-Debug-Mode: true 可获取调试信息
    """
    try:
        report_id = request.get("report_id")
        basic_result = request.get("basic_result")
        
        if not report_id or not basic_result:
            return {
                "success": False,
                "error": "缺少 report_id 或 basic_result 参数"
            }
        
        # 检查是否为调试模式
        debug_mode = http_request.headers.get("X-Debug-Mode", "").lower() == "true"
        
        # 执行 AI 分析
        ai_report = bazi_service.analyze_ai(report_id, basic_result)
        
        response = {
            "success": True,
            "ai_report": ai_report
        }
        
        # 调试模式下添加额外信息
        if debug_mode:
            response["_debug_info"] = {
                "report_id": report_id,
                "prompt_length": len(basic_result.get("ai_prompt", ""))
            }
        
        return response
        
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


# ==================== 启动 ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
