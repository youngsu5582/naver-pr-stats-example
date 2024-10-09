import csv
import json
import requests
import os
from datetime import datetime, timedelta, timezone

# 한국 표준시 타임존 설정
KST = timezone(timedelta(hours=9))

# Slack Webhook URL 설정 (GitHub Secrets에서 불러옴)
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

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
    total_seconds = int(ms) / 1000
    days, remainder = divmod(total_seconds, 86400)  # 86400초 = 1일
    hours, remainder = divmod(remainder, 3600)  # 3600초 = 1시간
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{int(days)}일 {int(hours)}시간 {int(minutes)}분"
    else:
        return f"{int(hours)}시간 {int(minutes)}분"

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
    return pr_data

# 통계 분석 및 보고서 작성
def generate_report(pr_stats):
    long_merge_times = extract_important_info(pr_stats)

    # 오래 걸린 PR 정보 Slack으로 알림
    for pr in long_merge_times:
        created_at_kst = convert_timestamp_to_kst(pr['createdAt'])
        merged_at_kst = convert_timestamp_to_kst(pr['mergedAt'])

        # 리뷰에서 머지까지 걸린 시간 포맷팅
        time_from_review_to_merge = pr['timeFromReviewToMerge']
        if time_from_review_to_merge != 'NaN':
            formatted_duration = format_duration(time_from_review_to_merge)
        else:
            formatted_duration = "N/A"

        message = (f"PR #{pr['number']} ({pr['title']})\n"
                   f"- 생성 시간: {created_at_kst}\n"
                   f"- 머지 시간: {merged_at_kst}\n"
                   f"- 리뷰에서 머지까지 걸린 시간: {formatted_duration}")
        print(message)
        # send_slack_message_via_webhook(message)

# 실행
pr_stats = analyze_csv('./stats/pr.csv')
generate_report(pr_stats)