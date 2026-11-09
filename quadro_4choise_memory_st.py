# quadro_4choise_memory_st.py
# 二次関数の択問題

import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
import time
import gspread
from google.oauth2.service_account import Credentials

# =====================================================
# フォント設定
# =====================================================
font_manager.fontManager.addfont("ipaexg.ttf")

plt.rcParams["font.family"] = "IPAexGothic"
plt.rcParams["axes.unicode_minus"] = False

#plt.rcParams["font.family"] = "Meiryo"

# =====================================================
# 頂点形式の表示
# =====================================================
def format_vertex_form(a, p, q):

    if a == 1:
        a_str = ""
    elif a == -1:
        a_str = "-"
    else:
        a_str = str(a)

    if p == 0:
        p_str = "x"
    elif p > 0:
        p_str = f"(x-{p})"
    else:
        p_str = f"(x+{-p})"

    if q > 0:
        q_str = f"+{q}"
    elif q < 0:
        q_str = f"-{-q}"
    else:
        q_str = ""

    return f"y={a_str}{p_str}²{q_str}"


# =====================================================
# 二次関数生成
# =====================================================
def generate_quadratic():

    a = random.choice([-3, -2, -1, 1, 2, 3])

    p = random.randint(-2, 2)

    q = random.randint(-2, 2)

    return a, p, q


# =====================================================
# Google Sheetsへ送信
# =====================================================
def send_to_sheet(
    eq_str,
    selected,
    correct_index,
    is_correct,
    elapsed
):

    try:

        if "gcp_service_account" not in st.secrets:
            return

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=scope
        )

        gc = gspread.authorize(creds)

        sheet = gc.open_by_key(
            "1S_koL8VGN2iPs11BR-dl5aDpmfRGCWKzwam6AKB1FmY"
        ).worksheet("二次関数_履歴")

        now = time.strftime("%Y-%m-%d %H:%M:%S")

        sheet.append_row([
            now,
            eq_str,
            selected + 1,
            correct_index + 1,
            "○" if is_correct else "×",
            elapsed
        ])

    except Exception:
        pass


# =====================================================
# 新しい問題
# =====================================================
def new_problem():

    correct = generate_quadratic()

    choices = [correct]

    while len(choices) < 4:

        candidate = generate_quadratic()

        if candidate not in choices:
            choices.append(candidate)

    random.shuffle(choices)

    st.session_state.problem = correct

    st.session_state.choices = choices

    st.session_state.correct_index = choices.index(correct)

    st.session_state.start_problem = time.time()

    st.session_state.answered = False

    st.session_state.question_id += 1


# =====================================================
# 初期化
# =====================================================
if "initialized" not in st.session_state:

    st.session_state.initialized = True

    st.session_state.correct_count = 0

    st.session_state.total_count = 0

    st.session_state.study_start = time.time()

    st.session_state.problem = None

    st.session_state.choices = []

    st.session_state.correct_index = -1

    st.session_state.answered = False

    st.session_state.question_id = 0

if st.session_state.problem is None:
    new_problem()


# =====================================================
# 画面設定
# =====================================================
st.set_page_config(
    page_title="二次関数グラフ選択問題",
    layout="centered"
)

# =====================================================
# タイトル
# =====================================================
st.title("📈 二次関数グラフ選択問題")

st.info("""
【使い方】

① 表示された二次関数を確認します。

② 4つの放物線の中から正しいグラフを選びます。

③ 「答え合わせ」を押して正誤を確認します。

④ 「次の問題」を押して次の問題へ進みます。

⑤ 最後に「学習結果を表示」を押して振り返りをします。

頂点・軸・開く向き・広がり方に注目しましょう！
""")


# =====================================================
# 線の太さ
# =====================================================
line_width = st.slider(
    "線の太さ",
    1,
    5,
    2
)

# =====================================================
# 問題表示
# =====================================================
a, p, q = st.session_state.problem

st.subheader(
    f"問題： {format_vertex_form(a,p,q)}"
)

# =====================================================
# グラフ描画
# =====================================================
fig, ax = plt.subplots(figsize=(6, 6))

x = np.linspace(-6, 6, 600)

colors = [
    "red",
    "blue",
    "green",
    "orange"
]

labels = [
    "選択肢1",
    "選択肢2",
    "選択肢3",
    "選択肢4"
]

for i, (aa, pp, qq) in enumerate(
    st.session_state.choices
):

    y = aa * (x - pp) ** 2 + qq

    ax.plot(
        x,
        y,
        color=colors[i],
        linewidth=line_width,
        label=labels[i]
    )

    ax.scatter(
        [pp],
        [qq],
        color=colors[i],
        s=50
    )

    ax.axvline(
        pp,
        color=colors[i],
        linestyle="--",
        alpha=0.4
    )

ax.axhline(0, color="black")
ax.axvline(0, color="black")

ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)

ax.grid(True)

ax.legend()

st.pyplot(fig)

# =====================================================
# 選択
# =====================================================
answer = st.radio(
    "選択してください",
    options=[0, 1, 2, 3],
    format_func=lambda x: f"選択肢{x+1}",
    index=None,
    key=f"answer_radio_{st.session_state.question_id}"
)

# =====================================================
# 答え合わせ
# =====================================================
if st.button("答え合わせ"):

    if st.session_state.answered:

        st.warning(
            "この問題は採点済みです。"
        )

    elif answer is None:

        st.warning(
            "選択肢を選んでください。"
        )

    else:

        elapsed = int(
            time.time()
            - st.session_state.start_problem
        )

        is_correct = (
            answer
            == st.session_state.correct_index
        )

        st.session_state.total_count += 1

        if is_correct:

            st.session_state.correct_count += 1

            st.success(
                "正解です！\n\n次の問題へ進みましょう。"
            )

        else:

            st.error(
                f"不正解です。\n\n正解は選択肢 {st.session_state.correct_index+1} です。"
            )

        st.session_state.answered = True

        send_to_sheet(
            format_vertex_form(a, p, q),
            answer,
            st.session_state.correct_index,
            is_correct,
            elapsed
        )

# =====================================================
# 次の問題
# =====================================================
if st.button("次の問題"):

    new_problem()

    st.rerun()

# =====================================================
# 学習結果
# =====================================================
st.divider()

if st.button("学習結果を表示"):

    if st.session_state.total_count == 0:
        rate = 0
    else:
        rate = (
            st.session_state.correct_count
            / st.session_state.total_count
            * 100
        )

    elapsed = int(
        time.time()
        - st.session_state.study_start
    )

    minutes = elapsed // 60
    seconds = elapsed % 60

    st.markdown("## 学習結果")

    st.write(
        f"正解数：{st.session_state.correct_count}"
    )

    st.write(
        f"問題数：{st.session_state.total_count}"
    )

    st.write(
        f"正答率：{rate:.1f}%"
    )

    st.write(
        f"学習時間：{minutes}分 {seconds}秒"
    )

    if rate >= 90:
        st.success("素晴らしい集中力でした！")

    elif rate >= 70:
        st.success("よく頑張りました！")

    elif rate >= 50:
        st.info("あと少しで完璧です！")

    else:
        st.warning("続ければ必ず伸びます！")
