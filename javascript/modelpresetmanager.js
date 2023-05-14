function send_generation_info_to_preset_manager(name = "Embed Resource") {
	const textbox_container = document.getElementById("def_model_gen_data_textbox");
    const textarea_element = textbox_container.querySelector("textarea");
	
	const tab = get_uiCurrentTabContent().id;
	const prompt =	tab === "tab_txt2img"? gradioApp().querySelector("#generation_info_txt2img textarea").value: gradioApp().querySelector("#img2img_prompt textarea").value;
    
	textarea_element.value = prompt;	
	const html_info_txt2img = gradioApp().querySelector("#html_info_txt2img");
	textarea_element.value = html_info_txt2img.innerText;
	
    const input_event = new Event('input', { bubbles: true });
    textarea_element.dispatchEvent(input_event);
	go_to_tab()
}

function go_to_tab(tabname = "Model Preset Manager", tabsId = "tabs") {
	Array.from(
		gradioApp().querySelectorAll(`#${tabsId} > div:first-child button`)
	).forEach((button) => {
		if (button.textContent.trim() === tabname) {
			button.click();
		}
	});
}
