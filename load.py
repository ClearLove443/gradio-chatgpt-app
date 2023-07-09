import gradio as gr

chatbot = gr.Interface.load("models/microsoft/DialoGPT-medium",
                            api_key="")
chatbot.launch()
