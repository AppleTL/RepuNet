import random
import os
import sys
from pathlib import Path

random.seed(42)
from reputation.reputation_update import (
    reputation_update_sign_up,
    reputation_update_sign_up_with_publicreputation,
)
from reputation.gossip import first_order_gossip, first_order_gossip_with_publicreputation
from reputation.prompt_template.run_gpt_prompt import (
    run_gpt_prompt_gossip_listener_select_v2,
    run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation

)
from reputation.social_network import social_network_update_after_new_sign_up, social_network_update_after_new_sign_up_with_publicreputation

from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_decide_to_talk_v1_with_publicreputation,
    run_gpt_prompt_sign_up_v3,
    run_gpt_prompt_decide_to_talk_v1,
    run_gpt_prompt_create_chat_v1,
    run_gpt_prompt_sign_up_v3_with_publicreputation,
    run_gpt_prompt_summarize_chat_v1,
    run_gpt_prompt_willingness_to_gossip_v1,
    run_gpt_prompt_init_sign_up_v1,
    run_gpt_prompt_decide_to_talk_v1_with_publicreputation
    

)


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list


def get_ava_satisfy(ps):
    sum_s = 0
    for persona_name, persona in ps.items():
        if persona.scratch.total_chat_num == 0:
            sum_s += 0
        else:
            sum_s += persona.scratch.success_chat_num / persona.scratch.total_chat_num
    return round(sum_s / len(ps), 2)


def get_ava_num_bibd_connections(ps, G):
    sum_s = 0
    for persona_name, persona in ps.items():
        sum_s += len(get_d_connect(persona, G))
    return round(sum_s / len(ps), 2)


def chat_pair(personas):
    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    for i in range(0, len(personas_keys), 2):
        pairs.append((personas[personas_keys[i]], personas[personas_keys[i + 1]]))
        print(personas_keys[i], personas_keys[i + 1])
    return pairs


def sign_up(personas, step, save_folder, G): 
    save_m = ""
    res = f"--------------------Sign up info {step}--------------------\n"
    count = 0
    for persona_name, persona in personas.items():
        count += 1
        if step != 1:
            # output = run_gpt_prompt_sign_up_v1(persona)[0]
            output = run_gpt_prompt_sign_up_v3(persona)[0]
        else:
            output = run_gpt_prompt_init_sign_up_v1(persona)[0]
        if "error" in output.lower():
            raise Exception("GPT ERROR")
        # output_res = Yes or No
        output_res = output.split(".")[0].strip()
        save_m += f"{persona_name}: {output_res}\n"
        # res += f"{count}. {persona_name}: {output}\n"
        output_reason = ".".join(output.split(".")[1:]).strip()
        if not output_reason.startswith("<"):
            output_reason = f"<{output_reason}>"
        res += f"{count}. {persona_name}: {output_res}. {output_reason}\n"
        # TODO: Implement sign up
        # sign up info as EVENT save to memory
    res += "--------------------End of Sign up info--------------------\n\n"

    os.makedirs(save_folder, exist_ok=True)

    with open(f"{save_folder}/sign_up_results_{step}.txt", "a") as f:
        f.write(res)



    for _, persona in personas.items():
        # update sign up info to memory
        persona.associativeMemory.add_event(
            subject=persona.name,
            predicate="sign up",
            obj="All persona",
            description=save_m,
            created_at=step,
        )
        # update reputation after sign up
        repus = persona.reputationDB.get_all_reputations("resident", persona.scratch.ID)
        known_personas = [repu["name"] for _, repu in repus.items()]

        # # --- Debug ---
        # print(f"DEBUG: Step {step}, {persona.name} knows: {known_personas}")
        # # ---------------------
        for target_persona_name in known_personas:
            target_persona = personas[target_persona_name]
            update_info = {
                "reason": "reputation update after sign up",
                "total_number_of_people": len(personas),
                "number_of_bidirectional_connections": len(get_d_connect(target_persona, G["resident"])),
                "ava_num_bibd_connections": get_ava_num_bibd_connections(personas, G["resident"]),
            }
            # reputation_update_sign_up(persona, target_persona, update_info)
            reputation_update_sign_up(persona, target_persona, update_info, save_folder, step, personas)
            # social_network_update_after_new_sign_up(persona, target_persona)
            social_network_update_after_new_sign_up(persona, target_persona, save_folder, step)


def sign_up_with_publicreputation(personas, step, save_folder, output_save_dir, G, stats_collector, version): 
    save_m = ""
    res = f"--------------------Sign up info {step}--------------------\n"
    count = 0
    for persona_name, persona in personas.items():
        count += 1
        if step != 1:
            # output = run_gpt_prompt_sign_up_v1(persona)[0]

            # add public
            output = run_gpt_prompt_sign_up_v3_with_publicreputation(persona, output_save_dir)[0]
        else:

            output = run_gpt_prompt_init_sign_up_v1(persona, output_save_dir)[0]
        if "error" in output.lower():
            raise Exception("GPT ERROR")
        # output_res = Yes or No
        output_res = output.split(".")[0].strip()
        save_m += f"{persona_name}: {output_res}\n"
        # res += f"{count}. {persona_name}: {output}\n"
        output_reason = ".".join(output.split(".")[1:]).strip()
        if not output_reason.startswith("<"):
            output_reason = f"<{output_reason}>"
        res += f"{count}. {persona_name}: {output_res}. {output_reason}\n"
        # stats_collector.log_sign_up_decision(
        #     round_idx=step,
        #     player_name=persona.name,
        #     sign_up_result=sign_up_bool,
        #     version=version
        # )

        
        # TODO: Implement sign up
        # sign up info as EVENT save to memory
    res += "--------------------End of Sign up info--------------------\n\n"

    os.makedirs(save_folder, exist_ok=True)

    with open(f"{save_folder}/sign_up_results_{step}.txt", "a") as f:
        f.write(res)



    for _, persona in personas.items():
        # update sign up info to memory
        persona.associativeMemory.add_event(
            subject=persona.name,
            predicate="sign up",
            obj="All persona",
            description=save_m,
            created_at=step,
        )
        # update reputation after sign up
        repus = persona.reputationDB.get_all_reputations("resident", persona.scratch.ID)
        known_personas = [repu["name"] for _, repu in repus.items()]

        # # --- Debug ---
        # print(f"DEBUG: Step {step}, {persona.name} knows: {known_personas}")
        # # ---------------------
        for target_persona_name in known_personas:
            target_persona = personas[target_persona_name]
            update_info = {
                "reason": "reputation update after sign up",
                "total_number_of_people": len(personas),
                "number_of_bidirectional_connections": len(get_d_connect(target_persona, G["resident"])),
                "ava_num_bibd_connections": get_ava_num_bibd_connections(personas, G["resident"]),
            }
            # reputation_update_sign_up(persona, target_persona, update_info)

            # add public
            # reputation_after_new_sign_up_with_publicreputation(init_persona, target_persona, update_info, output_save_dir, step)
            reputation_update_sign_up_with_publicreputation(persona, target_persona, update_info, output_save_dir)
            # social_network_update_after_new_sign_up(persona, target_persona)

            social_network_update_after_new_sign_up_with_publicreputation(persona, target_persona, output_save_dir)
        

# def start_chat(pair, G, ps):
def start_chat(pair, G, ps, save_folder, step, personas):
    p0_repu = pair[0].reputationDB.get_targets_individual_reputation(pair[1].scratch.ID, "resident")
    p1_repu = pair[1].reputationDB.get_targets_individual_reputation(pair[0].scratch.ID, "resident")
    if p1_repu:
        if [pair[1], "resident"] in pair[0].scratch.relationship["black_list"]:
            p0_willing = "no"
        else:
            p0_res = run_gpt_prompt_decide_to_talk_v1(pair[0], pair[1])[0]
            p0_willing = p0_res.split("step 2:")[-1].strip()
            if "error" in p0_willing.lower():
                raise Exception("GPT ERROR")
    else:
        p0_willing = "yes"

    if p0_repu:
        if [pair[0], "resident"] in pair[1].scratch.relationship["black_list"]:
            p1_willing = "no"
        else:
            p1_res = run_gpt_prompt_decide_to_talk_v1(pair[1], pair[0])[0]
            p1_willing = p1_res.split("step 2:")[-1].strip()
            if "error" in p1_willing.lower():
                raise Exception("GPT ERROR")
    else:
        p1_willing = "yes"

    if "yes" in p0_willing.lower() and "yes" in p1_willing.lower():
        pair[0].scratch.total_chat_num += 1
        pair[1].scratch.total_chat_num += 1
        pair[0].scratch.success_chat_num += 1
        pair[1].scratch.success_chat_num += 1
        # chat
        convo = run_gpt_prompt_create_chat_v1(pair[0], pair[1])[0]
        sum_covno = run_gpt_prompt_summarize_chat_v1(pair[0], pair[1], convo)[0]
        if "error" in sum_covno.lower() or "error" in convo.lower():
            raise Exception("GPT ERROR")
        
        Path(save_folder).mkdir(parents=True, exist_ok=True)
        with open(f"{save_folder}/chat_at_step_{step}.txt", "a") as f:
            f.write("Conversation:\n")
            f.write(convo + '\n')
            f.write("Summary:\n")
            f.write(sum_covno + '\n')
            f.write("---------------------End of Chat--------------------\n\n")
        pair[0].associativeMemory.add_chat(
            subject=pair[0].name,
            predicate="basic chat",
            obj=pair[1].name,
            description=sum_covno,
            created_at=pair[0].scratch.curr_step,
            conversation=convo,
        )
        pair[1].associativeMemory.add_chat(
            subject=pair[0].name,
            predicate="basic chat",
            obj=pair[1].name,
            description=sum_covno,
            conversation=convo,
            created_at=pair[0].scratch.curr_step,
        )

        # Chat satisfaction & Gossip willingness
        p0_gossip = run_gpt_prompt_willingness_to_gossip_v1(pair[0], pair[1], sum_covno)[0]
        p1_gossip = run_gpt_prompt_willingness_to_gossip_v1(pair[1], pair[0], sum_covno)[0]
        if "error" in p0_gossip.lower() or "error" in p1_gossip.lower():
            raise Exception("GPT ERROR")
        if "yes" in p0_gossip.split(",")[0].lower():
            pair[0].scratch.complain_buffer.append(
                {
                    "complaint_target_ID": pair[1].scratch.ID,
                    "complaint_target": pair[1].name,
                    "complaint_target_role": "resident",
                    "complaint_reason": p0_gossip.split(",")[-1].strip(),
                }
            )
        if "yes" in p1_gossip.split(",")[0].lower():
            pair[1].scratch.complain_buffer.append(
                {
                    "complaint_target_ID": pair[0].scratch.ID,
                    "complaint_target": pair[0].name,
                    "complaint_target_role": "resident",
                    "complaint_reason": p1_gossip.split(",")[-1].strip(),
                }
            )

        update_info_0 = {
            "reason": "reputation update after interaction",
            "sum_convo": sum_covno,
            "total_number_of_people": len(ps),
            "number_of_bidirectional_connections": len(get_d_connect(pair[1], G["resident"])),
            "ava_satisfy": get_ava_satisfy(ps),
            "ava_num_bibd_connections": get_ava_num_bibd_connections(ps, G["resident"]),
        }
        update_info_1 = {
            "reason": "reputation update after interaction",
            "sum_convo": sum_covno,
            "total_number_of_people": len(ps),
            "number_of_bidirectional_connections": len(get_d_connect(pair[0], G["resident"])),
            "ava_satisfy": get_ava_satisfy(ps),
            "ava_num_bibd_connections": get_ava_num_bibd_connections(ps, G["resident"]),
        }
        # reputation_update_sign_up(pair[0], pair[1], update_info_0)
        # reputation_update_sign_up(pair[1], pair[0], update_info_1)
        reputation_update_sign_up(pair[0], pair[1], update_info_0, save_folder, step, personas)
        reputation_update_sign_up(pair[1], pair[0], update_info_1, save_folder, step, personas)
    else:
        pair[0].scratch.total_chat_num += 1
        pair[1].scratch.total_chat_num += 1



def start_chat_with_publicreputation(pair, G, ps, output_save_dir, personas):
    p0_repu = pair[0].reputationDB.get_targets_individual_reputation(pair[1].scratch.ID, "resident")
    p1_repu = pair[1].reputationDB.get_targets_individual_reputation(pair[0].scratch.ID, "resident")
    if p1_repu:
        if [pair[1], "resident"] in pair[0].scratch.relationship["black_list"]:
            p0_willing = "no"
        else:
            p0_res = run_gpt_prompt_decide_to_talk_v1_with_publicreputation(pair[0], pair[1], output_save_dir)[0]
            p0_willing = p0_res.split("step 2:")[-1].strip()
            if "error" in p0_willing.lower():
                raise Exception("GPT ERROR")
    else:
        p0_willing = "yes"

    if p0_repu:
        if [pair[0], "resident"] in pair[1].scratch.relationship["black_list"]:
            p1_willing = "no"
        else:
            p1_res = run_gpt_prompt_decide_to_talk_v1_with_publicreputation(pair[1], pair[0], output_save_dir)[0]
            p1_willing = p1_res.split("step 2:")[-1].strip()
            if "error" in p1_willing.lower():
                raise Exception("GPT ERROR")
    else:
        p1_willing = "yes"

    if "yes" in p0_willing.lower() and "yes" in p1_willing.lower():
        pair[0].scratch.total_chat_num += 1
        pair[1].scratch.total_chat_num += 1
        pair[0].scratch.success_chat_num += 1
        pair[1].scratch.success_chat_num += 1
        # chat
        convo = run_gpt_prompt_create_chat_v1(pair[0], pair[1], output_save_dir)[0]
        sum_covno = run_gpt_prompt_summarize_chat_v1(pair[0], pair[1], convo, output_save_dir)[0]
        if "error" in sum_covno.lower() or "error" in convo.lower():
            raise Exception("GPT ERROR")

        pair[0].associativeMemory.add_chat(
            subject=pair[0].name,
            predicate="basic chat",
            obj=pair[1].name,
            description=sum_covno,
            created_at=pair[0].scratch.curr_step,
            conversation=convo,
        )
        pair[1].associativeMemory.add_chat(
            subject=pair[0].name,
            predicate="basic chat",
            obj=pair[1].name,
            description=sum_covno,
            conversation=convo,
            created_at=pair[0].scratch.curr_step,
        )

        # Chat satisfaction & Gossip willingness
        p0_gossip = run_gpt_prompt_willingness_to_gossip_v1(pair[0], pair[1], sum_covno, output_save_dir)[0]
        p1_gossip = run_gpt_prompt_willingness_to_gossip_v1(pair[1], pair[0], sum_covno, output_save_dir)[0]
        if "error" in p0_gossip.lower() or "error" in p1_gossip.lower():
            raise Exception("GPT ERROR")
        if "yes" in p0_gossip.split(",")[0].lower():
            pair[0].scratch.complain_buffer.append(
                {
                    "complaint_target_ID": pair[1].scratch.ID,
                    "complaint_target": pair[1].name,
                    "complaint_target_role": "resident",
                    "complaint_reason": p0_gossip.split(",")[-1].strip(),
                }
            )
        if "yes" in p1_gossip.split(",")[0].lower():
            pair[1].scratch.complain_buffer.append(
                {
                    "complaint_target_ID": pair[0].scratch.ID,
                    "complaint_target": pair[0].name,
                    "complaint_target_role": "resident",
                    "complaint_reason": p1_gossip.split(",")[-1].strip(),
                }
            )

        update_info_0 = {
            "reason": "reputation update after interaction",
            "sum_convo": sum_covno,
            "total_number_of_people": len(ps),
            "number_of_bidirectional_connections": len(get_d_connect(pair[1], G["resident"])),
            "ava_satisfy": get_ava_satisfy(ps),
            "ava_num_bibd_connections": get_ava_num_bibd_connections(ps, G["resident"]),
        }
        update_info_1 = {
            "reason": "reputation update after interaction",
            "sum_convo": sum_covno,
            "total_number_of_people": len(ps),
            "number_of_bidirectional_connections": len(get_d_connect(pair[0], G["resident"])),
            "ava_satisfy": get_ava_satisfy(ps),
            "ava_num_bibd_connections": get_ava_num_bibd_connections(ps, G["resident"]),
        }
        # reputation_update_sign_up(pair[0], pair[1], update_info_0)
        # reputation_update_sign_up(pair[1], pair[0], update_info_1)
        reputation_update_sign_up_with_publicreputation(pair[0], pair[1], update_info_0, output_save_dir)
        reputation_update_sign_up_with_publicreputation(pair[1], pair[0], update_info_1, output_save_dir)
    else:
        pair[0].scratch.total_chat_num += 1
        pair[1].scratch.total_chat_num += 1






def start_sign_up(personas, G, step, stats_collector, save_floder, sign_up_f=False):
    os.makedirs(save_floder, exist_ok=True)
    
    if sign_up_f:
        # sign up ever 5th step
        sign_up(personas, step, save_floder, G)
    print(save_floder)

    # interaction
    pairs = chat_pair(personas)
    for pair in pairs:
        # start_chat(pair, G, personas)
        start_chat(pair, G, personas, save_floder, step, personas)

        if pair[0].scratch.complain_buffer:
            # gossip
            # gossip target choose
            for person in pair[0].scratch.complain_buffer:
                # gossip target choose
                # gossip_targets = run_gpt_prompt_gossip_listener_select_v2(pair[0], "resident", personas[person["complaint_target"]])[0]
                res = gossip_targets = run_gpt_prompt_gossip_listener_select_v2(pair[0], "resident", personas[person["complaint_target"]])
                gossip_targets = res[0]
                with open(f"{save_floder}/gossip_targets_{pair[0].name}_at_step_{step}.txt", "a") as f:
                    f.write(str(res) + '\n')
                
                for gossip_target in gossip_targets:
                    # gossip chat
                    gossip_target_persona = personas[gossip_target]
                    first_order_gossip(
                        pair[0],
                        gossip_target_persona,
                        "resident",
                        "resident",
                        personas,
                        G,
                        val=person,
                        # 新增
                        save_folder=save_floder,
                        step=step,
                    )
        if pair[1].scratch.complain_buffer:
            # gossip
            # gossip target choose
            for person in pair[1].scratch.complain_buffer:
                # gossip target choose
                gossip_targets = run_gpt_prompt_gossip_listener_select_v2(pair[1], "resident", personas[person["complaint_target"]])[0]
                for gossip_target in gossip_targets:
                    # gossip chat
                    gossip_target_persona = personas[gossip_target]
                    first_order_gossip(
                        pair[1],
                        gossip_target_persona,
                        "resident",
                        "resident",
                        personas,
                        G,
                        val=person,
                    )




def start_sign_up_with_publicreputation(personas, G, step, stats_collector, version, save_floder, sign_up_f=False):
    os.makedirs(save_floder, exist_ok=True)
    parent_sim_path = os.path.dirname(os.path.dirname(save_floder))
    output_save_dir = os.path.join(parent_sim_path, "sign_up_with_publicreputation")
    
    if sign_up_f:
        # sign up ever 5th step
        sign_up_with_publicreputation(personas, step, save_floder, output_save_dir, G, stats_collector, version)
    print(save_floder)
    
    # interaction
    pairs = chat_pair(personas)
    for pair in pairs:
        # start_chat(pair, G, personas)
        start_chat_with_publicreputation(pair, G, personas, output_save_dir, personas)

        if pair[0].scratch.complain_buffer:
            # gossip
            # gossip target choose
            for person in pair[0].scratch.complain_buffer:
                # gossip target choose
                # gossip_targets = run_gpt_prompt_gossip_listener_select_v2(pair[0], "resident", personas[person["complaint_target"]])[0]
                res = gossip_targets = run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(pair[0], personas[person["complaint_target"]], output_save_dir, "resident")
                gossip_targets = res[0]
                with open(f"{save_floder}/gossip_targets_{pair[0].name}_at_step_{step}.txt", "a") as f:
                    f.write(str(res) + '\n')
                
                for gossip_target in gossip_targets:
                    # gossip chat
                    gossip_target_persona = personas[gossip_target]
                    # first_order_gossip_with_publicreputation(init_persona, target_persona, init_persona_role, complain_persona_role, personas, G, output_save_dir, val):

                    first_order_gossip_with_publicreputation(
                        pair[0],
                        gossip_target_persona,
                        "resident",
                        "resident",
                        personas,
                        G,
                        output_save_dir,
                        val=person,
                    )
        if pair[1].scratch.complain_buffer:
            # gossip
            # gossip target choose
            for person in pair[1].scratch.complain_buffer:
                # gossip target choose
                gossip_targets = run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(pair[1], personas[person["complaint_target"]], output_save_dir, "resident")[0]
                for gossip_target in gossip_targets:
                    # gossip chat
                    gossip_target_persona = personas[gossip_target]
                    first_order_gossip_with_publicreputation(
                        pair[1],
                        gossip_target_persona,
                        "resident",
                        "resident",
                        personas,
                        G,
                        output_save_dir,
                        val=person,
                    )

    # stats_collector.log_sign_up(
    #     round_idx=step,
    #     player_name=persona.name,
    #     sign_up_result=sign_up_bool,
    #     private_rep=private_rep,
    #     public_rep=public_rep,
    #     version=version,
    #     bind_list=bind_list,
    #     black_list=black_list
    # )

