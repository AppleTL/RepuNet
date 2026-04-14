import sys
import os

from .prompt_template.run_gpt_prompt import (
    run_gpt_prompt_connection_build_player_v1,
    run_gpt_prompt_connection_build_player_v1_with_publicreputation,
    run_gpt_prompt_connection_build_player_v1_with_gossip_with_publicreputation,
    run_gpt_prompt_connection_build_investor_v1,
    run_gpt_prompt_connection_build_trustee_v1,
    run_gpt_prompt_disconnection_after_observed_v1_with_publicreputation,
    run_gpt_prompt_disconnection_investor_v1,
    run_gpt_prompt_disconnection_player_v1_with_publicreputation,
    run_gpt_prompt_disconnection_player_v1_with_gossip_with_publicreputation,
    run_gpt_prompt_disconnection_trustee_v1,
    run_gpt_prompt_disconnection_after_gossip_v2,
    run_gpt_prompt_disconnection_after_gossip_v2_with_publicreputation,
    run_gpt_prompt_connection_build_after_chat_sign_up_v2,
    run_gpt_prompt_disconnection_after_chat_sign_up_v2,
    run_gpt_prompt_disconnection_after_new_sign_up_v1,
    run_gpt_prompt_disconnection_after_observed_v1,
    run_gpt_prompt_disconnection_player_v1,
    run_gpt_prompt_disconnection_player_v1_with_publicreputation_with_buffer,
    run_gpt_prompt_connection_build_player_v1_with_publicreputation_with_buffer,
    run_gpt_prompt_disconnection_after_new_sign_up_v1_with_publicreputation,
    run_gpt_prompt_disconnection_investor_v1_with_publicreputation,
    run_gpt_prompt_disconnection_after_chat_sign_up_v2_with_publicreputation,
    run_gpt_prompt_disconnection_trustee_v1_with_publicreputation,
    run_gpt_prompt_connection_build_investor_v1_with_publicreputation,
    run_gpt_prompt_connection_build_trustee_v1_with_publicreputation,
    run_gpt_prompt_connection_build_after_chat_sign_up_v2_with_publicreputation,

    run_gpt_prompt_rebuild_connection_after_gossip_v2_with_publicreputation
    
)


def social_network_update(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    output_save_dir,
    update_info=None,
    full_investment=True,
    
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, target_persona_role])
        if init_persona_role == "investor":
            disconnection_res = run_gpt_prompt_disconnection_investor_v1(
                output_save_dir,
                init_persona,
                target_persona,
                target_persona_role,
                interaction_memory=update_info["target_behavior_summary"],
            )[0]
        elif init_persona_role == "trustee":
            disconnection_res = run_gpt_prompt_disconnection_trustee_v1(
                output_save_dir,
                init_persona,
                target_persona,
                target_persona_role,
                interaction_memory=update_info["target_behavior_summary"],
            )[0]
        elif init_persona_role == "resident":
            disconnection_res = run_gpt_prompt_disconnection_after_chat_sign_up_v2(
                init_persona,
                target_persona,
                target_persona_role,
                update_info["sum_convo"],
            )[0]
        elif init_persona_role == "player":
            # add publicreputation
            disconnection_res = run_gpt_prompt_disconnection_player_v1(
                init_persona,
                target_persona,
                target_persona_role,
                update_info["target_behavior_summary"],
                output_save_dir
            )[0]
        else:
            disconnection_res = "error"

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, target_persona_role])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])

    except Exception as e:
        if not full_investment:
            pass
        else:
            if isinstance(e, Exception) and str(e) == "GPT ERROR":
                sys.exit(str(e))

            if init_persona_role == "investor":
                bind_res = run_gpt_prompt_connection_build_investor_v1(
                    output_save_dir,
                    init_persona,
                    target_persona,
                    target_persona_role,
                    update_info["target_behavior_summary"],
                )[0]
            elif init_persona_role == "trustee":
                bind_res = run_gpt_prompt_connection_build_trustee_v1(
                    output_save_dir,
                    init_persona,
                    target_persona,
                    target_persona_role,
                    update_info["target_behavior_summary"],
                )[0]
            elif init_persona_role == "resident":
                bind_res = run_gpt_prompt_connection_build_after_chat_sign_up_v2(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    update_info["sum_convo"],
                )[0]
            elif init_persona_role == "player":
                # add publicreputation
                bind_res = run_gpt_prompt_connection_build_player_v1(
                    init_persona,
                    target_persona,
                    update_info["target_behavior_summary"],
                    output_save_dir
                )[0]
            else:
                bind_res = "error"

            if type(bind_res) is str and "error" in bind_res.lower():
                sys.exit("GPT ERROR")

            if bind_res["Connect"].lower() == "yes":
                init_persona.scratch.relationship["bind_list"].append([target_persona.scratch.name, target_persona_role])



def social_network_update_with_publicreputation(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    output_save_dir, 
    update_info=None,
    full_investment=True,
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, target_persona_role])
        if init_persona_role == "investor" or init_persona_role == "trustee":
            # add public
            disconnection_res = run_gpt_prompt_disconnection_investor_v1_with_publicreputation(
                init_persona,
                target_persona,
                target_persona_role,
                output_save_dir,
                interaction_memory=update_info["target_behavior_summary"],
            )[0]
        # 这两个prompt是一样的呀?
        # elif init_persona_role == "trustee":
        #     disconnection_res = run_gpt_prompt_disconnection_trustee_v1_with_publicreputation(
        #         init_persona,
        #         target_persona,
        #         target_persona_role,
        #         output_save_dir,
        #         interaction_memory=update_info["target_behavior_summary"],
        #     )[0]
        elif init_persona_role == "resident":
            disconnection_res = run_gpt_prompt_disconnection_after_chat_sign_up_v2_with_publicreputation(
                init_persona,
                target_persona,
                output_save_dir,
                target_persona_role,
                update_info["sum_convo"],
            )[0]
        elif init_persona_role == "player":
            # add publicreputation

            disconnection_res = run_gpt_prompt_disconnection_player_v1_with_publicreputation(
                init_persona,
                target_persona,
                target_persona_role,
                update_info["target_behavior_summary"],
            )[0]
        else:
            disconnection_res = "error"

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, target_persona_role])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])

    except Exception as e:
        if not full_investment:
            pass
        else:
            if isinstance(e, Exception) and str(e) == "GPT ERROR":
                sys.exit(str(e))

            if init_persona_role == "investor":
                bind_res = run_gpt_prompt_connection_build_investor_v1_with_publicreputation(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    output_save_dir,
                    update_info["target_behavior_summary"],
                )[0]
            elif init_persona_role == "trustee":
                bind_res = run_gpt_prompt_connection_build_trustee_v1_with_publicreputation(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    output_save_dir,
                    update_info["target_behavior_summary"],
                )[0]
            elif str(init_persona_role.lower()) == "resident":
                bind_res = run_gpt_prompt_connection_build_after_chat_sign_up_v2_with_publicreputation(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    output_save_dir,
                    update_info["sum_convo"],
                )[0]
            elif init_persona_role == "player":
                # add publicreputation
                
                bind_res = run_gpt_prompt_connection_build_player_v1_with_publicreputation(
                    init_persona,
                    target_persona,
                    update_info["target_behavior_summary"],
                )[0]
            else:
                bind_res = "error"

            if type(bind_res) is str and "error" in bind_res.lower():
                sys.exit("GPT ERROR")

            if bind_res["Connect"].lower() == "yes":
                init_persona.scratch.relationship["bind_list"].append([target_persona.scratch.name, target_persona_role])



def get_social_network_decisions(init_persona, target_persona, init_persona_role, target_persona_role, update_info, init_persona_learned, target_persona_reputation, target_public_reputation, output_save_dir):
    """
    只负责 GPT 调用，返回意向结果，不修改 Persona 状态。
    """
    
    # 检查当前是否已建立连接
    is_connected = any(link[0] == target_persona.scratch.name for link in init_persona.scratch.relationship["bind_list"])
    
    res_data = {"action": None, "result": ""}

    if is_connected:
        # --- 情况 A: 已连接，决定是否断开 ---
        res_data["action"] = "disconnect"
        if init_persona_role == "investor":
            prompt_func = run_gpt_prompt_disconnection_investor_v1
            args = [init_persona, target_persona, target_persona_role, update_info["target_behavior_summary"]]
        # elif init_persona_role == "trustee":
        #     prompt_func = run_gpt_prompt_disconnection_trustee_v1
        #     args = [init_persona, target_persona, target_persona_role, update_info["target_behavior_summary"]]
        # elif init_persona_role == "resident":
        #     prompt_func = run_gpt_prompt_disconnection_after_chat_sign_up_v2
        #     args = [init_persona, target_persona, target_persona_role, update_info["sum_convo"]]
        elif init_persona_role == "player":
            prompt_func = run_gpt_prompt_disconnection_player_v1_with_publicreputation_with_buffer
            args = [init_persona, target_persona, init_persona_learned, target_persona_reputation, target_public_reputation, output_save_dir]
        else:
            return res_data

        gpt_res = prompt_func(*args)[0]
        if isinstance(gpt_res, str) and "error" in gpt_res.lower(): raise Exception("SN_GPT_ERROR")
        res_data["result"] = gpt_res.get("Disconnect", "").lower()

    else:
        # --- 情况 B: 未连接，决定是否建立 ---
        res_data["action"] = "connect"
        if init_persona_role == "investor":
            prompt_func = run_gpt_prompt_connection_build_investor_v1
            args = [init_persona, target_persona, target_persona_role, update_info["target_behavior_summary"]]
        # elif init_persona_role == "trustee":
        #     prompt_func = run_gpt_prompt_connection_build_trustee_v1
        #     args = [init_persona, target_persona, target_persona_role, update_info["target_behavior_summary"]]
        # elif init_persona_role == "resident":
        #     prompt_func = run_gpt_prompt_connection_build_after_chat_sign_up_v2
        #     args = [init_persona, target_persona, target_persona_role, update_info["sum_convo"]]
        elif init_persona_role == "player":
            prompt_func = run_gpt_prompt_connection_build_player_v1_with_publicreputation_with_buffer
            args = [init_persona, target_persona, init_persona_learned, target_persona_reputation, target_public_reputation, output_save_dir]
        else:
            return res_data

        gpt_res = prompt_func(*args)[0]
        if isinstance(gpt_res, str) and "error" in gpt_res.lower(): raise Exception("SN_GPT_ERROR")
        res_data["result"] = gpt_res.get("Connect", "").lower()

    return res_data



def social_network_update_with_gossip_with_publicreputation(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    update_info=None,
    full_investment=True,
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, target_persona_role])
        if init_persona_role == "investor":
            disconnection_res = run_gpt_prompt_disconnection_investor_v1(
                init_persona,
                target_persona,
                target_persona_role,
                interaction_memory=update_info["target_behavior_summary"],
            )[0]
        elif init_persona_role == "trustee":
            disconnection_res = run_gpt_prompt_disconnection_trustee_v1(
                init_persona,
                target_persona,
                target_persona_role,
                interaction_memory=update_info["target_behavior_summary"],
            )[0]
        elif init_persona_role == "resident":
            disconnection_res = run_gpt_prompt_disconnection_after_chat_sign_up_v2(
                init_persona,
                target_persona,
                target_persona_role,
                update_info["sum_convo"],
            )[0]
        elif init_persona_role == "player":
            # add publicreputation

            disconnection_res = run_gpt_prompt_disconnection_player_v1_with_gossip_with_publicreputation(
                init_persona,
                target_persona,
                target_persona_role,
                update_info["target_behavior_summary"],
            )[0]
        else:
            disconnection_res = "error"

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, target_persona_role])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])

    except Exception as e:
        if not full_investment:
            pass
        else:
            if isinstance(e, Exception) and str(e) == "GPT ERROR":
                sys.exit(str(e))

            if init_persona_role == "investor":
                bind_res = run_gpt_prompt_connection_build_investor_v1(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    update_info["target_behavior_summary"],
                )[0]
            elif init_persona_role == "trustee":
                bind_res = run_gpt_prompt_connection_build_trustee_v1(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    update_info["target_behavior_summary"],
                )[0]
            elif init_persona_role == "resident":
                bind_res = run_gpt_prompt_connection_build_after_chat_sign_up_v2(
                    init_persona,
                    target_persona,
                    target_persona_role,
                    update_info["sum_convo"],
                )[0]
            elif init_persona_role == "player":
                # add publicreputation
                
                bind_res = run_gpt_prompt_connection_build_player_v1_with_gossip_with_publicreputation(
                    init_persona,
                    target_persona,
                    update_info["target_behavior_summary"],
                )[0]
            else:
                bind_res = "error"

            if type(bind_res) is str and "error" in bind_res.lower():
                sys.exit("GPT ERROR")

            if bind_res["Connect"].lower() == "yes":
                init_persona.scratch.relationship["bind_list"].append([target_persona.scratch.name, target_persona_role])



# def social_network_update_with_publicreputation_with_buffer(
#     init_persona,
#     target_persona,
#     init_persona_role,
#     target_persona_role,
#     update_info=None,
#     full_investment=True,
# ):
#     sn_buffer = {
#             "disconnection": [],
#             "connection": []
#         }
#     try:
#         _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, target_persona_role])
#         if init_persona_role == "investor":
#             disconnection_res = run_gpt_prompt_disconnection_investor_v1(
#                 init_persona,
#                 target_persona,
#                 target_persona_role,
#                 interaction_memory=update_info["target_behavior_summary"],
#             )[0]
#         elif init_persona_role == "trustee":
#             disconnection_res = run_gpt_prompt_disconnection_trustee_v1(
#                 init_persona,
#                 target_persona,
#                 target_persona_role,
#                 interaction_memory=update_info["target_behavior_summary"],
#             )[0]
#         elif init_persona_role == "resident":
#             disconnection_res = run_gpt_prompt_disconnection_after_chat_sign_up_v2(
#                 init_persona,
#                 target_persona,
#                 target_persona_role,
#                 update_info["sum_convo"],
#             )[0]
#         elif init_persona_role == "player":
#             # add publicreputation

#             disconnection_res = run_gpt_prompt_disconnection_player_v1_with_publicreputation(
#                 init_persona,
#                 target_persona,
#                 target_persona_role,
#                 update_info["target_behavior_summary"],
#             )[0]
#         else:
#             disconnection_res = "error"

#         if type(disconnection_res) is str and "error" in disconnection_res.lower():
#             raise Exception("GPT ERROR")
            
#         # 先放入buffer，没问题再移动
#         if disconnection_res["Disconnect"].lower() == "yes":
#             sn_buffer["disconnection"].append([target_persona_role, disconnection_res])
#             # init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, target_persona_role])
#             # init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])

#     except Exception as e:
#         if not full_investment:
#             pass
#         else:
#             if isinstance(e, Exception) and str(e) == "GPT ERROR":
#                 # sys.exit(str(e))
#                 raise Exception("GPT ERROR")

#             if init_persona_role == "investor":
#                 bind_res = run_gpt_prompt_connection_build_investor_v1(
#                     init_persona,
#                     target_persona,
#                     target_persona_role,
#                     update_info["target_behavior_summary"],
#                 )[0]
#             elif init_persona_role == "trustee":
#                 bind_res = run_gpt_prompt_connection_build_trustee_v1(
#                     init_persona,
#                     target_persona,
#                     target_persona_role,
#                     update_info["target_behavior_summary"],
#                 )[0]
#             elif init_persona_role == "resident":
#                 bind_res = run_gpt_prompt_connection_build_after_chat_sign_up_v2(
#                     init_persona,
#                     target_persona,
#                     target_persona_role,
#                     update_info["sum_convo"],
#                 )[0]
#             elif init_persona_role == "player":
#                 # add publicreputation
                
#                 bind_res = run_gpt_prompt_connection_build_player_v1_with_publicreputation(
#                     init_persona,
#                     target_persona,
#                     update_info["target_behavior_summary"],
#                 )[0]
#             else:
#                 bind_res = "error"

#             if type(bind_res) is str and "error" in bind_res.lower():
#                 # sys.exit("GPT ERROR")
#                 raise Exception("GPT ERROR")

#             # 先放入buffer，没问题再移动
#             if bind_res["Connect"].lower() == "yes":
#                 sn_buffer["connection"].append([target_persona_role, bind_res])
#                 # init_persona.scratch.relationship["bind_list"].append([target_persona.scratch.name, target_persona_role])

#     return sn_buffer
                

def social_network_update_after_new_sign_up(
    init_persona,
    target_persona,
    save_folder,
    step,
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, "resident"])
        disconnection_res = run_gpt_prompt_disconnection_after_new_sign_up_v1(
            init_persona,
            target_persona,
            "resident",
        )[0]

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")
        
        with open(f"{save_folder}/disconnection_after_new_sign_up_{step}.txt", "a") as f:
            f.write(str(disconnection_res) + '\n')

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, "resident"])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, "resident"])
    except Exception as e:
        if isinstance(e, Exception) and str(e) == "GPT ERROR":
            sys.exit(str(e))




def social_network_update_after_new_sign_up_with_publicreputation(
    init_persona,
    target_persona,
    output_save_dir
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, "resident"])
        disconnection_res = run_gpt_prompt_disconnection_after_new_sign_up_v1_with_publicreputation(
            init_persona,
            target_persona,
            output_save_dir,
            "resident",
        )[0]

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, "resident"])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, "resident"])
    except Exception as e:
        if isinstance(e, Exception) and str(e) == "GPT ERROR":
            sys.exit(str(e))






def social_network_update_after_observed_invest(
    output_save_dir,
    init_persona,
    target_persona,
    update_info,
):
    try:
        _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, "resident"])
        disconnection_res = run_gpt_prompt_disconnection_after_observed_v1(
            output_save_dir,
            init_persona,
            target_persona,
            update_info["init_persona_role"],
            update_info["target_persona_role"],
            update_info["interaction_memory"],
        )[0]

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, "resident"])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, "resident"])
    except Exception as e:
        if isinstance(e, Exception) and str(e) == "GPT ERROR":
            sys.exit(str(e))




def social_network_update_after_observed_invest_with_publicreputation(
    init_persona,
    target_persona,
    update_info,
    output_save_dir
):
    try:
        # _ = init_persona.scratch.relationship["bind_list"].index([target_persona.scratch.name, "resident"])
        disconnection_res = run_gpt_prompt_disconnection_after_observed_v1_with_publicreputation(
            output_save_dir,
            init_persona,
            target_persona,
            update_info["init_persona_role"],
            update_info["target_persona_role"],
            update_info["interaction_memory"],
        )[0]

        if type(disconnection_res) is str and "error" in disconnection_res.lower():
            raise Exception("GPT ERROR")

        if disconnection_res["Disconnect"].lower() == "yes":
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, "resident"])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, "resident"])
    except Exception as e:
        if isinstance(e, Exception) and str(e) == "GPT ERROR":
            sys.exit(str(e))



def social_network_update_after_gossip(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    gossiper_name,
    gossip_info,
    output_save_dir
):
    gossip_res = run_gpt_prompt_disconnection_after_gossip_v2(init_persona, target_persona, init_persona_role, target_persona_role, gossiper_name, gossip_info, output_save_dir)[0]
    if gossip_res["Disconnect"].lower() == "yes":
        try:
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, target_persona_role])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])
        except ValueError:
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])
            pass


def social_network_update_after_gossip_with_publicreputation(
    init_persona,
    target_persona,
    init_persona_role,
    target_persona_role,
    gossiper_name,
    gossip_info,
    output_save_dir
):
    gossip_res = run_gpt_prompt_disconnection_after_gossip_v2_with_publicreputation(init_persona, target_persona, init_persona_role, target_persona_role, gossiper_name, gossip_info, output_save_dir)[0]
    if gossip_res["Disconnect"].lower() == "yes":
        try:
            init_persona.scratch.relationship["bind_list"].remove([target_persona.scratch.name, target_persona_role])
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])
        except ValueError:
            init_persona.scratch.relationship["black_list"].append([target_persona.scratch.name, target_persona_role])
            pass

    # if [target_persona.scratch.name, target_persona_role] in init_persona.scratch.relationship["black_list"]:
    #     rebuild_res = run_gpt_prompt_rebuild_connection_after_gossip_v2_with_publicreputation(init_persona, target_persona, init_persona_role, target_persona_role, gossiper_name, gossip_info, output_save_dir)[0]
    #     if rebuild_res["Connect"].lower() == "yes":
    #         try:
    #             init_persona.scratch.relationship["bind_list"].append([target_persona.scratch.name, target_persona_role])
    #             init_persona.scratch.relationship["black_list"].remove([target_persona.scratch.name, target_persona_role])
    #         except ValueError:
    #             pass