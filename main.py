import openai
import os
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build


OPEN_AI_KEY = os.environ["OPEN_AI_KEY"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
CUSTOM_SEARCH_ENGINE_ID = os.environ["CUSTOM_SEARCH_ENGINE_ID"]

openai.api_key = OPEN_AI_KEY

query = "チェンソーマンのアニメ化はいつされた？"

template = """
次の入力文から検索すべきキーワードを3つ出し出力文に従って出力しなさい。

# 出力文
[キーワード], [キーワード], [キーワード]

# 入力文
{query}
"""
prompt = template.format(query=query)

# 検索キーワードをどうしたら良いかChatGPTに聞く
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "user", "content": prompt}])
answer = completion.choices[0].message.content
print("1つめの問いに対する答え:\n" + answer)

# ググる
keywords = answer.split(",")
service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
result = service.cse().list(
     q= " ".join(keywords),
     cx=CUSTOM_SEARCH_ENGINE_ID,
     lr='lang_ja', # 日本語で
     num=3, # とりあえず 3 ウェブサイト
     start=1 # 検索結果1ページ目
     ).execute()


answers = []
for item in result["items"]:
    url = item["link"]

    # ヒットしたURLをスクレイピングします
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.body # body要素の取得
    text = body.get_text() # body要素内のテキストを抜き出す

    template = """
    次のコンテキストを読み取って、入力文に関する情報を箇条書きで3つ書いてください。

    # 入力文
    {query}

    # 出力文
    - [情報]
    - [情報]
    - [情報]

    # コンテキスト
    {context}
    """
    prompt = template.format(context=text[:2000], query=query)

    # スクレイピングした情報を与えて関係ある情報を集める
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "user", "content": prompt}])
    answer = completion.choices[0].message.content
    print("2つめの問いに対する答え:\n" + answer)
    answers.append(answer)


template = """
入力文にたいし、コンテキストから推測される回答を答えなさい。

# コンテキスト
{context}

# 入力文
{query}
"""
prompt = template.format(context="\n".join(answers), query=query)

# 集めた情報をコンテキストとして渡して最終の答えを出させる。
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "user", "content": prompt}])
answer = completion.choices[0].message.content
print("最終の答え:\n" + answer)
