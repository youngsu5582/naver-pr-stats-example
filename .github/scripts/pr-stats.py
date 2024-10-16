import csv
import json
import requests
import os
from datetime import datetime, timedelta, timezone

# 한국 표준시 타임존 설정
KST = timezone(timedelta(hours=9))

# Slack Webhook URL 설정 (GitHub Secrets에서 불러옴)
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
pr_html_url = os.getenv("PULL_REQUEST_URL")
assignee = os.getenv("ASSIGNEE")

def construct_message(title,created_at,merged_at,file_count,line_count,conversation_count,response_time,approval_time):
    slack_message= {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<{pr_html_url}|{title}> 이 머지되었습니다. 😎 ( 수고했어요 {assignee} )"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": " PR 정보 "
                                }
                            ]
                        },
                        {
                            "type": "rich_text_list",
                            "style": "bullet",
                            "elements": [
                                {
                                    "type": "rich_text_section",
                                    "elements": [
                                        {
                                            "type": "text",
                                            "text": f"PR 기간 : {created_at} ~ {merged_at} "
                                        }
                                    ]
                                },
                                {
                                    "type": "rich_text_section",
                                    "elements": [
                                        {
                                            "type": "text",
                                            "text": f"변경 된 파일 수 : {file_count} ( 라인 수 : {line_count} )"
                                        }
                                    ]
                                },
                                {
                                    "type": "rich_text_section",
                                    "elements": [
                                        {
                                            "type": "text",
                                            "text": f"대화 수 : {conversation_count} "
                                        },
                                        {
                                            "type": "emoji",
                                            "name": "thumbsup"
                                        }
                                    ]
                                },
                                {
                                    "type": "rich_text_section",
                                    "elements": [
                                        {
                                            "type": "text",
                                            "text": f"응답 시간 : {response_time}"
                                        }
                                    ]
                                },
                                {
                                    "type": "rich_text_section",
                                    "elements": [
                                        {
                                            "type": "text",
                                            "text": f"승인 시간 : {approval_time}"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
    }
    return slack_message
    

# Slack Webhook 메시지 전송 함수
def send_slack_message_via_webhook(message):
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        "text": message
    }
    response = requests.post(slack_webhook_url, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")

# 타임스탬프를 한국 시간으로 변환하는 함수
def convert_timestamp_to_kst(timestamp_ms):
    timestamp_sec = int(timestamp_ms) / 1000
    dt = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc).astimezone(KST)
    return dt.strftime("%m월%d일 %H시 %M분")

# 밀리초 시간을 사람이 읽을 수 있는 형식으로 변환하는 함수
def format_duration(ms):
    if ms == 'NaN':
        return "N/A "

    total_seconds = int(ms) / 1000
    days, remainder = divmod(total_seconds, 86400)  # 86400초 = 1일
    hours, remainder = divmod(remainder, 3600)  # 3600초 = 1시간
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{int(days)}일 {int(hours)}시간 {int(minutes)}분 😢"
    else:
        return f"{int(hours)}시간 {int(minutes)}분 🙂"

# CSV 파일 분석 함수
def analyze_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        stats = []
        for row in reader:
            stats.append(row)
    return stats

# 주요 통계 정보 추출
def extract_important_info(pr_data):
    return pr_data[0]

# 통계 분석 및 보고서 작성
def generate_report(pr_stats):
    pr = extract_important_info(pr_stats)

    print(pr)
    # 정보 추출
    created_at = convert_timestamp_to_kst(pr['createdAt'])
    merged_at = convert_timestamp_to_kst(pr['mergedAt'])
    title = pr['title']
    file_count = pr['fileCount']
    changed_line_count = pr['changedLineCount']
    conversation_count = pr['changedLineCount']

    # 시간 포맷팅
    response_time = format_duration(pr['averageResponseTime'])
    approval_time = format_duration(pr['averageTimeToApproval'])
    
    message = construct_message(title,created_at,merged_at,file_count,changed_line_count,conversation_count,response_time,approval_time)
    
    send_slack_message_via_webhook(message)

# 실행
pr_stats = analyze_csv('./stats/pr.csv')
generate_report(pr_stats)
