"""Qwen Coding Plan subscription model validation script."""

import asyncio
import os
import sys
from pathlib import Path
from openai import AsyncOpenAI

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Qwen Coding Plan subscription models to test
CODING_PLAN_MODELS = [
    "qwen-coder-plus",      # Main coding model
    "qwen-max",             # Most powerful model
    "qwen-coder-instruct",  # Instruction-based coding model
    "qwen-coder-480b",      # 480B parameter coding model
    "qwen-plus",            # General purpose model
    "qwen-turbo",           # Fast/low-cost model
    "qwen-long",            # Long context model
]

QWEN_API_KEY = "sk-2284c837ff0e4166a225e3b5e8ccbb47"


async def test_model(model_name: str, client: AsyncOpenAI):
    """Test a single Qwen model."""
    test_prompt = "Please describe your main purpose in one sentence (max 20 words)."

    try:
        print(f"\n{'='*60}")
        print(f"Testing Model: {model_name}")
        print(f"{'='*60}")

        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": test_prompt}
            ],
            max_tokens=100,
        )

        result = response.choices[0].message.content
        print(f"[OK] Success! Response: {result}")
        print(f"   Model used: {response.model}")
        print(f"   Usage: input={response.usage.prompt_tokens}, output={response.usage.completion_tokens}, total={response.usage.total_tokens}")

        return True, result, response.usage

    except Exception as e:
        print(f"[FAIL] Failed! Error: {str(e)}")
        return False, str(e), None


async def main():
    """Main test function."""
    print("="*60)
    print("Qwen Coding Plan Subscription Model Validation")
    print("="*60)
    print(f"API Key: {QWEN_API_KEY[:20]}...{QWEN_API_KEY[-10:]}")
    print(f"Models to test: {len(CODING_PLAN_MODELS)}")
    print()

    # Initialize Qwen client
    client = AsyncOpenAI(
        api_key=QWEN_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    results = {}

    for model in CODING_PLAN_MODELS:
        success, result, usage = await test_model(model, client)
        results[model] = {
            "success": success,
            "result": result,
            "usage": usage
        }
        # Small delay between requests to avoid rate limiting
        await asyncio.sleep(0.5)

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    successful = [m for m, r in results.items() if r["success"]]
    failed = [m for m, r in results.items() if not r["success"]]

    print(f"\n[OK] Successful ({len(successful)}/{len(CODING_PLAN_MODELS)}):")
    for model in successful:
        print(f"   - {model}")

    print(f"\n[FAIL] Failed ({len(failed)}/{len(CODING_PLAN_MODELS)}):")
    for model in failed:
        print(f"   - {model}: {results[model]['result']}")

    # Coding-specific models summary
    coding_models = [m for m in CODING_PLAN_MODELS if "coder" in m]
    print(f"\n[CODE] Coding-specific models status:")
    for model in coding_models:
        status = "[OK] Available" if results[model]["success"] else "[FAIL] Not available"
        print(f"   {model}: {status}")

    # Calculate total tokens used
    total_tokens = sum(r["usage"].total_tokens for r in results.values() if r["usage"] and r["success"])
    print(f"\n[STATS] Total Tokens Used: {total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())