---
name: keywords
track: core
kind: local_formatter
provider: none
requires_env: []
inputs: [text, max_keywords]
outputs: [keywords, count]
side_effect: false
---
# keywords

Extracts frequent, meaningful keywords from user-supplied text locally. It does
not search for information and has no external side effects. Use it only for an
explicit keyword or tag extraction request.
