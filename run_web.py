#!/usr/bin/env python3
"""
SKAX-RA-AI-SEARCH 웹 인터페이스 실행 파일
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import argparse

from src.core.search_engine import SearchEngine
from config.settings import WEB_HOST, WEB_PORT, DEBUG

app = FastAPI(
    title="SKAX-RA-AI-SEARCH 웹 인터페이스",
    description="AI 기반 개발자 검색 시스템",
    version="1.0.0"
)

# 정적 파일과 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")

# 시스템 인스턴스
search_engine = SearchEngine()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """검색 페이지"""
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/filter", response_class=HTMLResponse)
async def filter_page(request: Request):
    """필터 페이지"""
    return templates.TemplateResponse("filter.html", {"request": request})

@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    """통계 페이지"""
    stats = search_engine.get_stats()
    return templates.TemplateResponse("stats.html", {"request": request, "stats": stats})

@app.get("/profile/{developer_id}", response_class=HTMLResponse)
async def profile_page(request: Request, developer_id: str):
    """개발자 상세 프로필 페이지"""
    try:
        # 개발자 데이터 가져오기
        developer_data = search_engine.get_developer_by_id(developer_id)
        if developer_data:
            return templates.TemplateResponse("profile.html", {
                "request": request, 
                "developer": developer_data
            })
        else:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "개발자를 찾을 수 없습니다."
            })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": f"오류가 발생했습니다: {str(e)}"
        })

@app.post("/api/search")
async def api_search(query: str = Form(...), search_type: str = Form("comprehensive"), 
                    filter_mode: str = Form("default"), limit: int = Form(10)):
    """검색 API"""
    try:
        # 필터 모드에 따른 검색 엔진 생성
        search_engine_with_mode = SearchEngine(user_config=filter_mode)
        
        # 필터 추출 정보도 함께 반환
        extracted_filters = search_engine_with_mode.filter_engine.extract_filters(query)
        results = search_engine_with_mode.search_developers(query, search_type, limit)
        
        # 필터 정보 텍스트 생성
        filter_info = search_engine_with_mode.filter_engine.get_filter_info(extracted_filters)
        
        return {
            "success": True, 
            "results": results, 
            "query": query,
            "extracted_filters": extracted_filters,
            "filter_info": filter_info,
            "filter_mode": filter_mode
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/filter")
async def api_filter(seniority: str = Form(None), primary_role: str = Form(None), 
                    availability: str = Form(None), location: str = Form(None), limit: int = Form(10)):
    """필터 API"""
    try:
        filters = {}
        if seniority:
            filters["seniority"] = seniority
        if primary_role:
            filters["primary_role"] = primary_role
        if availability:
            filters["availability"] = availability
        if location:
            filters["location"] = location
        
        results = search_engine.search_by_filters(filters, limit)
        return {"success": True, "results": results, "filters": filters}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/init-data")
async def api_init_data():
    """데이터 초기화 API"""
    try:
        developers = search_engine.create_sample_data(30)
        search_engine.add_developers(developers)
        stats = search_engine.get_stats()
        return {"success": True, "message": f"{len(developers)}명의 개발자 데이터가 추가되었습니다.", "stats": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="SKAX-RA-AI-SEARCH 웹 인터페이스")
    parser.add_argument("--host", default=WEB_HOST, help="호스트 주소")
    parser.add_argument("--port", type=int, default=WEB_PORT, help="포트 번호")
    parser.add_argument("--dev", action="store_true", help="개발 모드")
    
    args = parser.parse_args()
    
    print(f"🚀 SKAX-RA-AI-SEARCH 웹 인터페이스 시작")
    print(f"📍 주소: http://{args.host}:{args.port}")
    print(f"🔧 개발 모드: {args.dev}")
    
    uvicorn.run(
        app, 
        host=args.host, 
        port=args.port,
        reload=args.dev
    )

if __name__ == "__main__":
    main() 