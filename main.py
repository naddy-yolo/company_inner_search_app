"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
from dotenv import load_dotenv
import logging
import streamlit as st
import utils
from initialize import initialize
import components as cn
import constants as ct


############################################################
# 設定関連
############################################################
st.set_page_config(page_title=ct.APP_NAME)
logger = logging.getLogger(ct.LOGGER_NAME)


############################################################
# 初期化処理
############################################################
try:
    initialize()
except Exception as e:
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    st.stop()

if not "initialized" in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)

if "messages" not in st.session_state:
    st.session_state.messages = []


############################################################
# 初期表示
############################################################
cn.display_sidebar_info()
cn.display_select_mode()  # ← この行を追加
cn.display_app_title()
cn.display_initial_ai_message()


############################################################
# 会話ログの表示
############################################################
try:
    cn.display_conversation_log()
except Exception as e:
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    st.stop()


############################################################
# チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)


############################################################
# チャット送信時の処理
############################################################
if chat_message:
    st.write("チャットメッセージ受信")
    st.write(chat_message)
    logger.info({"message": chat_message, "application_mode": st.session_state.sidebar_mode})
    with st.chat_message("user"):
        st.markdown(chat_message)

    res_box = st.empty()
    with st.spinner(ct.SPINNER_TEXT):
        try:
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
            st.write(e)  # 追加
            st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            st.stop()

    with st.chat_message("assistant"):
        try:
            cn.display_search_llm_response(llm_response)
        except Exception as e:
            logger.error(f"{ct.DISPLAY_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
            st.write(e)  # ここを追加
            st.error(utils.build_error_message(ct.DISPLAY_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            st.stop()

    st.session_state.messages.append({"role": "user", "content": chat_message})
    st.session_state.messages.append({"role": "assistant", "content": llm_response["answer"]})
