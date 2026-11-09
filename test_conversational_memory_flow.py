import json

import modules.memory as memory_module
from ai import AI
from modules.memory import Memory


def isolated_memory(tmp_path):
    store = Memory()
    store.file = tmp_path / "memory.json"
    store.save({})
    return store


def test_remember_command_accepts_free_form_statement(monkeypatch, tmp_path):
    store = isolated_memory(tmp_path)
    monkeypatch.setattr(memory_module, "memory", store)

    response = memory_module.remember_command(
        "that I am testing your voice"
    )

    assert response == "I'll remember that you said: I am testing your voice."
    assert store.latest_remembered_note() == "I am testing your voice"


def test_remembered_notes_are_persistent_but_not_profile_facts(tmp_path):
    store = isolated_memory(tmp_path)

    assert store.remember_note("I am testing your voice") is True
    assert store.remember_note("The microphone is working") is True

    reloaded = Memory()
    reloaded.file = store.file

    assert reloaded.latest_remembered_note() == "The microphone is working"
    assert [item["text"] for item in reloaded.remembered_notes()] == [
        "I am testing your voice",
        "The microphone is working",
    ]
    assert reloaded.all() == {}

    raw_data = json.loads(store.file.read_text(encoding="utf-8"))
    assert len(raw_data["_remembered_notes"]) == 2


def test_memory_summary_includes_notes_even_without_profile_facts(monkeypatch, tmp_path):
    store = isolated_memory(tmp_path)
    store.remember_note("I am testing your voice")
    monkeypatch.setattr(memory_module, "memory", store)

    response = memory_module.all_memory_command()

    assert "I am testing your voice" in response


def test_ai_formats_existing_fused_conversation_context():
    formatter = AI()
    context = {
        "topic": {"current": "voice testing", "previous": "microphone setup"},
        "intent": {"current": "knowledge", "parameters": {}},
        "reference": {
            "detected": True,
            "type": "current_topic",
            "target": "voice testing",
        },
        "recent_turns": [
            {
                "user_message": "I am testing your voice",
                "assistant_message": "Understood.",
            }
        ],
    }

    rendered = formatter._format_fused_context(context)

    assert "Current topic: voice testing" in rendered
    assert "Current intent: knowledge" in rendered
    assert "Resolved reference (current_topic): voice testing" in rendered
    assert "User: I am testing your voice" in rendered
    assert "FRIDAY: Understood." in rendered
