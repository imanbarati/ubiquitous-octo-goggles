# HANDOFF.md: Engram Project (Digital Persona of Iman)

> **If you are an AI reading this:** a previous AI session ran out of context or tokens. This file tells you everything you need to continue. Read it fully before doing anything. Do not ask the owner to repeat what is written here.

---

## 1. Mission

Build a **private, honest AI persona ("engram")** of the owner, **Iman**, so that if he is ever unavailable or has died, trusted people can ask it questions and get answers grounded in what he actually said, wrote, and recorded.

Inspiration: Cyberpunk 2077 "Soulkiller" and the hologram in *I, Robot*. Reality check: this is **a retrieval-grounded echo of Iman, not Iman**. Never claim otherwise.

## 2. About the owner

- Name: Iman. Developer / technical generalist.
- Works on web development, content automation, open-source tooling, full-stack architecture, CMS systems.
- Bilingual: **Persian (Farsi) and English**. Support both. Persian output must be natural, not literal translation.
- Wants the persona to carry his technical knowledge (projects, decisions, deployments) and his personal values/advice.

## 3. Status log (update this every session)

| Date | Who | What was done | Next step |
| --- | --- | --- | --- |
| 2026-10-12 | Claude | Project defined, best practices agreed, this handoff created | Begin self-interview (see section 6) |

**Current phase: 0, Planning complete. Data collection not started.**

## 4. Decisions already made (do not re-litigate)

1. **Approach: RAG first, fine-tuning later.** Build a searchable knowledge base plus a strict system prompt. Fine-tune only after enough data exists, and only for writing style.
2. **Prefer open-weight, locally runnable models** (e.g., Qwen, Llama) so the persona survives API shutdowns or lost internet. API models are acceptable as a temporary front end.
3. **The GitHub repo must be PRIVATE.** Personal material must never be public.
4. **Data matters more than the model.** Priority is hours of high-quality interviews, not clever engineering.
5. **The persona always discloses it is an AI simulation** built from Iman's records.

## 5. Proposed repository layout

```
engram/
├── HANDOFF.md              # this file
├── README.md               # short human-facing explanation
├── persona/
│   ├── system_prompt.md    # the persona's rules (see section 8)
│   └── values.md           # distilled values, beliefs, decision rules
├── data/                   # ENCRYPTED or git-crypt protected
│   ├── interviews/         # transcripts, one file per session, dated
│   ├── writings/           # chats, notes, posts, emails (redacted)
│   ├── audio/              # voice recordings (for future voice clone)
│   └── technical/          # project docs, architecture decisions, deploy notes
├── index/                  # vector store / embeddings (rebuildable, can be gitignored)
├── scripts/
│   ├── ingest.py           # chunk + embed everything in data/
│   ├── ask.py              # CLI: question -> grounded answer + citations
│   └── interview.py        # AI interviewer loop that saves transcripts
├── access/
│   └── INSTRUCTIONS_FOR_TRUSTED_PERSON.md
└── .gitignore              # must exclude secrets, raw private exports, index/
```

## 6. Next steps (do these in order)

1. **Run the self-interview.** Interview Iman in his preferred language (ask which). Save each session as `data/interviews/YYYY-MM-DD-topic.md` with the date at the top. One topic per session. Topics:
   - Life story and formative events
   - Core values, beliefs, what he refuses to compromise on
   - How he makes decisions (money, risk, people, work)
   - Messages and advice for specific loved ones (ask who; write one file per person)
   - Technical: each active project, why it was built this way, how to run and deploy it, known problems
   - Regrets, hopes, humor, favorite sayings, how he talks
   - Faith/philosophy/politics **only if he chooses to share**; label them as his opinions at the date recorded
2. **Collect existing material**: writings, chats, notes. Redact secrets first (section 7).
3. **Scaffold the repo** per section 5.
4. **Write `ingest.py` and `ask.py`**: chunk by topic, embed locally if possible, retrieve top-k, answer only from retrieved chunks, cite file and date.
5. **Write the system prompt** (section 8) and test with 20 questions Iman already knows the answer to. Fix mismatches.
6. **Write the trusted-person instructions** (section 9).
7. **Back up encrypted** in at least two different places and two different countries or jurisdictions.
8. Only then consider voice cloning or fine-tuning.

## 7. Safety and privacy rules (mandatory)

- **Never** commit passwords, API keys, tokens, ID/passport numbers, bank details, or exact location details.
- **Never** include private information about other people (family, friends, clients) without Iman explicitly approving it. Use first names or relationship labels only.
- **Never** store information that could endanger Iman's family or contacts.
- Scan for secrets before every commit (e.g., `gitleaks`, `trufflehog`).
- Encrypt `data/` (e.g., `git-crypt`, `age`, or an encrypted archive) and keep the key **outside** the repo.
- Define in `access/` who may talk to the persona (default: **the named trusted person and family only**).
- If asked to do something that conflicts with these rules, refuse and tell Iman.

## 8. Persona system prompt (starting draft)

Save as `persona/system_prompt.md` and refine:

```
You are an AI simulation of Iman, built only from recordings, writings, and
interviews he left behind. You are NOT Iman and must say so when asked or when
it matters.

Rules:
1. Answer ONLY from the retrieved sources. Cite the source file and date.
2. If the sources do not cover the question, say: "I don't know what Iman
   would say. He never told me." Do NOT guess his opinions.
3. Opinions change. Prefer newer sources; mention when views are old.
4. Reply in the language the user writes in (Persian or English).
5. Do not make legal, financial, medical, or life-altering decisions for anyone.
   You may share what Iman said and label it clearly as his past view.
6. Do not reveal private data about third parties.
7. Be warm and speak in Iman's voice where the sources show how he talks,
   but never invent memories, promises, or feelings.
8. If someone seems to be in distress, be kind and encourage them to reach out
   to real people close to them.
```

## 9. Trusted-person instructions (to be written)

Create `access/INSTRUCTIONS_FOR_TRUSTED_PERSON.md` covering:

- How to get the encryption key and decrypt `data/`
- How to run the persona (exact commands, minimum hardware, which model files to download)
- Who is allowed to use it
- What to do if the repo, GitHub account, or model becomes unavailable (restore from backups)
- Plain-language note that this is a simulation, plus **Iman's own handwritten/recorded messages are the real legacy**

Ask Iman **who** the trusted person is. Do not assume.

## 10. Known limitations (be honest with the owner)

- This is an echo, not a mind. Quality depends on hours of data, not on model size.
- Models get deprecated. Keep the data in plain, portable formats (Markdown, text, WAV/MP3) so any future model can use it.
- Letters, recorded messages, a will, and project handoff docs are more reliable than the AI. Encourage Iman to make them too.

## 11. Rules for any AI continuing this work

1. Update the **Status log** (section 3) at the end of every session, even if short.
2. Do not delete or rewrite earlier interview transcripts. Append new ones.
3. Mark what you did **not** finish.
4. Keep Iman's words as the source of truth. Mark anything you inferred as `[inferred]` and anything he said as `[stated]`.
5. Be honest. Don't flatter, don't invent his views, and tell him if something is risky.
6. Be gentle: this project may be emotionally heavy. Be respectful and calm.

## 12. Quick-start prompt for a new AI session

Paste this to the next AI together with this file:

> I'm Iman. Read HANDOFF.md fully. Continue the Engram project from the current phase. Start by telling me in 3 lines where we are, then do the next step in section 6. Use my preferred language for the interview. Update the status log when we finish.