"""
상표권/브랜드 블랙리스트 관리 모듈

온라인 쇼핑 키워드에서 상표권 침해를 방지하기 위한 브랜드/상표명 데이터베이스.
카테고리별로 분류되어 있으며, 향후 사용자가 직접 추가/제거할 수 있도록 확장 가능합니다.
"""

# ============================================================
# 카테고리별 브랜드/상표 블랙리스트
# ============================================================

# 전자제품 / IT
_ELECTRONICS_BRANDS = {
    "삼성", "samsung", "갤럭시", "galaxy", "lg", "엘지",
    "애플", "apple", "아이폰", "iphone", "아이패드", "ipad", "맥북", "macbook",
    "소니", "sony", "파나소닉", "panasonic",
    "필립스", "philips", "보스", "bose", "jbl",
    "다이슨", "dyson", "샤오미", "xiaomi", "화웨이", "huawei",
    "레노버", "lenovo", "에이수스", "asus", "델", "dell", "hp",
    "캐논", "canon", "니콘", "nikon", "올림푸스", "olympus",
    "로지텍", "logitech", "레이저", "razer",
    "브라운", "braun", "일렉트로룩스", "electrolux",
    "하이얼", "haier", "위닉스", "winix", "쿠쿠", "cuku", "쿠첸", "cuchen",
    "밀레", "miele", "보쉬", "bosch",
}

# 생활용품 / 가정용품
_HOUSEHOLD_BRANDS = {
    "다이소", "daiso", "이케아", "ikea",
    "3m", "쓰리엠", "락앤락", "locknlock",
    "글라스락", "glasslock", "코렐", "corelle",
    "옥소", "oxo", "조셉조셉", "josephjoseph",
    "테팔", "tefal", "휘슬러", "fissler", "WMF", "wmf",
    "실리트", "silit", "쯔비링", "zwilling", "헹켈", "henkel",
    "피죤", "비트", "퍼실", "persil", "다우니", "downy",
    "유한킴벌리", "크리넥스", "kleenex", "스카트", "하기스",
    "무인양품", "muji",
    "홈플러스", "이마트", "코스트코", "costco",
    "오늘의집",
}

# 패션 / 의류 / 잡화
_FASHION_BRANDS = {
    "나이키", "nike", "아디다스", "adidas",
    "뉴발란스", "new balance", "퓨마", "puma",
    "컨버스", "converse", "반스", "vans",
    "노스페이스", "north face", "코오롱", "kolon",
    "디스커버리", "discovery", "내셔널지오그래픽",
    "구찌", "gucci", "루이비통", "louis vuitton",
    "프라다", "prada", "샤넬", "chanel", "에르메스", "hermes",
    "자라", "zara", "h&m", "유니클로", "uniqlo",
    "무신사", "musinsa", "스타일난다",
    "게스", "guess", "폴로", "polo", "라코스테", "lacoste",
    "캘빈클라인", "calvin klein", "타미힐피거", "tommy hilfiger",
    "까르띠에", "cartier", "티파니", "tiffany",
    "리바이스", "levis", "갭", "gap",
    "크록스", "crocs", "빌켄슈탁", "birkenstock",
    "헤지스", "hazzys", "빈폴", "beanpole", "탑텐", "topten",
}

# 식품 / 음료
_FOOD_BRANDS = {
    "농심", "nongshim", "오뚜기", "ottogi", "삼양", "samyang",
    "cj", "씨제이", "비비고", "bibigo", "해찬들",
    "풀무원", "pulmuone", "동원", "dongwon",
    "매일유업", "남양유업", "서울우유",
    "코카콜라", "coca cola", "펩시", "pepsi",
    "스타벅스", "starbucks", "네스카페", "nescafe",
    "해태", "롯데", "lotte", "오리온", "orion",
    "빙그레", "binggrae",
    "하이트진로", "카스", "cass",
}

# 뷰티 / 화장품
_BEAUTY_BRANDS = {
    "아모레퍼시픽", "amorepacific", "설화수", "sulwhasoo",
    "이니스프리", "innisfree", "라네즈", "laneige",
    "에뛰드", "etude", "미샤", "missha",
    "더페이스샵", "thefaceshop", "스킨푸드", "skinfood",
    "올리브영", "oliveyoung",
    "로레알", "loreal", "에스티로더", "estee lauder",
    "맥", "mac", "클리니크", "clinique",
    "시세이도", "shiseido",
    "뉴트로지나", "neutrogena",
    "AHC", "ahc", "메디힐", "mediheal",
    "닥터자르트", "dr.jart",
}

# 가구 / 인테리어
_FURNITURE_BRANDS = {
    "한샘", "hanssem", "리바트", "livart", "일룸", "iloom",
    "시디즈", "sidiz", "듀오백", "duoback",
    "까사미아", "casamia", "에몬스", "emons",
    "에이스침대", "시몬스", "simmons", "씰리", "sealy",
    "템퍼", "tempur",
    "데스커", "desker",
}

# 스포츠 / 아웃도어
_SPORTS_BRANDS = {
    "아식스", "asics", "미즈노", "mizuno",
    "언더아머", "under armour", "리복", "reebok",
    "휠라", "fila", "프로스펙스", "prospecs",
    "블랙야크", "blackyak", "네파", "nepa", "아이더", "eider",
    "몽벨", "montbell", "콜맨", "coleman",
    "데카트론", "decathlon",
    "나이키골프", "타이틀리스트", "titleist", "캘러웨이", "callaway",
    "요넥스", "yonex", "윌슨", "wilson",
}

# 유아 / 키즈
_KIDS_BRANDS = {
    "보랒드림", "레고", "lego",
    "피셔프라이스", "fisher price", "뽀로로", "pororo",
    "핑크퐁", "pinkfong", "캐리", "헬로카봇",
    "타요", "콩순이", "시크릿쥬쥬",
    "맘스보드", "스토케", "stokke",
}

# 자동차 / 모빌리티
_AUTO_BRANDS = {
    "현대", "hyundai", "기아", "kia",
    "벤츠", "benz", "mercedes", "BMW", "bmw",
    "아우디", "audi", "폭스바겐", "volkswagen",
    "도요타", "toyota", "혼다", "honda", "닛산", "nissan",
    "테슬라", "tesla", "볼보", "volvo",
    "포르쉐", "porsche", "렉서스", "lexus",
}

# 기타 유명 브랜드 / 플랫폼 / 유통
_MISC_BRANDS = {
    "쿠팡", "coupang", "네이버", "naver",
    "카카오", "kakao", "배달의민족", "배민",
    "당근마켓", "번개장터",
    "11번가", "지마켓", "gmarket", "옥션", "auction",
    "위메프", "wemakeprice", "티몬", "tmon",
    "아마존", "amazon", "알리익스프레스", "aliexpress",
    "시즈맥스",
}


# ============================================================
# 통합 블랙리스트 (모든 카테고리 합산)
# ============================================================

TRADEMARK_BLACKLIST: set = (
    _ELECTRONICS_BRANDS
    | _HOUSEHOLD_BRANDS
    | _FASHION_BRANDS
    | _FOOD_BRANDS
    | _BEAUTY_BRANDS
    | _FURNITURE_BRANDS
    | _SPORTS_BRANDS
    | _KIDS_BRANDS
    | _AUTO_BRANDS
    | _MISC_BRANDS
)


def contains_trademark(keyword: str) -> bool:
    """
    키워드에 상표/브랜드가 포함되어 있는지 확인합니다.
    
    Args:
        keyword: 검사할 키워드 문자열
        
    Returns:
        True if trademark is found, False otherwise
    """
    keyword_lower = keyword.lower().replace(" ", "")
    
    for brand in TRADEMARK_BLACKLIST:
        brand_lower = brand.lower().replace(" ", "")
        if brand_lower in keyword_lower:
            return True
    return False


def filter_trademarked_keywords(keywords: list) -> tuple:
    """
    키워드 리스트에서 상표가 포함된 키워드를 분리합니다.
    
    Args:
        keywords: 검사할 키워드 리스트
        
    Returns:
        (safe_keywords, removed_keywords) 튜플
    """
    safe = []
    removed = []
    
    for kw in keywords:
        if contains_trademark(kw):
            removed.append(kw)
        else:
            safe.append(kw)
    
    return safe, removed


if __name__ == "__main__":
    # 테스트
    test_keywords = [
        "삼성 무선청소기", "무선 핸디 청소기", "다이슨 청소기",
        "스텐 빨래건조대", "원형 건조대", "이케아 선반",
        "나이키 운동화", "쿠션 운동화", "편한 러닝화",
        "데스크 정리함", "투명 화장품 정리함",
    ]
    
    safe, removed = filter_trademarked_keywords(test_keywords)
    print(f"✅ 안전한 키워드 ({len(safe)}개): {safe}")
    print(f"🚫 제거된 키워드 ({len(removed)}개): {removed}")
