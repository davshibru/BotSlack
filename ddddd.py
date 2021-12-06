import slack
import os
from pathlib import Path
from dotenv import load_dotenv

import logging

import json
import datetime

import time

# second tut
from flask import Flask
from slackeventsapi import SlackEventAdapter

# third tut
from flask import request, Response

# asynk
import schedule
from threading import Thread

logger = logging.getLogger(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# time settings
tomorrow = datetime.date.today()  # + datetime.timedelta(days=1)
scheduled_time = datetime.time(hour=13, minute=58)
schedule_timestamp = (datetime.datetime.combine(tomorrow, scheduled_time) + datetime.timedelta(seconds=0)).timestamp()

# set flask app
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

# словари -----------------------------------------------------------------------------------------

message_counts = {}
welcome_messages = {}
REPORTS = {}
USERS = {}
DEPARTMENT = {}

# -------------------------------------------------------------------------------------------------

# boolean переменные ------------------------------------------------------------------------------

isSetUpingUserNow = False


# -------------------------------------------------------------------------------------------------

class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to this awesome channel! \n\n'
                '*Get started by completing the tasks!*'
            )
        }
    }

    DIVIDER = {'type': 'divider'}

    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False

    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome robot!',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'

        text = f'{checkmark} *React to this message!*'

        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}


def send_welcome_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    if user in welcome_messages[channel]:
        return
    welcome = WelcomeMessage(channel, user)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    welcome_messages[channel][user] = welcome


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if user_id != None and BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1
        # client.chat_postMessage(channel=channel_id, text=text)

        if text.lower() == 'start':
            send_welcome_message(f'@{user_id}', user_id)

        if text.lower() == 'set':

            for i in USERS:
                if USERS[i]['department'] not in DEPARTMENT:
                    DEPARTMENT[USERS[i]['department']] = {'count': 0, 'users_id': []}

                if i not in DEPARTMENT[USERS[i]['department']]['users_id']:
                    DEPARTMENT[USERS[i]['department']]['count'] += 1
                    DEPARTMENT[USERS[i]['department']]['users_id'].append(i)

            textForDep = 'Users by department:\n'

            for i in DEPARTMENT:
                textForDep = f'{textForDep}{i}:\n'

                for x in DEPARTMENT[i]['users_id']:
                    textForDep = f'{textForDep}• {USERS[x]["name"]}\n'

            # print(textForDep)
            message = {
                "channel": channel_id,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Change department"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Do you want to set department to indefined users"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Or you want to change user department"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Select the appropriate button"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Users by department"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "• Schedule meetings \n • Manage and update attendees \n • Get notified about changes of your meetings"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": "This is a plain text section block."
                        }
                    }
                ]
            }
            response = client.chat_postMessage(**message).data
            print(response)
            # attachments = [{
            #     "text": 'Choose a option',
            #     "callback_id": "option_for_department",
            #     "color": "#3AA3E3",
            #     "attachment_type": "default",
            #     "actions": [
            #         {
            #             "name": "change_exist_users",
            #             "text": "Change users department",
            #             "type": "button",
            #             "value": "change_exist_users"
            #         },
            #         {
            #             "name": "set_indefined_user",
            #             "text": "Set department for indefined users",
            #             "type": "button",
            #             "value": "set_indefined_user"
            #         }
            #     ]
            # }]

        if text.lower() == 'add_department':
            print('add department')

        if text.lower() == 'report':
            print(schedule_timestamp)
            response = client.chat_scheduleMessage(
                channel=user_id,
                text="I am ReportBot ::robot_face::, and I\'m want your report",
                post_at=schedule_timestamp,
                attachments=[{
                    "text": "",
                    "callback_id": user_id + "report_order_form",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions": [{
                        "name": "report",
                        "text": "write report",
                        "type": "button",
                        "value": "report"
                    }]
                }]

            ).data
            print(response)


# функции который реагируют на что-то из слака ----------------------------------------------------

@slack_event_adapter.on('reaction_added')
def reaction(payload):
    event = payload.get('event', {})
    channel_id = event.get('item', {}).get('channel')
    user_id = event.get('user')

    if f'@{user_id}' not in welcome_messages:
        return

    welcome = welcome_messages[f'@{user_id}'][user_id]
    welcome.completed = True
    welcome.channel = channel_id
    message = welcome.get_message()
    updated_massage = client.chat_update(**message)
    welcome.timestamp = updated_massage['ts']


@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = message_counts.get(user_id, 0)
    client.chat_postMessage(channel=channel_id, text=f"Message: {message_count}")
    return Response(), 200


@app.route("/slack/message_action", methods=['POST'])
def message_action():
    message_action = json.loads(request.form["payload"])
    user_id = message_action["user"]["id"]
    print(message_action)
    if message_action["type"] == "interactive_message":
        # Add the message_ts to the user's order info
        if message_action["actions"][0]['name'] == 'report':
            open_dialog = client.dialog_open(
                trigger_id=message_action["trigger_id"],
                dialog={
                    "title": "Daily report",
                    "submit_label": "Submit",
                    "callback_id": user_id + "coffee_order_form",
                    "elements": [
                        {
                            "type": "text",
                            "label": "What did you do?",
                            "name": "didToday"
                        },
                        {
                            "type": "text",
                            "label": "What are you going to do?",
                            "name": "willDo"
                        },
                        {
                            "type": "text",
                            "label": "What problems do you have?",
                            "name": "problems"
                        },

                    ]
                }
            )

            print(open_dialog)

    elif message_action["type"] == "dialog_submission":
        time = message_action["action_ts"]

        today_var = datetime.date.today()
        REPORTS[today_var.strftime("%Y:%m:%d")]['users'][message_action["user"]['id']] = message_action['submission']

        # print(message_action)
        # print(REPORTS)
        client.chat_postMessage(
            channel=user_id,
            text='молодец что написал отчет gdsc тебя не забудет'
        )

    return Response(), 200


# -------------------------------------------------------------------------------------------------

# внутренние функции ------------------------------------------------------------------------------

def set_schedule_message_report_to_users():
    for i in USERS:
        response = client.chat_postMessage(
            channel=i,
            text="I am ReportBot ::robot_face::, and I\'m want your report",
            post_at=schedule_timestamp,
            attachments=[{
                "text": "",
                "callback_id": i + "report_order_form",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [{
                    "name": "report",
                    "text": "write report",
                    "type": "button",
                    "value": "report"
                }]
            }]

        ).data


def set_schedule_send_report_to_mentors():
    today_var = datetime.date.today()
    text_today_time = today_var.strftime("%Y:%m:%d")

    channel_id = 'C02PJSWQ8QK'
    text = 'Report:\nwith out department\n'
    print(REPORTS)
    print(USERS)
    for i in REPORTS[text_today_time]['users']:

        if i:
            # text = f'{text}{USERS[i]["name"]}\n'
            text = f'{text}{1}\n'
    send = client.chat_postMessage(channel=channel_id, text=text)


def add_to_list():
    result = client.users_list()
    if result['ok']:
        for item in result['members']:
            if item['id'] not in USERS:
                USERS[item['id']] = {}

            USERS[item['id']] = {'name': item['name'], 'department': 'indefined'}


def send_report():
    channel_id = 'C02PJSWQ8QK'
    text = 'Report:\nwith out department\n'
    for i in USERS:
        text = f'{text}{USERS[i]["name"]}\n'
    send = client.chat_postMessage(channel=channel_id, text=text)


def start_new_report_day():
    today_var = datetime.date.today()
    REPORTS[today_var.strftime("%Y:%m:%d")] = {'users': {}}


# -------------------------------------------------------------------------------------------------


# set time ----------------------------------------------------------------------------------------
schedule.every(2).minutes.do(set_schedule_message_report_to_users)
schedule.every(3).minutes.do(set_schedule_send_report_to_mentors)


# schedule.every().day().at("17:00").do(start_new_report_day)
# -------------------------------------------------------------------------------------------------


# scehedule set up

def schedule_run():
    while 1:
        schedule.run_pending()
        time.sleep(5)


th = Thread(target=schedule_run)
th.start()
if __name__ == "__main__":
    start_new_report_day()
    add_to_list()
    app.run(debug=True)


