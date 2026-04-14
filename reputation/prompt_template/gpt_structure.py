import json
import time
import os

import openai
from openai import OpenAI

from pathlib import Path
from utils import openai_api_key, api_base

import httpx

# client = openai.OpenAI(api_key=openai_api_key, base_url=api_base, http_client=httpx.Client(verify=False))
proxy_url = "http://127.0.0.1:7897"

client = openai.OpenAI(
    api_key=openai_api_key, 
    base_url=api_base, 
    http_client=httpx.Client(proxy=proxy_url, verify=False),
    timeout=60.0
)



def temp_sleep(seconds=0.1):
    time.sleep(seconds)


def GPT_4o_request(prompt, gpt_parameter):
    """
    Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
    server and returns the response.
    ARGS:
      prompt: a str prompt
      gpt_parameter: a python dictionary with the keys indicating the names of
                     the parameter and the values indicating the parameter
                     values.
    RETURNS:
      a str of GPT-4o-mini's response.
    """
    temp_sleep()
    try:

        '''
        # Please install OpenAI SDK first: `pip3 install openai`
        import os
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
            ],
            stream=False
        )

        print(response.choices[0].message.content)
        '''
        if type(prompt) is dict:
            msg = [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ]
        else:
            msg = [{"role": "user", "content": prompt}]
        completion = client.chat.completions.create(
            # model="gpt-4o-mini",
            model="openai/gpt-4o-mini",
            # model="deepseek",
            # model="qwen3-235b",
            messages=msg,
            max_tokens=gpt_parameter["max_tokens"],
            top_p=gpt_parameter["top_p"],
            frequency_penalty=gpt_parameter["frequency_penalty"],
            presence_penalty=gpt_parameter["presence_penalty"],
            temperature=gpt_parameter["temperature"],
        ) 
        # completion = client.chat.completions.create(
        #     model="qwen3-235b",
        #     messages=msg,
        #     max_tokens=gpt_parameter["max_tokens"],
        #     top_p=gpt_parameter["top_p"],
        #     frequency_penalty=gpt_parameter["frequency_penalty"],
        #     presence_penalty=gpt_parameter["presence_penalty"],
        #     temperature=gpt_parameter["temperature"],
        # )
        return completion.choices[0].message.content
    # except Exception as e:
    #     print("Exception: ", e)
    #     return "Error"

    except Exception as e:
        import traceback
        print(f"!!!! 发生错误 !!!!")
        print(f"错误类型: {type(e)}")
        print(f"错误信息: {e}")
        # 打印完整的堆栈，看看是不是 ReadTimeout 还是 RemoteProtocolError
        traceback.print_exc() 
        return "Error"


def safe_generate_response(
    prompt,
    gpt_parameter,
    repeat=5,
    fail_safe_response="error",
    func_validate=None,
    func_clean_up=None,
    verbose=False,
):
    if verbose:
        print(prompt)

    for i in range(repeat):
        curr_gpt_response = GPT_4o_request(prompt, gpt_parameter)
        if func_validate(curr_gpt_response, prompt=prompt):
            return func_clean_up(curr_gpt_response, prompt=prompt)
        if verbose:
            print("---- repeat count: ", i, curr_gpt_response)
            print(curr_gpt_response)
            print("~~~~")
    return fail_safe_response


def generate_prompt_role_play(curr_input, prompt_lib_file):
    """
    Takes in the current input (e.g. comment that you want to classifiy) and
    the path to a prompt file. The prompt file contains the raw str prompt that
    will be used, which contains the following substr: !<INPUT>! -- this
    function replaces this substr with the actual curr_input to produce the
    final promopt that will be sent to the GPT3 server.
    ARGS:
      curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                  INPUT, THIS CAN BE A LIST.)
      prompt_lib_file: the path to the promopt file.
    RETURNS:
      a str prompt that will be sent to OpenAI's GPT server.
    """
    if isinstance(curr_input, str):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]
    prompt_lib_file = os.path.join(os.path.dirname(__file__), prompt_lib_file)

    f = open(prompt_lib_file, "r", encoding="utf-8")
    prompt = f.read()
    f.close()
    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    return {"system": curr_input[0], "user": prompt.strip()}


def generate_prompt(curr_input, prompt_lib_file):
    """
    Takes in the current input (e.g. comment that you want to classifiy) and
    the path to a prompt file. The prompt file contains the raw str prompt that
    will be used, which contains the following substr: !<INPUT>! -- this
    function replaces this substr with the actual curr_input to produce the
    final promopt that will be sent to the GPT3 server.
    ARGS:
      curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                  INPUT, THIS CAN BE A LIST.)
      prompt_lib_file: the path to the promopt file.
    RETURNS:
      a str prompt that will be sent to OpenAI's GPT server.
    """
    if type(curr_input) is type("string"):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]
    prompt_lib_file = os.path.join(os.path.dirname(__file__), prompt_lib_file)

    f = open(prompt_lib_file, "r", encoding="utf-8")
    prompt = f.read()
    f.close()
    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    return prompt.strip()


def generate_prompt_role_play_false(curr_input, prompt_lib_file, role_play):
    """
    Takes in the current input (e.g. comment that you want to classifiy) and
    the path to a prompt file. The prompt file contains the raw str prompt that
    will be used, which contains the following substr: !<INPUT>! -- this
    function replaces this substr with the actual curr_input to produce the
    final promopt that will be sent to the GPT3 server.
    ARGS:
      curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                  INPUT, THIS CAN BE A LIST.)
      prompt_lib_file: the path to the promopt file.
    RETURNS:
      a str prompt that will be sent to OpenAI's GPT server.
    """
    if isinstance(curr_input, str):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]
    prompt_lib_file = os.path.join(os.path.dirname(__file__), prompt_lib_file)

    f = open(prompt_lib_file, "r", encoding="utf-8")
    prompt = f.read()
    f.close()
    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        user_prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    # return {"system": curr_input[0], "user": prompt.strip()}
    if role_play:
        return {"system": curr_input[0], "user": user_prompt.strip()}
    system_prompt = prompt.split("**system prompt:")[1].split("**")[0].strip()
    return {"system":system_prompt, "user": user_prompt.strip()}
    


def print_run_prompts(
    prompt_template=None,
    persona=None,
    gpt_param=None,
    prompt_input=None,
    prompt=None,
    output=None,
):
    print(f"=== {prompt_template}")
    print("~~~ persona    ---------------------------------------------------")
    print(persona.name, "\n")
    print("~~~ gpt_param ----------------------------------------------------")
    print(gpt_param, "\n")
    print("~~~ prompt_input    ----------------------------------------------")
    print(prompt_input, "\n")
    print("~~~ prompt    ----------------------------------------------------")
    print(prompt, "\n")
    print("~~~ output    ----------------------------------------------------")
    print(output, "\n")
    print("=== END ==========================================================")
    print("\n\n\n")



def save_run_prompts_single(
    prompt_template=None,
    persona=None,
    gpt_param=None,
    prompt_input=None,
    prompt=None,
    output=None,
    save_dir=None,
    save_txt=None,
):
    save_dir = Path(save_dir).resolve()
    save_dir.mkdir(parents=True, exist_ok=True)
    log_file = save_dir / save_txt
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(
            f"~~~ step ---------------------------------------------------------\n"
            f"step: {persona.scratch.curr_step}\n"
            f"=== {prompt_template}\n"
            f"~~~ persona ---------------------------------------------------\n"
            f"persona: {persona.name}\n"
            f"~~~ gpt_param ----------------------------------------------------\n"
            f"{gpt_param}\n"
            f"~~~ prompt_input ----------------------------------------------\n"
            f"{prompt_input}\n"
            f"~~~ prompt ----------------------------------------------------\n"
            f"{prompt}\n"
            f"~~~ output ----------------------------------------------------\n"
            f"{output}\n"
            f"=====================END========================\n"
            f"\n"
            f"\n"
        )


def save_run_prompts_pair(
    prompt_template=None,
    init_persona=None,
    target_persona=None,
    gpt_param=None,
    prompt_input=None,
    prompt=None,
    output=None,
    save_dir=None,
    save_txt=None,
):
    save_dir = Path(save_dir).resolve()
    save_dir.mkdir(parents=True, exist_ok=True)
    log_file = save_dir / save_txt
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(
            f"~~~ step ---------------------------------------------------------\n"
            f"step: {init_persona.scratch.curr_step}\n"
            f"=== {prompt_template}\n"
            f"~~~ init_persona -------------------------------------------------\n"
            f"init persona: {init_persona.name}\n"
            f"~~~ target_persona -----------------------------------------------\n"
            f"target persona: {target_persona.name}\n"
            f"~~~ gpt_param ----------------------------------------------------\n"
            f"{gpt_param}\n"
            f"~~~ prompt_input ----------------------------------------------\n"
            f"{prompt_input}\n"
            f"~~~ prompt ----------------------------------------------------\n"
            f"{prompt}\n"
            f"~~~ output ----------------------------------------------------\n"
            f"{output}\n"
            f"=====================END========================\n"
            f"\n"
            f"\n"
        )




def replace_full_name(name):
    # TODO change to the actual sim persona names
    personas = [
        "Liam OConnor",
        "Hiroshi Tanaka",
        "David Johnson",
        "Maria Rossi",
        "Sofia Hernandez",
        "James Wang",
        "Sergey Petrov",
        "Hannah Muller",
        "Nadia Novak",
        "Elena Ivanova",
        "Mohammed Al-Farsi",
        "Aisha Ibrahim",
        "Akiko Sato",
        "Emma Dubois",
        "Juan Carlos Reyes",
        "Ahmed Hassan",
        "Robert Miller",
        "Fatima Ali",
        "Isabella Costa",
        "Mateo Garcia",
    ]
    # for persona in personas:
    #     if name in persona:
    #         return persona
    search_name = name.lower().strip()
    
    for persona in personas:
        target_name = persona.lower()
        # 场景 A: 完全一致
        if search_name == target_name:
            return persona
        # 场景 B: 包含关系（如输入 Liam 匹配 Liam OConnor）
        if search_name in target_name:
            return persona
        # 场景 C: 针对 Mohammed Al-Farsi 这种带特殊符号的情况
        if search_name.replace("-", " ") == target_name.replace("-", " "):
            return persona
    return None
