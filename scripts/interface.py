import gradio as gr
from modules import scripts


class Script(scripts.Script):
    def title(self):
        return "ModelPresetManager"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def after_component(self, component, **kwargs):
        # Add button to both txt2img and img2img tabs
        if kwargs.get("elem_id") == "extras_tab":
            basic_send_button = gr.Button(
                "Send to Model Preset Manager", elem_id=f"model_preset_manager_button")
            basic_send_button.click(None, [], None,
                                    _js="() => send_generation_info_to_preset_manager('WebUI Resource')")
                                    
    def ui(self, is_img2img):
        return []
