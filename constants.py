# constants.py
"""비플로우 주문리스트 전용 칼럼명 정의"""

# 핵심 날짜/금액
COL_PAYMENT_DATE   = "결제일"
COL_ORDER_AMOUNT   = "상품별 총 주문금액"

# 식별/분류
COL_SELLER         = "입점사명"
COL_CHANNEL        = "판매채널"
COL_ORDER_ID       = "주문번호"

# 품목/수량
COL_ITEM_NAME      = "상품명"
COL_QTY            = "수량"

# 배송/상태/클레임
COL_STATUS         = "주문상태"   # G열
COL_REFUND_FIELD   = "클레임"     # H열
COL_SHIP_DATE      = "발송처리일"
COL_DELIVERED_DATE = "배송완료일"

# 고객 (기존)
COL_CUSTOMER       = "구매자아이디"

# 고객 식별용 (신규 추가)
COL_BUYER_NAME     = "구매자명"
COL_BUYER_PHONE    = "구매자연락처"

# 지역
COL_ADDRESS        = "배송지"
COL_POSTAL_CODE    = "우편번호"

# 카테고리
COL_CATEGORY       = "상품 카테고리"

# 정산
COL_SETTLEMENT     = "정산금액"
COL_PRODUCT_PRICE  = "상품가격"

# 환불/취소 키워드
REFUND_REGEX_OPEN  = r"(?:환불|취소|반품|refund|cancel)"