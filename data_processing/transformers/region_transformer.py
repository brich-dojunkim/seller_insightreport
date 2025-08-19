# data_processing/transformers/region_transformer.py
"""지역 추출 변환기"""

import pandas as pd

def extract_region_from_address(address_series: pd.Series) -> pd.Series:
    """주소에서 지역 추출 - 두 단어 추출 + 시/도 하드코딩 결합"""
    
    def extract_region_combined(address):
        if pd.isna(address):
            return None
        
        addr_str = str(address).strip()
        if not addr_str:
            return None
        
        # 1단계: 주소를 공백으로 분리해서 앞의 두 단어 추출
        parts = addr_str.split()
        
        if len(parts) == 0:
            return "기타"
        elif len(parts) == 1:
            raw_region = parts[0]
        else:
            # 앞의 두 단어만 결합
            raw_region = f"{parts[0]} {parts[1]}"
        
        # 2단계: 첫 번째 단어를 하드코딩 방식으로 표준화
        first_word = parts[0]
        standardized_sido = standardize_sido(first_word)
        
        # 3단계: 표준화된 시/도 + 두 번째 단어 (있는 경우)
        if len(parts) >= 2:
            return f"{standardized_sido} {parts[1]}"
        else:
            return standardized_sido
    
    return address_series.apply(extract_region_combined)

def standardize_sido(sido_text: str) -> str:
    """시/도명 하드코딩 표준화"""
    
    sido_text = sido_text.strip()
    
    # 시/도 하드코딩 매핑
    sido_mapping = {
        # 서울
        '서울': '서울', '서울시': '서울', '서울특별시': '서울',
        # 부산
        '부산': '부산', '부산시': '부산', '부산광역시': '부산',
        # 대구
        '대구': '대구', '대구시': '대구', '대구광역시': '대구',
        # 인천
        '인천': '인천', '인천시': '인천', '인천광역시': '인천',
        # 광주
        '광주': '광주', '광주시': '광주', '광주광역시': '광주',
        # 대전
        '대전': '대전', '대전시': '대전', '대전광역시': '대전',
        # 울산
        '울산': '울산', '울산시': '울산', '울산광역시': '울산',
        # 세종
        '세종': '세종', '세종시': '세종', '세종특별자치시': '세종',
        # 경기
        '경기': '경기', '경기도': '경기',
        # 강원
        '강원': '강원', '강원도': '강원', '강원특별자치도': '강원',
        # 충북
        '충북': '충북', '충청북': '충북', '충청북도': '충북',
        # 충남
        '충남': '충남', '충청남': '충남', '충청남도': '충남',
        # 전북
        '전북': '전북', '전라북': '전북', '전라북도': '전북', '전북특별자치도': '전북',
        # 전남
        '전남': '전남', '전라남': '전남', '전라남도': '전남',
        # 경북
        '경북': '경북', '경상북': '경북', '경상북도': '경북',
        # 경남
        '경남': '경남', '경상남': '경남', '경상남도': '경남',
        # 제주
        '제주': '제주', '제주도': '제주', '제주특별자치도': '제주'
    }
    
    # 정확한 매칭 시도
    if sido_text in sido_mapping:
        return sido_mapping[sido_text]
    
    # 부분 매칭 시도 (앞 2글자 기준)
    for full_name, short_name in sido_mapping.items():
        if sido_text.startswith(full_name[:2]) and len(full_name) >= 2:
            return short_name
    
    # 매칭되지 않으면 원본 그대로 반환
    return sido_text