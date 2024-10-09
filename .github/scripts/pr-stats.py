import csv
import json
import requests
import os

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
    print(pr_data)
    # long_merge_times = [pr for pr in pr_data if int(pr["timeFromReviewToMerge"]) > 10000000]
    return pr_data
    # return long_merge_times

# 통계 분석 및 보고서 작성
def generate_report(pr_stats):
    long_merge_times = extract_important_info(pr_stats)

    # 오래 걸린 PR 정보 Slack으로 알림
    for pr in long_merge_times:
        message = f"PR #{pr['number']} ({pr['title']}) took {pr['timeFromReviewToMerge']} ms to merge."
        print(message)
        # send_slack_message_via_webhook(message)

    # 유저 참여율 정보 이메일로 발송
    # report_body = "User Participation Report:\n\n"
    # for user, participation in user_participation.items():
    #     report_body += f"User {user} has a participation rate of {participation}%.\n"




# 실행
pr_stats = analyze_csv('./stats/pr.csv')

generate_report(pr_stats)
