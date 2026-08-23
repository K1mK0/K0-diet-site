import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 웹페이지 기본 설정
st.set_page_config(page_title="청소년을 위한 맞춤 식단 추천", page_icon="🥗", layout="centered")

# 상단 UI (보내주신 사진 스타일 반영)
st.markdown("<h1 style='text-align: center;'>청소년을 위한 맞춤 식단 추천</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>지친 청소년들의 현실적인 식습관 고민을 해결해 주는 스마트 푸드 가이드입니다!</p>", unsafe_allow_html=True)
st.markdown("---")

# 1. 고민 카테고리 선택 (선택 안 함 옵션 추가)
st.markdown("💡 **해결하고 싶은 고민 선택**")
category = st.selectbox(
    "고민 선택",
    (
        "선택 안 함 (고민 없이 자유롭게 추천 받기)",
        "1) 📚 오후 수업만 되면 찾아오는 '식곤증' 줄이기",
        "2) ⚖️ 건강하게 체중을 관리하는 '다이어트' 식단",
        "3) 🍔 먹고 싶은데 살찔까 걱정되는 음식 '대체제' 찾기"
    ),
    label_visibility="collapsed"
)

# 2. 카테고리별 맞춤 데이터 정의
condition = {}

if "선택 안 함" in category:
    condition = {
        "name": "자유로운 메뉴 추천",
        "avoid": [],
        "tag": "건강식 영양",
        "reason": "특별한 제한 없이 입력한 재료를 바탕으로 제공하는 추천 식단"
    }
elif "식곤증" in category:
    condition = {
        "name": "식곤증 예방 및 집중력 유지 식단",
        "avoid": ['라면', '면', '짜장면', '피자', '햄버거', '빵', '과자', '설탕', '떡볶이'],
        "tag": "단백질 통곡물 채소 저탄수화물 샐러드",
        "reason": "혈당 스파이크를 유발하는 정제 탄수화물을 배제하고, 인슐린 급증을 막아 식후 졸음을 방지하는 단백질·식이섬유 중심 구성"
    }
elif "다이어트" in category:
    condition = {
        "name": "칼로리 부담 없는 건강 다이어트 식단",
        "avoid": ['튀김', '삼겹살', '버터', '마요네즈', '설탕', '떡볶이', '크림'],
        "tag": "저칼로리 닭가슴살 두부 곤약 채소",
        "reason": "포화지방과 단순당을 제한하고 포만감을 오래 유지하는 저칼로리 고단백 식품 중심"
    }
elif "대체제" in category:
    craving = st.text_input("😋 지금 어떤 음식을 먹고 싶나요? (예: 떡볶이, 치킨, 피자, 초콜릿)")
    if craving:
        condition = {
            "name": f"'{craving}' 건강 대체 레시피 추천",
            "avoid": ['밀가루', '설탕', '트랜스지방'],
            "tag": f"건강한 {craving} 대체 저당 저칼로리",
            "reason": f"고열량 간식인 '{craving}'의 영양적 문제점을 보완하고, 대체 식재료를 활용한 건강 지향적 레시피 매칭"
        }
    else:
        condition = {
            "name": "건강한 대체 식단",
            "avoid": ['인스턴트'],
            "tag": "저당 저칼로리 건강식",
            "reason": "고열량 음식을 대체할 수 있는 영양 균형 식단"
        }

# 재료 입력창
st.markdown("🥬 **먹고 싶은 재료나 음식을 입력하세요**")
if "대체제" not in category:
    user_input = st.text_input("재료 입력", "두부", label_visibility="collapsed")
else:
    user_input = craving if 'craving' in locals() and craving else "두부"

st.markdown("")

# 3. 크롤링 및 추천 실행 버튼
if st.button("🔍 맞춤형 식단 추천받기"):
    if not user_input and "대체제" not in category:
        st.warning("재료나 음식을 입력해주세요!")
    else:
        search_keyword = f"{user_input} {condition['tag']}"
        base_url = "https://www.10000recipe.com/recipe/list.html?q="
        site_root = "https://www.10000recipe.com"
        encoded_query = urllib.parse.quote(search_keyword)
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(base_url + encoded_query, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            recipe_list = soup.select('ul.common_sp_list_ul li.common_sp_list_li')

            st.markdown(f"### 🔍 분석 결과: {condition['name']}")
            st.info(f"💡 **식품영양학적 추천 원리:** {condition['reason']}")
            st.markdown("---")

            count = 0
            for item in recipe_list:
                title_tag = item.select_one('div.common_sp_caption_tit')
                link_tag = item.select_one('a.common_sp_link')
                
                if title_tag and link_tag:
                    title = title_tag.get_text().strip()
                    link = site_root + link_tag['href']
                    
                    # 필터링 로직
                    is_safe = True
                    for word in condition['avoid']:
                        if word in title:
                            is_safe = False
                            break
                    
                    if is_safe:
                        st.success(f"✅ **[추천 레시피] {title}**")
                        st.markdown(f"🔗 [레시피 보러 가기]({link})")
                        st.markdown("---")
                        count += 1
                        
                        if count >= 3: 
                            break 
            
            if count == 0:
                st.warning("현재 조건에 딱 맞는 안전한 레시피를 찾지 못했어요. 검색어를 살짝 바꿔보세요!")

        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
