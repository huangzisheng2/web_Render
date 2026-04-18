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
from feedback import submit_feedback, get_feedback_stats, get_admin_feedback_stats, export_feedback_to_csv

from fastapi.responses import StreamingResponse
import io

app = FastAPI(
    title="天赋性格测评系统 API",
    description="基于八字命理的天赋与性格分析 API",
    version="1.0.0"
)

# CORS 配置 - 允许所有域名访问（解决WiFi/跨域问题）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # 使用通配符*时不能同时为True
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "*",
        "Content-Type",
        "Authorization",
        "Accept",
        "Accept-Language",
        "Accept-Encoding",
        "Origin",
        "X-Requested-With",
        "X-Debug-Mode",
    ],
    expose_headers=["*"],
    max_age=86400,  # 预检请求缓存24小时
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
    rating_overall: Optional[int] = Field(None, ge=1, le=5, description="整体体验评分 1-5")
    rating_design: Optional[int] = Field(None, ge=1, le=5, description="设计美观评分 1-5")
    rating_content: Optional[int] = Field(None, ge=1, le=5, description="分析内容评分 1-5")
    rating_helpful: Optional[int] = Field(None, ge=1, le=5, description="是否有帮助评分 1-5")
    feedback_text: Optional[str] = Field(None, max_length=500, description="反馈文字内容")


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


# 带重试机制的AI分析函数
async def analyze_ai_with_retry(bazi_service, report_id, result, max_retries=2, timeout=60):
    """
    带重试机制的AI分析
    
    Args:
        bazi_service: 分析服务实例
        report_id: 报告ID
        result: 基础分析结果
        max_retries: 最大重试次数（默认2次）
        timeout: 单次超时时间（秒，默认60秒）
    
    Returns:
        AI分析报告文本
    
    Raises:
        Exception: 所有重试都失败时抛出异常
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    executor = ThreadPoolExecutor()
    
    for attempt in range(max_retries + 1):
        try:
            print(f"[RETRY] AI分析尝试 {attempt + 1}/{max_retries + 1}")
            
            # 在线程池中执行AI分析，支持超时
            loop = asyncio.get_event_loop()
            future = executor.submit(bazi_service.analyze_ai, report_id, result)
            ai_report = await asyncio.wait_for(
                loop.run_in_executor(None, future.result),
                timeout=timeout
            )
            
            print(f"[RETRY] AI分析成功（尝试 {attempt + 1}）")
            executor.shutdown(wait=False)
            return ai_report
            
        except asyncio.TimeoutError:
            print(f"[RETRY] AI分析超时（尝试 {attempt + 1}/{max_retries + 1}）")
            if attempt < max_retries:
                wait_time = 2 ** attempt  # 指数退避：1s, 2s
                print(f"[RETRY] 等待 {wait_time}s 后重试...")
                await asyncio.sleep(wait_time)
            else:
                executor.shutdown(wait=False)
                raise Exception(f"AI分析超时，已重试{max_retries}次仍未成功")
                
        except Exception as e:
            print(f"[RETRY] AI分析失败（尝试 {attempt + 1}/{max_retries + 1}）: {str(e)}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"[RETRY] 等待 {wait_time}s 后重试...")
                await asyncio.sleep(wait_time)
            else:
                executor.shutdown(wait=False)
                raise


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_bazi(request: AnalyzeRequest, http_request: Request):
    """
    八字分析主接口

    接收用户出生信息，返回八字分析结果
    
    调试模式（X-Debug-Mode: true）：仅返回基础分析数据，AI分析需手动调用 /api/analyze-ai
    用户模式（默认）：自动执行 Step 4（基础分析）+ Step 5（AI分析），合并返回完整结果
    """
    import time
    import asyncio
    total_start = time.time()
    
    try:
        # 检测调试模式
        debug_mode = http_request.headers.get("X-Debug-Mode", "").lower() == "true"
        print(f"[TIMER] ========== 新的分析请求 ==========")
        print(f"[TIMER] 调试模式: {debug_mode}")
        print(f"[TIMER] 请求数据: {request.name}, {request.year}-{request.month}-{request.day}")
        
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

        # 执行基础分析（Step 4）
        step4_start = time.time()
        print(f"[TIMER] Step 4 开始: 基础八字分析")
        result = bazi_service.analyze_basic(birth_data)
        step4_time = time.time() - step4_start
        print(f"[TIMER] Step 4 完成: 基础八字分析耗时 {step4_time:.2f}s")
        
        if debug_mode:
            # 调试模式：返回完整基础数据（Step 4完成，Step 5需手动触发）
            print("[TIMER] 调试模式，返回基础分析数据（Step 4完成，Step 5需手动触发）")
            total_time = time.time() - total_start
            print(f"[TIMER] ========== 请求完成(调试模式) 总耗时: {total_time:.2f}s ==========")
            return {
                "success": True,
                "data": result
            }
        else:
            # 用户模式：自动执行 AI 分析（Step 4 + Step 5 合并）
            print("[TIMER] Step 5 开始: AI 分析报告生成（带重试机制）")
            
            # 获取 report_id 用于 AI 分析
            report_id = result.get("report_id")
            if not report_id:
                report_id = f"bazi_{request.name}_{request.year}{request.month:02d}{request.day:02d}"
            
            # 自动执行 AI 分析（Step 5）- 带重试机制，单次60秒超时，最多重试2次
            step5_start = time.time()
            try:
                ai_report = await analyze_ai_with_retry(
                    bazi_service, 
                    report_id, 
                    result, 
                    max_retries=2, 
                    timeout=60
                )
                step5_api_time = time.time() - step5_start
                print(f"[TIMER] Step 5 API完成: DeepSeek调用耗时 {step5_api_time:.2f}s")
            except Exception as e:
                step5_time = time.time() - step5_start
                print(f"[TIMER] [FAIL] Step 5 失败: AI 分析耗时 {step5_time:.2f}s, 错误: {str(e)}")
                # 返回部分结果，前端可以基于此继续
                return {
                    "success": False,
                    "error": f"AI分析超时，请稍后重试。{str(e)}"
                }
            
            # 记录DeepSeek返回后的处理时间
            step5_post_start = time.time()
            
            # 清理用户模式不需要的大字段
            if "raw_data" in result:
                del result["raw_data"]
            if "ai_prompt" in result:
                del result["ai_prompt"]
            
            # 构建用户模式的精简响应（只包含必要字段 + AI报告）
            user_result = {
                "report_id": result.get("report_id"),
                "user_info": result.get("user_info"),
                "ai_report": ai_report
            }
            
            step5_post_time = time.time() - step5_post_start
            total_time = time.time() - total_start
            print(f"[TIMER] Step 5 后处理: 数据清理组装耗时 {step5_post_time:.3f}s")
            print(f"[TIMER] ========== 请求完成 总耗时: {total_time:.2f}s (Step4: {step4_time:.2f}s, Step5-API: {step5_api_time:.2f}s, Step5-Post: {step5_post_time:.3f}s) ==========")
            
            # 如果后处理时间超过5秒，记录警告（可能是网络传输慢）
            if step5_post_time > 5:
                print(f"[WARN] 后处理时间过长: {step5_post_time:.2f}s，可能网络传输缓慢")
            
            return {
                "success": True,
                "data": user_result
            }

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[TIMER] [FAIL] 分析失败: {str(e)}")
        print(f"[TIMER] [FAIL] 错误详情:\n{error_trace}")
        total_time = time.time() - total_start
        print(f"[TIMER] ========== 请求失败 总耗时: {total_time:.2f}s ==========")
        return {
            "success": False,
            "error": f"分析失败: {str(e)}"
        }


async def generate_sse_stream(bazi_service, birth_data):
    """
    生成SSE流式响应
    
    事件类型：
    - stage: 阶段更新 (data: {stage: 'data'|'ai-parse'|'generating'|'complete'})
    - content: AI报告内容片段 (data: {chunk: '文本片段'})
    - done: 完成 (data: {success: true, report_id: 'xxx'})
    - error: 错误 (data: {error: '错误信息'})
    """
    import time
    import json
    
    try:
        # Step 4: 基础分析
        yield f"event: stage\ndata: {json.dumps({'stage': 'data', 'message': '正在分析出生信息...'})}\n\n"
        
        step4_start = time.time()
        result = bazi_service.analyze_basic(birth_data)
        step4_time = time.time() - step4_start
        print(f"[SSE] Step 4 完成: 耗时 {step4_time:.2f}s")
        
        # 发送基础信息
        yield f"event: stage\ndata: {json.dumps({'stage': 'ai-parse', 'message': '正在解析数据...', 'user_info': result.get('user_info')})}\n\n"
        
        # Step 5: AI分析
        yield f"event: stage\ndata: {json.dumps({'stage': 'generating', 'message': 'AI正在生成报告...'})}\n\n"
        
        report_id = result.get("report_id", f"report_{int(time.time())}")
        
        step5_start = time.time()
        
        # 调用AI分析（这会等待完整结果，但我们可以优化成真正的流式）
        # 目前先模拟流式，实际内容一次性返回
        ai_report = bazi_service.analyze_ai(report_id, result)
        
        step5_time = time.time() - step5_start
        print(f"[SSE] Step 5 完成: DeepSeek调用耗时 {step5_time:.2f}s")
        
        # 模拟流式输出AI报告内容（每100字符分一块）
        chunk_size = 100
        for i in range(0, len(ai_report), chunk_size):
            chunk = ai_report[i:i+chunk_size]
            yield f"event: content\ndata: {json.dumps({'chunk': chunk})}\n\n"
            # 小延迟模拟打字效果
            await asyncio.sleep(0.01)
        
        # 发送完成事件
        yield f"event: done\ndata: {json.dumps({'success': True, 'report_id': report_id, 'user_info': result.get('user_info')})}\n\n"
        
        total_time = time.time() - step4_start
        print(f"[SSE] 流式响应完成: 总耗时 {total_time:.2f}s")
        
    except Exception as e:
        error_msg = str(e)
        print(f"[SSE] 错误: {error_msg}")
        yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"


@app.post("/api/analyze-stream")
async def analyze_bazi_stream(request: AnalyzeRequest):
    """
    流式分析接口 - 使用SSE(Server-Sent Events)
    
    前端使用EventSource连接此接口，逐步接收：
    1. stage事件：阶段更新（data/ai-parse/generating/complete）
    2. content事件：AI报告内容片段
    3. done事件：完成
    4. error事件：错误
    """
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
    
    return StreamingResponse(
        generate_sse_stream(bazi_service, birth_data),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
        }
    )


@app.post("/api/analyze-ai")
def analyze_ai_endpoint(request: dict):
    """
    AI 天赋分析接口（传统非流式）
    
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
    提交用户反馈（完全匿名，多维度评分）
    
    用户可以对整体体验、设计美观、分析内容、是否有帮助等维度进行1-5分评分
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
        
        # 提交反馈（多维度评分）
        result = submit_feedback(
            rating_overall=request.rating_overall,
            rating_design=request.rating_design,
            rating_content=request.rating_content,
            rating_helpful=request.rating_helpful,
            feedback_text=request.feedback_text,
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


# ==================== 管理员接口（仅调试模式） ====================

@app.get("/admin/feedback/stats")
def admin_feedback_stats(http_request: Request):
    """
    管理员反馈统计数据（调试模式专用）
    
    返回总反馈数、平均评分、各星级分布、最近20条评论
    需要 X-Debug-Mode: true 请求头
    """
    # 验证调试模式
    debug_mode = http_request.headers.get("X-Debug-Mode", "").lower() == "true"
    if not debug_mode:
        raise HTTPException(status_code=403, detail="禁止访问：需要调试模式权限")
    
    try:
        stats = get_admin_feedback_stats()
        return stats
    except Exception as e:
        return {
            "success": False,
            "error": f"获取统计失败: {str(e)}"
        }


@app.get("/admin/feedback/export")
def admin_feedback_export(http_request: Request):
    """
    导出所有反馈数据为CSV（调试模式专用）
    
    需要 X-Debug-Mode: true 请求头
    """
    # 验证调试模式
    debug_mode = http_request.headers.get("X-Debug-Mode", "").lower() == "true"
    if not debug_mode:
        raise HTTPException(status_code=403, detail="禁止访问：需要调试模式权限")
    
    try:
        # 生成CSV数据
        csv_data = export_feedback_to_csv()
        
        # 生成文件名
        from datetime import datetime
        filename = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # 返回流式响应
        return StreamingResponse(
            io.StringIO(csv_data),
            media_type="text/csv; charset=utf-8-sig",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        return {
            "success": False,
            "error": f"导出失败: {str(e)}"
        }


# ==================== 启动 ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
