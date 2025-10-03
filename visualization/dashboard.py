"""
실시간 기술 트렌드 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import requests
from collections import Counter
import os

# 페이지 설정
st.set_page_config(
    page_title="주식 기술 트렌드 분석",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .trend-up {
        color: #28a745;
    }
    .trend-down {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

class TrendDashboard:
    """트렌드 대시보드 클래스"""
    
    def __init__(self):
        self.data_sources = {
            'reddit': 'reddit_posts',
            'hackernews': 'hackernews_items', 
            'github': 'github_repos'
        }
    
    def load_data(self, source: str, days: int = 7):
        """데이터 로드"""
        # 실제 구현에서는 데이터베이스에서 로드
        # 여기서는 샘플 데이터 사용
        return self._generate_sample_data(source, days)
    
    def _generate_sample_data(self, source: str, days: int):
        """샘플 데이터 생성"""
        import random
        from datetime import datetime, timedelta
        
        tech_keywords = [
            'AI', 'machine learning', 'blockchain', 'cloud computing',
            'cybersecurity', 'data science', 'IoT', '5G', 'quantum computing',
            'AR', 'VR', 'metaverse', 'NFT', 'cryptocurrency'
        ]
        
        sentiments = ['positive', 'negative', 'neutral']
        
        data = []
        for i in range(100):
            date = datetime.now() - timedelta(days=random.randint(0, days))
            data.append({
                'id': f"{source}_{i}",
                'title': f"Sample {source} post {i}",
                'content': f"This is a sample {source} content about {random.choice(tech_keywords)}",
                'score': random.randint(1, 1000),
                'num_comments': random.randint(0, 100),
                'sentiment': random.choice(sentiments),
                'tech_keywords': random.sample(tech_keywords, random.randint(1, 3)),
                'created_at': date.isoformat(),
                'source': source
            })
        
        return pd.DataFrame(data)
    
    def render_header(self):
        """헤더 렌더링"""
        st.markdown('<h1 class="main-header">📈 주식 기술 트렌드 분석 대시보드</h1>', unsafe_allow_html=True)
        st.markdown("---")
    
    def render_sidebar(self):
        """사이드바 렌더링"""
        st.sidebar.title("⚙️ 설정")
        
        # 데이터 소스 선택
        data_source = st.sidebar.selectbox(
            "데이터 소스",
            options=list(self.data_sources.keys()),
            index=0
        )
        
        # 기간 선택
        days = st.sidebar.slider(
            "분석 기간 (일)",
            min_value=1,
            max_value=30,
            value=7
        )
        
        # 자동 새로고침
        auto_refresh = st.sidebar.checkbox("자동 새로고침", value=False)
        if auto_refresh:
            refresh_interval = st.sidebar.selectbox(
                "새로고침 간격",
                options=[30, 60, 300, 600],
                index=1,
                format_func=lambda x: f"{x}초"
            )
        
        return data_source, days, auto_refresh
    
    def render_metrics(self, data: pd.DataFrame):
        """메트릭 카드 렌더링"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 총 포스트 수",
                value=len(data),
                delta=f"+{len(data)//10}" if len(data) > 0 else "0"
            )
        
        with col2:
            avg_score = data['score'].mean() if 'score' in data.columns else 0
            st.metric(
                label="⭐ 평균 점수",
                value=f"{avg_score:.1f}",
                delta=f"+{avg_score//10:.1f}" if avg_score > 0 else "0"
            )
        
        with col3:
            avg_comments = data['num_comments'].mean() if 'num_comments' in data.columns else 0
            st.metric(
                label="💬 평균 댓글 수",
                value=f"{avg_comments:.1f}",
                delta=f"+{avg_comments//5:.1f}" if avg_comments > 0 else "0"
            )
        
        with col4:
            positive_ratio = len(data[data['sentiment'] == 'positive']) / len(data) if len(data) > 0 else 0
            st.metric(
                label="😊 긍정적 감성 비율",
                value=f"{positive_ratio:.1%}",
                delta=f"+{positive_ratio*10:.1%}" if positive_ratio > 0 else "0%"
            )
    
    def render_keyword_analysis(self, data: pd.DataFrame):
        """키워드 분석 렌더링"""
        st.subheader("🔍 기술 키워드 분석")
        
        # 모든 키워드 수집
        all_keywords = []
        for keywords in data['tech_keywords']:
            if isinstance(keywords, list):
                all_keywords.extend(keywords)
            elif isinstance(keywords, str):
                all_keywords.extend(keywords.split(','))
        
        if all_keywords:
            keyword_counts = Counter(all_keywords)
            top_keywords = dict(keyword_counts.most_common(15))
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 키워드 빈도 차트
                fig = px.bar(
                    x=list(top_keywords.values()),
                    y=list(top_keywords.keys()),
                    orientation='h',
                    title="상위 기술 키워드",
                    labels={'x': '빈도', 'y': '키워드'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 키워드 워드클라우드 (텍스트로 대체)
                st.subheader("키워드 분포")
                for keyword, count in list(top_keywords.items())[:10]:
                    st.write(f"**{keyword}**: {count}회")
        else:
            st.info("키워드 데이터가 없습니다.")
    
    def render_sentiment_analysis(self, data: pd.DataFrame):
        """감성 분석 렌더링"""
        st.subheader("😊 감성 분석")
        
        if 'sentiment' in data.columns:
            sentiment_counts = data['sentiment'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 감성 분포 파이 차트
                fig = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    title="감성 분포",
                    color_discrete_map={
                        'positive': '#28a745',
                        'negative': '#dc3545',
                        'neutral': '#6c757d'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 감성 통계
                st.subheader("감성 통계")
                for sentiment, count in sentiment_counts.items():
                    percentage = count / len(data) * 100
                    st.write(f"**{sentiment}**: {count}개 ({percentage:.1f}%)")
        else:
            st.info("감성 분석 데이터가 없습니다.")
    
    def render_engagement_trends(self, data: pd.DataFrame):
        """참여도 트렌드 렌더링"""
        st.subheader("📈 참여도 트렌드")
        
        if 'created_at' in data.columns and 'score' in data.columns:
            # 시간별 트렌드
            data['date'] = pd.to_datetime(data['created_at']).dt.date
            daily_stats = data.groupby('date').agg({
                'score': 'mean',
                'num_comments': 'mean'
            }).reset_index()
            
            # 이중 축 차트
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=daily_stats['date'], y=daily_stats['score'], 
                          name="평균 점수", line=dict(color='blue')),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=daily_stats['date'], y=daily_stats['num_comments'], 
                          name="평균 댓글 수", line=dict(color='red')),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="날짜")
            fig.update_yaxes(title_text="평균 점수", secondary_y=False)
            fig.update_yaxes(title_text="평균 댓글 수", secondary_y=True)
            fig.update_layout(title="일별 참여도 트렌드")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("참여도 데이터가 없습니다.")
    
    def render_top_posts(self, data: pd.DataFrame):
        """상위 포스트 렌더링"""
        st.subheader("🏆 인기 포스트")
        
        if 'score' in data.columns:
            top_posts = data.nlargest(10, 'score')
            
            for idx, post in top_posts.iterrows():
                with st.expander(f"#{idx+1} {post['title'][:50]}... (점수: {post['score']})"):
                    st.write(f"**제목**: {post['title']}")
                    st.write(f"**내용**: {post['content'][:200]}...")
                    st.write(f"**점수**: {post['score']}")
                    st.write(f"**댓글 수**: {post['num_comments']}")
                    st.write(f"**감성**: {post['sentiment']}")
                    st.write(f"**키워드**: {', '.join(post['tech_keywords'])}")
        else:
            st.info("포스트 데이터가 없습니다.")
    
    def run(self):
        """대시보드 실행"""
        # 헤더 렌더링
        self.render_header()
        
        # 사이드바 설정
        data_source, days, auto_refresh = self.render_sidebar()
        
        # 자동 새로고침
        if auto_refresh:
            st.rerun()
        
        # 데이터 로드
        with st.spinner(f"{data_source} 데이터 로딩 중..."):
            data = self.load_data(data_source, days)
        
        if data.empty:
            st.warning(f"{data_source} 데이터가 없습니다.")
            return
        
        # 메트릭 카드
        self.render_metrics(data)
        
        st.markdown("---")
        
        # 키워드 분석
        self.render_keyword_analysis(data)
        
        st.markdown("---")
        
        # 감성 분석
        self.render_sentiment_analysis(data)
        
        st.markdown("---")
        
        # 참여도 트렌드
        self.render_engagement_trends(data)
        
        st.markdown("---")
        
        # 상위 포스트
        self.render_top_posts(data)
        
        # 푸터
        st.markdown("---")
        st.markdown(
            f"<div style='text-align: center; color: #666;'>"
            f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            f"</div>",
            unsafe_allow_html=True
        )


def main():
    """메인 함수"""
    dashboard = TrendDashboard()
    dashboard.run()


if __name__ == '__main__':
    main()

