from flask import Flask, request, abort
import os
import datetime

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, MessageAction,
    TemplateSendMessage, TextSendMessage,
    ButtonsTemplate, QuickReply, QuickReplyButton, URIAction,
    PostbackAction, PostbackEvent)

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    uid = event.source.user_id
    text = event.message.text

    if text == "メニューを表示する":
        buttons_template = ButtonsTemplate(title="メニュー", text="以下タップしてください",
            actions=[
                PostbackAction(label="練習日程", data="練習日程"),
                PostbackAction(label="大会情報", data="大会情報"),
                URIAction(label='ホームページへ', uri='https://mog-vb.com/')
            ]
        )
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
        """
        QuickReplyはURIAction使えない？
        line_bot_api.reply_message(
            event.reply_token,
             TextSendMessage(
                text='メニュー',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="練習日程", data="練習日程")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="大会情報", data="大会情報")
                        ),
                        QuickReplyButton(
                            action=URIAction(label='ホームページへ', uri='https://mog-vb.com/')
                        ),
                    ]
                )
            )
        )
        """
    else:
        dt_now = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))
        )
        aisatsu = ""
        if 5 < dt_now.hour & dt_now.hour < 12:
            aisatsu="おはようございます！"
        elif 12 <= dt_now.hour & dt_now.hour < 18:
            aisatsu="こんにちは！"
        else:
            aisatsu="こんばんは！"
        
        profile = line_bot_api.get_profile(event.source.user_id)
        messages = TemplateSendMessage(
            alt_text="Buttons template",
            template=ButtonsTemplate(
                thumbnail_image_url=profile.picture_url,
                title=f"{profile.display_name} {aisatsu}",
                text=f"直近の情報はメニューから表示してください。",
                actions=[MessageAction(label="メニューを表示する", text="メニューを表示する")]
            )
        )
        line_bot_api.reply_message(
            event.reply_token,
            messages=messages
        )

@handler.add(PostbackEvent)
def on_postback(event):
    reply_token = event.reply_token
    user_id = event.source.user_id
    postback_msg = event.postback.data

    if postback_msg == "練習日程":
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text='https://mog-vb.com/schedule.html')
        )
        messages = TemplateSendMessage(
            alt_text="Buttons template",
            template=ButtonsTemplate(
                title=f"練習参加希望の方はこちらから",
                text=f"直近の情報はメニューから表示してください。",
                actions=[URIAction(label='問合せ', uri='https://www.secure-cloud.jp/sf/1599540224gaXtNNUs')]
            )
        )
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text='上記URLから確認ください！')
        )
    elif postback_msg == '大会情報':
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text="現在開催予定はありません")
        )

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)