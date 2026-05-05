from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="K-Billiards 보도자료 생성 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

class PressRequest(BaseModel):
    release_type: str
    tournament_name: str
    organizer: str = "대한당구연맹"
    date: str = ""
    venue: str = ""
    discipline: str = ""
    participants: str = ""
    winner: str = ""
    runner_up: str = ""
    prize: str = ""
    total_prize: str = ""
    highlights: str = ""
    contact_name: str = ""
    contact_tel: str = ""

@app.get("/")
def health_check():
    key = os.getenv("GEMINI_API_KEY")
    return {
        "status": "ok",
        "gemini_key_set": key is not None,
        "gemini_key_preview": key[:8] + "..." if key else "NOT SET"
    }

@app.post("/generate")
def generate_press_release(req: PressRequest):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    prompt = f"""당신은 대한당구연맹 공식 보도자료 담당자입니다.
아래 정보로 공식 보도자료를 작성해주세요.

[작성 규칙]
- 공식적이고 격조 있는 문체
- 구성: 제목 → 부제 → 발표일 → 본문(3~4단락) → 연맹 소개 → 문의처
- 총 분량: 600~900자

[대회 정보]
- 유형: {req.release_type}
- 대회명: {req.tournament_name}
- 주최/주관: {req.organizer}
- 일정: {req.date}
- 장소: {req.venue}
- 종목: {req.discipline}
- 참가 규모: {req.participants or '미입력'}
- 우승: {req.winner or '미입력'}
- 준우승: {req.runner_up or '미입력'}
- 우승 상금: {req.prize or '미입력'}
- 총 상금: {req.total_prize or '미입력'}
- 주요 내용: {req.highlights or '없음'}
- 담당자: {req.contact_name or '대한당구연맹 사무국'}
- 연락처: {req.contact_tel or ''}

보도자료만 출력하세요."""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        response = requests.post(
            url,
            json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 1500}},
            timeout=30
        )
        
        # 응답 상태 및 내용 확인
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Gemini API 오류 {response.status_code}: {response.text}")
        
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"result": text}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 상세: {str(e)}")
