#!/usr/bin/env python3
"""
interview.py - AI interviewer for the Engram project.

An AI asks you ONE question at a time about a topic. Your answers are saved
as dated Markdown transcripts in data/interviews/, tagged [stated], ready to
be indexed later by ingest.py.

No third-party packages needed (Python 3.8+ standard library only).

Backends
  ollama     (default) local open-weight model, free, works offline
             -> install Ollama, then e.g.:  ollama pull qwen2.5:14b
  anthropic  Claude API -> set ANTHROPIC_API_KEY

Examples
  python interview.py --list
  python interview.py --topic values --lang fa
  python interview.py --topic life-story --lang both --provider anthropic
  python interview.py --topic "my grandfather's stories"      # custom topic

In-session commands (type them instead of an answer)
  /next    save and pick another topic      /skip   ask a different question
  /topics  list topics                      /quit   save and exit
  /help    show commands
  End a line with \\ to continue your answer on the next line.

PRIVACY: never type passwords, keys, ID numbers, bank details, exact
locations, or private details about other people. The script warns if an
answer looks like a secret. Keep data/ encrypted and the repo PRIVATE.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

OUT_DIR = Path("data/interviews")
CONTEXT_MESSAGES = 21  # how much recent chat the model sees (transcript keeps everything)

TOPICS = {
    "life-story": "Life story: childhood, family background, formative events, turning points.",
    "values": "Core values and beliefs: what matters most, what he refuses to compromise on, and why.",
    "decisions": "How he makes decisions about money, risk, people, work, and conflict. Ask for real examples.",
    "advice": "Advice and messages for specific people. Ask who they are first; use first names or relationship labels only.",
    "technical": "Technical knowledge: each active project, why it was built that way, how to run and deploy it, known problems. Never ask for passwords or keys.",
    "voice": "How he talks and thinks: humor, favorite sayings, pet peeves, what he finds beautiful, how he comforts or encourages people.",
    "regrets-hopes": "Regrets, fears, hopes, and what he wants people to remember about him.",
    "work-craft": "Work and craft: how he learns, debugs, designs, and what he would teach a young developer.",
}

LANG_RULES = {
    "fa": "Conduct the interview entirely in natural, warm Persian (Farsi). Not literal translation.",
    "en": "Conduct the interview in English.",
    "both": "Match the language the person writes in; they use both Persian (Farsi) and English. Never force a language.",
}

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_\-]{16,}",
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"\b(?:\d[ -]?){13,19}\b",
    r"(?i)\b(password|passwd|api[_ -]?key|secret|token)\b\s*[:=]",
    r"(رمز\s*عبور|پسورد)\s*[:=]?",
]


def system_prompt(topic_desc, lang):
    return f"""You are a thoughtful interviewer helping a person record who they are, so that an AI
persona built from their own words can answer questions about them later.

Topic: {topic_desc}
{LANG_RULES[lang]}

Rules:
1. Ask exactly ONE question per turn. Keep it short and clear.
2. Prefer concrete stories and examples over abstractions ("tell me about a time when...").
3. Follow up on interesting specifics before moving on. Probe the WHY behind choices.
4. Never put words in the person's mouth. Never summarize or flatter at length.
5. Never ask for passwords, keys, ID or bank numbers, exact locations, or private details
   about other people. If the person starts sharing such things, gently steer away.
6. If they seem distressed, respond with brief kindness and let them choose to continue.
7. Output only the question (plus at most one short acknowledging sentence)."""


# ----------------------------- model backends -----------------------------

def _post(url, payload, headers):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:500]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connection failed: {e.reason}")


def ask_ollama(system, messages, model):
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    payload = {
        "model": model,
        "stream": False,
        "messages": [{"role": "system", "content": system}] + messages,
    }
    return _post(f"{host}/api/chat", payload, {})["message"]["content"].strip()


def ask_anthropic(system, messages, model):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("Set ANTHROPIC_API_KEY to use the anthropic provider.")
    payload = {"model": model, "max_tokens": 600, "system": system, "messages": messages}
    data = _post(
        "https://api.anthropic.com/v1/messages",
        payload,
        {"x-api-key": key, "anthropic-version": "2023-06-01"},
    )
    return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text").strip()


def next_question(provider, model, system, messages):
    window = messages[-CONTEXT_MESSAGES:]
    while window and window[0]["role"] != "user":  # APIs expect a user-first window
        window = window[1:]
    fn = ask_ollama if provider == "ollama" else ask_anthropic
    return fn(system, window, model)


# ------------------------------- file handling -------------------------------

def slugify(text):
    slug = re.sub(r"[^\w\-]+", "-", text.strip().lower(), flags=re.UNICODE).strip("-")
    return slug[:60] or "topic"


def transcript_path(slug):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR / f"{date.today().isoformat()}-{slug}.md"


def init_transcript(path, slug, desc, lang, provider, model):
    if path.exists():
        return
    path.write_text(
        f"---\ntopic: {slug}\ndate: {date.today().isoformat()}\nlanguage: {lang}\n"
        f"interviewer: {provider}/{model}\nsource: self-interview\n---\n\n"
        f"# {slug}\n\n_{desc}_\n\n"
        "> Answers tagged [stated] are the owner's own words. Everything else is the interviewer's question.\n\n",
        encoding="utf-8",
    )


def append_qa(path, question, answer):
    with path.open("a", encoding="utf-8") as f:
        f.write(f"**Q:** {question}\n\n**A:** [stated] {answer}\n\n")


def looks_secret(text):
    return any(re.search(p, text) for p in SECRET_PATTERNS)


def read_answer():
    lines = []
    while True:
        line = input("> " if not lines else "… ")
        if line.endswith("\\"):
            lines.append(line[:-1])
            continue
        lines.append(line)
        return "\n".join(lines).strip()


# --------------------------------- session ---------------------------------

def list_topics():
    print("\nTopics:")
    for k, v in TOPICS.items():
        print(f"  {k:<14} {v}")
    print("  (or any text of your own for a custom topic)\n")


def pick_topic():
    list_topics()
    choice = input("Topic: ").strip()
    return choice or "values"


def run_topic(topic, lang, provider, model):
    desc = TOPICS.get(topic, topic)  # custom topic text is used as-is
    slug = topic if topic in TOPICS else slugify(topic)
    path = transcript_path(slug)
    init_transcript(path, slug, desc, lang, provider, model)

    system = system_prompt(desc, lang)
    start = "Begin the interview with your first question."
    if path.stat().st_size > 800:  # resuming: give the interviewer the recent tail
        tail = path.read_text(encoding="utf-8")[-3000:]
        start = ("We already covered part of this topic today. Recent transcript:\n\n"
                 f"{tail}\n\nContinue with a NEW question that does not repeat these.")
    messages = [{"role": "user", "content": start}]

    print(f"\nTopic: {slug}  |  saving to {path}\nType /help for commands.\n")

    while True:
        try:
            question = next_question(provider, model, system, messages)
        except RuntimeError as e:
            print(f"\n[error] {e}\nYour transcript so far is saved at {path}.")
            return "quit"
        messages.append({"role": "assistant", "content": question})
        print(f"\n{question}\n")

        try:
            answer = read_answer()
        except (EOFError, KeyboardInterrupt):
            print("\nSaved. Bye.")
            return "quit"

        low = answer.lower()
        if low in ("/quit", "/exit"):
            print(f"Saved at {path}. Bye.")
            return "quit"
        if low == "/next":
            return "next"
        if low == "/topics":
            list_topics()
            messages.pop()  # re-ask a fresh question
            continue
        if low == "/help":
            print(__doc__.split("In-session commands")[1].split("PRIVACY")[0])
            messages.pop()
            continue
        if low == "/skip":
            messages.append({"role": "user", "content": "Skip that. Ask a different question."})
            continue
        if not answer:
            messages.pop()
            continue

        if looks_secret(answer):
            ok = input("That looks like it may contain a secret or ID number. Save it anyway? [y/N] ")
            if ok.strip().lower() != "y":
                messages.append({"role": "user", "content": "I'd rather not answer that. Ask something else."})
                continue

        append_qa(path, question, answer)
        messages.append({"role": "user", "content": answer})


def main():
    ap = argparse.ArgumentParser(description="Self-interview for the Engram project.")
    ap.add_argument("--topic", help="topic key (see --list) or any custom text")
    ap.add_argument("--lang", choices=LANG_RULES.keys(), default="both")
    ap.add_argument("--provider", choices=["ollama", "anthropic"], default="ollama")
    ap.add_argument("--model", help="model name (default: qwen2.5:14b for ollama, claude-sonnet-5-5 for anthropic)")
    ap.add_argument("--list", action="store_true", help="list topics and exit")
    args = ap.parse_args()

    if args.list:
        list_topics()
        return

    model = args.model or ("qwen2.5:14b" if args.provider == "ollama" else "claude-sonnet-5-5")
    topic = args.topic or pick_topic()

    while True:
        result = run_topic(topic, args.lang, args.provider, model)
        if result != "next":
            break
        topic = pick_topic()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
