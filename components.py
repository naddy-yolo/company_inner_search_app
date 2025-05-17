"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import streamlit as st
import utils
import constants as ct


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.title(ct.APP_NAME)


def display_select_mode():
    """
    回答モードのラジオボタンを表示
    """
    # 回答モードを選択する用のラジオボタンを表示
    col1, col2 = st.columns([100, 1])
    with col1:
        # 「label_visibility="collapsed"」とすることで、ラジオボタンを非表示にする
        st.session_state.mode = st.radio(
            label="",
            options=[ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
            label_visibility="collapsed"
        )


def display_sidebar_info():
    with st.sidebar:
        st.markdown("### 利用目的")
        st.radio(
            label="",
            options=[ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
            key="sidebar_mode"
        )

        st.markdown("---")
        st.markdown("**『社内文書検索』を選択した場合**")
        st.markdown(
            '<div style="background-color:#e3f2fd; padding:8px; border-radius:6px; margin-bottom:4px;">'
            '入力内容と関連性が高い社内文書のありかを検索できます。</div>',
            unsafe_allow_html=True
        )
        st.markdown("###### 【入力例】")
        st.markdown("社の育成方針に関するMTGの議事録")

        st.markdown("---")
        st.markdown("**『社内問い合わせ』を選択した場合**")
        st.markdown(
            '<div style="background-color:#e3f2fd; padding:8px; border-radius:6px; margin-bottom:4px;">'
            '質問・要望に対して、社内文書の情報をもとに回答を得られます。</div>',
            unsafe_allow_html=True
        )
        st.markdown("###### 【入力例】")
        st.markdown("人事部に所属している従業員情報を一覧化して")


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    # 修正後TOP画面の説明文（緑色のボックス）
    st.markdown(
        """
        <div style="background-color:#e8f5e9; padding:16px; border-radius:8px; margin-bottom:10px;">
        こんにちは、私は社内文書の情報をもとに回答する生成AIチャットボットです。サイドバーで利用目的を選択し、画面下部のチャット欄からメッセージを送信してください。
        </div>
        """,
        unsafe_allow_html=True
    )
    # 注意文（黄色のボックス）
    st.markdown(
        """
        <div style="background-color:#fffde7; padding:12px; border-radius:8px;">
        <span style="color:#fbc02d;">⚠️ 具体的に入力したほうが期待通りの回答を得やすいです。</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    # 会話ログのループ処理
    for message in st.session_state.messages:
        # 「message」辞書の中の「role」キーには「user」か「assistant」が入っている
        with st.chat_message(message["role"]):

            # ユーザー入力値の場合、そのままテキストを表示するだけ
            if message["role"] == "user":
                st.markdown(message["content"])
            
            # LLMからの回答の場合
            else:
                # 「社内文書検索」の場合、テキストの種類に応じて表示形式を分岐処理
                if message["content"]["mode"] == ct.ANSWER_MODE_1:
                    
                    # ファイルのありかの情報が取得できた場合（通常時）の表示処理
                    if not "no_file_path_flg" in message["content"]:
                        # ==========================================
                        # ユーザー入力値と最も関連性が高いメインドキュメントのありかを表示
                        # ==========================================
                        # 補足文の表示
                        st.markdown(message["content"]["main_message"])

                        # 参照元のありかに応じて、適したアイコンを取得
                        icon = utils.get_source_icon(message['content']['main_file_path'])
                        # ページ番号が存在する場合のみ表示
                        if "main_page_number" in message["content"]:
                            st.success(f"{message['content']['main_file_path']}（ページNo.{message['content']['main_page_number']}）", icon=icon)
                        else:
                            st.success(f"{message['content']['main_file_path']}", icon=icon)
                        
                        # ==========================================
                        # ユーザー入力値と関連性が高いサブドキュメントのありかを表示
                        # ==========================================
                        if "sub_message" in message["content"]:
                            # 補足メッセージの表示
                            st.markdown(message["content"]["sub_message"])

                            # サブドキュメントのありかを一覧表示
                            for sub_choice in message["content"]["sub_choices"]:
                                icon = utils.get_source_icon(sub_choice['source'])
                                if "page_number" in sub_choice:
                                    st.info(f"{sub_choice['source']}（ページNo.{sub_choice['page_number']}）", icon=icon)
                                else:
                                    st.info(f"{sub_choice['source']}", icon=icon)
                    # ファイルのありかの情報が取得できなかった場合、LLMからの回答のみ表示
                    else:
                        st.markdown(message["content"]["answer"])
                
                # 「社内問い合わせ」の場合の表示処理
                else:
                    # LLMからの回答を表示
                    st.markdown(message["content"]["answer"])

                    # 参照元のありかを一覧表示
                    if "file_info_list" in message["content"]:
                        # 区切り線の表示
                        st.divider()
                        # 「情報源」の文字を太字で表示
                        st.markdown(f"##### {message['content']['message']}")
                        # ドキュメントのありかを一覧表示
                        for file_info in message["content"]["file_info_list"]:
                            # 参照元のありかに応じて、適したアイコンを取得
                            icon = utils.get_source_icon(file_info)
                            st.info(file_info, icon=icon)


def display_search_llm_response(llm_response):
    st.markdown("入力内容に関する情報は、以下のファイルに含まれている可能性があります。")
    docs = llm_response.get("docs", [])
    for doc in docs:
        display_doc_link(doc["path"], doc["page"], highlight=True)
    # その他候補
    st.markdown("その他、ファイルありかの候補を提示します。")


def display_contact_llm_response(llm_response):
    """
    「社内問い合わせ」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからの回答を表示
    st.markdown(llm_response["answer"])

    # ユーザーの質問・要望に適切な回答を行うための情報が、社内文書のデータベースに存在しなかった場合
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        # 区切り線を表示
        st.divider()

        # 補足メッセージを表示
        message = "情報源"
        st.markdown(f"##### {message}")

        # 参照元のファイルパスの一覧を格納するためのリストを用意
        file_path_list = []
        file_info_list = []

        # LLMが回答生成の参照元として使ったドキュメントの一覧が「context」内のリストの中に入っているため、ループ処理
        for document in llm_response["context"]:
            file_path = document.metadata["source"]
            if file_path in file_path_list:
                continue

            # ページ番号が取得できた場合のみ、ページ番号を表示
            if "page" in document.metadata:
                page_number = document.metadata["page"]
                file_info = f"{file_path}（ページNo.{page_number}）"
            else:
                file_info = f"{file_path}"

            # 参照元のありかに応じて、適したアイコンを取得
            icon = utils.get_source_icon(file_path)
            # ファイル情報を表示
            st.info(file_info, icon=icon)

            # 重複チェック用に、ファイルパスをリストに順次追加
            file_path_list.append(file_path)
            # ファイル情報をリストに順次追加
            file_info_list.append(file_info)

    # 表示用の会話ログに格納するためのデータを用意
    # - 「mode」: モード（「社内文書検索」or「社内問い合わせ」）
    # - 「answer」: LLMからの回答
    # - 「message」: 補足メッセージ
    # - 「file_path_list」: ファイルパスの一覧リスト
    content = {}
    content["mode"] = ct.ANSWER_MODE_2
    content["answer"] = llm_response["answer"]
    # 参照元のドキュメントが取得できた場合のみ
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        content["message"] = message
        content["file_info_list"] = file_info_list

    return content


def display_doc_link(doc_path, page_no, highlight=False):
    color = "#e8f5e9" if highlight else "#e3f2fd"
    st.markdown(
        f'''
        <div style="background-color:{color}; padding:12px; border-radius:8px; margin-bottom:8px;">
            <span style="font-size:16px;">{ct.DOC_SOURCE_ICON}{doc_path} <u>（ページNo.{page_no}）</u></span>
        </div>
        ''',
        unsafe_allow_html=True
    )