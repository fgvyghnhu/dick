import streamlit as st
import requests
import json

# ===================== 页面基础配置（适配抖音风格） =====================
st.set_page_config(
    page_title="抖音话题助手 (Kimi AI版)",
    page_icon="🎵",
    layout="wide"
)

# 自定义样式（抖音红为主色调）
st.markdown("""
    <style>
    .main {padding: 2rem;}
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px; 
        border: 1px solid #ff2e2e; 
        padding: 0.6rem;
        font-size: 14px;
    }
    .stButton button {
        background-color: #ff2e2e; 
        color: white; 
        border-radius: 8px; 
        padding: 0.6rem 2rem;
        border: none;
        font-weight: 600;
    }
    .stButton button:hover {
        background-color: #e02727;
    }
    .sidebar .sidebar-content {
        background-color: #fef7f8; 
        padding: 1.5rem;
    }
    .generated-content {
        background-color: #f9fafb; 
        padding: 1.5rem; 
        border-radius: 8px; 
        margin-top: 1rem;
        border-left: 4px solid #ff2e2e;
    }
    .topic-tag {
        color: #ff2e2e;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)


# ===================== Kimi API 核心函数（保留，仅适配Prompt） =====================
def call_kimi_api(api_key, prompt, model="moonshot-v1-8k"):
    """
    调用Kimi（月之暗面）API生成抖音相关内容
    :param api_key: Kimi的API密钥
    :param prompt: 适配抖音的提示词
    :param model: 使用的模型
    :return: 生成的文本内容或错误信息
    """
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,  # 抖音内容更需要创意，调高创意度
        "max_tokens": 1500  # 支持更长的文案/话题生成
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        return f"API请求错误：{e}，响应内容：{response.text}"
    except requests.exceptions.Timeout:
        return "API请求超时，请检查网络或稍后重试"
    except Exception as e:
        return f"未知错误：{str(e)}"


# ===================== Streamlit 界面交互（抖音场景定制） =====================
# 侧边栏：API密钥配置（保留核心功能，文案微调）
with st.sidebar:
    st.header("🔑 API配置")
    kimi_api_key = st.text_input(
        "Kimi API Key",
        type="password",
        placeholder="请输入你的Kimi API密钥",
        help="API Key可从月之暗面官网（https://platform.moonshot.cn/）获取"
    )

    # 模型选择（保留，适配抖音长文案需求）
    model_option = st.selectbox(
        "选择模型（越长支持内容越丰富）",
        ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        help="8k：短文案/话题；32k/128k：长脚本/多话题组合"
    )

# 主界面：抖音话题助手核心功能
st.title("🎵 抖音话题助手")
st.subheader("基于Kimi AI生成爆款话题、文案、脚本")

# 功能选择（抖音核心需求分类）
function_type = st.radio(
    "选择生成类型",
    ["爆款话题推荐", "短视频文案", "直播口播脚本", "评论区互动话术"],
    horizontal=True
)

# 输入区（根据选择的功能适配占位符）
placeholder_map = {
    "爆款话题推荐": "例如：宝妈副业、秋冬穿搭、职场干货（生成10个高热度相关话题）",
    "短视频文案": "例如：秋冬奶茶推荐，要求口语化、有钩子、结尾引导点赞",
    "直播口播脚本": "例如：美妆直播开场+产品介绍+逼单话术，时长3分钟",
    "评论区互动话术": "例如：回复粉丝问产品价格的话术，亲切有转化力"
}

user_input = st.text_area(
    "输入你的需求",
    placeholder=placeholder_map[function_type],
    height=150
)

# 额外配置（抖音专属：是否带热门标签/背景音乐建议）
add_tags = st.checkbox("✅ 生成时附带热门标签（#xxx）", value=True)
add_bgm = st.checkbox("🎶 推荐适配的背景音乐风格（仅文案/脚本类）", value=True)

# 生成按钮（抖音风格文案）
if st.button("🔥 生成爆款内容", use_container_width=True):
    # 校验输入
    if not kimi_api_key:
        st.error("❌ 请先在左侧侧边栏输入Kimi API Key！")
    elif not user_input.strip():
        st.warning("⚠️ 请输入生成需求！")
    else:
        # 构建抖音专属Prompt（核心改造点）
        prompt_base = f"""
        你是专业的抖音运营助手，请按照「{function_type}」类型，基于需求「{user_input}」生成内容，要求：
        1. 符合抖音平台调性，语言口语化、有网感，避免生硬；
        2. 结构清晰，爆款话题要带热度分析，文案要有开头钩子（前3秒吸引人）；
        3. 内容原创，符合抖音内容规范，无违规词；
        """

        # 附加配置
        if add_tags:
            prompt_base += "4. 生成5-8个相关的抖音热门标签（格式：#话题名）；"
        if add_bgm and function_type in ["短视频文案", "直播口播脚本"]:
            prompt_base += "5. 推荐3首适配的背景音乐风格（例如：温馨轻音乐、动感流行乐）；"

        # 显示加载状态
        with st.spinner("🤔 AI正在挖掘爆款话题..."):
            generated_text = call_kimi_api(kimi_api_key, prompt_base, model_option)

        # 展示结果（抖音风格格式化）
        st.success("✅ 爆款内容生成完成！")
        st.markdown(f'<div class="generated-content">{generated_text}</div>', unsafe_allow_html=True)

# 示例提示（抖音场景专属）
with st.expander("📌 爆款需求参考"):
    st.write("""
    1. 爆款话题推荐：生成10个关于「冬季养生」的抖音高热度话题，带热度等级
    2. 短视频文案：生成一条「平价羽绒服推荐」的抖音文案，开头有钩子，结尾引导关注
    3. 直播口播脚本：生成家居清洁产品直播的开场+产品卖点+逼单话术，时长5分钟
    4. 评论区互动话术：生成回复粉丝问「产品效果」的互动话术，亲切且能促单
    """)