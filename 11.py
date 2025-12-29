import streamlit as st
# 核心：用ChatOpenAI对接Kimi（替代缺失的ChatMoonshot）
from langchain_openai import ChatOpenAI
# 修正LangChain 1.x的导入路径
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
import time

# ===================== 页面基础配置（保留抖音风格） =====================
st.set_page_config(
    page_title="抖音话题助手 (LangChain+Kimi版)",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式（抖音红为主色调）
st.markdown("""
    <style>
    .main {padding: 1rem !important;}
    @media (max-width: 768px) {.main {padding: 0.5rem !important;}}
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px; border: 1px solid #ff2e2e; padding: 0.6rem; font-size: 14px; width: 100%;
    }
    .stButton button {
        background-color: #ff2e2e; color: white; border-radius: 8px; padding: 0.6rem 2rem;
        border: none; font-weight: 600; transition: all 0.2s ease;
    }
    .stButton button:hover {background-color: #e02727; transform: translateY(-2px);}
    .stButton button:disabled {
        background-color: #ff9494 !important; cursor: not-allowed; transform: none !important;
    }
    .sidebar .sidebar-content {background-color: #fef7f8; padding: 1.5rem;}
    .generated-content {
        background-color: #f9fafb; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;
        border-left: 4px solid #ff2e2e; white-space: pre-wrap;
    }
    .copy-btn {margin-top: 0.5rem; padding: 0.4rem 1rem; font-size: 12px;}
    </style>
""", unsafe_allow_html=True)


# ===================== 初始化会话状态（移除ChatMessageHistory） =====================
def init_session_state():
    """初始化Streamlit会话状态，去掉会话历史相关逻辑"""
    if "kimi_api_key" not in st.session_state:
        st.session_state.kimi_api_key = ""
    if "generated_result" not in st.session_state:
        st.session_state.generated_result = ""
    if "copy_success" not in st.session_state:
        st.session_state.copy_success = False


# ===================== LangChain + Kimi 核心函数（适配1.x） =====================
def init_kimi_llm(api_key, model="moonshot-v1-8k"):
    """初始化LangChain的Kimi LLM实例（替换ChatMoonshot为ChatOpenAI）"""
    try:
        llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",  # Kimi的OpenAI兼容接口
            model_name=model,
            temperature=0.9,  # 抖音内容创意度
            max_tokens=1500  # 最大生成字数
        )
        return llm
    except Exception as e:
        return f"初始化Kimi模型失败：{str(e)}"


def generate_douyin_content(api_key, function_type, user_input, add_tags, add_bgm, model="moonshot-v1-8k"):
    """
    基于LangChain生成抖音内容（移除会话历史，保留核心生成逻辑）
    """
    # 1. 初始化Kimi LLM
    llm = init_kimi_llm(api_key, model)
    if isinstance(llm, str):  # 初始化失败返回错误信息
        return llm

    # 2. 定义LangChain提示词模板（保留原有结构化模板）
    prompt_template = PromptTemplate(
        input_variables=["function_type", "user_input", "add_tags", "add_bgm"],
        template="""
        你是专业的抖音运营专家，熟悉抖音爆款逻辑和平台规范，请严格按照以下要求生成内容：

        【生成类型】{function_type}
        【用户需求】{user_input}

        【核心要求】
        1. 调性：符合抖音平台风格，语言口语化、有网感，无生硬广告感，无违规词；
        2. 结构：
           - 爆款话题推荐：生成10个高热度话题，附带热度等级（高/中/低）；
           - 短视频文案：开头3秒有钩子，结尾引导互动（点赞/关注/评论）；
           - 直播口播脚本：分段落标注（开场/产品介绍/逼单/收尾），标注时长；
           - 评论区互动话术：亲切自然，兼顾用户体验和转化力；
        3. 标签要求：{add_tags}
        4. 背景音乐：{add_bgm}
        """.strip()
    )

    # 3. 构建标签/背景音乐的提示词补充
    tag_prompt = "生成5-8个相关的抖音热门标签（格式：#话题名）" if add_tags else "无需生成标签"
    bgm_prompt = ""
    if add_bgm and function_type in ["短视频文案", "直播口播脚本"]:
        bgm_prompt = "推荐3首适配的背景音乐风格（例如：温馨轻音乐、动感流行乐）"
    else:
        bgm_prompt = "无需推荐背景音乐"

    # 4. 渲染提示词模板
    prompt = prompt_template.format(
        function_type=function_type,
        user_input=user_input,
        add_tags=tag_prompt,
        add_bgm=bgm_prompt
    )

    # 5. 调用Kimi（LangChain 1.x规范：用invoke）
    try:
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        # 处理空结果
        if not response.content.strip():
            return "⚠️ AI生成内容为空，请调整需求后重试。"
        return response.content.strip()
    except Exception as e:
        return f"❌ 生成失败：{str(e)}（请检查API Key是否有效）"


# ===================== 工具函数 =====================
def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    st.session_state.copy_success = True
    time.sleep(3)
    st.session_state.copy_success = False


# ===================== 主界面逻辑 =====================
# 初始化会话状态
init_session_state()

# 侧边栏：API配置
with st.sidebar:
    st.header("🔑 API配置")
    kimi_api_key = st.text_input(
        "Kimi API Key",
        type="password",
        placeholder="请输入你的Kimi API密钥",
        help="API Key可从月之暗面官网（https://platform.moonshot.cn/）获取",
        value=st.session_state.kimi_api_key
    )
    st.session_state.kimi_api_key = kimi_api_key

    # 模型选择
    model_option = st.selectbox(
        "选择Kimi模型",
        ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        index=0,
        help="8k（免费额度多）：短文案/话题；32k/128k：长脚本/多话题组合"
    )

    # 清空缓存按钮
    if st.button("🗑️ 清空API Key缓存", use_container_width=True):
        st.session_state.kimi_api_key = ""
        st.rerun()

# 主界面：抖音功能交互
st.title("🎵 抖音话题助手 (LangChain+Kimi版)")
st.subheader("基于LangChain框架对接Kimi AI，更易扩展")

# 功能选择
function_type = st.radio(
    "选择生成类型",
    ["爆款话题推荐", "短视频文案", "直播口播脚本", "评论区互动话术"],
    horizontal=True,
    key="function_type"
)

# 输入区
placeholder_map = {
    "爆款话题推荐": "例如：宝妈副业、秋冬穿搭、职场干货（生成10个高热度相关话题）",
    "短视频文案": "例如：秋冬奶茶推荐，要求口语化、有钩子、结尾引导点赞",
    "直播口播脚本": "例如：美妆直播开场+产品介绍+逼单话术，时长3分钟",
    "评论区互动话术": "例如：回复粉丝问产品价格的话术，亲切有转化力"
}
user_input = st.text_area(
    "输入你的需求",
    placeholder=placeholder_map[function_type],
    height=150,
    key="user_input"
)

# 额外配置
col1, col2 = st.columns(2)
with col1:
    add_tags = st.checkbox("✅ 生成时附带热门标签（#xxx）", value=True, key="add_tags")
with col2:
    add_bgm = st.checkbox("🎶 推荐适配的背景音乐风格", value=True, key="add_bgm")

# 生成按钮
btn_disabled = not (kimi_api_key and user_input.strip())
if st.button("🔥 生成爆款内容", use_container_width=True, disabled=btn_disabled):
    with st.spinner("🤔 AI正在挖掘爆款话题..."):
        result = generate_douyin_content(
            api_key=kimi_api_key,
            function_type=function_type,
            user_input=user_input,
            add_tags=add_tags,
            add_bgm=add_bgm,
            model=model_option
        )
    st.session_state.generated_result = result

# 展示生成结果
if st.session_state.generated_result:
    st.success("✅ 爆款内容生成完成！")
    st.markdown(f'<div class="generated-content">{st.session_state.generated_result}</div>', unsafe_allow_html=True)
    # 复制按钮
    col_copy, _ = st.columns([1, 9])
    with col_copy:
        if st.button("📋 复制内容", key="copy_btn"):
            copy_to_clipboard(st.session_state.generated_result)
            st.success("✅ 复制成功！") if st.session_state.copy_success else None

# 示例提示
with st.expander("📌 爆款需求参考"):
    st.write("""
    1. 爆款话题推荐：生成10个关于「冬季养生」的抖音高热度话题，带热度等级
    2. 短视频文案：生成一条「平价羽绒服推荐」的抖音文案，开头有钩子，结尾引导关注
    3. 直播口播脚本：生成家居清洁产品直播的开场+产品卖点+逼单话术，时长5分钟
    4. 评论区互动话术：生成回复粉丝问「产品效果」的互动话术，亲切且能促单
    """)
