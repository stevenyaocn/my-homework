from week7.sales_chatbot.interfaces.gradio_ui import GradioUI

if __name__ == "__main__":
    ui = GradioUI()
    app = ui.create_interface()

    app.launch(
        # server_name="0.0.0.0",
        server_port=5000,
        share=False
    )