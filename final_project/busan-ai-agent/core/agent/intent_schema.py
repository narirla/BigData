# core/agent/intent_schema.py
# LLM이 뽑을 JSON 스키마 정의

from pydantic import BaseModel, Field
from typing import Optional, Literal, List

Intent = Literal[
    "youth_policy_list",
    "youth_policy_detail",
    "training_list",
    "chit_chat",
    # 추후 채용정보, 직업정보 추가시 아래에 추가
    "job_list",
    "job_detail",
    "hiring_info",
]

class IntentResult(BaseModel):
    intent : Intent = Field(..., description="사용자 의도")
    keyword_csv : Optional[str] = Field(None, description="청년정책 키워드 CSV 예: 대출, 보조금, 바우처, 금리혜택, 교육지원, 맞춤형상담서비스, 인턴, 벤처, 중소기업, 청년가장, 장기미취업청년, 공공임대주택, 신용회복, 육아, 출산, 해외진출, 주거지원")
    plcy_no : Optional[str] = Field(None, description="청년정책 번호 plcyNo")
    policy_name: Optional[str] = Field(None, description="청년정책 정책명")
    training_keyword: Optional[str] = Field(None, description="훈련과정 검색 키워드 예: 웹, 개발, IT")
    job_keyword: Optional[str] = Field(None, description="직업 검색 키워드 예: 개발, 데이터")
    job_name: Optional[str] = Field(None, description="직업명 예: 웹개발자, 데이터분석가")
    job_cd: Optional[str] = Field(None, description="직업코드 jobCd (가능하면)")
    # 필요하면 나중에 확장(연령, 구군, 과정유형 등)
    hiring_keyword: Optional[str] = Field(None, description="채용 검색 키워드 예: 백엔드, 데이터, ai, 프론트엔드")