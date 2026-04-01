import gradio as gr
import random

def run():
    areas = [random.randint(20,80) for _ in range(3)]
    return f"Garbage levels: {areas}"

gr.Interface(fn=run, inputs=[], outputs="text").launch()