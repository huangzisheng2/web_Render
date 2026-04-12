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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import traceback

# 导入业务服务
from services.bazi_service import BaziAnalysisService
from services.pdf_service import PDFService

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


# ==================== 服务实例 ====================

bazi_service = BaziAnalysisService()
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
def analyze_bazi(request: AnalyzeRequest):
    """
    八字分析主接口
    
    接收用户出生信息，返回八字分析结果和 AI 报告
    """
    try:
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
        
        # 执行分析
        result = bazi_service.analyze(birth_data)
        
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


# ==================== 启动 ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
