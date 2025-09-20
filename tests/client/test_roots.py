import pytest

from fastmcp import Client, Context, FastMCP


@pytest.fixture
def fastmcp_server():
    mcp = FastMCP()

    @mcp.tool
    async def list_roots(context: Context) -> list[str]:
        roots = await context.list_roots()
        return [str(r.uri) for r in roots]

    return mcp


class TestClientRoots:
    @pytest.mark.parametrize("roots", [["x"], ["x", "y"]])
    async def test_invalid_roots(self, fastmcp_server: FastMCP, roots: list[str]):
        """
        Roots must be URIs
        """
        with pytest.raises(ValueError, match="Input should be a valid URL"):
            async with Client(fastmcp_server, roots=roots):
                pass

    @pytest.mark.parametrize("roots", [["file://x/y/z", "file://x/y/z"]])
    async def test_file_roots(self, fastmcp_server: FastMCP, roots: list[str]):
        async with Client(fastmcp_server, roots=roots) as client:
            result = await client.call_tool("list_roots", {})
            assert result.data == [
                "file://x/y/z",
                "file://x/y/z",
            ]

    @pytest.mark.parametrize("roots", [["https://x.com", "custom://protocol/resource"]])
    async def test_non_file_roots(self, fastmcp_server: FastMCP, roots: list[str]):
        """Test that non-file URI schemes are now supported"""
        async with Client(fastmcp_server, roots=roots) as client:
            result = await client.call_tool("list_roots", {})
            # URL normalization: https URLs get trailing slash, custom schemes don't
            assert result.data == [
                "https://x.com/",
                "custom://protocol/resource",
            ]
