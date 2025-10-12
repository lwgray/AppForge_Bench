import argparse
from typing import Optional
import json
import os

# Provider/env selection helpers
DEFAULT_PROVIDER = os.getenv("MODEL_PROVIDER", "openai").lower()
DEFAULT_MODEL = os.getenv("MODEL_NAME", None)


def _choose_model(provider: str) -> str:
    if DEFAULT_MODEL:
        return DEFAULT_MODEL
    # if provider == "openai":
    #     return "gpt-5"
    # dashscope default
    return "qwen-max"


def query_LLM(user_prompt: str, provider: Optional[str] = None) -> str:
    provider = (provider or DEFAULT_PROVIDER).lower()
    model = _choose_model(provider)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_prompt},
    ]

    # OpenAI official endpoint using legacy 0.28.x API
    # if provider == "openai":
    #     api_key = os.getenv("OPENAI_API_KEY") or "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"
        
    #     import openai
        
    #     openai.api_key = api_key
    #     completion = openai.ChatCompletion.create(
    #         model=model,
    #         messages=messages
    #     )
    #     return completion.choices[0].message.content.strip()

    # Generic custom endpoint using legacy 0.28.x API
    if provider == "custom":
        base_url = os.getenv("LLM_BASE_URL")
        api_key = os.getenv("LLM_API_KEY")
        if not base_url or not api_key:
            raise RuntimeError("custom provider requires LLM_BASE_URL and LLM_API_KEY env vars")
        
        import openai
        
        openai.api_key = api_key
        openai.api_base = base_url
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        return completion.choices[0].message.content.strip()
    # Default: DashScope (Aliyun) using legacy openai 0.28.x API
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY environment variable is required")
    
    import openai
    
    # Configure for DashScope using legacy API
    openai.api_key = api_key
    openai.api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    completion = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    return completion.choices[0].message.content.strip()


query_prompt = '''
You are a helpful assistant for generating a feature description on an Android APP with a given test case JSON.
The description must be detailed, each element touched in the test case should be described with its attribute (e.g., resource-id, content-desc, or text).
The description should be structured in one paragraph natural language, without a list format.
In first sentence, you must analyze the json and summarize the APP's functionality based on the test case. Next, describe the test process.
The description should not include "the test case xxx" or "the test case is xxx", but rather focus on "when doing xxx, yyy should happened".

Here is the information of the APP:
{app_info}

Here is the JSON data:
{json_data}

'''

example_prompt = '''
Example output:
The APP can navigate through directories. \
When the APP is opened, the "Download" folder is visible, identified by its text attribute. \
When click on the "Android" folder, the "data" folder becomes visible, while the "Download" folder is no longer visible, reflecting the directory change. \
Next, the user initiates a click action on the back button, which is identified by the resource-id "com.martinmimigames.simplefileexplorer/back_button". \
After navigating back, the "Download" folder reappears and is visible again, while the "data" folder becomes invisible, confirming the user has returned to the original main directory view. 
'''

def generate_prompt(test_json, app_info):
    # format the test_json into a string
    json_str = json.dumps(test_json, indent=2)
    user_prompt = query_prompt.format(
        app_info=app_info,
        json_data=json_str
    )
    user_prompt += example_prompt
    return user_prompt

overall_prompt = '''
You are a helpful assistant for generating a description of an Android APP's overall functionality based on multiple test cases.
The description must be organized in a three level hierarchy:
1. Overall functionality of the APP.
2. Features of the APP, each feature should be described in one sentence.
3. Sub-features of each feature, or test cases belong to this feature.
One test case should be exactly in one feature or one sub-feature, and should not be divided into multiple sub-features. 
You should not use list format, but rather use "feature-1", "sub-feature 1-1" to indicate the hierarchy.

The test cases are:
{refined_features}
for private_DNS_Quick_Tile，this is a high level description for each feature:
description:An app that allows users to quickly toggle and configure Private DNS settings on Android 9.0 and above via a quick settings tile.
    feature 1: Toggle Private DNS settings
    sub-feature 1-1: Enable or disable Private DNS functionality
    sub-feature 1-2: Configure Private DNS settings directly from the quick settings tile on devices running Android 9.0 and above
    feature 2: Simplified access to Private DNS management
    sub-feature 2-1: Provides a quick tile that enables easy access and streamlined management of Private DNS settings without navigating through system menus

    every test case correrpond to an sub-feature, and should be in order, and total is 3.
Example output:
description: An app for extracting APK files from installed apps on your Android device.  
feature 1: Extract APK files from installed apps.  
sub-feature 1-1: Allows users to search for installed apps by name. When the APP is opened, the "Apk Extractor" text is visible, indicating the name of the application. Within the app, the "Tethering" item, identified by the resource-id "axp.tool.apkextractor:id/txtAppName" is also visible, suggesting it is part of the directory or file list. When the user clicks on the search action, which is identified by the resource-id "axp.tool.apkextractor:id/action_search", the search bar becomes visible, as indicated by the resource-id "axp.tool.apkextractor:id/search_src_text". Finally, when the user clicks on the "Collapse" button, identified by the content-desc "Collapse", the search bar should close, and the user interface should return to its previous state, allowing the user to continue navigating through the directories.
sub-feature 1-2: Allows users to search for installed apps by name to quickly locate and extract their corresponding APK files.
    When the user clicks on the search icon, identified by the resource-id "axp.tool.apkextractor:id/action_search", the search bar becomes active. The user then inputs the word "camera" into the search field, which is recognized by the resource-id "axp.tool.apkextractor:id/search_src_text". After entering the search term, the user clicks the "Go" button, which has the content description "Go", to initiate the search. As a result, the search results are displayed, and the "Camera" app, with its name visible in the text "Camera" and resource-id "axp.tool.apkextractor:id/txtAppName", appears in the list. Additionally, the package name "com.android.camera2" is also visible, identified by the resource-id "axp.tool.apkextractor:id/txtPackageName", confirming the successful retrieval of the search results.
    When the user initiates a search by clicking on the search action button, identified by the resource-id "axp.tool.apkextractor:id/action_search", the search input field becomes active. The user then clicks on the search input field, which is also identified by the resource-id "axp.tool.apkextractor:id/search_src_text", and types in the word "google". After entering the search term, the user clicks on the "Go" button, which has the content description "Go", to start the search. As a result of the search, the Google app entry, with the resource-id "axp.tool.apkextractor:id/txtAppName" and text "Google", becomes visible, indicating that the search was successful. Finally, the user can collapse the search results by clicking on the "Collapse" button, which has the content description "Collapse", returning the interface to its initial state.
    When the user clicks on the search icon, identified by the resource-id "axp.tool.apkextractor:id/action_search", the search bar is activated. The user then clicks on the search input field, which has the resource-id "axp.tool.apkextractor:id/search_src_text", and types in the keyword "apk". After entering the search term, the user clicks the "Go" button, which is recognized by its content-desc attribute. Upon performing the search, the results should display the application "Apk Extractor" with the text "Apk Extractor" and the package name "axp.tool.apkextractor", both of which are identified by their respective resource-ids, "axp.tool.apkextractor:id/txtAppName" and "axp.tool.apkextractor:id/txtPackageName". This confirms that the search functionality is working as expected, allowing users to find and view details about specific applications.
'''

def generate_overall_prompt(refined_features, original_feature):
    prompt = overall_prompt.format(
        refined_features="\n".join(refined_features)
    )
    # overall_prompt += f"\n{original_feature}"
    return prompt


def generate_features(testcase_dir, original_feature):
    # read json files in the directory
    refined_features = []
    for filename in os.listdir(testcase_dir):
        # print(filename)
        if filename.endswith('.json'):
            with open(os.path.join(testcase_dir, filename), 'r') as f:
                test_json = json.load(f)
            user_prompt = generate_prompt(test_json, "")
            response = query_LLM(user_prompt)
            refined_features.append(response)
    print("\n\n\n".join(refined_features))
    print("====================================")
    user_prompt = generate_overall_prompt(refined_features, original_feature)
    overall_feature = query_LLM(user_prompt)
    return overall_feature



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate feature for AppDev-Bench")
    parser.add_argument("--path", type=str, default="./tasks/com.martinmimigames.simplefileexplorer/functional_tests/test2.json")
    # parser.add_argument("--app_info_path", type=str, default="")
    # app_info = "The APP is a simple file explorer that allows users to navigate through directories."
    app_info = ""
    args = parser.parse_args()

    # with open(args.path, 'r') as f:
    #     test_json = json.load(f)
    # user_prompt = generate_prompt(test_json, app_info)
    # response = query_LLM(user_prompt)
    response = generate_features(args.path, "")
    print(response)