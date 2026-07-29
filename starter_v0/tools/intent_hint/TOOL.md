---
name: intent_hint
track: bonus
kind: local_control
requires_env: []
inputs: [text]
outputs: [intent, suggested_tool, normalized_query, missing_fields, confidence]
side_effect: false
---
# intent_hint

Analyzes a user request locally and returns a likely research intent, a suggested tool, and missing fields.
It does not fetch external data and does not answer the user directly.
