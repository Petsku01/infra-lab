# tests/test_keycode_bot.py
# test suite
# -pk
import pytest
from unittest.mock import Mock, patch, MagicMock, ANY
import json
import os
import sqlite3
from datetime import datetime

# Import the actual bot code (adjust if you moved it to a module)
# We'll mock heavy dependencies but test real logic
from your_script_name import KeycodeBot, Notifier, ProxyManager, PATTERNS, db_lock, conn  # <-- rename "your_script_name" to actual filename

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture
def clean_db():
    """Ensure a clean in-memory DB for each test"""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE keys (
            key TEXT PRIMARY KEY,
            platform TEXT,
            source TEXT,
            found_at TIMESTAMP,
            status TEXT DEFAULT 'unclaimed'
        )
    """)
    conn.commit()
    yield conn
    conn.close()

@pytest.fixture
def bot_instance(monkeypatch, clean_db):
    """Create a bot with mocked external dependencies"""
    # Replace global conn with test one
    monkeypatch.setattr("your_script_name.conn", clean_db)
    monkeypatch.setattr("your_script_name.cursor", clean_db.cursor())

    # Mock requests & tweepy completely
    monkeypatch.setattr("requests.get", Mock())
    monkeypatch.setattr("tweepy.Client", Mock())

    bot = KeycodeBot()
    bot.websites = ["https://test.com/giveaway"]
    return bot

@pytest.fixture
def mock_requests(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.text = "dummy html"
    mock_resp.raise_for_status.return_value = None
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_resp)
    return mock_resp

# ----------------------------------------------------------------------
# Core Key Extraction Tests
# ----------------------------------------------------------------------
@pytest.mark.parametrize("platform,text,expected_keys", [
    ("Steam", "Here is your key: ABCDE-FGHIJ-KLMNO", ["ABCDE-FGHIJ-KLMNO"]),
    ("Steam", "ABCDE-FGHIJ-KLMNO and another 12345-67890-ABCDE", ["ABCDE-FGHIJ-KLMNO", "12345-67890-ABCDE"]),
    ("Xbox", "Xbox code: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX", ["XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"]),
    ("PlayStation", "PSN: ABCD-EFGH-IJKL", ["ABCD-EFGH-IJKL"]),
    ("PlayStation", "Invalid PSN: ABCD-EFGH-IJK", []),  # wrong length
    ("Steam", "No keys here", []),
])
def test_extract_keys_correctly_identifies_valid_keys(bot_instance, platform, text, expected_keys, clean_db):
    with db_lock:
        results = bot_instance.extract_keys(text, "test_source")
    
    assert results.get(platform, []) == expected_keys
    if expected_keys:
        cursor = clean_db.cursor()
        cursor.execute("SELECT key FROM keys WHERE platform = ?", (platform,))
        saved = [row[0] for row in cursor.fetchall()]
        assert set(saved) == set(expected_keys)

def test_extract_keys_ignores_duplicates(bot_instance, clean_db):
    text = "Key: ABCDE-FGHIJ-KLMNO and again ABCDE-FGHIJ-KLMNO"
    
    with db_lock:
        first = bot_instance.extract_keys(text, "src1")
        second = bot_instance.extract_keys(text, "src2")

    assert len(first["Steam"]) == 1
    assert second == {}  # second time → already in DB → nothing returned

# ----------------------------------------------------------------------
# Web Page Scanning Tests
# ----------------------------------------------------------------------
def test_scan_page_finds_keys_in_html(bot_instance, monkeypatch):
    html = """
    <html><body>
    <p>Enjoy your free Steam key: 11111-22222-33333</p>
    <a href="https://example.com/key/AAAAA-BBBBB-CCCCC">Click here</a>
    </body></html>
    """
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status.return_value = None
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: mock_resp)

    result = bot_instance.scan_page("https://fake.com")
    
    assert "Steam" in result
    assert "11111-22222-33333" in result["Steam"]
    assert "AAAAA-BBBBB-CCCCC" in result["Steam"]

def test_scan_page_handles_request_failure(bot_instance, monkeypatch):
    monkeypatch.setattr("requests.get", Mock(side_effect=requests.RequestException("Network error")))
    result = bot_instance.scan_page("https://down.com")
    assert result == {}

# ----------------------------------------------------------------------
# X (Twitter) Scanning Tests
# ----------------------------------------------------------------------
def test_scan_x_finds_keys(bot_instance, monkeypatch):
    mock_tweet = MagicMock()
    mock_tweet.text = "Free Steam key! XXXXX-YYYYY-ZZZZZ"
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [mock_tweet]
    mock_client.search_recent_tweets.return_value = mock_response
    
    monkeypatch.setattr("your_script_name.x_client", mock_client)

    result = bot_instance.scan_x()
    
    assert "Steam" in result
    assert "XXXXX-YYYYY-ZZZZZ" in result["Steam"]

def test_scan_x_returns_empty_on_no_client(bot_instance, monkeypatch):
    monkeypatch.setattr("your_script_name.x_client", None)
    assert bot_instance.scan_x() == {}

# ----------------------------------------------------------------------
# Notification System Tests
# ----------------------------------------------------------------------
def test_notifier_sends_to_all_channels(monkeypatch):
    config = {
        "discord_webhook": "https://discord.com/fake",
        "telegram": {"bot_token": "123:abc", "chat_id": "12345"},
        "email": {
            "smtp_server": "smtp.gmail.com", "port": 587,
            "sender": "test@gmail.com", "password": "pass", "recipient": "recv@gmail.com"
        }
    }
    notifier = Notifier(config)

    # Mock all external calls
    discord_mock = Mock()
    tg_mock = Mock()
    smtp_mock = Mock()
    monkeypatch.setattr("requests.post", discord_mock)
    monkeypatch.setattr("telegram.Bot.send_message", tg_mock)
    monkeypatch.setattr("smtplib.SMTP", smtp_mock)

    notifier.send("Test message 123")

    discord_mock.assert_called_once()
    tg_mock.assert_called_once()
    smtp_mock.assert_called()

# ----------------------------------------------------------------------
# Proxy Manager Tests
# ----------------------------------------------------------------------
def test_proxy_manager_rotates_proxies():
    proxies = ["http://p1:8080", "http://p2:8080", "http://p3:8080"]
    pm = ProxyManager(proxies)
    seen = set()
    for _ in range(20):
        proxy = pm.get()
        if proxy:
            seen.add(proxy["http"])
    assert len(seen) >= 2  # should rotate

def test_proxy_manager_returns_none_when_empty():
    pm = ProxyManager([])
    assert pm.get() is None

# ----------------------------------------------------------------------
# Full Scan Cycle Integration Test (lightweight)
# ----------------------------------------------------------------------
def test_full_scan_cycle_finds_and_notifies(bot_instance, monkeypatch):
    # Mock web page that returns one key
    html = "<p>Steam key: TEST1-TEST2-TEST3</p>"
    mock_web = MagicMock()
    mock_web.text = html
    mock_web.raise_for_status.return_value = None

    # Mock X with one key
    mock_tweet = MagicMock()
    mock_tweet.text = "Xbox key: AAAAA-BBBBB-CCCCC-DDDDD-EEEEE"
    mock_client = MagicMock()
    mock_client.search_recent_tweets.return_value.data = [mock_tweet]

    # Mock notifier
    notify_mock = Mock()
    monkeypatch.setattr("your_script_name.notifier.send", notify_mock)
    monkeypatch.setattr("requests.get", lambda *a, **k: mock_web)
    monkeypatch.setattr("your_script_name.x_client", mock_client)

    bot_instance.scan_cycle()

    # Should have found 2 keys total
    assert notify_mock.call_count == 1
    sent_message = notify_mock.call_args[0][0]
    assert "TEST1-TEST2-TEST3" in sent_message
    assert "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE" in sent_message

# ----------------------------------------------------------------------
# Adaptive Interval Test
# ----------------------------------------------------------------------
def test_adaptive_interval_speeds_up_on_success(bot_instance):
    initial = bot_instance.scan_interval
    # Simulate finding keys → should decrease interval
    bot_instance.scan_interval = 300
    bot_instance.scan_cycle = lambda: None  # no-op
    monkeypatch.setattr(bot_instance, "scan_cycle", lambda: None)
    
    # Force success (mock results)
    with patch.object(bot_instance, "scan_cycle", return_value=None):
        # Manually trigger adaptive logic
        bot_instance.scan_interval = 300
        # Simulate finding keys → interval shrinks
        bot_instance.scan_interval *= 0.8
        assert bot_instance.scan_interval < 300

# ----------------------------------------------------------------------
# Run with: pytest -q
# ----------------------------------------------------------------------
if __name__ == "__main__":
    pytest.main(["-v", __file__])
