import random
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "koko_wo_tekitou_na_nagaimoji_ni_kaeru_2026"

# 全10問のクイズデータ
QUIZZES = [
    {
        "id": 1,
        "images": ["q1_oikoshi.webp"],
        "question": "この標識（追い越しのための右側部分はみ出し通行禁止）の意味として正しいものは？",
        "choices": [
            "右側部分にはみ出さなければ追い越しをしてもよい",
            "いかなる場合も追い越し自体が禁止されている",
            "原付や軽車両の追い越しのみ許可されている",
            "追い抜きは禁止だが追い越しは許可されている",
        ],
        "answer": "右側部分にはみ出さなければ追い越しをしてもよい",
        "explanation": "【ポイント】『追い越し禁止』ではなく『はみ出し禁止』です。道路の左側部分だけで完結するなら追い越しOK！（※下に『追い越し禁止』の補助標識がある場合を除く）",
    },
    {
        "id": 2,
        "images": ["q2_nirin_igai.webp"],
        "question": "この標識（二輪の自動車以外の自動車通行止め）が示している通行できる車両はどれ？",
        "choices": [
            "大型自動二輪車・普通自動二輪車・原付・自転車",
            "普通自動車・軽自動車のみ（二輪車は通行止め）",
            "原付と自転車のみ（自動二輪車は通行止め）",
            "すべての自動車（原付と軽車両のみ通行止め）",
        ],
        "answer": "大型自動二輪車・普通自動二輪車・原付・自転車",
        "explanation": "【ポイント】『二輪の自動車【以外】の自動車』が通行止めなので、バイク（自動二輪）と原付・自転車は通れます。車マークに斜線ですが、バイクは除外されています。",
    },
    {
        "id": 3,
        "images": ["q3_shinnyu_kinshi.jpg", "q3_sharyo_tsukodome.jpg"],
        "question": "左の『車両進入禁止』と右の『車両通行止め』。右の『車両通行止め』の標識がある道路で通行できるのはどれ？",
        "choices": [
            "歩行者のみ（自転車を押して歩く人も含む）",
            "自転車と原付（エンジンを切らなくてもよい）",
            "軽車両（自転車やリヤカー）のみ",
            "指定された方向からの進入のみ可能",
        ],
        "answer": "歩行者のみ（自転車を押して歩く人も含む）",
        "explanation": "【ポイント】『車両』には自動車・原付だけでなく自転車（軽車両）も含まれます。したがって乗ったまま通れる車両はゼロ。自転車から降りて押して歩けば『歩行者』扱いになり通れます。",
    },
    {
        "id": 4,
        "images": ["q4_shitei_hoko.png"],
        "question": "この『指定方向外進行禁止』の標識がある交差点で、原動機付自転車が二段階右折をしようとしている。正しいのは？",
        "choices": [
            "二段階右折も禁止されているため右折できない",
            "二段階右折であれば右折することができる",
            "原付と軽車両はこの標識の対象外なので自由に右折できる",
            "交差点の直前まで行ってからなら右折できる",
        ],
        "answer": "二段階右折も禁止されているため右折できない",
        "explanation": "【ポイント】指定方向外進行禁止の標識がある場合、原付であっても二段階右折はできません（直進矢印があっても二段階右折の第一段階の直進すらアウトです）。",
    },
    {
        "id": 5,
        "images": ["q5_chusha_yochi.jpg"],
        "question": "青地に赤い斜めの線の標識（駐車余地）が示す意味は？",
        "choices": [
            "駐車したとき、車の右側にこの標識が示す距離以上の余地がなければ駐車してはいけない",
            "この標識から先、指定された距離の間は無料で駐車できる",
            "道路の左端から指定された距離だけ離して駐車しなければならない",
            "指定された時間内であれば荷物の積み下ろしのための駐車が許可される",
        ],
        "answer": "駐車したとき、車の右側にこの標識が示す距離以上の余地がなければ駐車してはいけない",
        "explanation": "【ポイント】ただの駐車場ではありません。駐車した車の『右側』に、標識に書かれた数字（例：6m）以上のスペースが空かない場所での駐車を禁止する標識です。",
    },
    {
        "id": 6,
        "images": ["q6_yusen_doro.png"],
        "question": "この『優先道路』の標識がある道路を通行中、見通しの悪い交差点に差し掛かった。正しい通行方法は？",
        "choices": [
            "徐行する必要はない（そのままの速度で通行できる）",
            "見通しが悪いため必ず徐行しなければならない",
            "一時停止は不要だが、必ず徐行しなければならない",
            "交差点の30m手前から徐行しなければならない",
        ],
        "answer": "徐行する必要はない（そのままの速度で通行できる）",
        "explanation": "【ポイント】原則として見通しの悪い交差点は徐行義務がありますが、『優先道路を通行している場合』は例外として徐行義務が免除されます。",
    },
    {
        "id": 7,
        "images": ["q7_joko.jpg"],
        "question": "赤枠に白い逆三角形の『徐行』標識がある場所での正しい運転はどれ？",
        "choices": [
            "車がすぐに停止できるような速度で進む",
            "停止線の直前で必ず一時停止する",
            "時速20km以下であればどんな状況でもよい",
            "前方に歩行者がいる場合のみ減速する",
        ],
        "answer": "車がすぐに停止できるような速度で進む",
        "explanation": " 【解説】法令上の徐行の定義は『車がすぐに停止できるような速度（目安として時速10km以下）』です。時速20kmでは速すぎます。",
    },
    {
        "id": 8,
        "images": ["q8_chuteisha_kinshi.jpg"],
        "question": "青地に赤枠・赤い『×』印（駐停車禁止）の場所で、例外的に『停車』してもよいケースはどれ？",
        "choices": [
            "赤信号や危険防止のための一時停止",
            "人の乗り降りのための1分以内の停車",
            "5分以内の荷物の積み下ろし",
            "運転手がすぐ運転できる状態で車内にいる場合",
        ],
        "answer": "赤信号や危険防止のための一時停止",
        "explanation": "【ポイント】駐停車禁止の場所では、人の乗り降りも5分以内の荷物積み下ろしも一切アウト。信号待ちや危険防止などのやむを得ない停止のみ例外です。",
    },
    {
        "id": 9,
        "images": ["q9_hokosha_senyo.jpg"],
        "question": "青地に白い親子（大人と子供）が描かれた『歩行者専用』標識がある道路を通行できる車両は？",
        "choices": [
            "警察の許可を受けた車や、車椅子・シニアカー（歩行者扱い）",
            "自転車（徐行すれば通行可能）",
            "郵便配達や宅配便の原動機付自転車",
            "沿道に車庫がある普通自動車（許可は不要）",
        ],
        "answer": "警察の許可を受けた車や、車椅子・シニアカー（歩行者扱い）",
        "explanation": "【ポイント】歩行者専用道路は自転車も原則通行禁止です（押し歩きならOK）。車椅子や電動カート（シニアカー）は法律上『歩行者』なので通れます。",
    },
    {
        "id": 10,
        "images": ["q10_kanjo_kosaten.jpg"],
        "question": "青地に白い3本の矢印が円を描いている『環状交差点あり（ラウンドアバウト）』での正しい通行方法は？",
        "choices": [
            "時計回り（右回り）に通行し、あらかじめできる限り道路の左端に寄って徐行で進入する",
            "反時計回り（左回り）に通行し、進入時は必ず一時停止しなければならない",
            "時計回り（右回り）に通行し、すでに環状交差点内を通行している車より進入車が優先される",
            "時計回り（右回り）に通行し、交差点を出るときはウインカーを出さなくてよい",
        ],
        "answer": "時計回り（右回り）に通行し、あらかじめできる限り道路の左端に寄って徐行で進入する",
        "explanation": "【ポイント】一時停止標識がなければ一時停止は不要（徐行で進入）。また、環状交差点『内』を走っている車が優先で、出るときは左ウインカーが必要です。",
    },
]


@app.route("/")
def index():
  # まだスタートしていない場合はタイトル画面を表示
  if not session.get("started"):
    return render_template("index.html", started=False)

  current_index = session["current_index"]
  quiz_order = session["quiz_order"]

  if current_index >= len(quiz_order):
    return render_template(
        "index.html",
        started=True,
        finished=True,
        score=session["score"],
        total=len(quiz_order),
    )

  current_quiz_id = quiz_order[current_index]
  quiz = next((q for q in QUIZZES if q["id"] == current_quiz_id), None)

  shuffled_choices = list(quiz["choices"])
  random.shuffle(shuffled_choices)

  return render_template(
      "index.html",
      started=True,
      finished=False,
      quiz=quiz,
      choices=shuffled_choices,
      current_num=current_index + 1,
      total=len(quiz_order),
      result=None,
  )


@app.route("/start")
def start():
  # スタートボタンが押されたときにクイズを初期化して開始
  quiz_ids = [q["id"] for q in QUIZZES]
  random.shuffle(quiz_ids)
  session["started"] = True
  session["quiz_order"] = quiz_ids
  session["current_index"] = 0
  session["score"] = 0
  return redirect(url_for("index"))


@app.route("/answer", methods=["POST"])
def answer():
  quiz_id = int(request.form.get("quiz_id"))
  user_choice = request.form.get("choice")

  quiz = next((q for q in QUIZZES if q["id"] == quiz_id), None)
  is_correct = user_choice == quiz["answer"]

  if is_correct:
    session["score"] = session.get("score", 0) + 1

  session["current_index"] = session.get("current_index", 0) + 1

  result = {
      "is_correct": is_correct,
      "answer": quiz["answer"],
      "explanation": quiz["explanation"],
      "user_choice": user_choice,
  }

  return render_template(
      "index.html",
      started=True,
      finished=False,
      quiz=quiz,
      current_num=session["current_index"],
      total=len(session["quiz_order"]),
      result=result,
  )


@app.route("/reset")
def reset():
  session.clear()
  return redirect(url_for("index"))


if __name__ == "__main__":
  app.run(debug=True)
