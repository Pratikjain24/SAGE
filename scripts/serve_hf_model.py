#!/usr/bin/env python3
"""High-Performance OpenAI-Compatible Server for Kaggle & Multi-GPU Environments.

Serves Qwen2.5-Coder-7B-Instruct (and any Hugging Face causal LM) using native
PyTorch & Transformers over FastAPI/Uvicorn on port 8001.

Key Advantages over vLLM:
1. Zero compilation or C-extension ABI conflicts on Python 3.13 / CUDA 13.
2. Zero Dynamo / Triton dependencies; runs in standard PyTorch eager mode.
3. Automatically shards across multi-GPU (e.g. 2x Tesla T4) via accelerate device_map="auto".
4. Implements the exact /v1/models and /v1/chat/completions API required by SAGE.
"""

from __future__ import annotations
import argparse
import os
import sys
import time
import uuid
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="SAGE Transformers Model Server", version="1.0.0")

# Global state
MODEL = None
TOKENIZER = None
MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"
IS_MOCK = False
GEN_LOCK: Optional[Any] = None


@app.on_event("startup")
async def startup_event():
    global GEN_LOCK
    import asyncio
    GEN_LOCK = asyncio.Lock()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.2
    top_p: Optional[float] = 0.95
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False


@app.get("/health")
@app.get("/v1/health")
def health():
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "ready": IS_MOCK or (MODEL is not None and TOKENIZER is not None),
    }


@app.get("/models")
@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "sage-transformers",
            }
        ],
    }


@app.post("/chat/completions")
@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    global MODEL, TOKENIZER, MODEL_NAME, IS_MOCK

    if not IS_MOCK and (MODEL is None or TOKENIZER is None):
        raise HTTPException(status_code=503, detail="Model weights are still initializing.")

    # Offline mock mode for testing
    if IS_MOCK:
        mock_code = "```python\ndef solve():\n    return 42\n```"
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": MODEL_NAME,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": mock_code},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 30,
                "completion_tokens": 15,
                "total_tokens": 45,
            },
        }

    import asyncio, anyio
    import torch

    # Prepare message dicts
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    # Apply tokenizer chat template (official Jinja template for Qwen/ChatML)
    try:
        prompt_text = TOKENIZER.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        # Fallback simple ChatML formatting if template fails
        prompt_text = ""
        for m in messages:
            prompt_text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
        prompt_text += "<|im_start|>assistant\n"

    # Tokenize input
    inputs = TOKENIZER(prompt_text, return_tensors="pt")
    input_ids = inputs.input_ids.to(MODEL.device)
    prompt_tokens = input_ids.shape[1]

    # Stop tokens: include standard EOS, <|im_end|>, and <|endoftext|>
    eos_ids = [TOKENIZER.eos_token_id]
    for sp_tok in ["<|im_end|>", "<|endoftext|>"]:
        try:
            tid = TOKENIZER.convert_tokens_to_ids(sp_tok)
            if isinstance(tid, int) and tid not in eos_ids:
                eos_ids.append(tid)
        except Exception:
            pass

    # Cap max new tokens: coding tasks in SAGE need 150-600 tokens max
    # Capping prevents runaway generation and 5-minute per-task stalls
    temp = req.temperature if req.temperature is not None else 0.2
    top_p = req.top_p if req.top_p is not None else 0.95
    max_new_tokens = min(req.max_tokens or 1024, 1024)

    gen_kwargs: Dict[str, Any] = {
        "max_new_tokens": max_new_tokens,
        "pad_token_id": TOKENIZER.pad_token_id or eos_ids[0],
        "eos_token_id": eos_ids if len(eos_ids) > 1 else eos_ids[0],
        "use_cache": True,
    }
    if temp > 0.01:
        gen_kwargs["do_sample"] = True
        gen_kwargs["temperature"] = temp
        gen_kwargs["top_p"] = top_p
    else:
        gen_kwargs["do_sample"] = False

    def _sync_generate():
        with torch.inference_mode():
            return MODEL.generate(input_ids, **gen_kwargs)

    # Serialize generation to prevent GPU memory thrashing and thread lock contention
    lock = GEN_LOCK or asyncio.Lock()
    async with lock:
        output_ids = await anyio.to_thread.run_sync(_sync_generate)

    # Slice out generated completion tokens
    completion_ids = output_ids[0][prompt_tokens:]
    completion_tokens = len(completion_ids)
    generated_text = TOKENIZER.decode(completion_ids, skip_special_tokens=True)

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": MODEL_NAME,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": generated_text,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def parse_args():
    parser = argparse.ArgumentParser(description="SAGE Transformers OpenAI-Compatible Model Server")
    parser.add_argument("--model", type=str, default=MODEL_NAME, help="Hugging Face model ID or path")
    parser.add_argument("--revision", type=str, default="c03e6d358207e414f1eca0bb1891e29f1db0e242", help="Pinned commit revision")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address to bind")
    parser.add_argument("--port", type=int, default=8001, help="Port to listen on (default: 8001)")
    parser.add_argument("--dtype", type=str, default="float16", choices=["float16", "bfloat16", "float32", "auto"])
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without loading real model weights")
    return parser.parse_args()


def main():
    global MODEL, TOKENIZER, MODEL_NAME, IS_MOCK

    args = parse_args()
    MODEL_NAME = args.model
    IS_MOCK = args.mock

    if IS_MOCK:
        print(f"[MOCK] Running in mock server mode for {MODEL_NAME} on port {args.port}...")
    else:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        num_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 0
        print("=" * 65)
        print(f"SAGE Transformers Model Server")
        print(f"  Model    : {MODEL_NAME}")
        print(f"  Revision : {args.revision}")
        print(f"  GPUs     : {num_gpus} detected ({[torch.cuda.get_device_name(i) for i in range(num_gpus)]})")
        print(f"  Port     : {args.port}")
        print("=" * 65)

        print(f"[1/2] Loading tokenizer for {MODEL_NAME}...")
        TOKENIZER = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            revision=args.revision,
            trust_remote_code=True,
        )
        if TOKENIZER.pad_token_id is None:
            TOKENIZER.pad_token_id = TOKENIZER.eos_token_id

        dtype_map = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
            "auto": "auto",
        }
        torch_dtype = dtype_map.get(args.dtype, torch.float16)

        device_map = "auto" if num_gpus > 0 else "cpu"
        print(f"[2/2] Loading weights (dtype={args.dtype}, device_map={device_map})...")
        MODEL = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            revision=args.revision,
            torch_dtype=torch_dtype,
            device_map=device_map,
            trust_remote_code=True,
        )
        MODEL.eval()

        if hasattr(MODEL, "hf_device_map"):
            print(f"✓ Model sharded across devices: {MODEL.hf_device_map}")
        print(f"✓ Model loaded successfully. Server starting on http://{args.host}:{args.port}/v1 ...")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()

