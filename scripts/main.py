import base64
import gradio as gr
import hashlib
import json
import numpy as np
import os
import re
import requests  # Replace urllib.request with requests
import subprocess
import time

from io import BytesIO
from modules import generation_parameters_copypaste as parameters_copypaste
from modules import script_callbacks
from modules import shared
from PIL import Image
from pathlib import Path
from typing import Any

CIVITAI_MODEL_INFO_BY_HASH_URL = 'https://civitai.com/api/v1/model-versions/by-hash/'
CIVITAI_MODEL_PAGE_BY_ID_URL = 'https://civitai.com/models/'
CIVITAI_MODEL_DESCRIPTION_TAG = 'mantine-TypographyStylesProvider-root mantine-dfvxn9'
CIVITAI_MODEL_DESCRIPTION_PRESET_PREFIX = '###ModelPresets###'

def get_model_info_file_path(model_hash):
    current_directory = os.path.dirname(__file__)
    return os.path.join(current_directory, "model presets",f"{model_hash}.json")

def empty_model_info():
    return  {
                "url": "",
                "default_preset" : "default",
                "trigger_words": [],
                "presets": {"default": ""}
            }

def initialize_model_info_file(model_hash):
    model_info_file_path = get_model_info_file_path(model_hash)
    
    os.makedirs(os.path.dirname(model_info_file_path), exist_ok=True)
    
    if not os.path.exists(model_info_file_path):
        with open(model_info_file_path, "w") as file:
            empty_model_info_file = empty_model_info()

            json.dump(empty_model_info_file, file, indent=4)
    return model_info_file_path

def get_model_hash_and_info_from_model_filename(model_filename, initializeIfMissing = True):    
    short_hash = get_short_hash_from_filename(model_filename)
    if initializeIfMissing:
        model_info_file_path = initialize_model_info_file(short_hash)
    else:
        model_info_file_path = get_model_info_file_path(short_hash)
    
    try:
        with open(model_info_file_path, "r") as file:
            return short_hash, json.load(file)
    except FileNotFoundError:
        return short_hash, empty_model_info()
        
def get_model_hash_and_info_from_current_model(initializeIfMissing = True):
    return get_model_hash_and_info_from_model_filename(current_model_filename(), initializeIfMissing)

def get_model_info_from_model_hash(model_hash):     
    model_info_file_path = initialize_model_info_file(model_hash)
    with open(model_info_file_path, "r") as file:
        return json.load(file)

def save_model_info(short_hash, model_info):
    model_info_file_path = initialize_model_info_file(short_hash)
    with open(model_info_file_path, "w") as file:
        json.dump(model_info, file, indent=4)

def get_model_url_trigger_words_and_first_image_url_from_hash(short_hash):
    response = requests.get(f"{CIVITAI_MODEL_INFO_BY_HASH_URL}{short_hash}")
    data = response.json()

    # The get() method returns None if the key does not exist.
    trigger_words = data.get("trainedWords", [])
    images = data.get("images", [{}])
    model_url = f'{CIVITAI_MODEL_PAGE_BY_ID_URL}{data.get("modelId", "")}'

    first_image_url = images[0].get("url", None)

    return model_url, trigger_words, first_image_url

def get_short_hash_from_filename(filename):
    match = re.search(r'\[(.*?)\]', filename)
    if match:
        return match.group(1)
    filename = remove_hash_and_whitespace(filename)
    os.path.join("models", "Stable-diffusion", filename)
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()[:10]

def remove_hash_and_whitespace(s, remove_extension = False):
    # Remove any whitespace and hash surrounded by square brackets
    cleaned_string = re.sub(r'\s*\[.*?\]', '', s)
    
    # If remove_extension is set to True, remove the file extension as well
    if remove_extension:
        cleaned_string = re.sub(r'\.[^.]*$', '', cleaned_string)
    
    return cleaned_string

def get_model_presets_from_civitai_model_url(model_url):   
    headers = {'User-Agent': 'Mozilla/5.0'}
    model_page_html = requests.get(model_url, headers=headers).text

    data_start_index = model_page_html.find(CIVITAI_MODEL_DESCRIPTION_TAG)
    if data_start_index == -1:
        return None

    model_page_html = model_page_html[data_start_index + len(CIVITAI_MODEL_DESCRIPTION_TAG):]
    
    preset_start_index = model_page_html.find(CIVITAI_MODEL_DESCRIPTION_PRESET_PREFIX)
    if preset_start_index == -1:
        return None
    else:
        preset_start_index += len(CIVITAI_MODEL_DESCRIPTION_PRESET_PREFIX)
    
    opened_braces = 0
    json_start_index = -1
    for i in range(preset_start_index, len(model_page_html)):
        if model_page_html[i] == '{':
            if opened_braces == 0:
                json_start_index = i
            opened_braces += 1
        elif model_page_html[i] == '}':
            opened_braces -= 1
            if opened_braces == 0:
                try:
                    possible_json_str = model_page_html[json_start_index:i + 1]
                    json_obj = json.loads(possible_json_str)
                    return json_obj
                except json.JSONDecodeError:
                    pass
    return None




def get_thumbnail_path(modelName):
    return os.path.join("models", "Stable-diffusion", modelName + ".png")

def download_thumbnail(image_url, modelName):
    thumbnail_path = get_thumbnail_path(modelName)
    if os.path.exists(thumbnail_path):
        return
    response = requests.get(image_url)
    response.raise_for_status()

    # Open the image using PIL and create a thumbnail with max size 300x300
    img = Image.open(BytesIO(response.content))
    img.thumbnail((300, 300))
    
    # Save the thumbnail
    img.save(thumbnail_path)
    
def save_thumbnail_from_np_array(current_model, image):
    if image is None:
        print("no image in np array")
        return
        
    current_model = remove_hash_and_whitespace(current_model, True)
    
    # Open the image and create a thumbnail with max size 300x300
    image = Image.fromarray(np.uint8(image))
    image.thumbnail((300, 300))
    
    # Save the thumbnail
    thumbnail_path = get_thumbnail_path(current_model)
    image.save(thumbnail_path)
    
def get_model_thumbnail(image_url, short_hash, local, modelName):
    thumbnail_path = get_thumbnail_path(modelName)

    if not local or not os.path.exists(thumbnail_path):
        if image_url:
            download_thumbnail(image_url, modelName)

    if os.path.exists(thumbnail_path):
        return thumbnail_path
    else:
        print("no local model thumbnail found")
        return None

def update_default_preset(model_info):
    default_preset_name = model_info.get("default_preset", "default") or "default"
    presets = model_info.get("presets", {})

    if default_preset_name not in presets:
        if presets:
            first_preset_name = next(iter(presets.keys()))
            model_info["default_preset"] = first_preset_name
        else:
            model_info["default_preset"] = "default"
            model_info["presets"]["default"] = ""

    return model_info

def get_default_preset(model_info):
    default_preset_name = model_info.get("default_preset", "default")
    
    if default_preset_name == "" or default_preset_name is None:
        default_preset_name = "default"

    presets = model_info.get("presets", {})

    if default_preset_name in presets:
        return default_preset_name, presets[default_preset_name]
    elif len(presets) > 0:
        first_preset_name, first_preset_value = next(iter(presets.items()))
        return first_preset_name, first_preset_value
    else:
        return "default", ""

def validate_model_info(model_info):
    required_keys = ["url", "default_preset", "trigger_words", "presets"]
    return model_info and all(key in model_info for key in required_keys)

def download_model_info():
    model_filename = current_model_filename()
    short_hash, model_info = get_model_hash_and_info_from_model_filename(model_filename)
    model_url, trigger_words, first_image_url = get_model_url_trigger_words_and_first_image_url_from_hash(short_hash)
    full_presets_file =  get_model_presets_from_civitai_model_url(model_url)
    
    
    if first_image_url:
        model_thumbnail = get_model_thumbnail(first_image_url, short_hash, False, remove_hash_and_whitespace(model_filename, True))
    
    model_info = get_model_info_from_model_hash(short_hash)   
    
    global triggerWordChoices
    triggerWordChoices = trigger_words
    if validate_model_info(full_presets_file):
        model_info = full_presets_file
        triggerWordChoices = trigger_words = model_info.get("trigger_words", [])
        save_model_info(short_hash, model_info)
    else:            
        set_trigger_words(model_filename)
        set_model_url(model_filename, model_url) 
           
    preset_name, current_generation_data = get_default_preset(model_info)        
    presets = model_info.get("presets",{})
        
    return model_filename, model_url, model_thumbnail, model_generation_data_update_return(current_generation_data, preset_name), gr.CheckboxGroup.update(choices = trigger_words), gr.Dropdown.update(choices = list(presets.keys()), value = preset_name), preset_name, short_hash

def model_generation_data_update_return(current_generation_data, preset_name):
    model_hash, model_info = get_model_hash_and_info_from_current_model()
    default_preset_name, preset_original_data = get_default_preset(model_info)
    default = default_preset_name == preset_name
    return gr.Textbox.update(label = model_generation_data_label_text(default), value = current_generation_data)

def current_model_filename():
    return shared.opts.data.get('sd_model_checkpoint', 'Not found')

def retrieve_model_info_from_disk(current_generation_data):
    model_filename = current_model_filename()

    short_hash, model_info = get_model_hash_and_info_from_model_filename(model_filename, False)

    if model_info:
        model_url = model_info['url']

        if model_url:
            model_thumbnail = get_model_thumbnail("", short_hash, True, remove_hash_and_whitespace(model_filename, True))
            
            preset_name, current_generation_data = get_default_preset(model_info)
            presets = model_info.setdefault('presets', {"default": ""})
            trigger_words = model_info.setdefault('trigger_words', [])
                
            global triggerWordChoices
            triggerWordChoices = trigger_words
            return model_filename, model_url, model_thumbnail, model_generation_data_update_return(current_generation_data, preset_name), gr.CheckboxGroup.update(choices = trigger_words), gr.Dropdown.update(choices = list(presets.keys()), value = preset_name), preset_name, short_hash
        else:
            presets = model_info.setdefault('presets', {"default": ""})
            return download_model_info()

    else:
        # Handle the case when the model is not found in the data structure
        presets = model_info.setdefault('presets', {"default": ""})
        return download_model_info()

def set_model_info(model_filename, label, info):
    short_hash, model_info = get_model_hash_and_info_from_model_filename(model_filename)    
    
    model_info[label] = info
    
    save_model_info(short_hash, model_info)
    return f"{label} updated."

def set_model_url(current_model, model_url):
    return set_model_info(current_model, 'url', model_url)
    
def show_model_url(model_url):
    iframe_html = f'<iframe src="{model_url}" width="100%" height="1080" frameborder="0"></iframe>'
    return iframe_html

def set_trigger_words(current_model):
    global triggerWordChoices
    return set_model_info(current_model, 'trigger_words', triggerWordChoices)

def bind_buttons(buttons, source_text_component):
    for tabname, button in buttons.items():
        parameters_copypaste.register_paste_params_button(parameters_copypaste.ParamBinding(paste_button=button, tabname=tabname, source_text_component=source_text_component, source_image_component=None, source_tabname=None))

def getCheckedBoxesFromPrompt(prompt):
    global triggerWordChoices
    checked_boxes = [choice for choice in triggerWordChoices if choice in prompt]
    return checked_boxes

def adjustPromptToCheckBox(checkBoxChange: gr.SelectData, prompt):
    new_prompt = prompt    
    if checkBoxChange.selected and checkBoxChange.value not in new_prompt:
        new_prompt = f"{checkBoxChange.value} {new_prompt}"
    elif not checkBoxChange.selected and checkBoxChange.value in new_prompt:
        new_prompt = re.sub(f"{checkBoxChange.value} ?", "", new_prompt).strip()
    return new_prompt

def compare_lists(list_a, list_b):
    # Remove duplicates from list_a
    list_a_no_duplicates = list(set(list_a))

    # Check if the lengths of the lists are the same
    if len(list_a_no_duplicates) != len(list_b):
        return False

    # Sort the lists
    list_a_no_duplicates.sort()
    list_b.sort()

    # Check if the lists contain the same elements
    for i in range(len(list_a_no_duplicates)):
        if list_a_no_duplicates[i] != list_b[i]:
            return False

    return True

def model_generation_data_label_text(default=False):
    return f"Model Generation Data{' (default preset)' if default else ''}"
  
def handle_text_change(prompt):
    checked_boxes = getCheckedBoxesFromPrompt(prompt)
    return checked_boxes

def handle_checkbox_change(checkBoxChange: gr.SelectData, prompt):
    new_prompt = adjustPromptToCheckBox(checkBoxChange, prompt)
    return new_prompt

def save_preset(preset_name_textbox_value, model_generation_data):
    short_hash, model_info = get_model_hash_and_info_from_current_model()
    model_info['presets'][preset_name_textbox_value] = model_generation_data
    save_model_info(short_hash, model_info)
    return gr.Dropdown.update(choices = list(model_info['presets'].keys()), value = preset_name_textbox_value),  f"{preset_name_textbox_value} saved", model_generation_data_update_return(model_generation_data, preset_name_textbox_value)

def rename_preset(preset_dropdown_value, preset_name_textbox_value, model_generation_data):
    short_hash, model_info = get_model_hash_and_info_from_current_model()
    new_current_preset_name = preset_name_textbox_value

    # Check if the preset name is already the same
    if preset_dropdown_value == preset_name_textbox_value:
        message = f"Preset already named {preset_name_textbox_value}"        
    # Check if the new preset name already exists
    elif preset_name_textbox_value in model_info['presets'].keys():
        message = f"Preset name {preset_name_textbox_value} already exists"
        new_current_preset_name = preset_dropdown_value
    else:
        # Rename the preset by creating a new key with the same value and removing the old one
        model_info['presets'][preset_name_textbox_value] = model_info['presets'][preset_dropdown_value]
        del model_info['presets'][preset_dropdown_value]
        if model_info['default_preset'] == preset_dropdown_value:
            model_info['default_preset'] = preset_name_textbox_value
        message = f"Preset {preset_dropdown_value} renamed to {preset_name_textbox_value}"

    save_model_info(short_hash, model_info)
    return gr.Dropdown.update(choices = list(model_info['presets'].keys()), value = new_current_preset_name), message, model_generation_data_update_return(model_generation_data, preset_dropdown_value)

def delete_preset(preset_dropdown_value, model_generation_data):   
    short_hash, model_info = get_model_hash_and_info_from_current_model()
    del model_info['presets'][preset_dropdown_value]
    model_info = update_default_preset(model_info)
    save_model_info(short_hash, model_info)
    new_current_preset_name, model_generation_data = get_default_preset(model_info)
    formatted_dict = json.dumps(model_info, indent=4)
    return gr.Dropdown.update(choices = list(model_info['presets'].keys()), value = new_current_preset_name), new_current_preset_name, f"Preset {preset_dropdown_value} deleted", model_generation_data_update_return(model_generation_data, new_current_preset_name)

def update_current_preset(preset_dropdown_value):
    model_hash, model_info = get_model_hash_and_info_from_current_model()
    new_model_generation_data = model_info['presets'].get(preset_dropdown_value,"")
    return preset_dropdown_value, model_generation_data_update_return(new_model_generation_data, preset_dropdown_value)

def set_default_preset(preset_dropdown_value, model_generation_data):
    short_hash, model_info = get_model_hash_and_info_from_current_model()
    model_info['default_preset'] = preset_dropdown_value
    save_model_info(short_hash, model_info)
    return f"{preset_dropdown_value} set to default", model_generation_data_update_return(model_generation_data, preset_dropdown_value)

def reveal_presets_file_in_explorer(model_hash):
    if not model_hash:
        return "no presets file for this model or no model retrieved"
        
    model_info_file_path = initialize_model_info_file(model_hash)

    explorer_path = os.path.join(os.environ["WINDIR"], "explorer.exe")
    explorer_command = f'"{explorer_path}" /e,/select,"{model_info_file_path}"'
    subprocess.run(explorer_command, shell=True)
    
def get_civitai_preset_sharing_text():
    short_hash, model_info = get_model_hash_and_info_from_current_model()
    return f"###ModelPresets###\n{json.dumps(model_info)}"

def get_template_generation_data(includeExamplePrompt):
    prompt = "{Your Prompt Here}\n" if includeExamplePrompt else ""
    return (prompt + """Negative prompt:
Steps: 20, Sampler: Euler a, CFG scale: 7, Size: 512x512, Clip skip: 1
""")

def append_template_generation_info(generation_data):
    return generation_data + get_template_generation_data(generation_data == "")

triggerWordChoices = None
def on_ui_tabs():
    with gr.Blocks() as custom_tab_interface:
        current_model_textbox = gr.Textbox(interactive=False, label="Current Model:", visible=False) 
        with gr.Row():
            with gr.Column(scale = 1):
                pass  

            with gr.Column(min_width=1000, scale = 3):
                
                with gr.Column():
                    gr.Markdown('<center><h3>Model Info</h2></center>')
                    with gr.Box():
                        with gr.Row():
                            with gr.Column(min_width=300, scale = 1):
                                image_input = gr.Image(source="upload", width=300, height=300)
                            with gr.Column(scale = 4):
                                with gr.Row():
                                    with gr.Column(scale = 4):
                                        model_url_textbox = gr.Textbox(label="Model URL", scale = 40)
                                    with gr.Column(min_width=100, scale = 0.1):
                                        model_hash_textbox = gr.Textbox(label="Model Hash", interactive = False)  
                                    show_presets_in_explorer_button = gr.Button("Reveal Presets File")
                                with gr.Row():
                                    retrieve_button = gr.Button("Retrieve Local Model Info", elem_id = "retrieve_model_info_button")
                                    download_button = gr.Button("Download and Overwrite Model Info")
                                with gr.Row():
                                    open_model_page_button = gr.Button("Open Model Page")
                                    set_model_url_button = gr.Button("Set Model URL") 

                                                  
                with gr.Row():
                    with gr.Column():                    
                        gr.Markdown('<center><h3>Generation Data</h2></center>')
                        with gr.Box():
                            with gr.Row():
                                with gr.Column(scale = 6): 
                                    model_generation_data = gr.Textbox(label = model_generation_data_label_text(), value = "", lines = 3, elem_id = "def_model_gen_data_textbox").style(show_copy_button=True)       
                                append_template_button = gr.Button("Append Template")
                                
                            triggerWords = gr.CheckboxGroup([], multiselect=True, label="Trigger Words", interactive = True).style(container=True, item_container=True)
                            with gr.Row():
                                gr.Markdown('<div style="height: 10px;"></div>')
                            with gr.Row():
                                buttons = parameters_copypaste.create_buttons(["txt2img","img2img", "inpaint"])  
                    
                    with gr.Column():                  
                        gr.Markdown('<center><h3>Model Presets</h2></center>')
                        with gr.Box():
                            with gr.Row():
                                with gr.Column():
                                    preset_dropdown = gr.Dropdown(choices=[], label="Presets") 
                                    preset_name_textbox = gr.Textbox(label="Current Preset Name")
                                
                                with gr.Box():
                                    with gr.Row():
                                        gr.Markdown('<div style="height: 10px;"></div>')
                                    with gr.Row():
                                        save_preset_button = gr.Button("Save Preset")
                                        set_preset_button = gr.Button("Set Preset as Default") 
                                        delete_preset_button = gr.Button("Delete Preset")   
                                        rename_preset_button = gr.Button("Rename Preset")
                                    with gr.Row():
                                        gr.Markdown('<div style="height: 10px;"></div>')
                         
                with gr.Row():
                    with gr.Column(scale = 4):
                        output_textbox = gr.Textbox(interactive=False, label="Output").style(show_copy_button=True)
                    with gr.Column(scale = 1):
                        get_civitai_preset_text = gr.Button("Get preset sharing text for Civitai description")
                    with gr.Column():
                        pass
              
            with gr.Column(scale = 1):
                pass
            
        

        # Update the preset name textbox when a preset is selected in the dropdown
        preset_dropdown.change(fn=update_current_preset, inputs=[preset_dropdown], outputs=[preset_name_textbox, model_generation_data], show_progress=False)
                        
        model_url_output = gr.HTML(label="model page", height=800)  
   
        image_input.change(fn=save_thumbnail_from_np_array, inputs=[current_model_textbox, image_input])
        triggerWords.select(fn=handle_checkbox_change, inputs =[model_generation_data], outputs=[model_generation_data], show_progress=False)
        triggerWords.loading_html = ""            
                   
        open_model_page_button.click(fn=show_model_url, inputs=[model_url_textbox], outputs=[model_url_output])  
        set_model_url_button.click(fn=set_model_url, inputs=[current_model_textbox, model_url_textbox], outputs=[output_textbox]) 
        append_template_button.click(fn=append_template_generation_info, inputs=[model_generation_data], outputs=[model_generation_data]) 
        
        download_button.click(fn=download_model_info, inputs=[], outputs=[current_model_textbox, model_url_textbox, image_input, model_generation_data, triggerWords, preset_dropdown, preset_name_textbox, model_hash_textbox])
        retrieve_button.click(fn=retrieve_model_info_from_disk, inputs=[], outputs=[current_model_textbox, model_url_textbox, image_input, model_generation_data, triggerWords, preset_dropdown, preset_name_textbox, model_hash_textbox])
        show_presets_in_explorer_button.click(fn = reveal_presets_file_in_explorer, inputs = [model_hash_textbox], outputs = [output_textbox])
                
        set_preset_button.click(fn=set_default_preset, inputs=[preset_dropdown, model_generation_data], outputs=[output_textbox, model_generation_data ])                
        save_preset_button.click(fn=save_preset, inputs=[preset_name_textbox, model_generation_data], outputs=[preset_dropdown, output_textbox, model_generation_data])            
        rename_preset_button.click(fn=rename_preset, inputs=[preset_dropdown, preset_name_textbox, model_generation_data], outputs=[preset_dropdown, output_textbox, model_generation_data])
        delete_preset_button.click(fn=delete_preset, inputs=[preset_dropdown, model_generation_data], outputs=[preset_dropdown, preset_name_textbox, output_textbox, model_generation_data])         
        
        get_civitai_preset_text.click(fn=get_civitai_preset_sharing_text, inputs=[], outputs=[output_textbox])         
        
        model_generation_data.change(fn = handle_text_change, inputs = [model_generation_data], outputs = [triggerWords], show_progress=False)
        
        bind_buttons(buttons, model_generation_data)       
        

    return [(custom_tab_interface, "Model Preset Manager", "model preset manager")]


script_callbacks.on_ui_tabs(on_ui_tabs)

