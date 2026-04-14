from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_reputation_update_after_stage4_investor_v1,
    run_gpt_prompt_reputation_update_after_stage4_trustee_v1,
    run_gpt_prompt_reputation_update_after_gossip_invest_v1,
    run_gpt_prompt_reputation_update_after_gossip_sign_up_v1,
    run_gpt_prompt_reputation_update_after_gossip_pd_game_v1,
    run_gpt_prompt_update_learned_in_description_invest_v1_with_publicreputation,
    run_gpt_prompt_update_learned_in_description_pd_game_v1_with_publicreputation_with_buffer,
    run_gpt_prompt_update_learned_in_description_sign_v1,
    run_gpt_prompt_update_learned_in_description_invest_v1,
    run_gpt_prompt_reputation_update_after_stage1_trustee_v1,
    run_gpt_prompt_reputation_update_after_stage1_investor_v1,
    run_gpt_prompt_self_reputation_init_sign_up_v1,
    run_gpt_prompt_self_reputation_update_after_chat_sign_up_v1,
    run_gpt_prompt_other_reputation_update_after_chat_sign_up_v1,
    run_gpt_prompt_other_reputation_update_after_new_sign_up_v1,
    run_gpt_prompt_reputation_update_after_observed_v1,
    run_gpt_prompt_self_reputation_update_after_pd_game_v1,
    run_gpt_prompt_other_reputation_update_after_pd_game_v1,
    run_gpt_prompt_update_learned_in_description_pd_game_v1,
    run_gpt_prompt_sign_up_decide_to_report_to_publicreputationDB,

    run_gpt_prompt_pd_game_decide_to_report_to_publicreputationDB_with_gossip,
    run_gpt_prompt_pd_game_update_target_publicreputation,
    run_gpt_prompt_update_learned_in_description_pd_game_v1_with_publicreputation,
    run_gpt_prompt_update_learned_in_description_pd_game_v1_with_gossip_with_publicreputation,
    run_gpt_prompt_self_reputation_update_after_pd_game_v1_with_publicreputation,
    run_gpt_prompt_self_reputation_update_after_pd_game_v1_with_gossip_with_publicreputation,
    run_gpt_prompt_other_reputation_update_after_pd_game_v1_with_publicreputation,
    run_gpt_prompt_other_reputation_update_after_pd_game_v1_with_gossip_with_publicreputation,
    run_gpt_prompt_pd_game_update_target_publicreputation_content,
    run_gpt_prompt_pd_game_update_target_publicreputation_content_with_gossip,
    run_gpt_prompt_pd_game_update_target_publicreputation_record,
    run_gpt_prompt_pd_game_update_target_publicreputation_record_with_gossip,
    run_gpt_prompt_reputation_update_after_gossip_pd_game_v1_with_publicreputation,
    run_gpt_prompt_pd_game_decide_to_report_to_publicreputationDB_with_buffer,
    run_gpt_prompt_pd_game_update_target_publicreputation_with_buffer,
    run_gpt_prompt_update_learned_in_description_sign_v1_with_publicreputation,
    run_gpt_prompt_reputation_update_after_gossip_sign_up_v1_with_publicreputation,
    run_gpt_prompt_sign_up_update_target_publicreputation_content,
    run_gpt_prompt_sign_up_update_target_publicreputation_record,
    run_gpt_prompt_investment_investor_decide_to_report_to_publicreputationDB,
    run_gpt_prompt_investment_trustee_decide_to_report_to_publicreputationDB,
    run_gpt_prompt_investment_update_target_publicreputation_content,
    run_gpt_prompt_investment_update_target_publicreputation_record,
    run_gpt_prompt_investment_decide_to_report_to_publicreputationDB
    

)
from .social_network import *
import os
from public_reputation.SharedPublicReputationDB import publicreputationDB
import datetime
import json


def reputation_init_sign_up(init_persona):
    res = run_gpt_prompt_self_reputation_init_sign_up_v1(init_persona)[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, "sign up repu init")


def reputation_update_pd_game(init_persona, target_persona, update_info, output_save_dir):
    if "pd_game" in update_info["reason"]:
        res_s = run_gpt_prompt_self_reputation_update_after_pd_game_v1(init_persona, update_info["init_behavior_summary"], output_save_dir)[0]
        if type(res_s) is str and "error" in res_s.lower():
            raise Exception("GPT ERROR")
        res_o = run_gpt_prompt_other_reputation_update_after_pd_game_v1(init_persona, target_persona, update_info["target_behavior_summary"], output_save_dir)[0]
        if type(res_o) is str and "error" in res_o.lower():
            raise Exception("GPT ERROR")
        init_persona.reputationDB.update_individual_reputation(res_s, init_persona.scratch.curr_step, update_info["reason"])
        init_persona.reputationDB.update_individual_reputation(res_o, init_persona.scratch.curr_step, update_info["reason"])
        new_learned = run_gpt_prompt_update_learned_in_description_pd_game_v1(init_persona, update_info["init_behavior_summary"], output_save_dir)[0]
        if type(new_learned) is str and "error" in new_learned.lower():
            raise Exception("GPT ERROR")
        init_persona.scratch.learned = new_learned
    elif "gossip" in update_info["reason"]:
        res_after_gossip = run_gpt_prompt_reputation_update_after_gossip_pd_game_v1(init_persona, target_persona, update_info["gossip"][0], output_save_dir)[0]
        if type(res_after_gossip) is str and "error" in res_after_gossip.lower():
            raise Exception("GPT ERROR")
        init_persona.reputationDB.update_individual_reputation(res_after_gossip, init_persona.scratch.curr_step, update_info["reason"])
        return

    social_network_update(init_persona, target_persona, "player", "player", output_save_dir, update_info)



def prepare_reputation_and_sn_plan(init_persona, target_persona, evaluation, output_save_dir, G):
    plan = {
        'res_s': None, 'res_o': None, 'report_to_public': "no", 
        'public_val': None, 'new_learned': None, 'sn_data': None
    }
    res_s = run_gpt_prompt_self_reputation_update_after_pd_game_v1_with_publicreputation(init_persona, evaluation["self_reputation"], output_save_dir)[0]
    res_o = run_gpt_prompt_other_reputation_update_after_pd_game_v1_with_publicreputation(init_persona, target_persona, evaluation["opponent_reputation"], output_save_dir)[0]
    
    if "error" in str(res_s).lower() or "error" in str(res_o).lower():
        raise Exception("REPUTATION_GPT_ERROR")
    plan['res_s'], plan['res_o'] = res_s, res_o

    target_public_reputation = publicreputationDB.get_target_public_reputation(target_persona.scratch.ID, role="player")
    report_dec = run_gpt_prompt_pd_game_decide_to_report_to_publicreputationDB_with_buffer(init_persona, target_persona, res_o, output_save_dir)[0]
    decision = report_dec.get("Result", "").lower() if isinstance(report_dec, dict) else str(report_dec).lower()
    if "yes" in decision:
        plan['report_to_public'] = "yes"
        target_public_reputation = update_target_publicreputation_with_buffer(init_persona, target_persona, evaluation["opponent_reputation"], output_save_dir)
       
    plan['public_val'] = target_public_reputation
    plan['new_learned'] = run_gpt_prompt_update_learned_in_description_pd_game_v1_with_publicreputation_with_buffer(init_persona, res_s, evaluation["self_reputation"], output_save_dir)[0]
    sn_update_info = {"target_behavior_summary": evaluation["opponent_reputation"]}
    plan['sn_data'] = get_social_network_decisions(init_persona, target_persona, "player", "player", sn_update_info, plan['new_learned'], res_o, plan['public_val'], output_save_dir)

    return plan


def sign_up_update_target_publicreputation(init_persona, target_persona, res_s, output_save_dir, target_persona_role):
    content_res = run_gpt_prompt_sign_up_update_target_publicreputation_content(init_persona, target_persona, res_s, output_save_dir, target_persona_role)[0]
    content = content_res.get("content")
    target_public_reputation = run_gpt_prompt_sign_up_update_target_publicreputation_record(target_persona, content, output_save_dir, target_persona_role)[0]
    return target_public_reputation



def investment_update_target_publicreputation(init_persona, target_persona, res_s, output_save_dir, target_persona_role):
    content_res = run_gpt_prompt_investment_update_target_publicreputation_content(init_persona, target_persona, res_s, output_save_dir, target_persona_role)[0]
    content = content_res.get("content")
    target_public_reputation = run_gpt_prompt_investment_update_target_publicreputation_record(target_persona, content, output_save_dir, target_persona_role)[0]
    return target_public_reputation





def update_target_publicreputation_with_buffer(init_persona, target_persona, update_info, output_save_dir):
    content_res = run_gpt_prompt_pd_game_update_target_publicreputation_content(init_persona, target_persona, update_info, output_save_dir, role="Player")[0]
    content = content_res.get("content")
    target_public_reputation = run_gpt_prompt_pd_game_update_target_publicreputation_record(target_persona, content, output_save_dir, role="Player")[0]
    return target_public_reputation


def reputation_update_pd_game_after_gossip_with_publicreputation(init_persona, target_persona, update_info, output_save_dir):
    try:
        res_after_gossip = run_gpt_prompt_reputation_update_after_gossip_pd_game_v1(init_persona, target_persona, update_info["gossip"][0], output_save_dir)[0]
        if type(res_after_gossip) is str and "error" in res_after_gossip.lower():
            raise Exception("GPT ERROR")
        init_persona.reputationDB.update_individual_reputation(res_after_gossip, init_persona.scratch.curr_step, update_info["reason"])
        return
    except Exception as e:
        raise e



# def reputation_update_pd_game_with_gossip_with_publicreputation(init_persona, target_persona, update_info, game_result):
#     try:
#         if "pd_game" in update_info["reason"]:
#             res_s = run_gpt_prompt_self_reputation_update_after_pd_game_v1_with_gossip_with_publicreputation(init_persona, update_info["init_behavior_summary"])[0]
#             if type(res_s) is str and "error" in res_s.lower():
#                 raise Exception("GPT ERROR in res_s")
            
#             res_o = run_gpt_prompt_other_reputation_update_after_pd_game_v1_with_gossip_with_publicreputation(init_persona, target_persona, update_info["target_behavior_summary"])[0]
#             if type(res_o) is str and "error" in res_o.lower():
#                 raise Exception("GPT ERROR in res_o")

#             init_persona.reputationDB.update_individual_reputation(res_s, init_persona.scratch.curr_step, update_info["reason"])
#             init_persona.reputationDB.update_individual_reputation(res_o, init_persona.scratch.curr_step, update_info["reason"])

#             res_data = run_gpt_prompt_pd_game_decide_to_report_to_publicreputationDB_with_gossip(init_persona, target_persona, update_info["target_behavior_summary"], target_persona_role="Player")[0]
            
#             decision = ""
#             if isinstance(res_data, dict):
#                 decision = res_data.get("Result", "").lower()
#             elif isinstance(res_data, str):
#                 decision = res_data.lower()

#             if decision == "yes":
#                 target_public_reputation = update_target_publicreputation_with_gossip(init_persona, target_persona, update_info["target_behavior_summary"])
#                 publicreputationDB.update_or_create(target_public_reputation, init_persona.scratch.curr_step, reason="update after pd game")
#                 new_learned = run_gpt_prompt_update_learned_in_description_pd_game_v1_with_gossip_with_publicreputation(init_persona, update_info["init_behavior_summary"])[0]
#                 if type(new_learned) is str and "error" in new_learned.lower():
#                     raise Exception("GPT ERROR in new_learned")
#             init_persona.scratch.learned = new_learned

#             social_network_update_with_gossip_with_publicreputation(init_persona, target_persona, "player", "player", update_info)
#         elif "gossip" in update_info["reason"]:
#             res_after_gossip = run_gpt_prompt_reputation_update_after_gossip_pd_game_v1_with_publicreputation(init_persona, target_persona, update_info["gossip"][0])[0]
#             if type(res_after_gossip) is str and "error" in res_after_gossip.lower():
#                 raise Exception("GPT ERROR")
#             init_persona.reputationDB.update_individual_reputation(res_after_gossip, init_persona.scratch.curr_step, update_info["reason"])
#             return
#     except Exception as e:
#         raise e



def reputation_update_invest(
    output_save_dir,
    init_persona,
    target_persona,
    update_info,
    full_investment=True,
):
    if "stage 1" in update_info["reason"]:
        reputation_update_after_stage1_invest(output_save_dir, init_persona, target_persona, update_info)
    elif "stage 4" in update_info["reason"]:
        reputation_update_after_stage4_invest(output_save_dir, init_persona, target_persona, update_info)
    elif "observed" in update_info["reason"]:
        reputation_update_after_observed_invest(output_save_dir, init_persona, target_persona, update_info)
        # NETWORK AFTER OBSERVED IS IN THE OBSERVED PART
        return

    elif "gossip" in update_info["reason"]:
        reputation_update_after_gossip_invest(init_persona, target_persona, update_info, output_save_dir)
        # NETWORK AFTER GOSSIP IS IN THE GOSSIP PART
        return

    if update_info["init_persona_role"] == "investor":
        social_network_update(
            init_persona,
            target_persona,
            "investor",
            "trustee",
            output_save_dir,
            update_info=update_info,
            full_investment=full_investment,
        )
    elif update_info["init_persona_role"] == "trustee":
        social_network_update(
            init_persona,
            target_persona,
            "trustee",
            "investor",
            output_save_dir,
            update_info=update_info,
            full_investment=full_investment,
        )


def investment_report_and_update_target_publicreputation(init_persona, init_persona_role, target_persona, output_save_dir, other_evaluation, reason):
    init_persona_role = init_persona_role.lower()
    if init_persona_role == "investor":
        target_persona_role = "trustee"
    else:
        target_persona_role = "investor"
    report_dec = run_gpt_prompt_investment_decide_to_report_to_publicreputationDB(init_persona, target_persona, output_save_dir, init_persona_role, target_persona_role)[0]

    decision = report_dec.get("Result", "").lower() if isinstance(report_dec, dict) else str(report_dec).lower()
    if "yes" in decision:
        #def update_target_publicreputation(init_persona, target_persona, update_info, output_save_dir, target_persona_role):
        target_public_reputation = investment_update_target_publicreputation(init_persona, target_persona, other_evaluation, output_save_dir, target_persona_role)
        publicreputationDB.update_or_create(target_public_reputation, target_persona.scratch.curr_step, reason)





def reputation_update_invest_with_publiceputation(
    init_persona,
    target_persona,
    update_info,
    output_save_dir,
    full_investment=True,
):

    if "stage 4" in update_info["reason"]:
        # add public report & update
        reputation_update_after_stage4_invest_with_publicreputation(init_persona, target_persona, update_info, output_save_dir)
    elif "observed" in update_info["reason"]:
        # add report & update public
        reputation_update_after_observed_invest_with_publicreputation(init_persona, target_persona, update_info, output_save_dir)
        # NETWORK AFTER OBSERVED IS IN THE OBSERVED PART
        return

    elif "gossip" in update_info["reason"]:
        reputation_update_after_gossip_invest(init_persona, target_persona, update_info, output_save_dir)
        # NETWORK AFTER GOSSIP IS IN THE GOSSIP PART
        return

    if update_info["init_persona_role"] == "investor":
        social_network_update_with_publicreputation(
            init_persona,
            target_persona,
            "investor",
            "trustee",
            output_save_dir,
            update_info=update_info,
            full_investment=full_investment,
        )
    elif update_info["init_persona_role"] == "trustee":
        social_network_update_with_publicreputation(
            init_persona,
            target_persona,
            "trustee",
            "investor",
            output_save_dir,
            update_info=update_info,
            full_investment=full_investment,
        )





def reputation_update_sign_up(init_persona, target_persona, update_info, save_folder, step):
    if "interaction" in update_info["reason"]:
        reputation_update_after_interaction_sign_up(init_persona, target_persona, update_info, save_folder, step)
    elif "sign up" in update_info["reason"]:
        # add public
        reputation_after_new_sign_up(init_persona, target_persona, update_info, save_folder, step)
        # NETWORK AFTER SIGN UP IS IN THE SIGN UP PART
        return
    elif "gossip" in update_info["reason"]:
        reputation_update_after_gossip_sign_up(init_persona, target_persona, update_info, save_folder, step)
        # NETWORK AFTER GOSSIP IS IN THE GOSSIP PART
        return
    social_network_update(init_persona, target_persona, "resident", "resident", update_info)


def reputation_update_sign_up_with_publicreputation(init_persona, target_persona, update_info, output_save_dir):
    if "interaction" in update_info["reason"]:
        reputation_update_after_interaction_sign_up_with_publicreputation(init_persona, target_persona, update_info, output_save_dir)
    elif "sign up" in update_info["reason"]:
        # add public
        reputation_after_new_sign_up_with_publicreputation(init_persona, target_persona, update_info, output_save_dir)
        # NETWORK AFTER SIGN UP IS IN THE SIGN UP PART
        return
    elif "gossip" in update_info["reason"]:
        reputation_update_after_gossip_sign_up_with_publicreputation(init_persona, target_persona, update_info, output_save_dir)
        # NETWORK AFTER GOSSIP IS IN THE GOSSIP PART
        return
    # add publicreputation
    social_network_update_with_publicreputation(init_persona, target_persona, "resident", "resident", output_save_dir,  update_info)



# def reputation_update_after_gossip_sign_up(init_persona, target_persona, update_info)
def reputation_update_after_gossip_sign_up(init_persona, target_persona, update_info, save_folder, step):
    res = run_gpt_prompt_reputation_update_after_gossip_sign_up_v1(
        init_persona,
        target_persona,
        update_info["gossip"][0],
        update_info["target_persona_role"],
        update_info["total_number_of_people"],
        update_info["number_of_bidirectional_connections"],
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    
    with open(f"{save_folder}/reputation_update_after_gossip_sign_up_{step}.txt", "a") as f:
        f.write(str(res) + '\n')
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])
    # print(res)


# def reputation_update_after_gossip_sign_up(init_persona, target_persona, update_info)
def reputation_update_after_gossip_sign_up_with_publicreputation(init_persona, target_persona, update_info, output_save_dir):
    res = run_gpt_prompt_reputation_update_after_gossip_sign_up_v1(
        init_persona,
        target_persona,
        update_info["gossip"][0],
        update_info["target_persona_role"],
        output_save_dir
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])
    # print(res)


def reputation_update_after_interaction_sign_up(init_persona, target_persona, update_info, output_save_dir):
    # Init persona self reputation update
    res_s = run_gpt_prompt_self_reputation_update_after_chat_sign_up_v1(init_persona, update_info["sum_convo"], update_info["ava_satisfy"], output_save_dir)[0]

    res_o = run_gpt_prompt_other_reputation_update_after_chat_sign_up_v1(
        init_persona,
        target_persona,
        update_info["sum_convo"],
        update_info["total_number_of_people"],
        update_info["number_of_bidirectional_connections"],
        update_info["ava_num_bibd_connections"],
        output_save_dir
    )[0]

    if type(res_s) is str and "error" in res_s.lower():
        raise Exception("GPT ERROR")
    if type(res_o) is str and "error" in res_o.lower():
        raise Exception("GPT ERROR")

    init_persona.reputationDB.update_individual_reputation(res_o, init_persona.scratch.curr_step, update_info["reason"])
    init_persona.reputationDB.update_individual_reputation(res_s, init_persona.scratch.curr_step, update_info["reason"])

    sum_covno_s = update_info["sum_convo"].strip().split("- ")
    self_view = ""
    for s in sum_covno_s:
        if f"{init_persona.name}'s Viewpoint" in s:
            self_view = s.split(":")[-1].strip()

    # learned_update_sign(init_persona, "resident", self_view)
    learned_update_sign(init_persona, "resident", self_view, output_save_dir)


def reputation_update_after_interaction_sign_up_with_publicreputation(init_persona, target_persona, update_info, output_save_dir):
    # Init persona self reputation update
    res_s = run_gpt_prompt_self_reputation_update_after_chat_sign_up_v1(init_persona, update_info["sum_convo"], update_info["ava_satisfy"], output_save_dir)[0]

    res_o = run_gpt_prompt_other_reputation_update_after_chat_sign_up_v1(
        init_persona,
        target_persona,
        update_info["sum_convo"],
        update_info["total_number_of_people"],
        update_info["number_of_bidirectional_connections"],
        update_info["ava_num_bibd_connections"],
        output_save_dir
    )[0]

    if type(res_s) is str and "error" in res_s.lower():
        raise Exception("GPT ERROR")
    if type(res_o) is str and "error" in res_o.lower():
        raise Exception("GPT ERROR")

    init_persona.reputationDB.update_individual_reputation(res_o, init_persona.scratch.curr_step, update_info["reason"])
    init_persona.reputationDB.update_individual_reputation(res_s, init_persona.scratch.curr_step, update_info["reason"])

    report_dec = run_gpt_prompt_sign_up_decide_to_report_to_publicreputationDB(init_persona, target_persona, output_save_dir, "resident")[0]
    decision = report_dec.get("Result", "").lower() if isinstance(report_dec, dict) else str(report_dec).lower()
    
    if "yes" in decision:
        target_public_reputation = sign_up_update_target_publicreputation(init_persona, target_persona, res_o, output_save_dir, "resident")
        publicreputationDB.update_or_create(target_public_reputation, target_persona.scratch.curr_step, "update after interaction")

    sum_covno_s = update_info["sum_convo"].strip().split("- ")
    self_view = ""
    for s in sum_covno_s:
        if f"{init_persona.name}'s Viewpoint" in s:
            self_view = s.split(":")[-1].strip()

    learned_update_sign_with_publicreputation(init_persona, "resident", self_view, output_save_dir)


def reputation_after_new_sign_up(init_persona, target_persona, update_info, save_folder, output_save_dir, step):
    res = run_gpt_prompt_other_reputation_update_after_new_sign_up_v1(
        init_persona,
        target_persona,
        update_info["total_number_of_people"],
        update_info["number_of_bidirectional_connections"],
        update_info["ava_num_bibd_connections"],
        output_save_dir
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    
    with open(f"{save_folder}/reputation_after_new_sign_up_{step}.txt", "a") as f:
        f.write(str(res) + '\n')
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])



def reputation_after_new_sign_up_with_publicreputation(init_persona, target_persona, update_info, output_save_dir):
    res = run_gpt_prompt_other_reputation_update_after_new_sign_up_v1(
        init_persona,
        target_persona,
        update_info["total_number_of_people"],
        update_info["number_of_bidirectional_connections"],
        update_info["ava_num_bibd_connections"],
        output_save_dir,
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")

    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])
    report_dec = run_gpt_prompt_sign_up_decide_to_report_to_publicreputationDB(init_persona, target_persona, output_save_dir, "resident")[0]
    decision = report_dec.get("Result", "").lower() if isinstance(report_dec, dict) else str(report_dec).lower()
    
    if "yes" in decision:
        target_public_reputation = sign_up_update_target_publicreputation(init_persona, target_persona, res, output_save_dir, "resident")
        publicreputationDB.update_or_create(target_public_reputation, target_persona.scratch.curr_step, "update after new sign up")




def reputation_update_after_gossip_invest(init_persona, target_persona, update_info, output_save_dir):
    res = run_gpt_prompt_reputation_update_after_gossip_invest_v1(
        output_save_dir,
        init_persona,
        target_persona,
        update_info["gossip"][0],
        update_info["init_persona_role"],
        update_info["target_persona_role"],
        update_info["gossip"][0]["credibility level"],
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])
    # print(res)


def reputation_update_after_observed_invest(output_save_dir, init_persona, target_persona, update_info):
    res = run_gpt_prompt_reputation_update_after_observed_v1(
        output_save_dir, 
        init_persona,
        target_persona,
        update_info["init_persona_role"],
        update_info["target_persona_role"],
        update_info["interaction_memory"],
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])





def reputation_update_after_observed_invest_with_publicreputation(init_persona, target_persona, update_info, output_save_dir):
    res = run_gpt_prompt_reputation_update_after_observed_v1(
        output_save_dir,
        init_persona,
        target_persona,
        update_info["init_persona_role"],
        update_info["target_persona_role"],
        update_info["interaction_memory"],
    )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])

def reputation_update_after_stage4_invest(output_save_dir, init_persona, target_persona, update_info):
    if update_info["init_persona_role"] == "investor":
        res = run_gpt_prompt_reputation_update_after_stage4_investor_v1(
            output_save_dir, 
            init_persona,
            target_persona,
            update_info,
        )[0]
    elif update_info["init_persona_role"] == "trustee":
        res = run_gpt_prompt_reputation_update_after_stage4_trustee_v1(
            output_save_dir,
            init_persona,
            target_persona,
            update_info,
        )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])
    learned_update_invest(
        output_save_dir,
        init_persona,
        update_info["init_persona_role"],
        update_info["init_behavior_summary"],
    )

    # print(res)



def reputation_update_after_stage4_invest_with_publicreputation(init_persona, target_persona, update_info, output_save_dir):
    if update_info["init_persona_role"] == "investor":
        res = run_gpt_prompt_reputation_update_after_stage4_investor_v1(
            output_save_dir,
            init_persona,
            target_persona,
            update_info,
        )[0]
    elif update_info["init_persona_role"] == "trustee":
        res = run_gpt_prompt_reputation_update_after_stage4_trustee_v1(
            output_save_dir,
            init_persona,
            target_persona,
            update_info,
        )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])

    # add report & update public
    investment_report_and_update_target_publicreputation(init_persona, update_info["init_persona_role"], target_persona, output_save_dir, update_info["target_behavior_summary"], reason="update after investment stage_4")
    
    learned_update_invest_with_publicreputation(
        output_save_dir,
        init_persona,
        update_info["init_persona_role"],
        update_info["init_behavior_summary"],
    )

    # print(res)




def reputation_update_after_stage1_invest(output_save_dir, init_persona, target_persona, update_info):
    """
    NOT USED NOW
    """
    if update_info["init_persona_role"] == "investor":
        res = run_gpt_prompt_reputation_update_after_stage1_investor_v1(
            output_save_dir,
            init_persona,
            target_persona,
            "investor",
            "trustee",
            update_info["allocation_plan"],
            update_info["reason_refusal"],
            update_info["total_number_of_people"],
            update_info["number_of_bidirectional_connections"],
        )[0]
    elif update_info["init_persona_role"] == "trustee":
        res = run_gpt_prompt_reputation_update_after_stage1_trustee_v1(
            output_save_dir,
            init_persona,
            target_persona,
            "trustee",
            "investor",
            update_info["allocation_plan"],
            update_info["reason_refusal"],
            update_info["total_number_of_people"],
            update_info["number_of_bidirectional_connections"],
        )[0]
    if type(res) is str and "error" in res.lower():
        raise Exception("GPT ERROR")
    init_persona.reputationDB.update_individual_reputation(res, init_persona.scratch.curr_step, update_info["reason"])
    learned_update_invest(
        output_save_dir,
        init_persona,
        update_info["init_persona_role"],
        update_info["init_behavior_summary"],
    )

def learned_update_sign(init_persona, init_persona_role, init_persona_view, output_save_dir):
    res = run_gpt_prompt_update_learned_in_description_sign_v1(init_persona, init_persona_role, init_persona_view, output_save_dir)[0]
    if "error" in res.lower():
        raise Exception("GPT ERROR")

    init_persona.scratch.learned = res


def learned_update_sign_with_publicreputation(init_persona, init_persona_role, init_persona_view, output_save_dir):
    res = run_gpt_prompt_update_learned_in_description_sign_v1_with_publicreputation(init_persona, init_persona_role, init_persona_view, output_save_dir)[0]
    if "error" in res.lower():
        raise Exception("GPT ERROR")
    
    init_persona.scratch.learned = res

def learned_update_invest(output_save_dir, init_persona, init_persona_role, init_persona_view):
    res = run_gpt_prompt_update_learned_in_description_invest_v1(output_save_dir, init_persona, init_persona_role, init_persona_view)[0]
    if "error" in res.lower() and len(res) < 10:
        raise Exception("GPT ERROR")
    init_persona.scratch.learned[init_persona_role] = res


def learned_update_invest_with_publicreputation(output_save_dir, init_persona, init_persona_role, init_persona_view):
    res = run_gpt_prompt_update_learned_in_description_invest_v1_with_publicreputation(output_save_dir, init_persona, init_persona_role, init_persona_view)[0]
    if "error" in res.lower() and len(res) < 10:
        raise Exception("GPT ERROR")
    init_persona.scratch.learned[init_persona_role] = res


def replace_full_name(personas, name):
    for persona in personas.keys():
        if name in personas:
            return persona
    return None
