from .gpt_structure import *
from persona.persona import Persona
import json
from public_reputation.SharedPublicReputationDB import publicreputationDB

def run_gpt_prompt_reputation_update_after_stage4_investor_v1(
    output_save_dir,
    init_persona,
    target_persona,
    Interaction_memory,
):
    def create_self_update_prompt_input(
        init_persona,
        Interaction_memory,
    ):
        prompt_input = []
        prompt_input.append(init_persona.scratch.learned["investor"])
        prompt_input.append(init_persona.scratch.name)
        prompt_input.append(init_persona.scratch.ID)
        prompt_input.append(Interaction_memory["init_behavior_summary"])
        init_persona_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "Investor")
        # target_persona_reputation = (
        #     init_persona.reputationDB.get_targets_individual_reputation(
        #         target_persona.scratch.ID, "Trustee"
        #     )
        # )
        prompt_input += [json.dumps(init_persona_repu)]

        return prompt_input

    def create_target_update_prompt_input(
        init_persona,
        target_persona,
        Interaction_memory,
    ):
        prompt_input = []
        # prompt_input.append(init_persona.scratch.learned)
        prompt_input.append(init_persona.scratch.learned["investor"])
        prompt_input.append(init_persona.scratch.name)
        prompt_input.append(target_persona.scratch.ID)
        prompt_input.append(Interaction_memory["target_behavior_summary"])
        target_persona_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "Trustee")
        prompt_input += [json.dumps(target_persona_repu)]
        prompt_input.append(target_persona.scratch.name)
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 1:
            return dict(final_res)
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template_1 = "prompt/investment/All-self_investor_reputation_update_after_full_investment_v1.txt"
    prompt_template_2 = "prompt/investment/All-investor_update_others_reputation_after_full_investment_v1.txt"

    prompt_input_1 = create_self_update_prompt_input(
        init_persona,
        Interaction_memory,
    )
    prompt_input_2 = create_target_update_prompt_input(
        init_persona,
        target_persona,
        Interaction_memory,
    )
    prompt_1 = generate_prompt_role_play(prompt_input_1, prompt_template_1)
    prompt_2 = generate_prompt_role_play(prompt_input_2, prompt_template_2)
    fail_safe = get_fail_safe()
    output_1 = safe_generate_response(prompt_1, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    output_2 = safe_generate_response(prompt_2, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    print_run_prompts(prompt_template_1, init_persona, gpt_param, prompt_input_1, prompt_1, output_1)
    print_run_prompts(prompt_template_2, init_persona, gpt_param, prompt_input_2, prompt_2, output_2)

    output = {**output_1, **output_2}


    save_run_prompts_pair(prompt_template_1, init_persona, target_persona, gpt_param, prompt_input_1, prompt_1, output_1,
        save_dir=output_save_dir,
        save_txt="All-self_investor_reputation_update_after_full_investment_v1.txt")

    save_run_prompts_pair(prompt_template_2, init_persona, target_persona, gpt_param, prompt_input_2, prompt_2, output_2,
        save_dir=output_save_dir,
        save_txt="All-investor_update_others_reputation_after_full_investment_v1.txt")
    return output, [
        output,
        prompt_1,
        prompt_2,
        gpt_param,
        prompt_input_1,
        prompt_input_2,
        fail_safe,
    ]


def run_gpt_prompt_reputation_update_after_stage1_investor_v1(
    output_save_dir,
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    allocation_plan,
    reason_refusal,
    total_number_of_people,
    number_of_bidirectional_connections,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        allocation_plan,
        reason_refusal,
        total_number_of_people,
        number_of_bidirectional_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [allocation_plan]
        prompt_input += [reason_refusal]
        init_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role)
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(init_persona_reputation)]
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 2:
            return final_res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment/reputation_update_after_stage1_investor_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        allocation_plan,
        reason_refusal,
        total_number_of_people,
        number_of_bidirectional_connections,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="reputation_update_after_stage1_investor_v1.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_stage4_trustee_v1(
    output_save_dir,
    init_persona,
    target_persona,
    Interaction_memory,
):
    def create_self_update_prompt_input(
        init_persona,
        Interaction_memory,
    ):
        prompt_input = []
        prompt_input.append(init_persona.scratch.learned["trustee"])
        prompt_input.append(init_persona.scratch.name)
        prompt_input.append(init_persona.scratch.ID)
        prompt_input.append(Interaction_memory["init_behavior_summary"])
        init_persona_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "Trustee")
        # target_persona_reputation = (
        #     init_persona.reputationDB.get_targets_individual_reputation(
        #         target_persona.scratch.ID, "Trustee"
        #     )
        # )
        prompt_input += [json.dumps(init_persona_repu)]

        return prompt_input

    def create_target_update_prompt_input(
        init_persona,
        target_persona,
        Interaction_memory,
    ):
        prompt_input = []
        # prompt_input.append(init_persona.scratch.learned)
        prompt_input.append(init_persona.scratch.learned["trustee"])
        prompt_input.append(init_persona.scratch.name)
        prompt_input.append(target_persona.scratch.ID)
        prompt_input.append(Interaction_memory["target_behavior_summary"])

        target_persona_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "Investor")
        prompt_input += [json.dumps(target_persona_repu)]
        prompt_input.append(target_persona.scratch.name)
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 1:
            return dict(final_res)
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template_1 = "prompt/investment/All-self_trustee_reputation_update_after_full_investment_v1.txt"
    prompt_template_2 = "prompt/investment/All-trustee_update_others_reputation_after_full_investment_v1.txt"
    prompt_input_1 = create_self_update_prompt_input(
        init_persona,
        Interaction_memory,
    )
    prompt_input_2 = create_target_update_prompt_input(
        init_persona,
        target_persona,
        Interaction_memory,
    )
    prompt_1 = generate_prompt_role_play(prompt_input_1, prompt_template_1)
    prompt_2 = generate_prompt_role_play(prompt_input_2, prompt_template_2)
    fail_safe = get_fail_safe()
    output_1 = safe_generate_response(prompt_1, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    output_2 = safe_generate_response(prompt_2, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    print_run_prompts(prompt_template_1, init_persona, gpt_param, prompt_input_1, prompt_1, output_1)
    print_run_prompts(prompt_template_2, init_persona, gpt_param, prompt_input_2, prompt_2, output_2)

    output = {**output_1, **output_2}

    save_run_prompts_pair(prompt_template_1, init_persona, target_persona, gpt_param, prompt_input_1, prompt_1, output_1,
        save_dir=output_save_dir,
        save_txt="All-self_trustee_reputation_update_after_full_investment_v1.txt")

    save_run_prompts_pair(prompt_template_2, init_persona, target_persona, gpt_param, prompt_input_2, prompt_2, output_2,
        save_dir=output_save_dir,
        save_txt="All-trustee_update_others_reputation_after_full_investment_v1.txt")
    return output, [
        output,
        prompt_1,
        prompt_2,
        gpt_param,
        prompt_input_1,
        prompt_input_2,
        fail_safe,
    ]


def run_gpt_prompt_reputation_update_after_observed_v1(
    output_save_dir,
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    interaction_memory,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [interaction_memory]
        prompt_input += [target_persona.scratch.ID]
        pre_target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(pre_target_persona_reputation)]
        prompt_input += [target_persona_role]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 1:
            return final_res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment/All_observe_update_others_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All_observe_update_others_v1.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_stage1_trustee_v1(
    output_save_dir,
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    allocation_plan,
    reason_refusal,
    total_number_of_people,
    number_of_bidirectional_connections,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        allocation_plan,
        reason_refusal,
        total_number_of_people,
        number_of_bidirectional_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [allocation_plan]
        prompt_input += [reason_refusal]
        init_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role)
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(init_persona_reputation)]
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]
        prompt_input += [init_persona.scratch.success_num_investor / init_persona.scratch.total_num_trustee]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 2:
            return final_res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment/reputation_update_after_stage1_trustee_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        allocation_plan,
        reason_refusal,
        total_number_of_people,
        number_of_bidirectional_connections,
    )
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="reputation_update_after_stage1_trustee_v1.txt")


    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_reputation_update_after_gossip_invest_v1(
    output_save_dir,
    init_persona,
    target_persona,
    gossip,
    init_persona_role,
    target_persona_role,
    cred_level,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        init_persona_role,
        target_persona_role,
        cred_level,
    ):
        prompt_input = []
        prompt_input.append(init_persona.scratch.learned[init_persona_role])
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [gossip["gossiper name"]]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [json.dumps(gossip)]
        if target_persona_role.lower() == "investor":
            prompt_input += ["Investor"]
        elif target_persona_role.lower() == "trustee":
            prompt_input += ["Trustee"]

        prompt_input += [cred_level]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        final_res = dict()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        for _, val in res.items():
            id = val["ID"]
            if val["role"].lower() == "investor":
                final_res[f"Investor_{id}"] = val
            elif val["role"].lower() == "trustee":
                final_res[f"Trustee_{id}"] = val
        if len(final_res) == 1:
            return final_res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment/All-update_others_reputation_after_gossip_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        init_persona_role,
        target_persona_role,
        cred_level,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="All-update_others_reputation_after_gossip_v1.txt")


    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

    
def run_gpt_prompt_reputation_update_after_gossip_sign_up_v1(
    init_persona,
    target_persona,
    gossip,
    target_persona_role,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [gossip["gossiper name"]]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [json.dumps(gossip)]
        if target_persona_role.lower() == "resident":
            prompt_input += ["Resident"]
        # prompt_input += [total_number_of_people]
        # prompt_input += [number_of_bidirectional_connections]
        prompt_input += [target_persona_role]
        prompt_input += [gossip["credibility level"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up/reputation_update_after_gossip_sign_up_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        target_persona_role,

    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="reputation_update_after_gossip_sign_up_v2.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



# def run_gpt_prompt_reputation_update_after_gossip_sign_up_v1(
#     init_persona,
#     target_persona,
#     gossip,
#     target_persona_role,
#     total_number_of_people,
#     number_of_bidirectional_connections,
# ):
#     def create_prompt_input(
#         init_persona,
#         target_persona,
#         gossip,
#         target_persona_role,
#         total_number_of_people,
#         number_of_bidirectional_connections,
#     ):
#         prompt_input = []
#         prompt_input += [init_persona.scratch.learned]
#         prompt_input += [init_persona.scratch.name]
#         prompt_input += [target_persona.scratch.name]
#         prompt_input += [target_persona.scratch.ID]
#         prompt_input += [gossip["gossiper name"]]
#         target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
#         prompt_input += [json.dumps(target_persona_reputation)]
#         prompt_input += [json.dumps(gossip)]
#         if target_persona_role.lower() == "resident":
#             prompt_input += ["Resident"]
#         # prompt_input += [total_number_of_people]
#         # prompt_input += [number_of_bidirectional_connections]
#         prompt_input += [target_persona_role]
#         prompt_input += [gossip["credibility level"]]

#         return prompt_input

#     def __func_validate(gpt_response, prompt=""):
#         try:
#             if __func_clean_up(gpt_response, prompt):
#                 return True
#             return False
#         except Exception as e:
#             print(e)
#             return False

#     def __func_clean_up(gpt_response, prompt=""):
#         gpt_response = gpt_response.split("</think>")[-1].strip()
#         response = gpt_response.split("```json")[-1].split("```")[0].strip()
#         # print(response)
#         res = json.loads(response)

#         for _, val in res.items():
#             full_name = replace_full_name(val["name"])
#             if full_name:
#                 val["name"] = full_name
#             else:
#                 print(f"Full name not found for {val['name']}")
#                 return False
#         if len(res) == 1:
#             return res
#         return False

#     def get_fail_safe():
#         fs = "error"
#         return fs

#     gpt_param = {
        
#         # "engine": "qwen",
#         # "engine": "qwen3-235b",
#         "engine": "qwen3-235b",
#         # "engine": "gpt-4o-mini",
#         "max_tokens": 4096,
#         "temperature": 0,
#         "top_p": 1,
#         "stream": False,
#         "frequency_penalty": 0,
#         "presence_penalty": 0,
#         "stop": None,
#     }
#     prompt_template = "prompt/sign_up/reputation_update_after_gossip_sign_up_v2.txt"
#     prompt_input = create_prompt_input(
#         init_persona,
#         target_persona,
#         gossip,
#         target_persona_role,
#         total_number_of_people,
#         number_of_bidirectional_connections,
#     )
#     prompt = generate_prompt_role_play(prompt_input, prompt_template)

#     fail_safe = get_fail_safe()
#     output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

#     print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
#     save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
#         save_dir="./reputation/output",
#         save_txt="reputation_update_after_gossip_sign_up_v2.txt")

#     return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_reputation_update_after_gossip_sign_up_v1_with_publicreputation(
    init_persona,
    target_persona,
    gossip,
    target_persona_role,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [gossip["gossiper name"]]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_persona_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += target_persona_public_reputation
        prompt_input += [json.dumps(gossip)]
        if target_persona_role.lower() == "resident":
            prompt_input += ["Resident"]
        # prompt_input += [total_number_of_people]
        # prompt_input += [number_of_bidirectional_connections]
        prompt_input += [target_persona_role]
        prompt_input += [gossip["credibility level"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up_with_publicreputation/reputation_update_after_gossip_sign_up_v2_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        gossip,
        target_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="reputation_update_after_gossip_sign_up_v2_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_reputation_update_after_gossip_pd_game_v1(
    init_persona,
    target_persona,
    gossip,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        gossip,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [gossip["gossiper name"]]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [json.dumps(gossip)]
        prompt_input += ["Player"]
        prompt_input += ["player"]
        prompt_input += [gossip["credibility level"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/reputation_update_after_gossip_pd_game_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        gossip,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="reputation_update_after_gossip_pd_game_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_reputation_update_after_gossip_pd_game_v1_with_publicreputation(
    init_persona,
    target_persona,
    gossip,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        gossip,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [gossip["gossiper name"]]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(target_persona_reputation)]
        target_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role="Player")
        prompt_input += [target_public_reputation]
        prompt_input += [json.dumps(gossip)]
        prompt_input += ["Player"]
        prompt_input += ["player"]
        prompt_input += [gossip["credibility level"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False
        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/reputation_update_after_gossip_pd_game_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        gossip,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="reputation_update_after_gossip_pd_game_v1_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_update_learned_in_description_pd_game_v1(
    init_persona,
    self_reflection,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        self_reflection,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating Innate Traits in an agent description based on its current reputation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "player"))]
        prompt_input += [self_reflection]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:**Your name is ")[-1].split(". Using the")[0].strip()
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        import re

        # 去除所有星号，避免格式干扰
        gpt_response = gpt_response.split("</think>")[-1]
        gpt_response = gpt_response.replace("*", "")

        # 只匹配"Updated Innate Traits Information:"，忽略大小写
        match = re.search(r"Updated\s+Innate\s+Traits\s+Information\s*:(.*)", gpt_response, re.IGNORECASE | re.DOTALL)
        if match:
            response = match.group(1).strip()
        else:
            response = gpt_response.strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/update_learned_in_description_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        self_reflection,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="update_learned_in_description_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_update_learned_in_description_pd_game_v1_with_publicreputation_with_buffer(
    init_persona,
    res_s,
    self_reflection,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        res_s,
        self_reflection,
    ):
        # - !<INPUT 4>!: Current Public Reputation
        prompt_input = []
        prompt_input += ["You are an expert tasked with updating an agent's “innate traits” based on their current reputation and recent Prisoner's Dilemma (PD) game evaluation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        # prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "player"))]
        prompt_input += [res_s]
        self_public_reputation = publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, role="Player")
        prompt_input += [self_public_reputation]
        prompt_input += [self_reflection]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:**Your name is ")[-1].split(". Using the")[0].strip()
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        import re

        # 去除所有星号，避免格式干扰
        gpt_response = gpt_response.split("</think>")[-1]
        gpt_response = gpt_response.split("```json")[-1].split("```")[0].strip()
        gpt_response = gpt_response.replace("*", "")

        # 只匹配"Updated Innate Traits Information:"，忽略大小写
        match = re.search(r"Updated\s+Innate\s+Traits\s+Information\s*:(.*)", gpt_response, re.IGNORECASE | re.DOTALL)
        if match:
            response = match.group(1).strip()
        else:
            response = gpt_response.strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_update_learned_in_description_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        res_s,
        self_reflection,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="update_learned_in_description_v1_with_publicreputation.txt")

    if str(output).lower() == "error":
        output = init_persona.scratch.learned

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_update_learned_in_description_pd_game_v1_with_publicreputation(
    init_persona,
    self_reflection,
):
    def create_prompt_input(
        init_persona,
        self_reflection,
    ):
        # - !<INPUT 4>!: Current Public Reputation
        prompt_input = []
        prompt_input += ["You are an expert tasked with updating an agent's “innate traits” based on their current reputation and recent Prisoner's Dilemma (PD) game evaluation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "player"))]
        reporter_public_reputation = publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, role="Player")
        prompt_input += [reporter_public_reputation]
        prompt_input += [self_reflection]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:**Your name is ")[-1].split(". Using the")[0].strip()
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        import re

        # 去除所有星号，避免格式干扰
        gpt_response = gpt_response.split("</think>")[-1]
        gpt_response = gpt_response.split("```json")[-1].split("```")[0].strip()
        gpt_response = gpt_response.replace("*", "")

        # 只匹配"Updated Innate Traits Information:"，忽略大小写
        match = re.search(r"Updated\s+Innate\s+Traits\s+Information\s*:(.*)", gpt_response, re.IGNORECASE | re.DOTALL)
        if match:
            response = match.group(1).strip()
        else:
            response = gpt_response.strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_update_learned_in_description_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        self_reflection,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
        save_dir="task/pd_game_without_gossip/output_with_publicreputation",
        save_txt="update_learned_in_description_v1_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_update_learned_in_description_pd_game_v1_with_gossip_with_publicreputation(
    init_persona,
    self_reflection,
):
    def create_prompt_input(
        init_persona,
        self_reflection,
    ):
        # - !<INPUT 4>!: Current Public Reputation
        prompt_input = []
        prompt_input += ["You are an expert tasked with updating an agent's “innate traits” based on their current reputation and recent Prisoner's Dilemma (PD) game evaluation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "player"))]
        reporter_public_reputation = publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, role="Player")
        prompt_input += [reporter_public_reputation]
        prompt_input += [self_reflection]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:**Your name is ")[-1].split(". Using the")[0].strip()
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        import re

        # 去除所有星号，避免格式干扰
        gpt_response = gpt_response.split("</think>")[-1]
        gpt_response = gpt_response.split("```json")[-1].split("```")[0].strip()
        gpt_response = gpt_response.replace("*", "")

        # 只匹配"Updated Innate Traits Information:"，忽略大小写
        match = re.search(r"Updated\s+Innate\s+Traits\s+Information\s*:(.*)", gpt_response, re.IGNORECASE | re.DOTALL)
        if match:
            response = match.group(1).strip()
        else:
            response = gpt_response.strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_update_learned_in_description_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        self_reflection,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
        save_dir="task/pd_game_without_gossip/output_with_publicreputation",
        save_txt="update_learned_in_description_v1_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_update_learned_in_description_sign_v1(
    init_persona,
    init_persona_role,
    init_persona_view,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating learned in an agent description based on its current reputation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role))]
        prompt_input += [init_persona_view]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            # return True

            persona_name = prompt["user"].split("**Task:** Based on “")[-1].split("’s Previous Learned")[0].strip()
            print(persona_name)
            print(gpt_response)
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("Updated “learned” information:")[-1].strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up/update_learned_in_description_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="update_learned_in_description_v2.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_update_learned_in_description_sign_v1_with_publicreputation(
    init_persona,
    init_persona_role,
    init_persona_view,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating learned in an agent description based on its current reputation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role))]
        prompt_input += [publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, role="resident")]
        prompt_input += [init_persona_view]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            # return True

            persona_name = prompt["user"].split("**Task:** Based on “")[-1].split("’s Previous Learned")[0].strip()
            print(persona_name)
            print(gpt_response)
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("Updated “learned” information:")[-1].strip()
        return response


    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up_with_publicreputation/update_learned_in_description_v2_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="update_learned_in_description_v2.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_update_learned_in_description_invest_v1(
    output_save_dir,
    init_persona,
    init_persona_role,
    init_persona_view,
):
    def create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating learned in an agent description based on its current reputation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role))]
        prompt_input += [init_persona_view]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:**")[-1].split("is a")[0].strip()
            print(persona_name)
            print(gpt_response)
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response= gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("Updated “learned” information:")[-1].strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    if init_persona_role == "investor":
        prompt_template = "prompt/investment/All-update-investor_learned_in_description.txt"
    elif init_persona_role == "trustee":
        prompt_template = "prompt/investment/All-update-trustee_learned_in_description.txt"

    prompt_input = create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All-update_learned_in_description.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_update_learned_in_description_invest_v1_with_publicreputation(
    output_save_dir,
    init_persona,
    init_persona_role,
    init_persona_view,
):
    def create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    ):
        prompt_input = []
        prompt_input += ["You are an expert on updating learned in an agent description based on its current reputation."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, init_persona_role))]
        prompt_input += [publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, init_persona_role)]
        prompt_input += [init_persona_view]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            persona_name = prompt["user"].split("**Task:**")[-1].split("is a")[0].strip()
            print(persona_name)
            print(gpt_response)
            if persona_name in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response= gpt_response.split("</think>")[-1].strip()
        gpt_response= gpt_response.split("**Learned:** ")[-1].strip()
        response = gpt_response.split("Updated “learned” information:")[-1].strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    if init_persona_role == "investor":
        prompt_template = "prompt/investment_with_publicreputation/All-update-investor_learned_in_description_with_publicreputation.txt"
    elif init_persona_role == "trustee":
        prompt_template = "prompt/investment_with_publicreputation/All-update-trustee_learned_in_description_with_publicreputation.txt"

    prompt_input = create_prompt_input(
        init_persona,
        init_persona_role,
        init_persona_view,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)


    
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="All-update_learned_in_description_with_publicreputation.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]








def run_gpt_prompt_gossip_listener_select_v2(
    init_persona,
    target_persona_role,
    target_persona,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[target_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        bind_list = list(init_persona.scratch.relationship["bind_list"])
        bind_list = [i[0] for i in bind_list]
        prompt_input += [bind_list]
        repus = dict()
        for peronsa_name in bind_list:
            repus[peronsa_name] = init_persona.reputationDB.get_targets_individual_reputation(peronsa_name, target_persona_role)
        prompt_input += [json.dumps(repus)]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt) or __func_clean_up(gpt_response, prompt) == []:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        if "None" in gpt_response:
            return []
        full_name = replace_full_name(gpt_response)
        if full_name:
            gpt_response = full_name
        else:
            print(f"Full name not found for {gpt_response}")
            return False
        return [gpt_response]

    def get_fail_safe():
        fs = []
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/gossip_listener_select_v3.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona=target_persona,
        target_persona_role=target_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="gossip_listener_select_v3.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(
    init_persona,
    target_persona,
    output_save_dir,
    target_persona_role,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        debug_dir="debug_prompt_dir"
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[target_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        bind_list = list(init_persona.scratch.relationship["bind_list"])
        bind_list = [i[0] for i in bind_list]
        prompt_input += [bind_list]

        repus = dict()
        public_repus = dict()
        
        # 获取 reputation 数据
        for persona_name in bind_list:
            repus[persona_name] = init_persona.reputationDB.get_targets_individual_reputation(persona_name, target_persona_role)
            public_repus[persona_name] = publicreputationDB.get_target_public_reputation(persona_name, target_persona_role)
        
        prompt_input += [json.dumps(repus)]
        
        # --- 裁剪逻辑开始 ---
        clipped_public_repus = {}
        
        # 收集调试信息
        debug_logs = []
        debug_logs.append(f"--- Processing for {init_persona.scratch.name} ---")
        debug_logs.append(f"Raw public_repus keys: {list(public_repus.keys())}")

        for persona_name, inner_dict in public_repus.items():
            try:
                # inner_dict 类似 {'Player_3': {...}}
                if not inner_dict or not isinstance(inner_dict, dict):
                    debug_logs.append(f"[WARNING] {persona_name} data is empty or not dict: {type(inner_dict)}")
                    continue

                first_key = next(iter(inner_dict)) # 例如 'Player_3'
                real_data = inner_dict[first_key]
                
                # 记录循环内的关键提取步骤
                debug_logs.append(f"  [Loop] {persona_name}: Extracted inner key '{first_key}'")
                
                clipped_public_repus[persona_name] = {}
                clipped_public_repus[persona_name]["content"] = real_data.get("content", "None")
                clipped_public_repus[persona_name]["numerical record"] = real_data.get("numerical record", "None")
                clipped_public_repus[persona_name]["tag"] = "public"
            except Exception as e:
                debug_logs.append(f"  [ERROR] processing {persona_name}: {str(e)}")

        # 将裁剪后的字典放入 prompt
        prompt_input += [clipped_public_repus] 

        # --- 写入日志文件 ---
        if debug_dir:
            os.makedirs(debug_dir, exist_ok=True)
            log_path = os.path.join(debug_dir, "debug_first_gossip_listener_select_log.txt")
            try:
                with open(log_path, "a", encoding='utf-8') as f:
                    f.write("\n" + "="*50 + "\n")
                    f.write("\n".join(debug_logs) + "\n")
                    f.write("-" * 20 + " Raw public_repus (First 500 chars) " + "-" * 20 + "\n")
                    f.write(json.dumps(public_repus, ensure_ascii=False, default=str)[:500] + "...\n")
                    f.write("-" * 20 + " Clipped Result " + "-" * 20 + "\n")
                    f.write(json.dumps(clipped_public_repus, indent=2, ensure_ascii=False, default=str) + "\n")
                    f.write("-" * 20 + " Final Prompt Input List Structure " + "-" * 20 + "\n")
                    # 打印列表里每个元素的类型，防止列表过长看不清
                    for idx, item in enumerate(prompt_input):
                        f.write(f"Index {idx}: {type(item)} - {str(item)[:100]}...\n")
            except Exception as e:
                print(f"Log write failed: {e}")
        
        return prompt_input



    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt) or __func_clean_up(gpt_response, prompt) == []:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        if "None" in gpt_response:
            return []
        full_name = replace_full_name(gpt_response)
        if full_name:
            gpt_response = full_name
        else:
            print(f"Full name not found for {gpt_response}")
            return False
        return [gpt_response]

    def get_fail_safe():
        fs = []
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/with_publicreputation/gossip_first_listener_select_v3_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="gossip_first_listener_select_v3_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]






def run_gpt_prompt_gossip_listener_select_v2_with_publicreputation(
    init_persona,
    target_persona_role,
    original_persona,
    target_persona,
    output_save_dir
):

    def create_prompt_input(
        init_persona,
        target_persona,
        original_persona,
        target_persona_role,
        debug_dir="debug_prompt_dir"
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[target_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        
        bind_list = list(init_persona.scratch.relationship["bind_list"])
        bind_list = [i[0] for i in bind_list]
        prompt_input += [bind_list]
        
        repus = dict()
        public_repus = dict()
        
        # 获取 reputation 数据
        for persona_name in bind_list:
            repus[persona_name] = init_persona.reputationDB.get_targets_individual_reputation(persona_name, target_persona_role)
            # 假设 publicreputationDB 是全局可访问的，或者你需要从某处传入
            public_repus[persona_name] = publicreputationDB.get_target_public_reputation(persona_name, target_persona_role)
        
        prompt_input += [json.dumps(repus)]
        
        # --- 裁剪逻辑开始 ---
        clipped_public_repus = {}
        
        # 收集调试信息
        debug_logs = []
        debug_logs.append(f"--- Processing for {init_persona.scratch.name} ---")
        debug_logs.append(f"Raw public_repus keys: {list(public_repus.keys())}")

        for persona_name, inner_dict in public_repus.items():
            try:
                # inner_dict 类似 {'Player_3': {...}}
                if not inner_dict or not isinstance(inner_dict, dict):
                    debug_logs.append(f"[WARNING] {persona_name} data is empty or not dict: {type(inner_dict)}")
                    continue

                first_key = next(iter(inner_dict)) # 例如 'Player_3'
                real_data = inner_dict[first_key]
                
                # 记录循环内的关键提取步骤
                debug_logs.append(f"  [Loop] {persona_name}: Extracted inner key '{first_key}'")
                
                clipped_public_repus[persona_name] = {}
                clipped_public_repus[persona_name]["content"] = real_data.get("content", "None")
                clipped_public_repus[persona_name]["numerical record"] = real_data.get("numerical record", "None")
                clipped_public_repus[persona_name]["tag"] = "public"
            except Exception as e:
                debug_logs.append(f"  [ERROR] processing {persona_name}: {str(e)}")

        # 将裁剪后的字典放入 prompt
        prompt_input += [clipped_public_repus] 
        prompt_input += [original_persona.scratch.name]

        # --- 写入日志文件 ---
        if debug_dir:
            os.makedirs(debug_dir, exist_ok=True)
            log_path = os.path.join(debug_dir, "debug_gossip_listener_select_log.txt")
            try:
                with open(log_path, "a", encoding='utf-8') as f:
                    f.write("\n" + "="*50 + "\n")
                    f.write("\n".join(debug_logs) + "\n")
                    f.write("-" * 20 + " Raw public_repus (First 500 chars) " + "-" * 20 + "\n")
                    f.write(json.dumps(public_repus, ensure_ascii=False, default=str)[:500] + "...\n")
                    f.write("-" * 20 + " Clipped Result " + "-" * 20 + "\n")
                    f.write(json.dumps(clipped_public_repus, indent=2, ensure_ascii=False, default=str) + "\n")
                    f.write("-" * 20 + " Final Prompt Input List Structure " + "-" * 20 + "\n")
                    # 打印列表里每个元素的类型，防止列表过长看不清
                    for idx, item in enumerate(prompt_input):
                        f.write(f"Index {idx}: {type(item)} - {str(item)[:100]}...\n")
            except Exception as e:
                print(f"Log write failed: {e}")
        
        return prompt_input
    # def create_prompt_input(
    #     init_persona,
    #     target_persona,
    #     original_persona,
    #     target_persona_role,
    # ):
    #     prompt_input = []
    #     prompt_input += [init_persona.scratch.learned[target_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
    #     prompt_input += [init_persona.scratch.name]
    #     prompt_input += [target_persona.scratch.name]
    #     bind_list = list(init_persona.scratch.relationship["bind_list"])
    #     bind_list = [i[0] for i in bind_list]
    #     prompt_input += [bind_list]
    #     repus = dict()
    #     public_repus = dict()
    #     for persona_name in bind_list:
    #         repus[persona_name] = init_persona.reputationDB.get_targets_individual_reputation(persona_name, target_persona_role)
    #         public_repus[persona_name] = publicreputationDB.get_target_public_reputation(persona_name, target_persona_role)
    #     prompt_input += [json.dumps(repus)]
    #     clipped_public_repus = {}
    #     # public_repus 是输入的原始字典
    #     for persona_name, inner_dict in public_repus.items():
    #         # inner_dict 类似 {'Player_3': {...}}，取里面字典的第一个 value
    #         first_key = next(iter(inner_dict)) # 'Player_3'
    #         real_data = inner_dict[first_key]
            
    #         clipped_public_repus[persona_name] = {}
    #         clipped_public_repus[persona_name]["content"] = real_data["content"]
    #         clipped_public_repus[persona_name]["numerical record"] = real_data["numerical record"]
    #         clipped_public_repus[persona_name]["tag"] = "public"
        
    #     prompt_input += [clipped_public_repus]
    #     prompt_input += [original_persona.scratch.name]
    #     return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt) or __func_clean_up(gpt_response, prompt) == []:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        if "None" in gpt_response:
            return []
        full_name = replace_full_name(gpt_response)
        if full_name:
            gpt_response = full_name
        else:
            print(f"Full name not found for {gpt_response}")
            return False
        return [gpt_response]

    def get_fail_safe():
        fs = []
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/with_publicreputation/gossip_listener_select_v3_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        original_persona,
        target_persona_role=target_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="gossip_listener_select_v3_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_gossip_v2(init_persona, target_persona, reason, complain_target, role=None):
    def create_prompt_input(init_persona, target_persona, reason, complain_target, role=None):
        prompt_input = []
        prompt_input += ["You are now a dialogue generation expert."]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned[role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [target_persona.scratch.learned[role]] if type(target_persona.scratch.learned) is dict else [target_persona.scratch.learned]
        prompt_input += [reason]
        prompt_input += [complain_target]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if ":" in gpt_response:
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        return gpt_response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/create_gossip_chat_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, reason, complain_target, role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_identify_and_summary_gossip_info_v1(
    init_persona,
    target_persona,
    complain_info,
    output_save_dir,
    init_persona_role,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        prompt_input += [complain_info["gossip chat"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("Gossip info:")[-1].strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/identify_and_summary_gossip_info_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role=init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="identify_and_summary_gossip_info_v2.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_identify_and_summary_gossip_info_v1_with_publicreputation(
    init_persona,
    target_persona,
    complain_info,
    init_persona_role,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        prompt_input += [complain_info["gossip chat"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].replace("**", "").strip()
        response = gpt_response.split("Gossip info:")[-1].strip()
        return response

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/identify_and_summary_gossip_info_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role=init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="identify_and_summary_gossip_info_v2.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_first_order_evaluation_v1(
    init_persona,
    target_persona,
    complain_info,
    init_persona_role,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        gossiper_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, complain_info["gossiper role"])
        prompt_input += [json.dumps(gossiper_reputation)]
        prompt_input += [complain_info["gossip info"]]
        prompt_input += [init_persona.gossipDB.gossips_count]
        prompt_input += [init_persona.gossipDB.gossips_incredible_count]
        prompt_input += [complain_info["complained role"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # response = gpt_response.split("```json")[-1].split("```")[0].strip()
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        res_fin = []
        for _, val in res.items():
            res_fin.append(val)
        return res_fin

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/first_order_evaluation_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role=init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="first_order_evaluation_v2.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_first_order_evaluation_v1_with_publicreputation(
    init_persona,
    target_persona,
    complain_info,
    init_persona_role,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        gossiper_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, complain_info["gossiper role"])
        prompt_input += [json.dumps(gossiper_reputation)]
        gossiper_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, complain_info["gossiper role"])
        prompt_input += [gossiper_public_reputation]
        prompt_input += [complain_info["gossip info"]]
        prompt_input += [init_persona.gossipDB.gossips_count]
        prompt_input += [init_persona.gossipDB.gossips_incredible_count]
        prompt_input += [complain_info["complained role"]]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # response = gpt_response.split("```json")[-1].split("```")[0].strip()
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        res_fin = []
        for _, val in res.items():
            res_fin.append(val)
        return res_fin

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/with_publicreputation/first_order_evaluation_v2_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role=init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="first_order_evaluation_v2_with_publicreputation.txt")
   
   
    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_second_order_evaluation_v1(
    init_persona,
    target_persona,
    complain_info,
    output_save_dir,
    init_persona_role,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [complain_info["first-order listener name"]]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        second_gossiper_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            complain_info["first-order listener ID"],
            complain_info["first-order listener role"],
        )
        prompt_input += [json.dumps(second_gossiper_reputation)]
        prompt_input += [complain_info["gossip info"]]
        prompt_input += [init_persona.gossipDB.gossips_count]
        prompt_input += [init_persona.gossipDB.gossips_incredible_count]
        prompt_input += [complain_info["complained role"]]
        prompt_input += [complain_info["original gossiper name"]]
        first_order_gossiper_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            complain_info["original gossiper ID"],
            complain_info["original gossiper role"],
        )
        prompt_input += [json.dumps(first_order_gossiper_reputation)]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # response = gpt_response.split("```json")[-1].split("```")[0].strip()
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        res_fin = []
        for _, val in res.items():
            res_fin.append(val)
        return res_fin

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/second_order_evaluation_v2.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role=init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="second_order_evaluation_v2.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_second_order_evaluation_v1_with_publicreputation(
    init_persona,
    target_persona,
    complain_info,
    init_persona_role,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        complain_info,
        init_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [complain_info["first-order listener name"]]
        prompt_input += [complain_info["complained name"]]
        prompt_input += [complain_info["complained ID"]]
        second_gossiper_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            complain_info["first-order listener ID"],
            complain_info["first-order listener role"],
        )
        prompt_input += [json.dumps(second_gossiper_reputation)]
        second_gossiper_public_reputation = publicreputationDB.get_target_public_reputation(complain_info["first-order listener ID"], complain_info["first-order listener role"])
        prompt_input += [second_gossiper_public_reputation]
        prompt_input += [complain_info["gossip info"]]
        prompt_input += [init_persona.gossipDB.gossips_count]
        prompt_input += [init_persona.gossipDB.gossips_incredible_count]
        prompt_input += [complain_info["complained role"]]
        prompt_input += [complain_info["original gossiper name"]]
        first_order_gossiper_reputation = init_persona.reputationDB.get_targets_individual_reputation(
            complain_info["original gossiper ID"],
            complain_info["original gossiper role"],
        )
        prompt_input += [json.dumps(first_order_gossiper_reputation)]
        first_order_gossiper_public_reputation = publicreputationDB.get_target_public_reputation(complain_info["original gossiper ID"], complain_info["original gossiper role"])
        prompt_input += [first_order_gossiper_public_reputation]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # response = gpt_response.split("```json")[-1].split("```")[0].strip()
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        res_fin = []
        for _, val in res.items():
            res_fin.append(val)
        return res_fin

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/with_publicreputation/second_order_evaluation_v2_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, complain_info, init_persona_role=init_persona_role)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="second_order_evaluation_v2_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_connection_build_player_v1(init_persona, target_persona, interaction_memory, output_save_dir):
    def create_prompt_input(init_persona, target_persona, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(target_persona_reputation)]
        # prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/connection_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="connection_after_pd_game_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


# bind_res = run_gpt_prompt_connection_build_player_v1_with_publicreputation(
#                     init_persona,
#                     target_persona,
#                     update_info["target_behavior_summary"],
#                 )[0]
def run_gpt_prompt_connection_build_player_v1_with_publicreputation(init_persona, target_persona, interaction_memory):
    def create_prompt_input(init_persona, target_persona, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(target_persona_reputation)]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, "Player")
        prompt_input += [target_previous_public_reputation]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/connection_after_pd_game_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir="task/pd_game_without_gossip/output_with_publicreputation",
        save_txt="connection_after_pd_game_v1_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_connection_build_player_v1_with_publicreputation_with_buffer(init_persona, target_persona, init_persona_learned, target_persona_reputation, target_public_reputation, output_save_dir):
    def create_prompt_input(init_persona, target_persona, init_persona_learned, target_persona_reputation, target_public_reputation):
        prompt_input = []
        prompt_input += [init_persona_learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        # target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        # prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [target_persona_reputation]
        # target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, "Player")
        prompt_input += [target_public_reputation]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/connection_after_pd_game_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, init_persona_learned, target_persona_reputation, target_public_reputation)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="connection_after_pd_game_v1_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]








def run_gpt_prompt_connection_build_player_v1_with_gossip_with_publicreputation(init_persona, target_persona, interaction_memory):
    def create_prompt_input(init_persona, target_persona, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(target_persona_reputation)]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, "Player")
        prompt_input += [target_previous_public_reputation]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/connection_after_pd_game_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir="task/pd_game/output_with_publicreputation",
        save_txt="connection_after_pd_game_v1_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_connection_build_investor_v1(output_save_dir, init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment/All-connection_build_after_investment_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All-connection_build_after_investment_v1.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_connection_build_investor_v1_with_publicreputation(init_persona, target_persona, target_persona_role, output_save_dir, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):

        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_previous_public_reputation]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment_with_publicreputation/All-connection_build_after_investment_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="All-connection_build_after_investment_v1_investor.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_disconnection_player_v1(init_persona, target_persona, target_persona_role, interaction_memory, output_save_dir):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/disconnection_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="disconnection_after_pd_game_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


# disconnection_res = run_gpt_prompt_disconnection_player_v1_with_publicreputation(
#                 init_persona,
#                 target_persona,
#                 target_persona_role,
#                 update_info["target_behavior_summary"],
#             )[0]
def run_gpt_prompt_disconnection_player_v1_with_publicreputation(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        # !<INPUT 3>! -- target's current private reputation  
        # !<INPUT 4>! -- target's current public reputation  
        prompt_input += [json.dumps(target_persona_reputation)]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, "Player")
        prompt_input += [target_previous_public_reputation]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/disconnection_after_pd_game_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir="task/pd_game_without_gossip/output_with_publicreputation",
        save_txt="disconnection_after_pd_game_v1_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_disconnection_player_v1_with_publicreputation_with_buffer(init_persona, target_persona, init_persona_learned, target_persona_reputation, target_public_reputation, output_save_dir):
    def create_prompt_input(init_persona, target_persona, init_persona_learned, target_persona_reputation, target_public_reputation):
        prompt_input = []
        prompt_input += [init_persona_learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        # target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        # prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [target_persona_reputation]
        # target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, "Player")
        # prompt_input += [target_previous_public_reputation]
        prompt_input += [target_public_reputation]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/disconnection_after_pd_game_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, init_persona_learned, target_persona_reputation, target_public_reputation)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="disconnection_after_pd_game_v1_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]






def run_gpt_prompt_disconnection_player_v1_with_gossip_with_publicreputation(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        # !<INPUT 3>! -- target's current private reputation  
        # !<INPUT 4>! -- target's current public reputation  
        prompt_input += [json.dumps(target_persona_reputation)]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, "Player")
        prompt_input += [target_previous_public_reputation]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/disconnection_after_pd_game_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir="task/pd_game/output_with_publicreputation",
        save_txt="disconnection_after_pd_game_v1_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_disconnection_investor_v1(output_save_dir, init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment/All-disconnection_after_investment_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All-disconnection_after_investment_v1.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_disconnection_investor_v1_with_publicreputation(init_persona, target_persona, target_persona_role, output_save_dir, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["investor"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_public_reputation]
        
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment_with_publicreputation/All-disconnection_after_investment_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)
    

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All-disconnection_after_investment_v1_with_publicreputation_investor.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_disconnection_after_observed_v1(
    output_save_dir,
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    interaction_memory,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [init_persona.scratch.learned]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment/All-disconnection_after_observe_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All-disconnection_after_observe_v1.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_disconnection_after_observed_v1_with_publicreputation(
    output_save_dir,
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    interaction_memory,
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_public_reputation]
        prompt_input += [init_persona.scratch.learned]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment_with_publicreputation/All-disconnection_after_observe_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All-disconnection_after_observe_v1_with_publicreputation.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_connection_build_trustee_v1(output_save_dir, init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # response = gpt_response.split("```json")[-1].split("```")[0].strip()
        response = gpt_response.split("</think>")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment/All-connection_build_after_investment_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All-connection_build_after_investment_v1.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_connection_build_trustee_v1_with_publicreputation(init_persona, target_persona, target_persona_role, output_save_dir, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_previous_public_reputation]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment_with_publicreputation/All-connection_build_after_investment_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="All-connection_build_after_investment_v1_trustee.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_disconnection_trustee_v1(output_save_dir, init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment/All-disconnection_after_investment_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All-disconnection_after_investment_v1.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_disconnection_trustee_v1_with_publicreputation(init_persona, target_persona, target_persona_role, output_save_dir, interaction_memory):
    def create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned["trustee"]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_public_reputation]
        prompt_input.append(interaction_memory)

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment_with_publicreputation/All-disconnection_after_investment_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, target_persona_role, interaction_memory)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="All-disconnection_after_investment_v1_with_publicreputation_trustee.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_connection_build_after_chat_sign_up_v2(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [interaction_memory]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up/connection_build_after_chat_sign_up_v3.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_connection_build_after_chat_sign_up_v2_with_publicreputation(init_persona, target_persona, target_persona_role, output_save_dir, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_previous_public_reputation]
        prompt_input += [interaction_memory]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up_with_publicreputation/connection_build_after_chat_sign_up_v3_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="connection_build_after_chat_sign_up_v3.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_disconnection_after_chat_sign_up_v2(init_persona, target_persona, target_persona_role, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [interaction_memory]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up/disconnection_after_chat_sign_up_v3.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_disconnection_after_chat_sign_up_v2_with_publicreputation(init_persona, target_persona, output_save_dir, target_persona_role, interaction_memory):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_public_reputation]
        prompt_input += [interaction_memory]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up_with_publicreputation/disconnection_after_chat_sign_up_v3_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
        interaction_memory,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="disconnection_after_chat_sign_up_v3_with_publicreputation.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_disconnection_after_new_sign_up_v1(init_persona, target_persona, target_persona_role):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]

        last_choice = init_persona.associativeMemory.get_latest_event()
        if type(last_choice) is dict:
            last_choice = last_choice["description"]
        else:
            last_choice = last_choice.toJSON()["description"]
        last_choice = last_choice.splitlines()
        for line in last_choice:
            if target_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]
            elif init_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up/disconnection_only_after_new_sign_up_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_disconnection_after_new_sign_up_v1_with_publicreputation(init_persona, target_persona, output_save_dir, target_persona_role):
    def create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, "resident")
        prompt_input += [target_public_reputation]


        last_choice = init_persona.associativeMemory.get_latest_event()
        if type(last_choice) is dict:
            last_choice = last_choice["description"]
        else:
            last_choice = last_choice.toJSON()["description"]
        last_choice = last_choice.splitlines()
        for line in last_choice:
            if target_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]
            elif init_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up_with_publicreputation/disconnection_only_after_new_sign_up_v1_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        target_persona_role,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="disconnection_only_after_new_sign_up_v1_with_publicreputation.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_disconnection_after_gossip_v2(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    gossiper_name,
    gossip_info,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        gossiper_name,
        gossip_info,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [gossiper_name]
        prompt_input += [gossip_info]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # response = gpt_response.split("```json")[-1].split("```")[0].strip()
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/disconnection_after_gossip_v3.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        gossiper_name,
        gossip_info,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="disconnection_after_gossip_v3.txt")

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_disconnection_after_gossip_v2_with_publicreputation(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    gossiper_name,
    gossip_info,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        gossiper_name,
        gossip_info,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_public_reputation]
        # prompt_input += [gossiper_name]
        prompt_input += [gossip_info]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/with_publicreputation/disconnection_after_gossip_v3_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        gossiper_name,
        gossip_info,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="disconnection_after_gossip_v3_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




# 听见gossip重建联系
def run_gpt_prompt_rebuild_connection_after_gossip_v2_with_publicreputation(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    gossiper_name,
    gossip_info,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        gossiper_name,
        gossip_info,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]] if type(init_persona.scratch.learned) is dict else [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        target_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_public_reputation]
        # prompt_input += [gossiper_name]
        prompt_input += [gossip_info]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/with_publicreputation/rebuild_connection_after_gossip_v3_with_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        init_persona_role,
        target_persona_role,
        gossiper_name,
        gossip_info,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)

    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="rebuild_connection_after_gossip_v3_with_publicreputation.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]






def run_gpt_prompt_self_reputation_init_sign_up_v1(init_persona):
    def create_prompt_input(init_persona):
        prompt_input = []
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.ID]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # response = gpt_response.split("```json")[-1].split("```")[0].strip()
        response = gpt_response.split("</think>")[-1].split("```")[0].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up/self_reputation_init_sign_up_v1.txt"
    prompt_input = create_prompt_input(init_persona)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
        save_dir="./reputation/output",
        save_txt="self_reputation_init_sign_up_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_self_reputation_update_after_pd_game_v1(init_persona, self_reflection, output_save_dir):
    def create_prompt_input(init_persona, self_reflection):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        # self_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "resident")
        self_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "player")
        prompt_input += [json.dumps(self_repu)]
        prompt_input += [self_reflection]
        
        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/self_reputation_update_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, self_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="self_reputation_update_after_pd_game_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

def run_gpt_prompt_self_reputation_update_after_pd_game_v1_with_publicreputation(init_persona, self_reflection, output_save_dir):
    def create_prompt_input(init_persona, self_reflection):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        # self_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "resident")
        self_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "player")
        prompt_input += [json.dumps(self_repu)]
        prompt_input += [self_reflection]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/self_reputation_update_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, self_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="self_reputation_update_after_pd_game_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_self_reputation_update_after_pd_game_v1_with_gossip_with_publicreputation(init_persona, self_reflection):
    def create_prompt_input(init_persona, self_reflection):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [self_reflection]
        # self_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "resident")
        self_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "player")
        prompt_input += [json.dumps(self_repu)]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/self_reputation_update_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, self_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
        save_dir="task/pd_game/output_with_publicreputation",
        save_txt="self_reputation_update_after_pd_game_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_other_reputation_update_after_pd_game_v1(init_persona, target_persona, other_reflection, output_save_dir):
    def create_prompt_input(init_persona, target_persona, other_reflection):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        prompt_input += [target_persona.scratch.ID]
        other_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(other_repu)]
        prompt_input += [other_reflection]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/other_reputation_update_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, other_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir=output_save_dir,
        save_txt="other_reputation_update_after_pd_game_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

def run_gpt_prompt_other_reputation_update_after_pd_game_v1_with_publicreputation(init_persona, target_persona, other_reflection, output_save_dir):
    def create_prompt_input(init_persona, target_persona, other_reflection):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        prompt_input += [target_persona.scratch.ID]
        other_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(other_repu)]
        prompt_input += [other_reflection]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/other_reputation_update_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, other_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
        save_dir=output_save_dir,
        save_txt="other_reputation_update_after_pd_game_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

def run_gpt_prompt_other_reputation_update_after_pd_game_v1_with_gossip_with_publicreputation(init_persona, target_persona, other_reflection):
    def create_prompt_input(init_persona, target_persona, other_reflection):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        prompt_input += [target_persona.scratch.ID]
        other_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
        prompt_input += [json.dumps(other_repu)]
        prompt_input += [other_reflection]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1]
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game/other_reputation_update_after_pd_game_v1.txt"
    prompt_input = create_prompt_input(init_persona, target_persona, other_reflection)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
        save_dir="task/pd_game/output_with_publicreputation",
        save_txt="other_reputation_update_after_pd_game_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

def run_gpt_prompt_self_reputation_update_after_chat_sign_up_v1(init_persona, sum_convo, ava_satisfy, output_save_dir):
    def create_prompt_input(init_persona, sum_convo, ava_satisfy):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [init_persona.scratch.ID]
        prompt_input += [sum_convo]
        prompt_input += [
            round(
                (init_persona.scratch.success_chat_num / init_persona.scratch.total_chat_num),
                3,
            )
        ]
        self_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "resident")
        prompt_input += [json.dumps(self_repu)]
        prompt_input += [ava_satisfy]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up/self_reputation_update_after_chat_sign_up_v2.txt"
    prompt_input = create_prompt_input(init_persona, sum_convo, ava_satisfy)
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, init_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="self_reputation_update_after_chat_sign_up_v2.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_other_reputation_update_after_chat_sign_up_v1(
    init_persona,
    target_persona,
    sum_convo,
    total_number_of_people,
    number_of_bidirectional_connections,
    ava_num_bibd_connections,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        sum_convo,
        total_number_of_people,
        number_of_bidirectional_connections,
        ava_num_bibd_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        prompt_input += [sum_convo]
        prompt_input += [target_persona.scratch.ID]
        other_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "resident")
        prompt_input += [json.dumps(other_repu)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]
        prompt_input += [ava_num_bibd_connections]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up/other_reputation_update_after_chat_sign_up_v2.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        sum_convo,
        total_number_of_people,
        number_of_bidirectional_connections,
        ava_num_bibd_connections,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="other_reputation_update_after_chat_sign_up_v2.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_other_reputation_update_after_new_sign_up_v1(
    init_persona,
    target_persona,
    total_number_of_people,
    number_of_bidirectional_connections,
    ava_num_bibd_connections,
    output_save_dir
):
    def create_prompt_input(
        init_persona,
        target_persona,
        total_number_of_people,
        number_of_bidirectional_connections,
        ava_num_bibd_connections,
    ):
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.name]
        prompt_input += [target_persona.name]
        last_choice = init_persona.associativeMemory.get_latest_event()
        if type(last_choice) is dict:
            last_choice = last_choice["description"]
        else:
            last_choice = last_choice.toJSON()["description"]
        last_choice = last_choice.splitlines()
        for line in last_choice:
            if target_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]

        prompt_input += [target_persona.scratch.ID]
        other_repu = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "resident")
        prompt_input += [json.dumps(other_repu)]
        prompt_input += [total_number_of_people]
        prompt_input += [number_of_bidirectional_connections]
        prompt_input += [ava_num_bibd_connections]
        for line in last_choice:
            if init_persona.name in line:
                # last choice of the persona in memory
                prompt_input += [line.split(":")[-1].strip()]

        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        gpt_response = gpt_response.split("</think>")[-1].strip()
        response = gpt_response.split("```json")[-1].split("```")[0].strip()
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()
        # print(response)
        res = json.loads(response)

        for _, val in res.items():
            full_name = replace_full_name(val["name"])
            if full_name:
                val["name"] = full_name
            else:
                print(f"Full name not found for {val['name']}")
                return False

        if len(res) == 1:
            return res
        return False

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen",
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up/other_reputation_update_only_after_new_sign_up_v1.txt"
    prompt_input = create_prompt_input(
        init_persona,
        target_persona,
        total_number_of_people,
        number_of_bidirectional_connections,
        ava_num_bibd_connections,
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)

    print_run_prompts(prompt_template, init_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="other_reputation_update_only_after_new_sign_up_v1.txt")

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_sign_up_decide_to_report_to_publicreputationDB(init_persona, target_persona, output_save_dir, target_persona_role):
    def create_prompt_input(init_persona, target_persona, target_persona_role):
        # !<INPUT 0>! -- agent's learned
        # !<INPUT 1>! -- agent's name
        # !<INPUT 2>! -- target's name
        # !<INPUT 3>! -- target's reputation

        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        response = json.loads(response)
        return response


    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/sign_up_with_publicreputation/sign_up_decide_to_report_to_publicreputationDB.txt"
    prompt_input = create_prompt_input(
        init_persona, target_persona, target_persona_role
        # interaction_memory
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="sign_up_decide_to_report_to_publicreputationDB.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_investment_decide_to_report_to_publicreputationDB(init_persona, target_persona, output_save_dir, init_persona_role, target_persona_role):
    def create_prompt_input(init_persona, target_persona, init_persona_role, target_persona_role):
        # !<INPUT 0>! -- agent's learned
        # !<INPUT 1>! -- agent's name
        # !<INPUT 2>! -- target's name
        # !<INPUT 3>! -- target's reputation

        prompt_input = []
        prompt_input += [init_persona.scratch.learned[init_persona_role]]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [init_persona_role]
        prompt_input += [target_persona_role]
        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        response = json.loads(response)
        return response


    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment_with_publicreputation/investment_decide_to_report_to_publicreputationDB.txt"
    prompt_input = create_prompt_input(
        init_persona, target_persona, init_persona_role, target_persona_role
        # interaction_memory
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="investment_decide_to_report_to_publicreputationDB.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_investment_investor_decide_to_report_to_publicreputationDB(init_persona, target_persona, output_save_dir, target_persona_role):
    def create_prompt_input(init_persona, target_persona, target_persona_role):
        # !<INPUT 0>! -- agent's learned
        # !<INPUT 1>! -- agent's name
        # !<INPUT 2>! -- target's name
        # !<INPUT 3>! -- target's reputation

        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        response = json.loads(response)
        return response


    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment_with_publicreputation/investment_investor_decide_to_report_to_publicreputationDB.txt"
    prompt_input = create_prompt_input(
        init_persona, target_persona, target_persona_role
        # interaction_memory
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="investment_investor_decide_to_report_to_publicreputationDB.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]




def run_gpt_prompt_investment_trustee_decide_to_report_to_publicreputationDB(init_persona, target_persona, output_save_dir, target_persona_role):
    def create_prompt_input(init_persona, target_persona, target_persona_role):
        # !<INPUT 0>! -- agent's learned
        # !<INPUT 1>! -- agent's name
        # !<INPUT 2>! -- target's name
        # !<INPUT 3>! -- target's reputation

        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        response = json.loads(response)
        return response


    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/investment_with_publicreputation/investment_trustee_decide_to_report_to_publicreputationDB.txt"
    prompt_input = create_prompt_input(
        init_persona, target_persona, target_persona_role
        # interaction_memory
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir=output_save_dir,
    save_txt="investment_trustee_decide_to_report_to_publicreputationDB.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_pd_game_decide_to_report_to_publicreputationDB_with_buffer(init_persona, target_persona, res_o, output_save_dir):
    def create_prompt_input(init_persona, target_persona, res_o):
        # !<INPUT 0>! -- agent's learned
        # !<INPUT 1>! -- agent's name
        # !<INPUT 2>! -- target's name
        # !<INPUT 3>! -- target's reputation

        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        # target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        # prompt_input += [json.dumps(target_persona_reputation)]
        prompt_input += [res_o]
        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        response = json.loads(response)
        return response
        # # get Yes or No
        # res = response.get("Result")
        # print(res)
        # if len(res) == 1:
        #     return res
        # return False
        # print(gpt_response)
        # return gpt_response


    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_decide_to_report_to_publicreputationDB.txt"
    prompt_input = create_prompt_input(
        init_persona, target_persona, res_o
        # interaction_memory
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
    save_dir=output_save_dir,
    save_txt="pd_game_decide_to_report_to_publicreputationDB.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_pd_game_decide_to_report_to_publicreputationDB_with_gossip(init_persona, target_persona, update_info, target_persona_role):
    def create_prompt_input(init_persona, target_persona, update_info, target_persona_role):
        # !<INPUT 0>! -- agent's learned
        # !<INPUT 1>! -- agent's name
        # !<INPUT 2>! -- target's name
        # !<INPUT 3>! -- target's reputation
        prompt_input = []
        prompt_input += [init_persona.scratch.learned]
        prompt_input += [init_persona.scratch.name]
        prompt_input += [target_persona.scratch.name]
        target_persona_reputation = init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [json.dumps(target_persona_reputation)]
        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        response = json.loads(response)
        return response
        # # get Yes or No
        # res = response.get("Result")
        # print(res)
        # if len(res) == 1:
        #     return res
        # return False
        # print(gpt_response)
        # return gpt_response


    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }
    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_decide_to_report_to_publicreputationDB.txt"
    prompt_input = create_prompt_input(
        init_persona, target_persona, update_info, target_persona_role
        # interaction_memory
    )
    prompt = generate_prompt_role_play(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir="task/pd_game/output_with_publicreputation",
    save_txt="pd_game_decide_to_report_to_publicreputationDB.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_pd_game_update_target_publicreputation_content(init_persona, target_persona, update_info, output_save_dir, role):
    def create_prompt_input(init_persona, target_persona, update_info, role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [init_persona.scratch.name]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role)
        prompt_input += [target_previous_public_reputation]
        # !<INPUT 4>!: -- reporter(init_persona)'s evaluation on the target
        # init_persona_repu = init_persona.reputationDB.get_targets_individual_reputation(init_persona.scratch.ID, "Investor")
        # prompt_input += [json.dumps(init_persona_repu)]
        # prompt_input += [json.dumps(init_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "Player"))]
        prompt_input += [update_info]
        # !<INPUT 5>!: -- reporter's own public reputation
        reporter_public_reputation = publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, role)
        prompt_input += [reporter_public_reputation]
        return prompt_input
    
    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_update_target_publicreputation_content.txt"
    prompt_input = create_prompt_input(
        init_persona, 
        target_persona, 
        update_info,
        role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
    save_dir=output_save_dir,
    save_txt="update_public_reputation_content.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]






def run_gpt_prompt_sign_up_update_target_publicreputation_content(init_persona, target_persona, res_s, output_save_dir, role):
    def create_prompt_input(init_persona, target_persona, res_s, role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [init_persona.scratch.name]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role)
        prompt_input += [target_previous_public_reputation]
        # !<INPUT 4>!: -- reporter's evaluation on the target
        prompt_input += [res_s]
        # !<INPUT 5>!: -- reporter's own public reputation
        reporter_public_reputation = publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, role)
        prompt_input += [reporter_public_reputation]
        return prompt_input
    
    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/sign_up_with_publicreputation/sign_up_update_target_publicreputation_content.txt"
    prompt_input = create_prompt_input(
        init_persona, 
        target_persona, 
        res_s,
        role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
    save_dir=output_save_dir,
    save_txt="update_public_reputation_content.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]






def run_gpt_prompt_investment_update_target_publicreputation_content(init_persona, target_persona, res_s, output_save_dir, target_persona_role):
    def create_prompt_input(init_persona, target_persona, res_s, target_persona_role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [init_persona.scratch.name]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_previous_public_reputation]
        # !<INPUT 4>!: -- reporter's evaluation on the target
        prompt_input += [res_s]
        # !<INPUT 5>!: -- reporter's own public reputation
        if target_persona_role == "investor":
            init_persona_role = "trustee"
        else:
            init_persona_role = "investor"
        reporter_public_reputation = publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, init_persona_role)
        prompt_input += [reporter_public_reputation]
        return prompt_input
    
    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/investment_with_publicreputation/investment_update_publicreputation_content.txt"
    prompt_input = create_prompt_input(
        init_persona, 
        target_persona, 
        res_s,
        target_persona_role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
    save_dir=output_save_dir,
    save_txt="investment_update_publicreputation_content.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]






def run_gpt_prompt_pd_game_update_target_publicreputation_content_with_gossip(init_persona, target_persona, update_info, role):
    def create_prompt_input(init_persona, target_persona, update_info, role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [init_persona.scratch.name]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role)
        prompt_input += [target_previous_public_reputation]
        # !<INPUT 4>!: -- reporter's evaluation on the target
        prompt_input += [update_info]
        # !<INPUT 5>!: -- reporter's own public reputation
        reporter_public_reputation = publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, role)
        prompt_input += [reporter_public_reputation]
        return prompt_input
    
    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_update_target_publicreputation_content.txt"
    prompt_input = create_prompt_input(
        init_persona, 
        target_persona, 
        update_info,
        role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir="task/pd_game/output_with_publicreputation",
    save_txt="update_public_reputation_content.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_pd_game_update_target_publicreputation_record(target_persona, content, output_save_dir, role):
    def create_prompt_input(target_persona, content, role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role)
        prompt_input += [target_previous_public_reputation]
        # !<INPUT 3>!: -- provided public reputation content
        prompt_input += [content]

        return prompt_input
    
    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_update_target_publicreputation_numerical_record.txt"
    prompt_input = create_prompt_input(
        target_persona, content, role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, target_persona, gpt_param, prompt_input, prompt, output,
    # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
    save_dir=output_save_dir,
    save_txt="update_public_reputation_record.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]






def run_gpt_prompt_sign_up_update_target_publicreputation_record(target_persona, content, output_save_dir, role):
    def create_prompt_input(target_persona, content, role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role)
        prompt_input += [target_previous_public_reputation]
        # !<INPUT 3>!: -- provided public reputation content
        prompt_input += [content]

        return prompt_input
    
    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/sign_up_with_publicreputation/sign_up_update_target_publicreputation_numerical_record.txt"
    prompt_input = create_prompt_input(
        target_persona, content, role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, target_persona, gpt_param, prompt_input, prompt, output,
    # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
    save_dir=output_save_dir,
    save_txt="update_public_reputation_record.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]






def run_gpt_prompt_investment_update_target_publicreputation_record(target_persona, content, output_save_dir, target_persona_role):
    def create_prompt_input(target_persona, content, target_persona_role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
        prompt_input += [target_previous_public_reputation]
        prompt_input += [content]
        prompt_input += [target_persona_role.capitalize()]
        prompt_input += [target_persona_role]

        return prompt_input
    
    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/investment_with_publicreputation/investment_update_target_publicreputation_numerical_record.txt"
    prompt_input = create_prompt_input(
        target_persona, content, target_persona_role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, target_persona, gpt_param, prompt_input, prompt, output,
    # save_dir="task/pd_game_without_gossip/output_with_publicreputation",
    save_dir=output_save_dir,
    save_txt="investment_update_target_publicreputation_numerical_record.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]





def run_gpt_prompt_pd_game_update_target_publicreputation_record_with_gossip(target_persona, content, role):
    def create_prompt_input(target_persona, content, role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role)
        prompt_input += [target_previous_public_reputation]
        # !<INPUT 3>!: -- provided public reputation content
        prompt_input += [content]

        return prompt_input
    
    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res

    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_update_target_publicreputation_numerical_record.txt"
    prompt_input = create_prompt_input(
        target_persona, content, role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_single(prompt_template, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir="task/pd_game/output_with_publicreputation",
    save_txt="update_public_reputation_record.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]






def run_gpt_prompt_pd_game_update_target_publicreputation(init_persona, target_persona, update_info, role):
    """因为是PD， 所以是一对一对进行博弈，只需要考虑单个输入就好了， 而且增加博弈结果"""
    def create_prompt_input(init_persona, target_persona, update_info, role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [init_persona.scratch.name]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role)
        prompt_input += [target_previous_public_reputation]
        prompt_input += [update_info]
        reporter_public_reputation = publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, role)
        prompt_input += [reporter_public_reputation]
        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res


    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_update_target_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona, 
        target_persona, 
        update_info,
        role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir="task/pd_game_without_gossip/output_with_publicreputation",
    save_txt="generate_or_update_public_reputation.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_pd_game_update_target_publicreputation_with_buffer(init_persona, target_persona, update_info, role):
    """因为是PD， 所以是一对一对进行博弈，只需要考虑单个输入就好了， 而且增加博弈结果"""
    def create_prompt_input(init_persona, target_persona, update_info, role):
        prompt_input = []
        prompt_input += [target_persona.scratch.name]
        prompt_input += [target_persona.scratch.ID]
        prompt_input += [init_persona.scratch.name]
        target_previous_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role)
        prompt_input += [target_previous_public_reputation]
        prompt_input += [update_info]
        reporter_public_reputation = publicreputationDB.get_target_public_reputation(init_persona.scratch.ID, role)
        prompt_input += [reporter_public_reputation]
        return prompt_input

    def __func_validate(gpt_response, prompt=None):
        try:
            if __func_clean_up(gpt_response, prompt):
                return True
            return False
        except Exception as e:
            print(e)
            return False

    def __func_clean_up(gpt_response, prompt=None):
        # json format
        response = gpt_response.split("</think>")[-1].strip()
        response = response.split("```json")[-1].split("```")[0].strip()
        print(response)
        open_braces = response.count('{')
        close_braces = response.count('}')
        if close_braces > open_braces and response.endswith('}'):
            response = response[:-1].strip()   
        res = json.loads(response)
        return res


    def get_fail_safe():
        fs = "Error"
        return fs

    gpt_param = {
        
        # "engine": "qwen3-235b",
        # "engine": "qwen3-235b",
        "engine": "gpt-4o-mini",
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    }

    prompt_template = "prompt/pd_game_with_publicreputation/pd_game_update_target_publicreputation.txt"
    prompt_input = create_prompt_input(
        init_persona, 
        target_persona, 
        update_info,
        role
    )
    prompt = generate_prompt_role_play_false(prompt_input, prompt_template, role_play=False)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe, __func_validate, __func_clean_up)
    
    print_run_prompts(prompt_template, target_persona, gpt_param, prompt_input, prompt, output)
    save_run_prompts_pair(prompt_template, init_persona, target_persona, gpt_param, prompt_input, prompt, output,
    save_dir="task/pd_game_without_gossip/output_with_publicreputation",
    save_txt="pd_game_update_target_publicreputation.txt")
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]

