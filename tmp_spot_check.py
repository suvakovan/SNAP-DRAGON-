import json
from pathlib import Path

sessions = sorted(Path('data/sessions').glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
for sf in sessions:
    data = json.loads(sf.read_text(encoding='utf-8'))
    quiz = data.get('quiz', [])
    transcript = data.get('transcript', '')
    if quiz and transcript.strip():
        print('Session:', data['metadata']['id'])
        print('LLM runtime:', json.dumps(data['metadata']['llm_backend']))
        print()
        print('TRANSCRIPT:')
        print(transcript)
        print()
        print('QUIZ QUESTIONS:')
        for i, q in enumerate(quiz):
            print(f"Q{i+1}: {q.get('question')}")
            opts = q.get('options', [])
            ci = q.get('correct_index', 0)
            print(f"  Correct answer: {opts[ci] if opts else 'N/A'}")
            print(f"  Explanation: {q.get('explanation', '')[:200]}")
            print()
        break
