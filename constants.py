# constants.py
"""
비플로우 주문리스트 전용 고정 칼럼명 정의
- 고객 집계는 '가명키(pseudokey)'로 수행:
  (구매자명) + (구매자연락처 뒤 4자리) + (우편번호 또는 주소 일부)
- 선택 컬럼이 없으면 자동으로 건너뛰고, 최종적으로는 '구매자명'만으로도 동작합니다.
"""

# ── 핵심 날짜/금액 ───────────────────────────────────────────────
COL_PAYMENT_DATE   = "결제일"               # 결제 기준일
COL_ORDER_AMOUNT   = "상품별 총 주문금액"    # 결제 금액(주문 라인 기준)
COL_SETTLEMENT     = "정산금액"             # (선택)

# ── 식별/분류 ───────────────────────────────────────────────────
COL_ORDER_ID       = "주문번호"
COL_SELLER         = "입점사명"
COL_CHANNEL        = "판매채널"
COL_CATEGORY       = "상품 카테고리"        # (선택)

# ── 품목/수량 ───────────────────────────────────────────────────
COL_ITEM_NAME      = "상품명"
COL_QTY            = "수량"

# ── 배송/상태/클레임 ────────────────────────────────────────────
COL_STATUS         = "주문상태"             # (G열)
COL_REFUND_FIELD   = "클레임"               # (H열) 예: '취소:1', '반품:1'
COL_SHIP_DATE      = "발송처리일"
COL_DELIVERED_DATE = "배송완료일"

# ── 고객(이름 우선, 아이디 폴백) ────────────────────────────────
COL_CUSTOMER_NAME  = "구매자명"
COL_CUSTOMER_ID    = "구매자아이디"         # 파일상 공란이 많아 폴백 용도

# ── 가명키 보조 정보(선택) ───────────────────────────────────────
# * 실제 파일의 정확한 헤더명을 사용하세요. 없으면 그냥 두세요.
COL_BUYER_PHONE    = "구매자연락처"         # 예: 010-1234-5678
COL_POSTCODE       = "배송지우편번호"        # 예: 06236
COL_ADDRESS_LINE   = "배송지주소"           # 예: 서울 강남구 역삼동 …

# ── 환불/취소 키워드(정규식) ────────────────────────────────────
REFUND_REGEX_OPEN  = r"(?:환불|취소|반품|refund|cancel)"

# ── 필수/선택 컬럼 집합 ─────────────────────────────────────────
REQUIRED_COLUMNS = {
    COL_PAYMENT_DATE,
    COL_ORDER_AMOUNT,
}
OPTIONAL_COLUMNS = {
    COL_SELLER, COL_CHANNEL, COL_STATUS, COL_REFUND_FIELD,
    COL_ITEM_NAME, COL_QTY, COL_SHIP_DATE, COL_DELIVERED_DATE,
    COL_ORDER_ID, COL_CUSTOMER_NAME, COL_CUSTOMER_ID,
    COL_CATEGORY, COL_SETTLEMENT,
    COL_BUYER_PHONE, COL_POSTCODE, COL_ADDRESS_LINE,
}
