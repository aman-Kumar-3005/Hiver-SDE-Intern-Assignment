import csv
import json
import random
import os

print("Loading dataset... (Isme 1-2 minute lag sakte hain kyunki file badi hai)")

brand_name = "AppleSupport"
filtered_tweets = []

# 1. In-built CSV reader se data load aur filter karo
with open('twcs.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['author_id'] == brand_name:
            filtered_tweets.append({
                'tweet_id': row['tweet_id'],
                'text': row['text'],
                'intent': '',
                'escalate': False,
                'escalation_reason': ''
            })

print(f"Total tweets by {brand_name}: {len(filtered_tweets)}")

# 2. 200 random examples sample karo
random.seed(42)
if len(filtered_tweets) > 2000:
    golden_samples = random.sample(filtered_tweets, 2000)
else:
    golden_samples = filtered_tweets

# 3. Data folder banakar JSONL format mein save karo
os.makedirs('data', exist_ok=True)
output_file = 'data/golden_set_unlabeled.jsonl'

with open(output_file, mode='w', encoding='utf-8') as file:
    for sample in golden_samples:
        file.write(json.dumps(sample) + '\n')

print(f"Done! Aapki file '{output_file}' ready hai. Ab manual labeling start kar sakte hain.")