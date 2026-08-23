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
        "2) ⚖️ 건강하게 체중을 관리하는 '다이어트' 식단"
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
        "science_reason": "특별한 제한이나 제약 없이, 누구나 즐기기 좋은 대중적인 메뉴입니다."
    }
elif "식곤증" in category:
    condition = {
        "name": "식곤증 예방 및 집중력 유지 식단",
        "avoid": ['라면', '면', '짜장면', '피자', '햄버거', '빵', '과자', '설탕', '떡볶이', '초콜릿', '초코', '시럽', '마라탕', '마라'],
        "random_pool": ["닭가슴살 샐러드", "소고기 샐러드", "연어구이", "샌드위치", "단호박죽", "스크램블에그"],
        "science_reason": "정제 탄수화물과 당분, 고지방식은 혈당을 급격히 올려(혈당 스파이크) 뇌에 피로물질을 쌓고 졸음을 유발합니다. 단백질과 식이섬유가 풍부한 식단이 졸음을 막아줍니다."
    }
elif "다이어트" in category:
    condition = {
        "name": "칼로리 부담 없는 건강 다이어트 식단",
        # 다이어트 시 피해야 할 고열량/고자극 식재료 및 음식 정의
        "avoid": ['튀김', '삼겹살', '버터', '마요네즈', '설탕', '크림', '초콜릿', '초코', '시럽', '마라탕', '마라', '떡볶이', '라면', '패스트푸드'],
        "random_pool": ["두부스테이크", "곤약볶음면", "닭가슴살볶음밥", "오이샐러드", "버섯볶음", "계란찜"],
        "science_reason": "포화지방과 단순당, 고자극 식품은 체내 지방 축적을 촉진합니다. 지방과 당류를 줄이고 단백질과 채소 중심의 식단이 체중 관리에 도움을 줍니다."
    }

# 재료 입력창
st.markdown("🥬 **먹고 싶은 재료나 음식을 입력하세요** (먹고 싶은 게 없다면 '없음' 입력)")
user_input = st.text_input("재료 입력", "", placeholder="예: 닭가슴살, 계란, 또는 없음", label_visibility="collapsed")

st.markdown("")

# 3. 크롤링 및 추천 실행 버튼
if st.button("🔍 맞춤형 식단 추천받기"):
    
    # 고자극·고칼로리 음식 입력 시 차단해야 하는 키워드 리스트
    heavy_foods = ['마라탕', '마라', '라면', '짜장면', '짬뽕', '피자', '햄버거', '치킨', '튀김', '떡볶이']
    
    is_inappropriate = False
    if not is_free_mode and user_input:
        for hf in heavy_foods:
            if hf in user_input.strip():
                is_inappropriate = True
                break

    # 부적합한 음식을 입력했을 때의 예외 처리
    if is_inappropriate:
        st.markdown(f"### ⚠️ 안내: '{user_input.strip()}'(은)는 선택하신 고민 카테고리에 부적합합니다")
        if "식곤증" in category:
            st.error(f"마라탕이나 고자극·고지방 음식은 혈당 스파이크를 유발해 **심한 졸음과 식곤증을 극대화**시킵니다. 😢")
        else:
            st.error(f"마라탕이나 고열량·고지방 음식은 **체중 증가와 지방 축적을 유발**하므로 다이어트 식단으로 적합하지 않습니다. 😢")
        st.warning("⚠️ **검색 결과가 없습니다.** 건강한 다이어트/식곤증 예방을 위해 닭가슴살, 두부, 채소 등 가벼운 식재료를 입력해 주세요!")
    else:
        if not user_input or user_input.strip() in ["없음", "없다", "몰라", "추천해줘"]:
            search_keyword = random.choice(condition["random_pool"])
            is_random_mode = True
        else:
            search_keyword = user_input.strip()
            is_random_mode = False

        base_url = "https://www000recipe.com/recipe/list.html?q=" if False else "https://www.10000recipe.com/recipe/list.html?q="
        encoded_query = urllib.parse.quote(search_keyword)
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(base_url + encoded_query, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            recipe_list = soup.select('ul.common_sp_list_ul li.common_sp_list_li')

            if is_free_mode:
                if is_random_mode:
                    st.markdown(f"### 🎲 랜덤 추천 메뉴: '{search_keyword}'")
                else:
                    st.markdown(f"### 🔍 검색 결과: '{search_keyword}'")
            else:
                if is_random_mode:
                    st.markdown(f"### 🎲 추천 결과: {condition['name']} (선택된 메뉴: {search_keyword})")
                else:
                    st.markdown(f"### 🔍 검색 결과: {condition['name']} ('{user_input.strip()}' 관련)")
            
            st.info(f"💡 **왜 이 식단이 도움이 될까요?**\n\n{condition['science_reason']}")
            st.markdown("---")

            count = 0
            for item in recipe_list:
                title_tag = item.select_one('div.common_sp_caption_tit')
                link_tag = item.select_one('a.common_sp_link')
                
                if title_tag and link_tag:
                    title = title_tag.get_text().strip()
                    link = "https://www.10000recipe.com" + link_tag['href']
                    
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
            
            # 검색 결과가 없거나 필터링되어 남은 게 없다면 명확하게 없다고 안내
            if count == 0:
                st.warning(f"⚠️ '{search_keyword}'와(과) 관련된 조건에 부합하는 안전한 레시피를 찾지 못했습니다. **검색 결과가 없습니다.** 다른 재료를 입력해 보세요!")

        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
