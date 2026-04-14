import json
import time
import sys
import os

from openai import OpenAI
from pathlib import Path

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

from utils import openai_api_key, api_base
import httpx



# client = OpenAI(api_key=openai_api_key, base_url=api_base, http_client=httpx.Client(verify=False), timeout = 3600)

# proxy_url = "http://127.0.0.1:10808"

# client = OpenAI(api_key=openai_api_key, base_url=api_base, http_client=httpx.Client(proxy=proxy_url, verify=False), timeout = 3600)

proxy_url = "http://127.0.0.1:7897"

client = OpenAI(
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
        if prompt.get("system"):
            msg = [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ]
        else:
            msg = [{"role": "user", "content": prompt["user"]}]
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
    except Exception as e:
        print("Exception: ", e)
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


def generate_prompt_role_play(curr_input, prompt_lib_file, role_play=True):
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
    if role_play:
        return {"system": curr_input[0], "user": prompt.strip()}
    return {"user": prompt.strip()}



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