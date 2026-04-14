import random

random.seed(42)
from decimal import Decimal
from reputation.gossip import first_order_gossip, first_order_gossip_with_publicreputation
from reputation.prompt_template.run_gpt_prompt import (
    run_gpt_prompt_gossip_listener_select_v2,
    run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation
)
from reputation.reputation_update import reputation_update_invest, reputation_update_invest_with_publiceputation
from reputation.social_network import *
from .prompt_template.run_gpt_prompt import *
from public_reputation.SharedPublicReputationDB import publicreputationDB
import re

from task.pd_game.game_statistics import *
import random

def pair_each(personas, G, output_save_dir):
    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    investor_list = []
    trustee_list = []
    score_list = []

    for i in range(0, len(personas_keys), 2):
        investor_list.append(personas_keys[i])
        trustee_list.append(personas_keys[i + 1])
        score = get_reputation_score(personas[personas_keys[i]], "investor", personas)
        score_list.append(score)

    sorted_indices = sorted(range(len(score_list)), key=lambda k: score_list[k], reverse=True)
    investor_list = [investor_list[i] for i in sorted_indices]
    remaining_trustees = set(trustee_list)
    for investor_name in investor_list:
        chosen_trustee = None
        investor_persona = personas[investor_name]
        if not remaining_trustees:
            break

        allowed_trustees = []
        for t_name in remaining_trustees:
            t_persona = personas[t_name]
            if [t_persona.scratch.name, "trustee"] not in investor_persona.scratch.relationship["black_list"]:
                allowed_trustees.append(t_name)
        
        if not allowed_trustees:
            allowed_trustees = list(remaining_trustees)

        use_reputation = random.random() < 0.5
        if use_reputation:
            s_connect_list = get_s_connect(investor_persona, G["trustee"])
            available_neighbors = [n for n in s_connect_list if n in allowed_trustees]
            target_pool = available_neighbors if available_neighbors else allowed_trustees
            learned = investor_persona.scratch.learned
            repu_list_str = ""

            for target_name in target_pool:
                target_persona = personas[target_name]
                repu = investor_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "trustee")                
                if repu and len(repu) > 0:
                    content = list(repu.values())[0]["content"]
                else:
                    content = "No private interaction history."                    
                repu_list_str += f"{target_persona.scratch.name}:{content}\n"

            for _ in range(2):
                try:
                    result, _ = run_gpt_prompt_select_trustee(investor_persona, learned, repu_list_str, output_save_dir)
                    if result in target_pool:
                        chosen_trustee = result
                        break
                    else:
                        print(f"GPT chose {result}, but not in target pool. Retrying...")
                except Exception as e:
                    print(f"GPT Error: {e}")

        if chosen_trustee is None:
            chosen_trustee = random.choice(allowed_trustees)         
        pairs.append((investor_name, chosen_trustee))
        remaining_trustees.remove(chosen_trustee)

    print(f"Generated {len(pairs)} investor-trustee pairs: {pairs}")
    return pairs



def pair_each_with_publicreputation(personas, G, output_save_dir):

    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    investor_list = []
    trustee_list = []
    score_list = []

    for i in range(0, len(personas_keys), 2):
        investor_list.append(personas_keys[i])
        trustee_list.append(personas_keys[i + 1])
        score = get_public_reputation_score(personas[personas_keys[i]], "investor")
        score_list.append(score)

    sorted_indices = sorted(range(len(score_list)), key=lambda k: score_list[k], reverse=True)
    investor_list = [investor_list[i] for i in sorted_indices]
    remaining_trustees = set(trustee_list)

    for i, investor_name in enumerate(investor_list):
        chosen_trustee = None
        investor_persona = personas[investor_name]
        if not remaining_trustees:
            break
        allowed_trustees = []
        for t_name in remaining_trustees:
            t_persona = personas[t_name]
            if [t_persona.scratch.name, "trustee"] not in investor_persona.scratch.relationship["black_list"]:
                allowed_trustees.append(t_name)
        if not allowed_trustees:
            allowed_trustees = list(remaining_trustees)

        use_reputation = random.random() < 0.5
        if use_reputation:            
            s_connect_list = get_s_connect(investor_persona, G["trustee"])
            available_neighbors = [n for n in s_connect_list if n in allowed_trustees]            
            target_pool = available_neighbors if available_neighbors else allowed_trustees
            learned = investor_persona.scratch.learned
            repu_list_str = ""
            public_repu_list_str = ""

            for target_name in target_pool:
                target_persona = personas[target_name]
                # Private Reputation
                repu = investor_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "trustee")
                content = list(repu.values())[0]["content"] if repu else "No private interaction history."
                repu_list_str += f"{target_persona.scratch.name}: {content}\n"

                # Public Reputation
                public_repu = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, "trustee")
                player_key = f"Trustee_{target_persona.scratch.ID}" 
                content_val = public_repu.get(player_key, {}).get("content", "No public reputation data available") if public_repu else "No data"
                public_repu_list_str += f"{target_persona.scratch.name}: {content_val}\n"

            for _ in range(2):
                try:
                    result, _ = run_gpt_prompt_select_trustee_with_publicreputation(
                        investor_persona, 
                        learned, 
                        repu_list_str, 
                        public_repu_list_str, 
                        output_save_dir
                    )
                    if result in target_pool:
                        chosen_trustee = result
                        break
                    else:
                        print(f"GPT chose {result}, but not in target pool. Retrying...")
                except Exception as e:
                    print(f"GPT Error: {e}")
        if chosen_trustee is None:
            chosen_trustee = random.choice(allowed_trustees)

        pairs.append((investor_name, chosen_trustee))
        remaining_trustees.remove(chosen_trustee)

    print(f"Generated {len(pairs)} investor-trustee pairs: {pairs}")
    return pairs

def check_if_chosen(pairs, trustee_name):
    for pair in pairs:
        if trustee_name in pair:
            return True
    return False


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list


def get_s_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            d_connect_list.append(edge[1])
    return d_connect_list

def get_reputation_score(target_persona, target_persona_role, personas):
    count = 0
    num = 0
    for _, persona in personas.items():
        reputation = persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        if reputation:
            count += 1
            repu_record = reputation[f"{target_persona_role.capitalize()}_{target_persona.scratch.ID}"]["numerical record"]
            if isinstance(repu_record, str):
                raw_chunks = re.findall(r'-?[\d\.]+', repu_record)
                scores = []
                for chunk in raw_chunks:
                    if chunk == '.' or chunk == '-': continue
                    if chunk.count('.') > 1:
                        first_dot = chunk.find('.')
                        chunk = chunk[:first_dot+1] + chunk[first_dot+1:].replace('.', '')
                    try:
                        scores.append(float(chunk))
                    except: continue
            elif isinstance(repu_record, (list, tuple)):
                scores = [float(x) for x in repu_record]
            else:
                continue
            score = scores[4] + scores[3] - scores[1] - scores[0]
            if score > 1:
                score = 1
            elif score < -1:
                score = -1
            num += score
    if count == 0:
        return 0
    return round((num / count), 3)



def get_public_reputation_score(target_persona, target_persona_role):
    publicreputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, target_persona_role)
    if publicreputation:
        repu_record = publicreputation[f"{target_persona_role.capitalize()}_{target_persona.scratch.ID}"]["numerical record"]
        if isinstance(repu_record, str):
            raw_chunks = re.findall(r'-?[\d\.]+', repu_record)
            scores = []
            for chunk in raw_chunks:
                if chunk == '.' or chunk == '-': continue 
                if chunk.count('.') > 1:
                    first_dot = chunk.find('.')
                    chunk = chunk[:first_dot+1] + chunk[first_dot+1:].replace('.', '')
                try:
                    scores.append(float(chunk))
                except: continue
        elif isinstance(repu_record, (list, tuple)):
            scores = [float(x) for x in repu_record]
        else:
            return 0
        score = scores[4] + scores[3] - scores[1] - scores[0]
        if score > 1:
            score = 1
        elif score < -1:
            score = -1
    else:
        score = 0
    return score


def update_all_personas_observation_memory(personas, info):
    for persona_name, persona in personas.items():
        persona.update_observation_memory(info["name"], info["role"], info["memory"])


def known_personas_list(persona, role):
    known_investor_repus = persona.reputationDB.get_all_reputations(role, persona.scratch.ID)
    known_list = []
    for repu in known_investor_repus.values():
        if repu["name"] not in known_list:
            known_list.append(repu["name"])
    return known_list


def update_knowns_reputation_observation(personas, save_folder):
    os.makedirs(save_folder, exist_ok=True)
    parent_sim_path = os.path.dirname(os.path.dirname(save_folder))
    output_save_dir = os.path.join(parent_sim_path, "investment")

    for persona_name, persona in personas.items():
        known_investor = known_personas_list(persona, "investor")
        known_trustee = known_personas_list(persona, "trustee")
        for known in known_investor:
            observe_mem = persona.get_observation_memory(known, "investor")
            if observe_mem:
                update_info = {
                    "reason": "observed",
                    "interaction_memory": observe_mem,
                    "target_persona_role": "investor",
                    "init_persona_role": "trustee",
                }
                reputation_update_invest(
                    output_save_dir,
                    persona,
                    personas[known],
                    update_info,
                )
                social_network_update_after_observed_invest(output_save_dir, persona, personas[known], update_info)

        for known in known_trustee:
            observe_mem = persona.get_observation_memory(known, "trustee")
            if observe_mem:
                update_info = {
                    "reason": "observed",
                    "interaction_memory": observe_mem,
                    "target_persona_role": "trustee",
                    "init_persona_role": "investor",
                }
                reputation_update_invest(
                    output_save_dir,
                    persona,
                    personas[known],
                    update_info,
                )
                social_network_update_after_observed_invest(output_save_dir, persona, personas[known], update_info)

        persona.clear_observation_memory()





def update_knowns_reputation_observation_with_publicreputation(personas, output_save_dir):
    for persona_name, persona in personas.items():
        known_investor = known_personas_list(persona, "investor")
        known_trustee = known_personas_list(persona, "trustee")
        for known in known_investor:
            observe_mem = persona.get_observation_memory(known, "investor")
            if observe_mem:
                update_info = {
                    "reason": "observed",
                    "interaction_memory": observe_mem,
                    "target_persona_role": "investor",
                    "init_persona_role": "trustee",
                }
                reputation_update_invest_with_publiceputation(
                    persona,
                    personas[known],
                    update_info,
                    output_save_dir,
                )
                social_network_update_after_observed_invest_with_publicreputation(persona, personas[known], update_info, output_save_dir)

        for known in known_trustee:
            observe_mem = persona.get_observation_memory(known, "trustee")
            if observe_mem:
                update_info = {
                    "reason": "observed",
                    "interaction_memory": observe_mem,
                    "target_persona_role": "trustee",
                    "init_persona_role": "investor",
                }
                reputation_update_invest_with_publiceputation(
                    persona,
                    personas[known],
                    update_info,
                    output_save_dir,
                )
                social_network_update_after_observed_invest_with_publicreputation(persona, personas[known], update_info, output_save_dir)

        persona.clear_observation_memory()



def start_investment(pair, personas, G, stats_collector, version, save_folder):
    os.makedirs(save_folder, exist_ok=True)
    parent_sim_path = os.path.dirname(os.path.dirname(save_folder))
    output_save_dir = os.path.join(parent_sim_path, "investment")
    

    # 初始化中间变量
    success_or_not = 0
    allocating_agreement = None
    
    # # 辅助变量，防止后续打印报错
    # trustee_part = "None" 
    # investor_part = "None"
    # reported_investment_outcome = "None"
    # trustee_allocation_part = 0
    # investor_allocation_part = 0

    print_stage1 = None
    print_stage3 = None
    print_stage4 = None

    
    # the pair[0] is investor and the pair[1] is trustee
    investor = personas[pair[0]]
    trustee = personas[pair[1]]

    if [trustee.name, "trustee"] in investor.scratch.relationship["black_list"] or [
        investor.name,
        "investor",
    ] in trustee.scratch.relationship["black_list"]:
        print_stage1 = {
            "plan": "There is no plan for this investment because both parties might be on each other's blacklist.",
            "investor_decided": "Refuse. The investors refused because the parties might be on each other's blacklist.",
        }
        trustee_plan = print_stage1["plan"]
        investor_decided = print_stage1["investor_decided"]
    else:
        # stage 1
        trustee_plan = run_gpt_prompt_trustee_plan_v1(output_save_dir, trustee, investor, verbose=True)[0]
        if "error" in trustee_plan.lower():
            raise Exception("GPT ERROR")
        # Negotiation - Trustee proposes a plan for resource allocation and profit sharing

        trustee_part = trustee_plan.lower().split("trustee retains")[-1].split(".")[0].strip()

        investor_part = trustee_plan.lower().split("investor receives")[-1].split("of")[0].strip()

        investor_decided = run_gpt_prompt_investor_decided_v1(output_save_dir, investor, trustee, trustee_plan, verbose=True)[0]
        if "error" in investor_decided.lower():
            raise Exception("GPT ERROR")

        print_stage1 = {
            "plan": f"trustee_part: {trustee_part}, investor_part: {investor_part}",
            "investor_decided": investor_decided,
        }

    if "Refuse" in investor_decided:
        # total investment num +1
        investor.scratch.total_num_investor += 1
        trustee.scratch.total_num_trustee += 1
        description = f"Failed investment. Investor is {investor.name} and Trustee is {trustee.name}.\nInvestor's decision and explanation:{investor_decided}"
        investor.associativeMemory.add_event(
            subject=investor.name,
            predicate="investment",
            obj=trustee.name,
            description=description,
            created_at=investor.scratch.curr_step,
        )
        trustee.associativeMemory.add_event(
            subject=trustee.name,
            predicate="investment",
            obj=investor.name,
            description=description,
            created_at=investor.scratch.curr_step,
        )

        full_investment = False
        update_info_investor = {"target_behavior_summary": description}
        update_info_trustee = {"target_behavior_summary": description}
        social_network_update(
            investor,
            trustee,
            "investor",
            "trustee",
            output_save_dir,
            update_info=update_info_investor,
            full_investment=full_investment,
        )
        social_network_update(
            trustee,
            investor,
            "trustee",
            "investor",
            output_save_dir,
            update_info=update_info_trustee,
            full_investment=full_investment,
        )
        investor.update_interaction_memory(role="investor", memory=description)
        trustee.update_interaction_memory(role="trustee", memory=description)
        trustee_gossip_willing = run_gpt_prompt_stage1_trustee_gossip_willing_v1(
            output_save_dir,
            trustee,
            trustee_plan,                                                                                                                                                                                                                             
            investor_decided.split("Refuse.")[-1].strip(),
            investor,
            verbose=True,
        )[0]
        investor_gossip_willing = run_gpt_prompt_stage1_investor_gossip_willing_v1(
            output_save_dir,
            investor,
            trustee_plan,
            investor_decided.split("Refuse.")[-1].strip(),
            verbose=True,
        )[0]

        if "error" in trustee_gossip_willing.lower() or "error" in investor_gossip_willing.lower():
            raise Exception("GPT ERROR")

        if "yes" in trustee_gossip_willing.split(",")[0].lower():
            trustee.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": investor.scratch.ID,
                    "complaint_target": investor.name,
                    "complaint_target_role": "investor",
                    "complaint_reason": ",".join(trustee_gossip_willing.split(",")[1:]),
                }
            )
        if "yes" in investor_gossip_willing.split(",")[0].lower():
            investor.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": trustee.scratch.ID,
                    "complaint_target": trustee.name,
                    "complaint_target_role": "trustee",
                    "complaint_reason": ",".join(investor_gossip_willing.split(",")[1:]),
                }
            )

        print_stage3 = None
        print_stage4 = {
            "trustee_gossip_willing": trustee_gossip_willing,
            "investor_gossip_willing": investor_gossip_willing,
        }

    elif "Accept" in investor_decided:
        # success investment num +1
        investor.scratch.total_num_investor += 1
        trustee.scratch.total_num_trustee += 1
        investor.scratch.success_num_investor += 1
        trustee.scratch.success_num_trustee += 1

        # stage 2
        a_unit = round(float(investor_decided.split("Allocation")[-1].split("unit")[0].strip()), 3)
        investor.scratch.resources_unit -= a_unit
        # k is 2
        k = 2
        unallocated_unit = a_unit * k

        # stage 3
        trustee_allocation = run_gpt_prompt_trustee_stage_3_actual_allocation_v1(output_save_dir, trustee, investor, trustee_plan, a_unit, k, unallocated_unit, verbose=True)[0]
        if "error" in str(trustee_allocation).lower(): raise Exception("GPT ERROR: Trustee Allocation")
        
        # actual
        trustee_allocation_part = k * float(trustee_allocation["Final Allocation"].split("receives")[1].split("%")[0].strip()) * a_unit / 100
        investor_allocation_part = k * float(trustee_allocation["Final Allocation"].split("receives")[-1].split("%")[0].strip()) * a_unit / 100

        # agreement
        # trustee_part = trustee_plan.lower().split("trustee retains")[-1].split(".")[0].strip()
        # investor_part = trustee_plan.lower().split("investor receives")[-1].split("of")[0].strip()
        trustee_part = float(trustee_part.split("%")[0].strip())
        investor_part = float(investor_part.split("%")[0].strip())
        plan_trustee_allocation_part = trustee_part * unallocated_unit / 100
        plan_investor_allocation_part = investor_part * unallocated_unit / 100
        

        # trustee_allocation_part = float(trustee_allocation["Final Allocation"].split("receives")[1].split("%")[0].strip())
        # investor_allocation_part = float(trustee_allocation["Final Allocation"].split("receives")[-1].split("%")[0].strip())
        
        # divide the resources
        trustee.scratch.resources_unit += trustee_allocation_part
        investor.scratch.resources_unit += investor_allocation_part

        reported_investment_outcome = trustee_allocation["reported_investment_outcome"]
        # print("trustee_allocation_part:" + str(trustee_allocation_part))
        # print("investor_allocation_part:" + str(investor_allocation_part))
        # print("reported_investment_outcome:" + str(reported_investment_outcome))

        try:
            trustee_is_match = abs(plan_trustee_allocation_part - trustee_allocation_part) < 0.001
            investor_is_match = abs(plan_investor_allocation_part - investor_allocation_part) < 0.001
            allocating_agreement = 1 if (trustee_is_match and investor_is_match)  else 0 
            investment_success_or_not = "Success" if (trustee_is_match and investor_is_match)  else "Failed"
        except:
            allocating_agreement = 0
            investment_success_or_not = "Failed"

        event_description = (
            # f"Success investment: investor is {investor.name}, trustee is {trustee.name}\n"
            f"{investment_success_or_not} investment: investor is {investor.name}, trustee is {trustee.name}\n"
            f"stage 1: trustee_plan is {trustee_plan}\n"
            f"stage 2: investor invests {a_unit} units\n"
            f"stage 3: trustee_allocation is {trustee_allocation}, and reported_investment_outcome is {reported_investment_outcome}"
        )
        investor.associativeMemory.add_event(
            subject=investor.name,
            predicate="investment",
            obj=trustee.name,
            description=event_description,
            created_at=investor.scratch.curr_step,
        )
        trustee.associativeMemory.add_event(
            subject=trustee.name,
            predicate="investment",
            obj=investor.name,
            description=event_description,
            created_at=investor.scratch.curr_step,
        )
        print_stage3 = {
            "investor_actual_allocation_part": investor_allocation_part,
            "trustee_actual_allocation_part": trustee_allocation_part,
            "reported_investment_outcome": reported_investment_outcome,
        }

        # stage 4
        investor_evaluation = run_gpt_prompt_stage4_investor_evaluation_v1(
            output_save_dir,
            investor,
            trustee,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_plan,
            trustee_allocation,
            reported_investment_outcome,
            verbose=True,
        )[0]
        trustee_evaluation = run_gpt_prompt_stage4_trustee_evaluation_v1(
            output_save_dir,
            trustee,
            investor,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_part,
            investor_part,
            reported_investment_outcome,
            trustee_allocation_part,
            investor_allocation_part,
            reflection=investor_evaluation["trustee_reputation"],
            verbose=True,
        )[0]
        full_investment = True
        if type(investor_evaluation) is str and "error" in investor_evaluation.lower():
            raise Exception("GPT ERROR")
        if type(trustee_evaluation) is str and "error" in trustee_evaluation.lower():
            raise Exception("GPT ERROR")

        # reputation update agter stage 4
        update_info_investor = {
            "reason": "reputation update agter stage 4",
            "init_persona_role": "investor",
            "init_behavior_summary": investor_evaluation["self_reputation"],
            "target_behavior_summary": investor_evaluation["trustee_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(trustee, G["trustee"])),
        }
        update_info_trustee = {
            "reason": "reputation update agter stage 4",
            "init_persona_role": "trustee",
            "init_behavior_summary": trustee_evaluation["self_reputation"],
            "target_behavior_summary": trustee_evaluation["investor_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(investor, G["investor"])),
        }
        update_all_personas_observation_memory(
            personas,
            {
                "name": trustee.name,
                "role": "trustee",
                "memory": update_info_investor["target_behavior_summary"],
            },
        )
        update_all_personas_observation_memory(
            personas,
            {
                "name": investor.name,
                "role": "investor",
                "memory": update_info_trustee["target_behavior_summary"],
            },
        )
        reputation_update_invest(output_save_dir, investor, trustee, update_info_investor, full_investment=full_investment)
        reputation_update_invest(output_save_dir, trustee, investor, update_info_trustee, full_investment=full_investment)

        investor.update_interaction_memory(role="investor", memory=update_info_investor["target_behavior_summary"])
        trustee.update_interaction_memory(role="trustee", memory=update_info_trustee["target_behavior_summary"])

        trustee_gossip_willing = run_gpt_prompt_stage4_trustee_gossip_v1(
            output_save_dir,
            trustee,
            investor,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_part,
            investor_part,
            reported_investment_outcome,
            trustee_allocation_part,
            investor_allocation_part,
            trustee_evaluation["investor_reputation"],
            verbose=True,
        )[0]
        investor_gossip_willing = run_gpt_prompt_stage4_investor_gossip_v1(
            output_save_dir,
            investor,
            trustee,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_part,
            investor_part,
            reported_investment_outcome,
            trustee_allocation_part,
            investor_allocation_part,
            investor_evaluation["trustee_reputation"],
            verbose=True,
        )[0]

        if "error" in trustee_gossip_willing.lower() or "error" in investor_gossip_willing.lower():
            raise Exception("GPT ERROR")

        if "yes" in trustee_gossip_willing.split(",")[0].lower():
            trustee.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": investor.scratch.ID,
                    "complaint_target": investor.name,
                    "complaint_target_role": "investor",
                    "complaint_reason": ",".join(trustee_gossip_willing.split(",")[1:]),
                }
            )
        if "yes" in investor_gossip_willing.split(",")[0].lower():
            investor.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": trustee.scratch.ID,
                    "complaint_target": trustee.name,
                    "complaint_target_role": "trustee",
                    "complaint_reason": ",".join(investor_gossip_willing.split(",")[1:]),
                }
            )
        print_stage4 = {
            "trustee_gossip_willing": trustee_gossip_willing,
            "investor_gossip_willing": investor_gossip_willing,
        }
    oppent = {"investor": "trustee", "trustee": "investor"}
    # gossip stage
    if investor.scratch.complain_buffer:
        for person in investor.scratch.complain_buffer:
            if person["complaint_target_role"] == "trustee":
                # gossip target choose
                gossip_target_investor = run_gpt_prompt_gossip_listener_select_v2(investor, "investor", personas[person["complaint_target"]], output_save_dir)[0]
            else:
                gossip_target_investor = run_gpt_prompt_gossip_listener_select_v2(investor, "trustee", personas[person["complaint_target"]], output_save_dir)[0]
            for gossip_target in gossip_target_investor:
                # gossip chat
                gossip_target_persona = personas[gossip_target]
                first_order_gossip(
                    investor,
                    gossip_target_persona,
                    oppent[person["complaint_target_role"]],
                    person["complaint_target_role"],
                    personas,
                    G,
                    output_save_dir,
                    val=person,
                )

    if trustee.scratch.complain_buffer:
        for person in trustee.scratch.complain_buffer:
            # gossip target choose
            if person["complaint_target_role"] == "trustee":
                gossip_target_trustee = run_gpt_prompt_gossip_listener_select_v2(trustee, "investor", personas[person["complaint_target"]], output_save_dir)[0]
            else:
                gossip_target_trustee = run_gpt_prompt_gossip_listener_select_v2(trustee, "trustee", personas[person["complaint_target"]], output_save_dir)[0]
            for gossip_target in gossip_target_trustee:
                # gossip chat
                gossip_target_persona = personas[gossip_target]
                first_order_gossip(
                    trustee,
                    gossip_target_persona,
                    oppent[person["complaint_target_role"]],
                    person["complaint_target_role"],
                    personas,
                    G,
                    output_save_dir,
                    val=person,
                )




    # curr_step = investor.scratch.curr_step              
    # # round_idx, player_name, success_num, total_num, private_rep, public_rep, version, target_persona_role, allocating_agreement, success_or_not
    # stats_collector.log_player_investment(
    #     round_idx=curr_step,
    #     player_name=investor.scratch.name,
    #     success_num=investor.scratch.success_num_investor,
    #     total_num=investor.scratch.total_num_investor,
    #     version=version,
    #     target_persona_role="investor",
    #     allocating_agreement=allocating_agreement,
    #     success_or_not=success_or_not
    # )
    
    # # round_idx, player_name, success_num, total_num, private_rep, public_rep, version, target_persona_role, allocating_agreement, success_or_not
    # stats_collector.log_player_investment(
    #     round_idx=curr_step,
    #     player_name=trustee.scratch.name,
    #     success_num=trustee.scratch.success_num_trustee,
    #     total_num=trustee.scratch.total_num_trustee,
    #     version=version,
    #     target_persona_role="trustee",
    #     allocating_agreement=allocating_agreement,
    #     success_or_not=success_or_not
    # )
    print_investment_result(investor, trustee, print_stage1, print_stage3, print_stage4, save_folder)


import os
import traceback

def start_investment_with_publicreputation(pair, personas, G, stats_collector, version, save_folder):

    os.makedirs(save_folder, exist_ok=True)
    parent_sim_path = os.path.dirname(os.path.dirname(save_folder))
    output_save_dir = os.path.join(parent_sim_path, "investment_with_publicreputation")
    
    # the pair[0] is investor and the pair[1] is trustee
    investor = personas[pair[0]]
    trustee = personas[pair[1]]

    success_or_not = 0          # Stage 1 (0: Fail, 1: Success)
    was_stage3_reached = 0      # Stage 3 (0: No, 1: Yes)
    allocating_agreement = 0    # Stage 3 (0: No/Not reached, 1: Yes)
    print_stage1 = None
    print_stage3 = None
    print_stage4 = None
    

    # --- Stage 1 & Blacklist Check ---
    if [trustee.name, "trustee"] in investor.scratch.relationship["black_list"] or [
        investor.name,
        "investor",
    ] in trustee.scratch.relationship["black_list"]:
        print_stage1 = {
            "plan": "There is no plan for this investment because both parties might be on each other's blacklist.",
            "investor_decided": "Refuse. The investors refused because the parties might be on each other's blacklist.",
        }
        trustee_plan = print_stage1["plan"]
        investor_decided = print_stage1["investor_decided"]
    else:
        # stage 1
        
        # add public
        trustee_plan = run_gpt_prompt_trustee_plan_v1_with_publicreputation(trustee, investor, output_save_dir, verbose=True)[0]
        if "error" in trustee_plan.lower():
            raise Exception("GPT ERROR: Trustee Plan")
        # Negotiation - Trustee proposes a plan for resource allocation and profit sharing

        trustee_part = trustee_plan.lower().split("trustee retains")[-1].split(".")[0].strip()
        investor_part = trustee_plan.lower().split("investor receives")[-1].split("of")[0].strip()

        # add public
        investor_decided = run_gpt_prompt_investor_decided_v1_with_publicreputation(investor, trustee, trustee_plan, output_save_dir, verbose=True)[0]
        
        if "error" in investor_decided.lower():
            raise Exception("GPT ERROR: Investor Decision")

        print_stage1 = {
            "plan": f"trustee_part: {trustee_part}, investor_part: {investor_part}",
            "investor_decided": investor_decided,
        }

    if "Accept" in investor_decided:
        success_or_not = 1
        was_stage3_reached = 1
        # success investment num +1
        investor.scratch.total_num_investor += 1
        trustee.scratch.total_num_trustee += 1
        investor.scratch.success_num_investor += 1
        trustee.scratch.success_num_trustee += 1
    else:
        success_or_not = 0
        # total investment num +1 
        investor.scratch.total_num_investor += 1
        trustee.scratch.total_num_trustee += 1

    if "Refuse" in investor_decided:
        # total investment num +1
        investor.scratch.total_num_investor += 1
        trustee.scratch.total_num_trustee += 1
    # if success_or_not == 0:
        # Refuse Branch
        description = f"Failed investment. Investor is {investor.name} and Trustee is {trustee.name}.\nInvestor's decision and explanation:{investor_decided}"
        investor.associativeMemory.add_event(
            subject=investor.name,
            predicate="investment",
            obj=trustee.name,
            description=description,
            created_at=investor.scratch.curr_step,
        )
        trustee.associativeMemory.add_event(
            subject=trustee.name,
            predicate="investment",
            obj=investor.name,
            description=description,
            created_at=investor.scratch.curr_step,
        )

        full_investment = False
        update_info_investor = {"target_behavior_summary": description}
        update_info_trustee = {"target_behavior_summary": description}

        # add public 
        social_network_update_with_publicreputation(
            investor,
            trustee,
            "investor",
            "trustee",
            output_save_dir,
            update_info=update_info_investor,
            full_investment=full_investment,
        )
        social_network_update_with_publicreputation(
            trustee,
            investor,
            "trustee",
            "investor",
            output_save_dir,
            update_info=update_info_trustee,
            full_investment=full_investment,
        )
        investor.update_interaction_memory(role="investor", memory=description)
        trustee.update_interaction_memory(role="trustee", memory=description)

        trustee_gossip_willing = run_gpt_prompt_stage1_trustee_gossip_willing_v1(
            output_save_dir,
            trustee,
            trustee_plan,
            investor_decided.split("Refuse.")[-1].strip(),
            investor,
            verbose=True,
        )[0]
        investor_gossip_willing = run_gpt_prompt_stage1_investor_gossip_willing_v1(
            output_save_dir,
            investor,
            trustee_plan,
            investor_decided.split("Refuse.")[-1].strip(),
            verbose=True,
        )[0]

        if "error" in trustee_gossip_willing.lower() or "error" in investor_gossip_willing.lower():
            raise Exception("GPT ERROR: Gossip Willingness Stage 1")

        if "yes" in trustee_gossip_willing.split(",")[0].lower():
            trustee.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": investor.scratch.ID,
                    "complaint_target": investor.name,
                    "complaint_target_role": "investor",
                    "complaint_reason": ",".join(trustee_gossip_willing.split(",")[1:]),
                }
            )
        if "yes" in investor_gossip_willing.split(",")[0].lower():
            investor.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": trustee.scratch.ID,
                    "complaint_target": trustee.name,
                    "complaint_target_role": "trustee",
                    "complaint_reason": ",".join(investor_gossip_willing.split(",")[1:]),
                }
            )

        print_stage3 = None
        print_stage4 = {
            "trustee_gossip_willing": trustee_gossip_willing,
            "investor_gossip_willing": investor_gossip_willing,
        }

        # print_stage4 = None
    elif "Accept" in investor_decided:
        # success investment num +1
        investor.scratch.total_num_investor += 1
        trustee.scratch.total_num_trustee += 1
        investor.scratch.success_num_investor += 1
        trustee.scratch.success_num_trustee += 1

    # elif success_or_not == 1:
        # Accept Branch
        
        # stage 2
        a_unit = round(float(investor_decided.split("Allocation")[-1].split("unit")[0].strip()), 3)
        investor.scratch.resources_unit -= a_unit
        # k is 2
        k = 2
        unallocated_unit = a_unit * k

        # stage 3
        trustee_allocation = run_gpt_prompt_trustee_stage_3_actual_allocation_v1_with_publicreputation(trustee, investor, trustee_plan, a_unit, k, unallocated_unit, output_save_dir, verbose=True)[0]
        if "error" in str(trustee_allocation).lower(): raise Exception("GPT ERROR: Trustee Allocation")

        # actual
        trustee_allocation_part = k * float(trustee_allocation["Final Allocation"].split("receives")[1].split("%")[0].strip()) * a_unit / 100
        investor_allocation_part = k * float(trustee_allocation["Final Allocation"].split("receives")[-1].split("%")[0].strip()) * a_unit / 100

        # agreement
        # trustee_part = trustee_plan.lower().split("trustee retains")[-1].split(".")[0].strip()
        # investor_part = trustee_plan.lower().split("investor receives")[-1].split("of")[0].strip()
        trustee_part = float(trustee_part.split("%")[0].strip())
        investor_part = float(investor_part.split("%")[0].strip())
        plan_trustee_allocation_part = trustee_part * unallocated_unit / 100
        plan_investor_allocation_part = investor_part * unallocated_unit / 100
        

        # trustee_allocation_part = float(trustee_allocation["Final Allocation"].split("receives")[1].split("%")[0].strip())
        # investor_allocation_part = float(trustee_allocation["Final Allocation"].split("receives")[-1].split("%")[0].strip())
        
        # divide the resources
        trustee.scratch.resources_unit += trustee_allocation_part
        investor.scratch.resources_unit += investor_allocation_part

        reported_investment_outcome = trustee_allocation["reported_investment_outcome"]
        # print("trustee_allocation_part:" + str(trustee_allocation_part))
        # print("investor_allocation_part:" + str(investor_allocation_part))
        # print("reported_investment_outcome:" + str(reported_investment_outcome))

        try:
            trustee_is_match = abs(plan_trustee_allocation_part - trustee_allocation_part) < 0.001
            investor_is_match = abs(plan_investor_allocation_part - investor_allocation_part) < 0.001
            allocating_agreement = 1 if (trustee_is_match and investor_is_match)  else 0 
            investment_success_or_not = "Success" if (trustee_is_match and investor_is_match)  else "Failed"
        except:
            allocating_agreement = 0
            investment_success_or_not = "Failed"
        
           
        event_description = (
            # f"Success investment: investor is {investor.name}, trustee is {trustee.name}\n"
            f"{investment_success_or_not} investment: investor is {investor.name}, trustee is {trustee.name}\n"
            f"stage 1: trustee_plan is {trustee_plan}\n"
            f"stage 2: investor invests {a_unit} units\n"
            f"stage 3: trustee_allocation is {trustee_allocation}, and reported_investment_outcome is {reported_investment_outcome}"
        )
        investor.associativeMemory.add_event(
            subject=investor.name,
            predicate="investment",
            obj=trustee.name,
            description=event_description,
            created_at=investor.scratch.curr_step,
        )
        trustee.associativeMemory.add_event(
            subject=trustee.name,
            predicate="investment",
            obj=investor.name,
            description=event_description,
            created_at=investor.scratch.curr_step,
        )
        print_stage3 = {
            "investor_actual_allocation_part": investor_allocation_part,
            "trustee_actual_allocation_part": trustee_allocation_part,
            "reported_investment_outcome": reported_investment_outcome,
        }

        # stage 4
        
        investor_evaluation = run_gpt_prompt_stage4_investor_evaluation_v1(
            output_save_dir,
            investor,
            trustee,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_plan,
            trustee_allocation,
            reported_investment_outcome,
            verbose=True,
        )[0]
        trustee_evaluation = run_gpt_prompt_stage4_trustee_evaluation_v1(
            output_save_dir,
            trustee,
            investor,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_part,
            investor_part,
            reported_investment_outcome,
            trustee_allocation_part,
            investor_allocation_part,
            reflection=investor_evaluation["trustee_reputation"],
            verbose=True,
        )[0]
        
        full_investment = True
        if type(investor_evaluation) is str and "error" in investor_evaluation.lower():
            raise Exception("GPT ERROR: Investor Evaluation")
        if type(trustee_evaluation) is str and "error" in trustee_evaluation.lower():
            raise Exception("GPT ERROR: Trustee Evaluation")

        # add public report and update

        # reputation update agter stage 4
        update_info_investor = {
            "reason": "reputation update agter stage 4",
            "init_persona_role": "investor",
            "init_behavior_summary": investor_evaluation["self_reputation"],
            "target_behavior_summary": investor_evaluation["trustee_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(trustee, G["trustee"])),
        }
        update_info_trustee = {
            "reason": "reputation update agter stage 4",
            "init_persona_role": "trustee",
            "init_behavior_summary": trustee_evaluation["self_reputation"],
            "target_behavior_summary": trustee_evaluation["investor_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(investor, G["investor"])),
        }
        update_all_personas_observation_memory(
            personas,
            {
                "name": trustee.name,
                "role": "trustee",
                "memory": update_info_investor["target_behavior_summary"],
            },
        )
        update_all_personas_observation_memory(
            personas,
            {
                "name": investor.name,
                "role": "investor",
                "memory": update_info_trustee["target_behavior_summary"],
            },
        )

        reputation_update_invest_with_publiceputation(investor, trustee, update_info_investor, output_save_dir, full_investment=full_investment)
        reputation_update_invest_with_publiceputation(trustee, investor, update_info_trustee, output_save_dir, full_investment=full_investment)

        investor.update_interaction_memory(role="investor", memory=update_info_investor["target_behavior_summary"])
        trustee.update_interaction_memory(role="trustee", memory=update_info_trustee["target_behavior_summary"])

        trustee_gossip_willing = run_gpt_prompt_stage4_trustee_gossip_v1(
            output_save_dir,
            trustee,
            investor,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_part,
            investor_part,
            reported_investment_outcome,
            trustee_allocation_part,
            investor_allocation_part,
            trustee_evaluation["investor_reputation"],
            verbose=True,
        )[0]
        investor_gossip_willing = run_gpt_prompt_stage4_investor_gossip_v1(
            output_save_dir,
            investor,
            trustee,
            trustee_plan,
            a_unit,
            k,
            a_unit * k,
            trustee_part,
            investor_part,
            reported_investment_outcome,
            trustee_allocation_part,
            investor_allocation_part,
            investor_evaluation["trustee_reputation"],
            verbose=True,
        )[0]

        if "error" in trustee_gossip_willing.lower() or "error" in investor_gossip_willing.lower():
            raise Exception("GPT ERROR: Gossip Willingness Stage 4")

        if "yes" in trustee_gossip_willing.split(",")[0].lower():
            trustee.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": investor.scratch.ID,
                    "complaint_target": investor.name,
                    "complaint_target_role": "investor",
                    "complaint_reason": ",".join(trustee_gossip_willing.split(",")[1:]),
                }
            )
        if "yes" in investor_gossip_willing.split(",")[0].lower():
            investor.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": trustee.scratch.ID,
                    "complaint_target": trustee.name,
                    "complaint_target_role": "trustee",
                    "complaint_reason": ",".join(investor_gossip_willing.split(",")[1:]),
                }
            )
        print_stage4 = {
            "trustee_gossip_willing": trustee_gossip_willing,
            "investor_gossip_willing": investor_gossip_willing,
        }
    
    oppent = {"investor": "trustee", "trustee": "investor"}


    # gossip stage
    if investor.scratch.complain_buffer:
        for person in investor.scratch.complain_buffer:
            if person["complaint_target_role"] == "trustee":
                # gossip target choose
                # add public
                gossip_target_investor = run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(investor, personas[person["complaint_target"]], output_save_dir, "investor")[0]
            else:
                gossip_target_investor = run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(investor, personas[person["complaint_target"]], output_save_dir, "trustee")[0]
            for gossip_target in gossip_target_investor:
                # gossip chat
                gossip_target_persona = personas[gossip_target]
                first_order_gossip_with_publicreputation(
                    investor,
                    gossip_target_persona,
                    oppent[person["complaint_target_role"]],
                    person["complaint_target_role"],
                    personas,
                    G,
                    output_save_dir,
                    val=person,
                )

    if trustee.scratch.complain_buffer:
        for person in trustee.scratch.complain_buffer:
            # gossip target choose
            if person["complaint_target_role"] == "trustee":
                gossip_target_trustee = run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(trustee, personas[person["complaint_target"]], output_save_dir, "investor")[0]
            else:
                gossip_target_trustee = run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(trustee, personas[person["complaint_target"]], output_save_dir, "trustee")[0]
            for gossip_target in gossip_target_trustee:
                # gossip chat
                gossip_target_persona = personas[gossip_target]
                first_order_gossip_with_publicreputation(
                    trustee,
                    gossip_target_persona,
                    oppent[person["complaint_target_role"]],
                    person["complaint_target_role"],
                    personas,
                    G,
                    output_save_dir,
                    val=person,
                )

    print_investment_result(investor, trustee, print_stage1, print_stage3, print_stage4, save_folder)


def print_investment_result(investor, trustee, stage1, stage3, stage4, save_folder):
    step = investor.scratch.curr_step
    print(f"Step: {step}")
    print("+" + "-" * (100 - 2) + "+")
    print("|" + " " * 38 + "**Investment  Result**" + " " * 38 + "|")
    print("+" + "-" * (100 - 2) + "+")

    width = 100

    # stage 1
    print("+" + "-" * (100 - 2) + "+")
    print("|" + "**Stage  1**" + " " * (width - 14) + "|")
    print("+" + "-" * (100 - 2) + "+")
    trustee_line = f"| Trustee: {trustee.name}: allocated plan {stage1['plan']}"
    # trustee_line = f"| Trustee: {trustee.name}: allocated plan {stage1['plan']}"
    print("+" + "-" * (width - 2) + "+")
    print(trustee_line + " " * (width - len(trustee_line) - 1) + "|")
    investor_line = f"| Investor: {investor.name}: investor decided {stage1['investor_decided']}"
    # investor_line = f"| Investor: {investor.name}: investor decided {stage1['investor_decided']}"
    print(investor_line + " " * (width - len(investor_line) - 1) + "|")
    print("+" + "-" * (width - 2) + "+")

    if "Refuse" in stage1["investor_decided"] or "Reject" in stage1["investor_decided"]:
        print("+" + "-" * (width - 2) + "+")
        print("|" + " " * 40 + "End of Investment " + " " * 40 + "|")
        print("+" + "-" * (width - 2) + "+")
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        with open(f"{save_folder}/investment_results_{investor.scratch.curr_step}.txt", "a") as f:
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write("|" + "**Stage  1**" + " " * (width - 14) + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n")
            trustee_line = f"| Trustee: {trustee.name}: allocated plan {stage1['plan']}"
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
            investor_line = f"| Investor: {investor.name}: investor decided {stage1['investor_decided']}"
            f.write(investor_line + " " * (width - len(investor_line) - 1) + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n")

            f.write("+" + "-" * (100 - 2) + "+\n")
            f.write("|" + "** gossip **" + " " * (width - 14) + "|\n")
            f.write("+" + "-" * (100 - 2) + "+\n")
            trustee_line = f"| Trustee: {trustee.name}: gossip willing {stage4['trustee_gossip_willing']}"
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
            investor_line = f"| Investor: {investor.name}: gossip willing {stage4['investor_gossip_willing']}"
            f.write(investor_line + " " * (width - len(investor_line) - 1) + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n")

            f.write("+" + "-" * (width - 2) + "+\n")
            f.write("|" + " " * 40 + "End of Investment " + " " * 40 + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n\n\n")

        return

    # stage 3
    print("+" + "-" * (100 - 2) + "+")
    print("|" + "**Stage  3**" + " " * (width - 14) + "|")
    print("+" + "-" * (100 - 2) + "+")
    trustee_line = f"| Trustee: {trustee.name}: actual allocation {stage3['trustee_actual_allocation_part']}"
    print("+" + "-" * (width - 2) + "+")
    print(trustee_line + " " * (width - len(trustee_line) - 1) + "|")
    investor_line = f"| Investor: {investor.name}: actual allocation {stage3['investor_actual_allocation_part']}"
    print(investor_line + " " * (width - len(investor_line) - 1) + "|")
    print("+" + "-" * (width - 2) + "+")

    # stage 4
    print("+" + "-" * (100 - 2) + "+")
    print("|" + "**Stage  4**" + " " * (width - 14) + "|")
    print("+" + "-" * (100 - 2) + "+")
    trustee_line = f"| Trustee: {trustee.name}: gossip willing {stage4['trustee_gossip_willing']}"
    print("+" + "-" * (width - 2) + "+")
    print(trustee_line + " " * (width - len(trustee_line) - 1) + "|")
    investor_line = f"| Investor: {investor.name}: gossip willing {stage4['investor_gossip_willing']}"
    print(investor_line + " " * (width - len(investor_line) - 1) + "|")
    print("+" + "-" * (width - 2) + "+")

    print("+" + "-" * (width - 2) + "+")
    print("|" + " " * 40 + "End of Investment " + " " * 40 + "|")
    print("+" + "-" * (width - 2) + "+")

    # Write investment results to file
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    with open(f"{save_folder}/investment_results_{investor.scratch.curr_step}.txt", "a") as f:
        f.write("+" + "-" * (width - 2) + "+\n")
        f.write("|" + "**Stage  1**" + " " * (width - 14) + "|\n")
        f.write("+" + "-" * (width - 2) + "+\n")
        trustee_line = f"| Trustee: {trustee.name}: allocated plan {stage1['plan']}"
        f.write("+" + "-" * (width - 2) + "+\n")
        f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
        investor_line = f"| Investor: {investor.name}: investor decided {stage1['investor_decided']}"
        f.write(investor_line + " " * (width - len(investor_line) - 1) + "|\n")
        f.write("+" + "-" * (width - 2) + "+\n")

        f.write("+" + "-" * (100 - 2) + "+\n")
        f.write("|" + "**Stage  3**" + " " * (width - 14) + "|\n")
        f.write("+" + "-" * (100 - 2) + "+\n")
        trustee_line = f"| Trustee: {trustee.name}: actual allocation {stage3['trustee_actual_allocation_part']}"
        f.write("+" + "-" * (width - 2) + "+\n")
        f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
        investor_line = f"| Investor: {investor.name}: actual allocation {stage3['investor_actual_allocation_part']}"
        f.write(investor_line + " " * (width - len(investor_line) - 1) + "|\n")
        f.write("+" + "-" * (width - 2) + "+\n")

        f.write("+" + "-" * (100 - 2) + "+\n")
        f.write("|" + "** gossip **" + " " * (width - 14) + "|\n")
        f.write("+" + "-" * (100 - 2) + "+\n")
        trustee_line = f"| Trustee: {trustee.name}: gossip willing {stage4['trustee_gossip_willing']}"
        f.write("+" + "-" * (width - 2) + "+\n")
        f.write(trustee_line + " " * (width - len(trustee_line) - 1) + "|\n")
        investor_line = f"| Investor: {investor.name}: gossip willing {stage4['investor_gossip_willing']}"
        f.write(investor_line + " " * (width - len(investor_line) - 1) + "|\n")
        f.write("+" + "-" * (width - 2) + "+\n")

        f.write("+" + "-" * (width - 2) + "+\n")
        f.write("|" + " " * 40 + "End of Investment " + " " * 40 + "|\n")
        f.write("+" + "-" * (width - 2) + "+\n\n\n")
    return


def random_choice_except_current(lst, current):
    # Filter out the current element
    filtered_list = [item for item in lst if item != current]
    # Randomly select from the filtered list
    if filtered_list:  # Ensure the list is not empty
        return random.choice(filtered_list)
    else:
        return None  # Return None if there are no other elements
