import json

with open('perfect_ratio_channels.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

expected_channel_keys = {
    'channel_name', 'channel_url', 'total_shorts', 'subscriber_count',
    'channel_age_months', 'monetized', 'posting_frequency_days',
    'has_long_form', 'shorts'
}
expected_short_keys = {
    'title', 'duration_seconds', 'first_3s_hook', 'thumbnail_text',
    'face_in_thumbnail', 'dominant_color', 'hashtags', 'has_longform_link',
    'upload_date_ist', 'views', 'likes', 'like_ratio', 'comments_count',
    'top_3_comments', 'audio_type', 'audio_name', 'loop_type',
    'loop_mechanic', 'pacing_cuts_per_sec', 'text_on_screen'
}
expected_hashtag_keys = {'broad', 'niche', 'category', 'emotional'}
expected_patterns_keys = {
    'avg_duration', 'most_common_duration_bucket', 'avg_title_char_count',
    'top_5_hooks', 'top_5_audio_tracks', 'hashtag_formula', 'loop_breakdown',
    'face_vs_faceless_ratio', 'posting_time_ist_best_window', 'avg_like_ratio',
    'avg_cuts_per_sec'
}

assert set(data['patterns_observed'].keys()) == expected_patterns_keys, f"Patterns mismatch: {set(data['patterns_observed'].keys()) ^ expected_patterns_keys}"
assert 5 <= len(data['channels']) <= 10, f"Channels count {len(data['channels'])} not in [5, 10]"

for c in data['channels']:
    assert set(c.keys()) == expected_channel_keys, f"Channel keys mismatch: {set(c.keys()) ^ expected_channel_keys}"
    assert 7 <= c['total_shorts'] <= 15, f"Shorts count {c['total_shorts']} not in [7, 15]"
    assert c['subscriber_count'] < 200000, f"Subscribers {c['subscriber_count']} >= 200000"
    assert c['channel_age_months'] < 12, f"Channel age {c['channel_age_months']} >= 12"
    assert c['monetized'] is True, f"Monetized not True: {c['monetized']}"
    assert len(c['shorts']) == c['total_shorts'], "Shorts length mismatch"
    for s in c['shorts']:
        assert set(s.keys()) == expected_short_keys, f"Short keys mismatch: {set(s.keys()) ^ expected_short_keys}"
        assert s['views'] >= 1000000, f"Short has views < 1M: {s['views']}"
        assert set(s['hashtags'].keys()) == expected_hashtag_keys, "Hashtag keys mismatch"
        assert len(s['top_3_comments']) == 3, "Comments count != 3"

print("[PASS] 100% Bit-for-bit Schema Verification Passed!")
