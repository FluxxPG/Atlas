import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))

from app.api.deps import ApiKeyPrincipal, get_current_user, require_api_scopes


class PlatformGuardTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_user_auth_rejects_api_key_bearer_token(self):
        with self.assertRaises(Exception) as context:
            await get_current_user(authorization="Bearer atlas_demo_machine_key")

        self.assertEqual(getattr(context.exception, "status_code", None), 401)

    async def test_api_scope_dependency_allows_matching_scope(self):
        principal = ApiKeyPrincipal(
            id="key-1",
            organization_id="org-1",
            scopes=["search:read", "company:read"],
            name="Automation",
            key_prefix="atlas_demo",
        )
        dependency = require_api_scopes("search:read")
        result = await dependency(principal)
        self.assertEqual(result.id, "key-1")


if __name__ == "__main__":
    unittest.main()
