import json
import mock
import pytest

from cloudwatch import get_slack_channel_from_alert_desc
from cloudwatch import notify_cloudwatch_alert_event



cloudwatch_event_sns = {
  "Records": [
    {
      "EventSource": "aws:sns",
      "EventVersion": "1.0",
      "EventSubscriptionArn": "arn:aws:sns:eu-west-1:000000000000:cloudwatch-alarms:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "Sns": {
        "Type": "Notification",
        "MessageId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "TopicArn": "arn:aws:sns:eu-west-1:000000000000:cloudwatch-alarms",
        "Subject": "ALARM: \"Example alarm name\" in EU - Ireland",
        "Message": "{\"AlarmName\":\"Example alarm name\",\"AlarmDescription\":\"Example alarm description. channel:ABCDEF\",\"AWSAccountId\":\"000000000000\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold Crossed: 1 datapoint (10.0) was greater than or equal to the threshold (1.0).\",\"StateChangeTime\":\"2017-01-12T16:30:42.236+0000\",\"Region\":\"EU - Ireland\",\"OldStateValue\":\"OK\",\"Trigger\":{\"MetricName\":\"DeliveryErrors\",\"Namespace\":\"ExampleNamespace\",\"Statistic\":\"SUM\",\"Unit\":null,\"Dimensions\":[],\"Period\":300,\"EvaluationPeriods\":1,\"ComparisonOperator\":\"GreaterThanOrEqualToThreshold\",\"Threshold\":1.0}}",
        "Timestamp": "2017-01-12T16:30:42.318Z",
        "SignatureVersion": "1",
        "Signature": "Cg==",
        "SigningCertUrl": "https://sns.eu-west-1.amazonaws.com/SimpleNotificationService-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.pem",
        "UnsubscribeUrl": "https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-west-1:000000000000:cloudwatch-alarms:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "MessageAttributes": {}
      }
    }
  ]
}


@mock.patch('cloudwatch.slack_cloudwatch_alert_message')
def test_notify_cloudwatch_alert_event(mock_slack_call):
    notify_cloudwatch_alert_event(cloudwatch_event_sns)
    expected_channel = "ABCDEF"
    expected_data = json.loads(cloudwatch_event_sns['Records'][0]['Sns']['Message'])
    expected_alarm_name = "Example alarm name"
    mock_slack_call.assert_called_with(alarm_name=expected_alarm_name,
                                       data=expected_data,
                                       channel=expected_channel)




def test_extract_channel():
    l = [
        "lalalalal channel:abc",
        "XXXd234234 channel:abc 232sfsfdsdf"
        "channel:abc",
        "channel:abc "
    ]

    for i in l:
        assert("abc" == get_slack_channel_from_alert_desc(i))

    l = [
        "",
        "something something 23dasd ."
        "channel: ",
    ]

    for i in l:
        with pytest.raises(Exception) as e:
            get_slack_channel_from_alert_desc(i)
            assert("No slack channel can be extracted " in e.message)
