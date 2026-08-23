import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import random

# 웹페이지 기본 설정
st.set_page_config(page_title="청소년을 위한 맞춤 식단 추천", page_icon="🥗", layout="centered")

# 상단 UI
st.markdown("<h1 style='text-align: center;'>청소년을 위한 맞춤 식단 추천</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>지친 청소년들의 현실적인 식습관 고민을 해결해 주는 스마트 푸드 가이드입니다!</p>", unsafe_allow_html=True)
st.markdown("---")

# 1. 고민 카테고리 선택
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

# 2. 카테고리별 데이터 정의
condition = {}
is_free_mode = False

if "선택 안 함" in category:
    is_free_mode = True
    condition = {
        "name": "자유로운 전체 메뉴 추천",
        "avoid": [],
        "random_pool": ["김치찌개", "떡볶이", "파스타", "치킨", "볶음밥", "제육볶음", "카레", "짜장면", "토스트", "돈가스", "오므라이스", "부대찌개"],
        "reason": "특별한 제한이나 카테고리 없이 추천"
    }
elif "식곤증" in category:
    condition = {
        "name": "식곤증 예방 및 집중력 유지 식단",
        "avoid": ['라면', '면', '짜장면', '피자', '햄버거', '빵', '과자', '설탕', '떡볶이', '초콜릿', '초코', '시럽'],
        "random_pool": ["닭가슴살 샐러드", "소고기 샐러드", "연어구이", "샌드위치", "단호박죽", "스크램블에그"],
        "reason": "혈당 스파이크를 유발하는 정제 탄수화물과 당분을 배제하고, 식후 졸음을 방지하는 단백질·채소 중심 구성"
    }
elif "다이어트" in category:
    condition = {
        "name": "칼로리 부담 없는 건강 다이어트 식단",
        "avoid": ['튀김', '삼겹살', '버터', '마요네즈', '설탕', '떡볶이', '크림', '초콜릿', '초코', '시럽'],
        "random_pool": ["두부스테이크", "곤약볶음면", "닭가슴살볶음밥", "오이샐러드", "버섯볶음", "계란찜"],
        "reason": "포화지방과 단순당, 고열량 당류를 제한하고 포만감을 유지하는 저칼로리 고단백 식품 중심"
    }
elif "대체제" in category:
    craving = st.text_input("😋 지금 어떤 음식을 먹고 싶나요? (예: 떡볶이, 치킨, 피자, 초콜릿)")
    if craving:
        condition = {
            "name": f"'{craving}' 건강 대체 레시피 추천",
            "avoid": ['밀가루', '설탕', '트랜스지방'],
            "random_pool": [f"다이어트 {craving}", f"저당 {craving}", "두부요리", "오트밀요리", "통밀빵샌드위치"],
            "reason": f"고열량 간식인 '{craving}'의 영양적 문제점을 보완하고 대체 식재료를 활용한 레시피 매칭"
        }
    else:
        condition = {
            "name": "건강한 대체 식단",
            "avoid": ['인스턴트', '설탕'],
            "random_pool": ["귀리밥", "통밀샌드위치", "그릭요거트", "단백질쉐이크"],
            "reason": "고열량 음식을 대체할 수 있는 영양 균형 식단"
        }

# 재료 입력창
st.markdown("🥬 **먹고 싶은 재료나 음식을 입력하세요** (먹고 싶은 게 없다면 '없음' 입력)")
if "대체제" not in category:
    user_input = st.text_input("재료 입력", "", placeholder="예: 초콜릿, 닭가슴살, 또는 없음", label_visibility="collapsed")
else:
    user_input = craving if 'craving' in locals() and craving else ""

st.markdown("")

# 3. 크롤링 및 추천 실행 버튼
if st.button("🔍 맞춤형 식단 추천받기"):
    
    if not user_input or user_input.strip() in ["없음", "없다", "몰라", "추천해줘"]:
        search_keyword = random.choice(condition["random_pool"])
        is_random_mode = True
    else:
        search_keyword = user_input.strip()
        is_random_mode = False

    base_url = "https://www.10000recipe.com/recipe/list.html?q="
    encoded_query = urllib.parse.quote(search_keyword)
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(base_url + encoded_query, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        recipe_list = soup.select('ul.common_sp_list_ul li.common_sp_list_li')

        # 화면 안내 문구 출력
        if is_free_mode:
            if is_random_mode:
                st.markdown(f"### 🎲 랜덤 추천 메뉴: '{search_keyword}'")
                st.info(f"💡 **안내:** 고민과 재료를 비워두셔서, 인기 메뉴 중 무작위로 골라왔어요!")
            else:
                st.markdown(f"### 🔍 검색 결과: '{search_keyword}'")
                st.info(f"💡 **안내:** 입력하신 재료를 바탕으로 추천합니다.")
        else:
            if is_random_mode:
                st.markdown(f"### 🎲 추천 결과: {condition['name']} (선택된 메뉴: {search_keyword})")
                st.info(f"💡 **식품영양학적 추천 원리:** {condition['reason']}")
            else:
                st.markdown(f"### 🔍 검색 결과: {condition['name']} ('{search_keyword}' 검색)")
                st.info(f"💡 **식품영양학적 추천 원리:** {condition['reason']}")
        
        st.markdown("---")

        count = 0
        for item in recipe_list:
            title_tag = item.select_one('div.common_sp_caption_tit')
            link_tag = item.select_one('a.common_sp_link')
            
            if title_tag and link_tag:
                title = title_tag.get_text().strip()
                link = "https://www.10000recipe.com" + link_tag['href']
                
                # 필터링 로직 (기피 식재료가 타이틀에 포함되어 있는지 확인)
                is_safe = True
                for word in condition['avoid']:
                    if word in title:
                        is_safe = False
                        break
                
                # 안전한 레시피인 경우에만 출력 (개수 제한 없이 나오는 대로 출력)
                if is_safe:
                    st.success(f"✅ **[추천 레시피] {title}**")
                    st.markdown(f"🔗 [레시피 보러 가기]({link})")
                    st.markdown("---")
                    count += 1
        
        # 검색 결과가 하나도 없을 때 명확하게 안내 메시지 출력
        if count == 0:
            st.warning(f"⚠️ '{search_keyword}'(은)는 선택하신 고민 카테고리의 건강 기준(유해 성분 회피)에 부합하는 안전한 레시피를 찾지 못했습니다. 다른 재료를 입력해 보세요!")

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
