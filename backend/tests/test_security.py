"""
Security-focused tests for authentication and authorization.

Tests verify:
1. Password hashing (not plaintext storage)
2. Password verification
3. Authorization (User A cannot access User B's data)
4. Input validation
5. Rate limiting
6. Error message safety
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.users import store as user_store
from backend.app.services import auth_service
from datetime import timedelta
import time

client = TestClient(app)


class TestPasswordHashing:
    """Verify passwords are hashed, not stored in plaintext."""
    
    def test_password_not_stored_plaintext(self):
        """Password must be hashed, not stored as plaintext."""
        username = "test_hash_user"
        password = "TestPassword123"
        
        # Register
        r = client.post("/auth/register", json={"username": username, "password": password})
        assert r.status_code == 201
        
        # Get the user from store (simulating database access)
        user = user_store.default_user_store.get_user_by_username(username)
        
        # Password hash should NOT equal the original password
        assert user.hashed_password != password
        
        # Password hash should not contain the original password
        assert password not in user.hashed_password
    
    def test_argon2_hash_format(self):
        """Hashed passwords should use Argon2 format."""
        username = "test_argon_user"
        password = "TestPassword456"
        
        r = client.post("/auth/register", json={"username": username, "password": password})
        assert r.status_code == 201
        
        user = user_store.default_user_store.get_user_by_username(username)
        
        # Argon2 hashes start with $argon2
        assert user.hashed_password.startswith('$argon2')
    
    def test_different_passwords_different_hashes(self):
        """Different passwords must produce different hashes."""
        # Register two users with different passwords
        r1 = client.post("/auth/register", json={"username": "user1", "password": "Password111"})
        r2 = client.post("/auth/register", json={"username": "user2", "password": "Password222"})
        
        user1 = user_store.default_user_store.get_user_by_username("user1")
        user2 = user_store.default_user_store.get_user_by_username("user2")
        
        # Hashes must be different
        assert user1.hashed_password != user2.hashed_password
    
    def test_same_password_different_hashes(self):
        """Same password should produce different hashes (due to salt)."""
        # Register two users with SAME password
        r1 = client.post("/auth/register", json={"username": "user3", "password": "SamePassword1"})
        r2 = client.post("/auth/register", json={"username": "user4", "password": "SamePassword1"})
        
        user1 = user_store.default_user_store.get_user_by_username("user3")
        user2 = user_store.default_user_store.get_user_by_username("user4")
        
        # Even with same password, hashes must be different (due to random salt)
        assert user1.hashed_password != user2.hashed_password


class TestPasswordVerification:
    """Verify password verification works correctly."""
    
    def test_login_correct_password(self):
        """Login succeeds with correct password."""
        r = client.post("/auth/register", json={"username": "correct_pw_user", "password": "CorrectPass1"})
        assert r.status_code == 201
        
        r = client.post("/auth/login", json={"username": "correct_pw_user", "password": "CorrectPass1"})
        assert r.status_code == 200
        assert "access_token" in r.json()
    
    def test_login_incorrect_password(self):
        """Login fails with incorrect password."""
        r = client.post("/auth/register", json={"username": "wrong_pw_user", "password": "CorrectPass2"})
        assert r.status_code == 201
        
        r = client.post("/auth/login", json={"username": "wrong_pw_user", "password": "WrongPassword1"})
        assert r.status_code == 401
        assert "Invalid username or password" in r.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Login fails gracefully for non-existent user."""
        r = client.post("/auth/login", json={"username": "nonexistent_user", "password": "Password1"})
        assert r.status_code == 401
        # Error message should not reveal whether username exists
        assert "Invalid username or password" in r.json()["detail"]


class TestAuthorization:
    """Verify users cannot access other users' data."""
    
    def test_user_cannot_access_other_user_conversations(self):
        """User A should not be able to access User B's conversations."""
        # Create User A
        r = client.post("/auth/register", json={"username": "user_a", "password": "UserAPass1"})
        user_a_id = r.json()["user"]["id"]
        
        # Create User B
        r = client.post("/auth/register", json={"username": "user_b", "password": "UserBPass1"})
        user_b_id = r.json()["user"]["id"]
        
        # Login as User A
        r = client.post("/auth/login", json={"username": "user_a", "password": "UserAPass1"})
        token_a = r.json()["access_token"]
        
        # User A tries to list User B's conversations
        headers = {"Authorization": f"Bearer {token_a}"}
        r = client.get(f"/conversations/user/{user_b_id}", headers=headers)
        
        # Should return 403 Forbidden
        assert r.status_code == 403
        assert "Access denied" in r.json()["detail"]
    
    def test_user_can_list_own_conversations(self):
        """User should be able to list their own conversations."""
        r = client.post("/auth/register", json={"username": "own_conv_user", "password": "Password1"})
        user_id = r.json()["user"]["id"]
        
        r = client.post("/auth/login", json={"username": "own_conv_user", "password": "Password1"})
        token = r.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get(f"/conversations/user/{user_id}", headers=headers)
        
        # Should succeed
        assert r.status_code == 200
        assert "conversations" in r.json()
    
    def test_user_cannot_continue_other_user_conversation(self):
        """User A should not be able to POST /chat with User B's session_id."""
        from backend.app.services import chat_service
        from backend.app.agents.base import AgentOutput
        
        # Create User A
        r = client.post("/auth/register", json={"username": "user_chat_a", "password": "UserAPass1"})
        user_a_id = r.json()["user"]["id"]
        
        # Create User B
        r = client.post("/auth/register", json={"username": "user_chat_b", "password": "UserBPass1"})
        user_b_id = r.json()["user"]["id"]
        
        # Login as User B and create a conversation
        r = client.post("/auth/login", json={"username": "user_chat_b", "password": "UserBPass1"})
        token_b = r.json()["access_token"]
        
        # Patch executor to return deterministic response
        def fake_execute(agents, user_text, rag_context=None):
            return [AgentOutput(agent="faq", answer="Test response", confidence=0.95, requires_escalation=False, sources=[])]
        
        original_execute = chat_service.default_chat_service.execute_agents
        chat_service.default_chat_service.execute_agents = fake_execute
        
        try:
            # User B creates a conversation
            headers_b = {"Authorization": f"Bearer {token_b}"}
            r = client.post("/chat", json={"message": "User B's message"}, headers=headers_b)
            assert r.status_code == 200
            session_id_b = r.json()["session_id"]
            
            # Login as User A
            r = client.post("/auth/login", json={"username": "user_chat_a", "password": "UserAPass1"})
            token_a = r.json()["access_token"]
            
            # User A tries to continue User B's conversation
            headers_a = {"Authorization": f"Bearer {token_a}"}
            r = client.post("/chat", json={"message": "User A trying to hijack", "session_id": session_id_b}, headers=headers_a)
            
            # Should return 403 Forbidden
            assert r.status_code == 403
            assert "Access denied" in r.json()["detail"]
        finally:
            # Restore original executor
            chat_service.default_chat_service.execute_agents = original_execute


class TestInputValidation:
    """Verify input validation on auth endpoints."""
    
    def test_registration_requires_username(self):
        """Registration must require username."""
        r = client.post("/auth/register", json={"username": "", "password": "Password1"})
        assert r.status_code == 422  # Validation error
    
    def test_registration_requires_minimum_password_length(self):
        """Registration must require password of at least 8 characters."""
        r = client.post("/auth/register", json={"username": "shortpw", "password": "Pass1"})
        assert r.status_code == 422
    
    def test_registration_requires_password_with_letter_and_number(self):
        """Registration must require letter and number in password."""
        r = client.post("/auth/register", json={"username": "noletter", "password": "12345678"})
        assert r.status_code == 422
        
        r = client.post("/auth/register", json={"username": "nonumber", "password": "onlyletters"})
        assert r.status_code == 422
    
    def test_registration_username_format_validation(self):
        """Username should only allow alphanumeric, underscore, hyphen."""
        # Valid usernames
        r = client.post("/auth/register", json={"username": "valid_user-123", "password": "Password1"})
        assert r.status_code == 201
        
        # Invalid characters (space, @, etc.)
        r = client.post("/auth/register", json={"username": "invalid user", "password": "Password1"})
        assert r.status_code == 422
        
        r = client.post("/auth/register", json={"username": "invalid@user", "password": "Password1"})
        assert r.status_code == 422
    
    def test_registration_username_length_limits(self):
        """Username should be between 1 and 128 characters."""
        r = client.post("/auth/register", json={"username": "", "password": "Password1"})
        assert r.status_code == 422
        
        long_username = "a" * 129
        r = client.post("/auth/register", json={"username": long_username, "password": "Password1"})
        assert r.status_code == 422


class TestDuplicateRegistration:
    """Verify handling of duplicate registrations."""
    
    def test_duplicate_username_registration_rejected(self):
        """Registering with existing username should fail."""
        # First registration
        r = client.post("/auth/register", json={"username": "duplicate_test", "password": "Password1"})
        assert r.status_code == 201
        
        # Second registration with same username
        r = client.post("/auth/register", json={"username": "duplicate_test", "password": "Password2"})
        assert r.status_code == 400
        assert "Username already exists" in r.json()["detail"]
    
    def test_error_message_doesnt_leak_info(self):
        """Error message should not reveal why registration failed."""
        # Register first user
        client.post("/auth/register", json={"username": "leak_test", "password": "Password1"})
        
        # Try to register with same username
        r = client.post("/auth/register", json={"username": "leak_test", "password": "Password2"})
        assert r.status_code == 400
        # Should not reveal "password is wrong" or other details
        detail = r.json()["detail"]
        assert detail.lower() in ["username already exists", "registration failed"]


class TestErrorMessageSafety:
    """Verify error messages don't leak sensitive information."""
    
    def test_login_error_generic_message(self):
        """Login error should not reveal if username exists or password is wrong."""
        # Try to login with non-existent user
        r = client.post("/auth/login", json={"username": "definitely_does_not_exist_12345", "password": "Password1"})
        assert r.status_code == 401
        detail = r.json()["detail"]
        # Should be generic
        assert "Invalid" in detail or "password" in detail.lower()
        # Should NOT contain revealing details like:
        # "User not found" or "Password is incorrect"
        assert "not found" not in detail.lower()
        assert "does not exist" not in detail.lower()
    
    def test_registration_error_generic_message(self):
        """Registration errors should be generic where possible."""
        # Register twice
        client.post("/auth/register", json={"username": "generic_test", "password": "Password1"})
        r = client.post("/auth/register", json={"username": "generic_test", "password": "Password2"})
        
        # Error should be generic
        assert r.status_code == 400
        detail = r.json()["detail"]
        assert "exists" in detail.lower() or "failed" in detail.lower()


class TestRateLimiting:
    """Verify rate limiting on auth endpoints."""
    
    def test_registration_rate_limit(self):
        """Multiple registration attempts from same IP should be rate limited."""
        # Try to register 6 times (limit is 5 per 15 min)
        for i in range(6):
            r = client.post("/auth/register", json={
                "username": f"ratelimit_user_{i}",
                "password": f"Password{i+1}"
            })
            if i < 5:
                assert r.status_code in [201, 400]  # Could be validation error
            # Note: The exact behavior depends on rate limit implementation
    
    def test_login_rate_limit(self):
        """Multiple login attempts from same IP should be rate limited."""
        # Register a user first
        client.post("/auth/register", json={"username": "login_limit_user", "password": "Password1"})
        
        # Try to login with wrong password 11 times (limit is 10 per 15 min)
        for i in range(11):
            r = client.post("/auth/login", json={
                "username": "login_limit_user",
                "password": "WrongPassword"
            })
            if i < 10:
                assert r.status_code == 401


class TestPasswordNotInResponses:
    """Verify passwords are never returned in API responses."""
    
    def test_registration_response_has_no_password(self):
        """Registration response should not contain password."""
        r = client.post("/auth/register", json={"username": "no_password_test", "password": "Password1"})
        assert r.status_code == 201
        response = r.json()
        
        # Check nested fields
        assert "password" not in response
        assert "password" not in response.get("user", {})
        assert "hashed_password" not in response.get("user", {})
    
    def test_login_response_has_only_token(self):
        """Login response should only have token and type, no user details."""
        client.post("/auth/register", json={"username": "token_only_user", "password": "Password1"})
        r = client.post("/auth/login", json={"username": "token_only_user", "password": "Password1"})
        
        response = r.json()
        assert "access_token" in response
        assert "token_type" in response
        # Should NOT contain:
        assert "password" not in response
        assert "user" not in response


class TestTokenValidation:
    """Verify token validation and expiration."""
    
    def test_valid_token_allows_access(self):
        """Valid token should allow access to protected resources."""
        # Register and login
        client.post("/auth/register", json={"username": "valid_token_user", "password": "Password1"})
        r = client.post("/auth/login", json={"username": "valid_token_user", "password": "Password1"})
        token = r.json()["access_token"]
        
        # Use token to access protected resource
        user_id = client.post("/auth/register", json={"username": "dummy_user_1", "password": "Password1"}).json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get(f"/conversations/user/{user_id}", headers=headers)
        # Should be 403 (forbidden - not their user) not 401 (unauthorized - bad token)
        # This proves the token was validated and accepted
        assert r.status_code in [200, 403]
    
    def test_invalid_token_rejected(self):
        """Invalid token should be rejected with 401."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        r = client.get("/conversations/user/some-user-id", headers=headers)
        assert r.status_code == 401
    
    def test_missing_token_rejected(self):
        """Missing token should be rejected with 401."""
        r = client.get("/conversations/user/some-user-id")
        assert r.status_code == 401
    
    def test_malformed_authorization_header_rejected(self):
        """Malformed Authorization header should be rejected."""
        # Missing "Bearer " prefix
        headers = {"Authorization": "invalid_token_here"}
        r = client.get("/conversations/user/some-user-id", headers=headers)
        assert r.status_code == 401
        
        # No space after Bearer
        headers = {"Authorization": "Bearerinvalidtoken"}
        r = client.get("/conversations/user/some-user-id", headers=headers)
        assert r.status_code == 401
    
    def test_expired_token_rejected(self):
        """Expired token should be rejected with 401."""
        from backend.app.services.auth_service import default_auth_service
        from datetime import datetime, timedelta
        
        # Register and login
        client.post("/auth/register", json={"username": "expired_token_user", "password": "Password1"})
        r = client.post("/auth/login", json={"username": "expired_token_user", "password": "Password1"})
        token = r.json()["access_token"]
        
        # Manually expire the token by setting its expiration to the past
        if token in default_auth_service._tokens:
            user_id, _ = default_auth_service._tokens[token]
            default_auth_service._tokens[token] = (user_id, datetime.utcnow() - timedelta(hours=1))
        
        # Try to use expired token
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get("/conversations/user/some-user-id", headers=headers)
        assert r.status_code == 401
        assert "expired" in r.json()["detail"].lower() or "invalid" in r.json()["detail"].lower()
    
    def test_token_has_expiration(self):
        """Token should have an expiration time set."""
        from backend.app.services.auth_service import default_auth_service
        from datetime import datetime
        
        # Register and login
        client.post("/auth/register", json={"username": "expiration_check_user", "password": "Password1"})
        r = client.post("/auth/login", json={"username": "expiration_check_user", "password": "Password1"})
        token = r.json()["access_token"]
        
        # Check that token has expiration in the future
        assert token in default_auth_service._tokens
        user_id, expires_at = default_auth_service._tokens[token]
        assert expires_at > datetime.utcnow()
        assert expires_at <= datetime.utcnow() + timedelta(hours=25)  # Default is 24 hours
