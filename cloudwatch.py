import json
import logging
import os
import re

import boto3
import requests



def get_slack_bot_token_from_parameter_store():
    parameter_name = os.environ['SLACK_TOKEN_PARAMNAME']
    ssm = boto3.client('ssm')
    response = ssm.get_parameters(
        Names=[
            parameter_name,
        ],
        WithDecryption=True
    )
    credentials = response['Parameters'][0]['Value']
    return credentials


def send_to_slack_with_channel(data, channel):
    data['channel'] = channel
    data['token'] = get_slack_bot_token_from_parameter_store()
    url = "https://slack.com/api/chat.postMessage"
    r = requests.post(url=url, data=data)
    if r.status_code != 200:
        raise Exception(r.text)


def custom_message_to_slack(title, icon, attachments, channel):
    data = {
        "username": "my_bot",
        "icon_emoji": icon,
        "text": title,
        "attachments": json.dumps(attachments)
    }
    send_to_slack_with_channel(data, channel)


def slack_cloudwatch_alert_message(alarm_name, data, channel):

    color = "danger"
    state = data['NewStateValue']
    if state in ["OK"]:
        color = "good"
    
    fields = [{
        'title': attribute_name,
        'value': attribute_value,
        'short': False
    } for attribute_name, attribute_value in data.items()]

    attachments = [{
        "color": color,
        "fields": fields
    }]
    
    custom_message_to_slack(
        channel=channel,
        title=":warning: Warning - Cloudwatch alert %s" % alarm_name,
        icon=":warning:",
        attachments=attachments)


def notify_cloudwatch_alert_event(event):
    sns_message = event['Records'][0]['Sns']['Message']
    data = json.loads(sns_message)
    channel = get_slack_channel_from_alert_desc(data['AlarmDescription'])
    alert_name = data['AlarmName']
    slack_cloudwatch_alert_message(alarm_name=alert_name,
                                   data=data, channel=channel)

    
def get_slack_channel_from_alert_desc(description):
    regex = r'.*channel:([^\s]*).*'
    try:
        match = re.match(regex, description)
        channel = match.group(1)
        if channel == "":
            raise Exception("empty channel")
        return channel
    except Exception:
        raise Exception("No slack channel can be extracted from: %s" %
                        description)


def is_cloudwatchalert_event(event):
    """
    returns true if given event corresponds to a codepipeline approval event
    """
    try:
        contains_alarm_name = 'AlarmName' in event['Records'][0]['Sns'][
            'Message']
        contains_alarm_desc = 'AlarmDescription' in event['Records'][0]['Sns'][
            'Message']
        return contains_alarm_name and contains_alarm_desc
    except Exception:
        return False


def sns_alert_to_slack(event, context):
    if is_cloudwatchalert_event(event):
        notify_cloudwatch_alert_event(event)
    else:
        logging.log("received event is not cloudwatch alert event: %s" % json.dumps(event))
        raise Exception("not recognized cloudwatch alert event")

print(get_slack_bot_token_from_parameter_store())
print("something else")
