"""
このファイルは、最初の画面読み込み時にのみ実行される初期化処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from uuid import uuid4
import sys
import unicodedata
from dotenv import load_dotenv
import streamlit as st
from docx import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import constants as ct

############################################################
# 設定関連
############################################################
print("📄 .env 読み込み開始")
load_dotenv()
print(f"✅ OPENAI_API_KEY = {os.getenv('OPENAI_API_KEY')}")

############################################################
# 関数定義
############################################################

def initialize():
    print("🔵 initialize() 開始")
    initialize_session_state()
    print("✅ セッションステート初期化完了")
    initialize_session_id()
    print("✅ セッションID生成完了")
    initialize_logger()
    print("✅ ロガー初期化完了")
    initialize_retriever()

def initialize_logger():
    os.makedirs(ct.LOG_DIR_PATH, exist_ok=True)
    logger = logging.getLogger(ct.LOGGER_NAME)
    if logger.hasHandlers():
        return
    log_handler = TimedRotatingFileHandler(
        os.path.join(ct.LOG_DIR_PATH, ct.LOG_FILE),
        when="D",
        encoding="utf8"
    )
    formatter = logging.Formatter(
        f"[%(levelname)s] %(asctime)s line %(lineno)s, in %(funcName)s, session_id={st.session_state.session_id}: %(message)s"
    )
    log_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

def initialize_session_id():
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid4().hex
        print(f"✅ 新規セッションID作成: {st.session_state.session_id}")

def initialize_retriever():
    logger = logging.getLogger(ct.LOGGER_NAME)
    if "retriever" in st.session_state:
        return

    print("🔵 Retriever初期化 開始")
    print("📂 データ読み込み開始")
    docs_all = load_data_sources()

    for doc in docs_all:
        doc.page_content = adjust_string(doc.page_content)
        for key in doc.metadata:
            doc.metadata[key] = adjust_string(doc.metadata[key])

    embeddings = OpenAIEmbeddings()
    text_splitter = CharacterTextSplitter(
        chunk_size=ct.CHUNK_SIZE,
        chunk_overlap=ct.CHUNK_OVERLAP,
        separator="\n"
    )
    splitted_docs = text_splitter.split_documents(docs_all)
    db = Chroma.from_documents(splitted_docs, embedding=embeddings)
    st.session_state.retriever = db.as_retriever(search_kwargs={"k": ct.NUM_RETRIEVAL_DOCS})

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.chat_history = []
        print("✅ セッションステート初期化完了（messages, chat_history）なし → 作成")
    else:
        print("✅ セッションステート初期化完了（messages, chat_history）あり")

def load_data_sources():
    logger = logging.getLogger(ct.LOGGER_NAME)
    print("🔍 データソース読み込み開始")
    docs_all = []
    recursive_file_check(ct.RAG_TOP_FOLDER_PATH, docs_all)

    web_docs_all = []
    for web_url in ct.WEB_URL_LOAD_TARGETS:
        print(f"🌐 Webページ読込: {web_url}")
        try:
            loader = WebBaseLoader(web_url)
            web_docs = loader.load()
            web_docs_all.extend(web_docs)
        except Exception as e:
            print(f"❌ Web読み込み失敗: {web_url}（原因: {e}）")
            logger.warning(f"Web読み込み失敗: {web_url}（原因: {e}）")

    docs_all.extend(web_docs_all)
    return docs_all

def recursive_file_check(path, docs_all):
    if os.path.isdir(path):
        files = os.listdir(path)
        for file in files:
            full_path = os.path.join(path, file)
            recursive_file_check(full_path, docs_all)
    else:
        file_load(path, docs_all)

def file_load(path, docs_all):
    logger = logging.getLogger(ct.LOGGER_NAME)
    file_extension = os.path.splitext(path)[1]
    file_name = os.path.basename(path)
    print(f"📄 読み込み対象ファイル: {file_name}")
    if file_extension in ct.SUPPORTED_EXTENSIONS:
        try:
            print(f"📥 データ読込処理開始: {file_name}")
            loader = ct.SUPPORTED_EXTENSIONS[file_extension](path)
            docs = loader.load()
            docs_all.extend(docs)
            print(f"✅ データ読込完了: {file_name}（件数: {len(docs)}）")
        except Exception as e:
            print(f"❌ 読み込み失敗: {file_name}（原因: {e}）")
            logger.warning(f"データ読み込み失敗: {file_name}（原因: {e}）")

def adjust_string(s):
    if type(s) is not str:
        return s
    if sys.platform.startswith("win"):
        s = unicodedata.normalize('NFC', s)
        s = s.encode("cp932", "ignore").decode("cp932")
        return s
    return s
