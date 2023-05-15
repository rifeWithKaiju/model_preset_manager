# Model Preset Manager

![ModelPresetManagerScreenshot](https://github.com/rifeWithKaiju/model_preset_manager/assets/111892089/3ae910a2-ae94-48db-ab87-f4312032f3b4)


This extension lets you create, manage, and share presets for models, so you don't have to remember what the best cfg_scale is for your favorite model, or which trigger words to get a cartoony style vs realistic from a particular model, or even just settings that got cool results to make a particular type of image. You can easily apply all of your preset generation data to txt2img and img2img tabs with a simple button press.

It also downloads the thumbnail preview image for your model from Civitai as well as the model's trigger words so you can apply or unapply them as needed. It can store all generation data that is output by txt2img and img2img when you generate such as prompt, negative prompt, cfg_scale, resolution, sampler, clip skip, steps, etc. 

The presets are saved to a small json file, so they will be easy to share for model creators or users. The json format will also make it easy to integrate into websites or other apps or extensions with very little effort.

If you find this useful, please consider leaving me a tip on:<br><br> <a href="https://ko-fi.com/rifewithkaiju" target="_blank" rel="noopener noreferrer">
  <img src="https://i.imgur.com/iFQKhei.png" alt="kofismall">
</a>





<br>

## TL;DR Quick Start

#### Install the extension
Go to the **Extensions** tab in Automatic1111 webui and go to the **Install from URL** tab and paste 
```
https://github.com/rifeWithKaiju/model_preset_manager
```
in **URL for extension's git repository** and click **Install**.  Then go to the **Settings** tab and click **Reload UI**

#### Get your model info
Go to the **Model Preset Manager** tab, and click on **Retrieve Local Model Info**. This will be slow the first time as it searches for the model info on Civitai. The next time you do this it should be near instant.

#### Create a preset
To input preset data you can either:
- Just type a prompt if you don't need anything else
- Click **Append Template** to get basic Generation Data to edit (you can also do this after typing in a prompt)
- Paste in generation data (copied from Civitai for instance)
- If you already generated something with the settings you want, just click **Send to Model Preset Manager** on the tab where you generated the image (e.g. **txt2img** or **img2img**).

#### Save a preset
Set the name you want in the **Current Preset Name** box and click **Save Preset**

#### Use a preset
Choose a preset from the **Presets** dropdown, and click **Send to txt2img** or **Send to img2img**



<br>

<br>

## Full Docs:

### Model Info

![PresetManagerModelInfo](https://github.com/rifeWithKaiju/model_preset_manager/assets/111892089/f748b45c-d48d-4c82-b5c0-928827a8ebbb)

##### Retrieve Local Model Info

Click this to retrieve the model locally. It will automatically attempt to search Civitai if you haven't downloaded it before. The initial download is slow, but retrieving model info is nearly instant.

##### Download and Overwrite Model Info

This will attempt to download model information from Civitai. It attempts to search Civitai for the model. If it finds it, it will download the model thumbnail and a list of trigger words for the model. This will overwrite only these settings if you have already downloaded this info. It won't overwrite your presets. The model thumbnail will also be used in the Checkpoints tab for networks in the txt2img and img2img tabs.

##### Thumbnail Image

This will display the model's thumbnail image. You can manually change this to a different image if you don't like the default one. The image you input will automatically be resized to 300x300.

##### Open Model Page

This will open the model page as a frame at the bottom of this tab for convenience. You can often find information about using the model in the model description. Things like resolution, cfg scale, clip skip, etc to make the best use of the model. The **Copy Generation Data buttons** on Civitai won't work in a frame like this, so open an image page in a new tab if you want to use this to create a preset.

##### Set Model URL

If the download button doesn't find the model URL, or you want to manually specify a URL, simply type it in the Model URL textbox, and press this button. If you press the download button after this, it will use the URL you gave. You can set the URL for models not hosted by Civitai, but it will not be able to automatically download the image or trigger words. [See below for how to manually add trigger words](#how-to-manually-add-trigger-words).

##### Reveal Presets File

This will highlight the presets file in Windows Explorer, so you can easily share your presets online or manually edit them.

<br>

### Generation Data

![PresetManagerGenerationData](https://github.com/rifeWithKaiju/model_preset_manager/assets/111892089/6297380c-02b4-4630-b6f7-599dc5a9277e)

##### Model Generation Data  

This is where you can view and edit the model generation data for a preset. You can send the last generated settings from txt2img or img2img tabs with the "Send to Model Preset Manager" buttons on those tabs. The model data here is in the typical format used to share generation settings online on forums, Civitai's **Copy Generation Data** button, etc, so pasting that into this box is one way to set up a preset. The label for this box will include "(default)" at the end if you're currently on your default preset.  There is a copy button in the top right corner if you want to copy the contents of Model Generation Data.

##### Append Template

Clicking this button will add the most common settings into model generation data (prompt, negative prompt, steps, sampler, CFG scale, size, clip skip: 1). These are already initialized with the default settings, so you can edit the ones you want and either leave the rest or delete them. If you already have a prompt typed in, it will add the template to the prompt. If you don't, it will put some sample text there so you know where to put your prompt.

##### Trigger Words

![modelPresetManagerTriggerWords](https://github.com/rifeWithKaiju/model_preset_manager/assets/111892089/c108cee2-505e-4c55-8299-93c6653089b7)

The trigger words for models are automatically downloaded with the other model info, and you can click these to add or remove them from the current Model Generation Data. If you didn't download your model info, or you just want to add your own trigger words, [see below for how to manually add trigger words](#how-to-manually-add-trigger-words).


##### Send to txt2img, etc

These will apply your preset to the indicated page.

<br>

### Model Presets

![PresetManagerModelPresets](https://github.com/rifeWithKaiju/model_preset_manager/assets/111892089/8abfeb45-6484-4f5f-bda9-90161e9bbc9c)

##### Presets

Your list of presets.

##### Current Preset Name

The name of the current preset. Change the name in here if you want to save a new preset or rename a preset.

##### Save Preset

This will save a preset and automatically overwrite any preset data to the name in "Current Preset Name".

##### Set Preset as Default

This will set a preset as default. This will be the preset selected when you first retrieve your model.

##### Delete Preset

Deletes the currently selected preset.

##### Rename Preset

Renames the currently selected preset to the name in "Current Preset Name".

<br>

### Output

![PresetManagerOutput](https://github.com/rifeWithKaiju/model_preset_manager/assets/111892089/4a11fa62-ffcf-4361-8655-12d9557eaac8)

This just outputs simple info like whether your preset was successfully renamed, etc for some operations.

<br>

## Additional Info

### How to Manually Add Trigger Words

Click the "Reveal Presets File" button near the top of the UI and open this file in a text editor and just edit the line with "trigger_words" with any trigger words you want, separated by commas, like this:

```json
"trigger_words": ["my_trigger_word","another_trigger_word"],
```

You can also separate them on different lines, like this:
```json
"trigger_words": [
    "my_trigger_word",
    "AnotherTriggerWord"
],
```

### How to add a model presets file someone shared online
Simply move the preset file to the folder that opens when you press the "Reveal Presets File" directory or manually save it to `/extensions/model_preset_manager/scripts/model presets.`
