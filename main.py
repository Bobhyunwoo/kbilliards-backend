from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="K-Billiards 보도자료 생성 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


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
    return {"status": "ok", "service": "K-Billiards Press Release Generator"}


@app.post("/generate")
def generate_press_release(req: PressRequest):
    prompt = f"""당신은 대한당구연맹(Korea Billiards Federation)의 공식 보도자료 담당자입니다.
아래 대회 정보를 바탕으로 언론사에 배포할 공식 보도자료를 작성해주세요.

[작성 규칙]
- 공식적이고 격조 있는 문체 사용 (뉴스 보도자료 형식)
- 제목은 간결하고 임팩트 있게 (핵심 내용 포함)
- 구성: 제목 → 부제 → 발표일 및 배포처 → 본문(3~4단락) → 연맹 소개 → 문의처
- 본문 첫 단락에 핵심 내용(5W1H) 요약
- 대한당구연맹의 위상, 스포츠 발전 기여 등 긍정적 프레이밍
- 인용구는 연맹 관계자 멘트로 자연스럽게 삽입
- 문의처는 마지막에 별도 표시
- 총 분량: 600~900자 내외

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
- 주요 내용/특이사항: {req.highlights or '없음'}
- 담당자: {req.contact_name or '대한당구연맹 사무국'}
- 연락처: {req.contact_tel or ''}

보도자료만 출력하세요. 추가 설명이나 안내 문구 없이 보도자료 본문만 작성하세요."""

    try:
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
