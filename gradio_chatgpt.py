import asyncio
import os
from typing import List, Optional

import async_timeout
import gradio as gr
import httpx
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")


class Message(BaseModel):
    role: str
    content: str


async def make_completion(
    messages: List[Message], nb_retries: int = 3, delay: int = 30
) -> Optional[str]:
    """
    Sends a request to the ChatGPT API to retrieve a response based on a list of previous messages.
    """
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    try:
        async with async_timeout.timeout(delay=delay):
            async with httpx.AsyncClient(headers=header) as aio_client:
                counter = 0
                keep_loop = True
                while keep_loop:
                    logger.debug(f"Chat/Completions Nb Retries : {counter}")
                    try:
                        resp = await aio_client.post(
                            # url = "https://api.openai.com/v1/chat/completions",
                            url=f"{OPENAI_API_BASE}/chat/completions",
                            json={"model": "gpt-3.5-turbo", "messages": messages},
                        )
                        logger.debug(f"Status Code : {resp.status_code}")
                        if resp.status_code == 200:
                            return resp.json()["choices"][0]["message"]["content"]
                        else:
                            logger.warning(resp.content)
                            keep_loop = False
                    except Exception as e:
                        logger.error(e)
                        counter = counter + 1
                        keep_loop = counter < nb_retries
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout {delay} seconds !")
    return None


async def predict(input, history):
    """
    Predict the response of the chatbot and complete a running list of chat history.
    """
    history.append({"role": "user", "content": input})
    response = await make_completion(history)
    history.append({"role": "assistant", "content": response})
    messages = [
        (history[i]["content"], history[i + 1]["content"])
        for i in range(0, len(history) - 1, 2)
    ]
    return messages, history


"""
Gradio Blocks low-level API that allows to create custom web applications (here our chat app)
"""
with gr.Blocks() as demo:
    logger.info("Starting Demo...")
    chatbot = gr.Chatbot(label="WebGPT")
    state = gr.State([])
    with gr.Row():
        txt = gr.Textbox(
            show_label=False, placeholder="Enter text and press enter"
        ).style(container=False)
    txt.submit(predict, [txt, state], [chatbot, state])

demo.launch(server_port=18080, share=True, server_name="0.0.0.0")
