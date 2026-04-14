import os
from os.path import exists
import random
import threading
import time
import re

random.seed(42)
import networkx as nx
from decimal import Decimal
from reputation.gossip import first_order_gossip, first_order_gossip_with_publicreputation
from reputation.prompt_template.run_gpt_prompt import (
    run_gpt_prompt_gossip_listener_select_v2,
    run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation,
)
from reputation.reputation_update import reputation_update_pd_game, prepare_reputation_and_sn_plan
from reputation.social_network import *
from .prompt_template.run_gpt_prompt import *
from persona.persona import Persona


gossip_lock = threading.Lock()
print_result_lock = threading.Lock()
gossip_thread_count = 0
total_thread_count = 0
gossip_queue = []


def set_gossip_sync(total_count):
    global total_thread_count
    total_thread_count = total_count


def add_gossip_task(player1, player2):
    global gossip_thread_count

    with gossip_lock:
        gossip_thread_count += 1
        print(f"Thread {threading.current_thread().name}: finished game logic ({gossip_thread_count}/{total_thread_count})")

        has_gossip = len(player1.scratch.complain_buffer) > 0 or len(player2.scratch.complain_buffer) > 0

        if has_gossip:
            print(f"Thread {threading.current_thread().name}: has gossip, adding to queue")

            gossip_queue.append({"player1": player1, "player2": player2, "thread_id": threading.current_thread().name})
        else:
            print(f"Thread {threading.current_thread().name}: no gossip, ending immediately")

        if gossip_thread_count == total_thread_count:
            print("All threads finished, gossip will be executed sequentially in the main program")


def execute_gossip_sequential(personas, G, output_save_dir, max_retries: int = 3):
    print(f"Starting to execute {len(gossip_queue)} gossip tasks...")

    for task in gossip_queue:
        player1 = task["player1"]
        player2 = task["player2"]
        thread_id = task["thread_id"]

        print(f"Executing gossip task {thread_id}")

        max_attempts = max_retries + 1
        for attempt in range(max_attempts):
            try:
                if player1.scratch.complain_buffer:
                    for person in player1.scratch.complain_buffer:
                        gossip_target_player1 = run_gpt_prompt_gossip_listener_select_v2(player1, "player", personas[person["complaint_target"]], output_save_dir)[0]
                        for gossip_target in gossip_target_player1:
                            gossip_target_persona = personas[gossip_target]
                            first_order_gossip(
                                player1,
                                gossip_target_persona,
                                "player",
                                "player",
                                personas,
                                G,
                                output_save_dir,
                                val=person,
                            )

                if player2.scratch.complain_buffer:
                    for person in player2.scratch.complain_buffer:
                        gossip_target_player2 = run_gpt_prompt_gossip_listener_select_v2(player2, "player", personas[person["complaint_target"]], output_save_dir)[0]
                        for gossip_target in gossip_target_player2:
                            gossip_target_persona = personas[gossip_target]
                            first_order_gossip(
                                player2,
                                gossip_target_persona,
                                "player",
                                "player",
                                personas,
                                G,
                                output_save_dir,
                                val=person,
                            )

                print(f"Gossip task {thread_id} executed successfully")
                break

            except Exception as e:
                print(f"Gossip task {thread_id} attempt {attempt + 1} failed: {e}")

                if attempt < max_attempts - 1:
                    print(f"Gossip task {thread_id} waiting 5 seconds before retrying...")
                    time.sleep(5)
                else:
                    print(f"Gossip task {thread_id} reached maximum retries, skipping this task")

    print("All gossip tasks completed")

    gossip_queue.clear()



def execute_gossip_sequential_with_publicreputation(personas, G, output_save_dir, max_retries: int = 3):
    print(f"Starting to execute {len(gossip_queue)} gossip tasks...")

    for task in gossip_queue:
        player1 = task["player1"]
        player2 = task["player2"]
        thread_id = task["thread_id"]

        print(f"Executing gossip task {thread_id}")

        max_attempts = max_retries + 1
        for attempt in range(max_attempts):
            try:
                if player1.scratch.complain_buffer:
                    for person in player1.scratch.complain_buffer:
                        # def run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(init_persona, target_persona, output_save_dir, target_persona_role):
                        gossip_target_player1 = run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(player1, personas[person["complaint_target"]], output_save_dir, "player")[0]
                        for gossip_target in gossip_target_player1:
                            gossip_target_persona = personas[gossip_target]
                            first_order_gossip_with_publicreputation(
                                player1,
                                gossip_target_persona,
                                "player",
                                "player",
                                personas,
                                G,
                                output_save_dir,
                                val=person,
                            )

                if player2.scratch.complain_buffer:
                    for person in player2.scratch.complain_buffer:
                        gossip_target_player2 = run_gpt_prompt_gossip_first_listener_select_v2_with_publicreputation(player2, personas[person["complaint_target"]], output_save_dir, "player")[0]
                        for gossip_target in gossip_target_player2:
                            gossip_target_persona = personas[gossip_target]
                            first_order_gossip_with_publicreputation(
                                player2,
                                gossip_target_persona,
                                "player",
                                "player",
                                personas,
                                G,
                                output_save_dir,
                                val=person,
                                
                            )

                print(f"Gossip task {thread_id} executed successfully")
                break

            except Exception as e:
                print(f"Gossip task {thread_id} attempt {attempt + 1} failed: {e}")

                if attempt < max_attempts - 1:
                    print(f"Gossip task {thread_id} waiting 5 seconds before retrying...")
                    time.sleep(5)
                else:
                    print(f"Gossip task {thread_id} reached maximum retries, skipping this task")

    print("All gossip tasks completed")

    gossip_queue.clear()



def check_if_chosen(pairs, player_name):
    for pair in pairs:
        if player_name in pair:
            return True
    return False


def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list

def get_reputation_score(target_persona, target_persona_role, personas):
    count = 0
    num = 0
    for _, persona in personas.items():
        reputation = persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, target_persona_role)
        if reputation:
            count += 1
            repu_record = reputation[f"Player_{target_persona.scratch.ID}"]["numerical record"]
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




def pair_each_bak(personas: dict[str, Persona], G: nx.Graph, output_save_dir: str):
    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    player1_list = []
    player2_list = []
    score_list = []

    for i in range(0, len(personas_keys), 2):
        player1_list.append(personas_keys[i])
        player2_list.append(personas_keys[i + 1])
        score = get_reputation_score(personas[personas_keys[i]], "player", personas)
        score_list.append(score)

    sorted_indices = sorted(range(len(score_list)), key=lambda k: score_list[k], reverse=True)
    player1_list = [player1_list[i] for i in sorted_indices]

    for player1_k in player1_list:
        player1 = personas[player1_k]
        d_connect_list = get_d_connect(player1, G["player"])
        d_connect_list_clean = [d_connect for d_connect in d_connect_list if (d_connect not in player1_list) and (not check_if_chosen(pairs, d_connect))]

        if random.random() >= 0.5 and d_connect_list_clean:
            repu_list = ""
            for persona in d_connect_list_clean:
                repu = player1.reputationDB.get_targets_individual_reputation(personas[persona].scratch.ID, "player")
                repu_list += personas[persona].scratch.name + ":" + list(repu.values())[0]["content"] + "\n"

            while True:
                result, _ = run_gpt_prompt_select_player_v1(personas[player1_k], repu_list, output_save_dir)
                if result in d_connect_list_clean:
                    break
                else:
                    print("Value error: The player selected does not exist.")
            chosen_player2 = result

        else:
            unchosen_list = []
            for player2 in player2_list:
                if not check_if_chosen(pairs, player2):
                    unchosen_list.append(player2)
            chosen_player2 = random.choice(unchosen_list)

        pairs.append((player1_k, chosen_player2))

    print(pairs)
    return pairs

import random
import networkx as nx

def pair_each(personas: dict[str, "Persona"], G: nx.Graph, output_save_dir: str):
    personas_keys = list(personas.keys())
    random.shuffle(personas_keys)

    pairs = []
    player1_list = []
    player2_list = []
    score_list = []

    for i in range(0, len(personas_keys), 2):
        p1 = personas_keys[i]
        p2 = personas_keys[i + 1] 
        player1_list.append(p1)
        player2_list.append(p2)
        score = get_reputation_score(personas[p1], "player", personas)
        score_list.append(score)

    sorted_indices = sorted(range(len(score_list)), key=lambda k: score_list[k], reverse=True)
    player1_list = [player1_list[i] for i in sorted_indices]
    remaining = set(player2_list)

    for initiator_name in player1_list:
        chosen_partner = None
        initiator_persona = personas[initiator_name]
        
        if not remaining:
            break

        use_reputation = random.random() < 0.5

        if use_reputation:
            bidirectional = get_d_connect(initiator_persona, G["player"])
            available_neighbors = [n for n in bidirectional if n in remaining]
            target_pool = available_neighbors if available_neighbors else list(remaining)
            repu_list = ""
            for target_name in target_pool:
                target_persona = personas[target_name]
                repu = initiator_persona.reputationDB.get_targets_individual_reputation(target_persona.scratch.ID, "player")
                if repu and len(repu) > 0:
                    content = list(repu.values())[0]["content"]
                else:
                    content = "No private interaction history."
                repu_list += f"{target_persona.scratch.name}:{content}\n"

            for _ in range(2):
                try:
                    result, _ = run_gpt_prompt_select_player_v1(initiator_persona, repu_list, output_save_dir)               
                    if result in target_pool:
                        chosen_partner = result
                        break 
                    else:
                        print(f"GPT invalid choice: {result}, retrying...")
                except Exception as e:
                    print(f"GPT Error: {e}")

        if chosen_partner is None:
            chosen_partner = random.choice(list(remaining))

        pairs.append((initiator_name, chosen_partner))
        remaining.remove(chosen_partner)

    print(f"Generated {len(pairs)} pairs: {pairs}")
    return pairs


def start_pd_game(
    pair: tuple[str, str],
    personas: dict[str, Persona],
    G: nx.Graph,
    save_folder: str,
    stats_collector,
    version: str,
    max_retries: int = 3,
):
    return _execute_pd_game(pair, personas, G, save_folder, stats_collector, version)

def start_pd_game_with_gossip_with_publicreputation(
    pair: tuple[str, str],
    personas: dict[str, Persona],
    G: nx.Graph,
    save_folder: str,
    stats_collector,
    version,
    max_retries: int = 3,
):
    try:
        return _execute_pd_game_with_gossip_with_publicreputation(pair, personas, G, save_folder, stats_collector, version)
    except Exception as e:
        import traceback
        print("\n" + "="*50)
        print(f"CRITICAL ERROR in round for pair {pair}:")
        traceback.print_exc() 
        print("="*50 + "\n")
        sys.exit(1)

    # max_attempts = max_retries + 1
    # for attempt in range(max_attempts):
    #     try:
    #         return _execute_pd_game_with_gossip_with_publicreputation(pair, personas, G, save_folder, stats_collector, version)
    #         # return _execute_pd_game_with_gossip_with_publicreputation(pair, personas, G, save_folder, global_save_folder, version)
    #     except Exception as e:
    #         print(f"Thread {threading.current_thread().name}: Attempt {attempt + 1} failed: {e}")

    #         if attempt < max_attempts - 1:
    #             print(f"Thread {threading.current_thread().name}: Waiting 5 seconds before retrying...")
    #             time.sleep(5)
    #         else:
    #             print(f"Thread {threading.current_thread().name}: Maximum retries reached, giving up")
    #             return None, None, None, None


def _execute_pd_game(pair: tuple[str, str], personas: dict[str, Persona], G: nx.Graph, save_folder: str, stats_collector, version):
    parent_sim_path = os.path.dirname(os.path.dirname(save_folder))
    output_save_dir = os.path.join(parent_sim_path, f"{version}")

    player1 = personas[pair[0]]
    player2 = personas[pair[1]]

    print_stage1 = {
        "player1_decision": "Accept to play.",
        "player2_decision": "Accept to play.",
    }
    player1_decision = print_stage1["player1_decision"]
    player2_decision = print_stage1["player2_decision"]

    if "Refuse" in player1_decision or "Refuse" in player2_decision:
        player1.scratch.total_chat_num += 1
        player2.scratch.total_chat_num += 1

        print_stage2 = None
        print_stage3 = None
        print_stage4 = None

    else:
        player1.scratch.total_chat_num += 1
        player2.scratch.total_chat_num += 1
        player1.scratch.success_chat_num += 1
        player2.scratch.success_chat_num += 1

        player1_strategy = run_gpt_prompt_stage2_game_result_v1(player1, player2, output_save_dir, verbose=True)[0]
        player2_strategy = run_gpt_prompt_stage2_game_result_v1(player2, player1, output_save_dir, verbose=True)[0]

        if type(player1_strategy) is str and "error" in player1_strategy.lower():
            raise Exception("GPT ERROR")
        if type(player2_strategy) is str and "error" in player2_strategy.lower():
            raise Exception("GPT ERROR")

        if isinstance(player1_strategy, dict):
            player1_strategy = player1_strategy.get("Decision", "")
        else:
            player1_strategy = player1_strategy
        if isinstance(player2_strategy, dict):
            player2_strategy = player2_strategy.get("Decision", "")
        else:
            player2_strategy = player2_strategy

        player1_strategy = player1_strategy.strip().capitalize()
        player2_strategy = player2_strategy.strip().capitalize()

        if player1_strategy == "Cooperate" and player2_strategy == "Cooperate":
            player1_payoff = 3
            player2_payoff = 3
            game_result = "All-Cooperate"
        elif player1_strategy == "Cooperate" and player2_strategy == "Defect":
            player1_payoff = 0
            player2_payoff = 5
            game_result = f"{player1.name}-Cooperate, {player2.name}-Defect"
        elif player1_strategy == "Defect" and player2_strategy == "Cooperate":
            player1_payoff = 5
            player2_payoff = 0
            game_result = f"{player1.name}-Defect, {player2.name}-Cooperate"
        elif player1_strategy == "Defect" and player2_strategy == "Defect":
            player1_payoff = 1
            player2_payoff = 1
            game_result = "All-Defect"
        else:
            player1_payoff = 0
            player2_payoff = 0
            game_result = "Error"

        if hasattr(player1.scratch, "resources_unit"):
            player1.scratch.resources_unit += player1_payoff
        if hasattr(player2.scratch, "resources_unit"):
            player2.scratch.resources_unit += player2_payoff

        event_description = f"Game_result is {game_result}. {player1.name} chose {player1_strategy}, {player2.name} chose {player2_strategy}"

        player1.associativeMemory.add_event(
            subject=player1.name,
            predicate="pd_game",
            obj=player2.name,
            description=event_description,
            created_at=player1.scratch.curr_step,
        )
        player2.associativeMemory.add_event(
            subject=player2.name,
            predicate="pd_game",
            obj=player1.name,
            description=event_description,
            created_at=player1.scratch.curr_step,
        )

        print_stage2 = {
            "player1_payoff": player1_payoff,
            "player2_payoff": player2_payoff,
            "game_result": game_result,
        }

        player1_evaluation = run_gpt_prompt_stage3_player_evaluation_v1(
            player1,
            player2,
            player1_strategy,
            player2_strategy,
            output_save_dir, 
            verbose=True,
        )[0]
        player2_evaluation = run_gpt_prompt_stage3_player_evaluation_v1(
            player2,
            player1,
            player2_strategy,
            player1_strategy,
            output_save_dir,
            verbose=True,
        )[0]

        if type(player1_evaluation) is str and "error" in player1_evaluation.lower():
            raise Exception("GPT ERROR")
        if type(player2_evaluation) is str and "error" in player2_evaluation.lower():
            raise Exception("GPT ERROR")

        update_info_player1 = {
            "reason": "reputation update after pd_game",
            "init_persona_role": "player",
            "init_behavior_summary": player1_evaluation["self_reputation"],
            "target_behavior_summary": player1_evaluation["opponent_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(player2, G["player"])),
        }
        update_info_player2 = {
            "reason": "reputation update after pd_game",
            "init_persona_role": "player",
            "init_behavior_summary": player2_evaluation["self_reputation"],
            "target_behavior_summary": player2_evaluation["opponent_reputation"],
            "total_number_of_people": len(personas),
            "number_of_bidirectional_connections": len(get_d_connect(player1, G["player"])),
        }

        reputation_update_pd_game(player1, player2, update_info_player1, output_save_dir)
        reputation_update_pd_game(player2, player1, update_info_player2, output_save_dir)

        player1_gossip_willing = run_gpt_prompt_stage4_player_gossip_willing_v1(
            player1,
            player2,
            player1_strategy,
            player2_strategy,
            player1_evaluation["opponent_reputation"],
            output_save_dir,
            verbose=True,
        )[0]
        player2_gossip_willing = run_gpt_prompt_stage4_player_gossip_willing_v1(
            player2,
            player1,
            player2_strategy,
            player1_strategy,
            player2_evaluation["opponent_reputation"],
            output_save_dir,
            verbose=True,
        )[0]

        if type(player1_gossip_willing) is str and "error" in player1_gossip_willing.lower():
            raise Exception("GPT ERROR")
        if type(player2_gossip_willing) is str and "error" in player2_gossip_willing.lower():
            raise Exception("GPT ERROR")

        if "yes" in player1_gossip_willing.split(",")[0].lower():
            player1.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": player2.scratch.ID,
                    "complaint_target": player2.name,
                    "complaint_target_role": "player",
                    "complaint_reason": ",".join(player1_gossip_willing.split(",")[1:]),
                }
            )
        if "yes" in player2_gossip_willing.split(",")[0].lower():
            player2.scratch.complain_buffer.append(
                {
                    "complaint_target_ID": player1.scratch.ID,
                    "complaint_target": player1.name,
                    "complaint_target_role": "player",
                    "complaint_reason": ",".join(player2_gossip_willing.split(",")[1:]),
                }
            )

        print_stage3 = {
            "player1_evaluation": player1_evaluation,
            "player2_evaluation": player2_evaluation,
        }
        print_stage4 = {
            "player1_gossip_willing": player1_gossip_willing,
            "player2_gossip_willing": player2_gossip_willing,
        }

    add_gossip_task(player1, player2)

    # p1_private_rep = get_reputation_score(player1, "player", personas)
    # p1_public_rep = get_public_reputation_score(player1, "player")
    # p2_private_rep = get_reputation_score(player2, "player", personas)
    # p2_public_rep = get_public_reputation_score(player2, "player")


    # # round_idx, player_name, decision, version, private_rep, public_rep
    # stats_collector.log_decision(player1.scratch.curr_step, player1.name, player1_strategy, version, p1_private_rep, p1_public_rep)
    # stats_collector.log_decision(player2.scratch.curr_step, player2.name, player2_strategy, version, p2_private_rep, p2_public_rep)

    print_pd_game_result(
        player1,
        player2,
        print_stage1,
        print_stage2,
        print_stage3,
        print_stage4,
        save_folder,
    )



def _execute_pd_game_with_gossip_with_publicreputation(pair: tuple[str, str], personas: dict[str, Persona], G: nx.Graph, save_folder: str, stats_collector_with_gossip_with_publicreputation, version: str):
    
    parent_sim_path = os.path.dirname(os.path.dirname(save_folder))
    output_save_dir = os.path.join(parent_sim_path, f"{version}")

    player1, player2 = personas[pair[0]], personas[pair[1]]
    p1_strat_raw = run_gpt_prompt_stage2_game_result_v1_with_publicreputation(player1, player2, output_save_dir, verbose=True)[0]
    p2_strat_raw = run_gpt_prompt_stage2_game_result_v1_with_publicreputation(player2, player1, output_save_dir, verbose=True)[0]
    if "error" in str(p1_strat_raw).lower() or "error" in str(p2_strat_raw).lower():
        raise Exception("GPT_DECISION_ERROR")

    s1 = p1_strat_raw.get("Decision", "").strip().capitalize() if isinstance(p1_strat_raw, dict) else p1_strat_raw.strip().capitalize()
    s2 = p2_strat_raw.get("Decision", "").strip().capitalize() if isinstance(p2_strat_raw, dict) else p2_strat_raw.strip().capitalize()
    if s1 == "Cooperate" and s2 == "Cooperate": p1_p, p2_p, res_str = 3, 3, "All-Cooperate"
    elif s1 == "Cooperate" and s2 == "Defect": p1_p, p2_p, res_str = 0, 5, f"{player1.name}-Cooperate, {player2.name}-Defect"
    elif s1 == "Defect" and s2 == "Cooperate": p1_p, p2_p, res_str = 5, 0, f"{player1.name}-Defect, {player2.name}-Cooperate"
    elif s1 == "Defect" and s2 == "Defect": p1_p, p2_p, res_str = 1, 1, "All-Defect"
    else: p1_p, p2_p, res_str = 0, 0, "Error"

    eval1 = run_gpt_prompt_stage3_player_evaluation_v1(player1, player2, s1, s2, output_save_dir, verbose=True)[0]
    eval2 = run_gpt_prompt_stage3_player_evaluation_v1(player2, player1, s2, s1, output_save_dir, verbose=True)[0]
    if "error" in str(eval1).lower() or "error" in str(eval2).lower():
        raise Exception("GPT_EVALUATION_ERROR")

    p1_plan = prepare_reputation_and_sn_plan(player1, player2, eval1, output_save_dir, G)
    p2_plan = prepare_reputation_and_sn_plan(player2, player1, eval2, output_save_dir, G)

    p1_gossip_raw = run_gpt_prompt_stage4_player_gossip_willing_v1_with_publicreputation_with_buffer(player1, player2, s1, s2, eval1["opponent_reputation"], p1_plan['new_learned'], p1_plan['res_o'], p1_plan['public_val'], output_save_dir, verbose=True)[0]
    p2_gossip_raw = run_gpt_prompt_stage4_player_gossip_willing_v1_with_publicreputation_with_buffer(player2, player1, s2, s1, eval2["opponent_reputation"], p2_plan['new_learned'], p2_plan['res_o'], p2_plan['public_val'], output_save_dir, verbose=True)[0]
    if "error" in str(p1_gossip_raw).lower() or "error" in str(p2_gossip_raw).lower():
        raise Exception("GPT_GOSSIP_ERROR")

    for p, payoff in [(player1, p1_p), (player2, p2_p)]:
        p.scratch.total_chat_num += 1
        p.scratch.success_chat_num += 1
        if hasattr(p.scratch, "resources_unit"):
            p.scratch.resources_unit += payoff

    event_desc = f"Game_result is {res_str}. {player1.name} chose {s1}, {player2.name} chose {s2}"
    for p, opp in [(player1, player2), (player2, player1)]:
        p.associativeMemory.add_event(subject=p.name, predicate="pd_game", obj=opp.name, 
                                      description=event_desc, created_at=p.scratch.curr_step)

    for p, plan, opp in [(player1, p1_plan, player2), (player2, p2_plan, player1)]:
        if plan['res_s']: p.reputationDB.update_individual_reputation(plan['res_s'], p.scratch.curr_step, "pd_game")
        if plan['res_o']: p.reputationDB.update_individual_reputation(plan['res_o'], p.scratch.curr_step, "pd_game")
        if plan['report_to_public'] == "yes":
            publicreputationDB.update_or_create(plan['public_val'], p.scratch.curr_step, "update after pd game")
        if plan['new_learned']: p.scratch.learned = plan['new_learned']
        commit_social_network_changes(p, opp, plan['sn_data'])                               
    
    for p, opp, gossip_raw in [(player1, player2, p1_gossip_raw), (player2, player1, p2_gossip_raw)]:
        parts = gossip_raw.split(",")
        if "yes" in parts[0].lower():
            p.scratch.complain_buffer.append({
                "complaint_target_ID": opp.scratch.ID,
                "complaint_target": opp.name,
                "complaint_target_role": "player",
                "complaint_reason": ",".join(parts[1:]),
            })

    add_gossip_task(player1, player2)

    print_pd_game_result(
        player1, player2, 
        {"player1_decision": "Accept to play.", "player2_decision": "Accept to play."}, 
        {"player1_payoff": p1_p, "player2_payoff": p2_p, "game_result": res_str}, 
        {"player1_evaluation": eval1, "player2_evaluation": eval2}, 
        {"player1_gossip_willing": p1_gossip_raw, "player2_gossip_willing": p2_gossip_raw}, 
        save_folder
    )




def commit_social_network_changes(p_self, p_target, sn_data):
    if not sn_data or sn_data["result"] != "yes":
        return

    target_name = p_target.scratch.name
    relation_pair = [target_name, "player"]

    if sn_data["action"] == "disconnect":
        try:
            p_self.scratch.relationship["bind_list"].remove(relation_pair)
            if relation_pair not in p_self.scratch.relationship["black_list"]:
                p_self.scratch.relationship["black_list"].append(relation_pair)
        except ValueError: pass 

    elif sn_data["action"] == "connect":
        if relation_pair not in p_self.scratch.relationship["bind_list"]:
            p_self.scratch.relationship["bind_list"].append(relation_pair)


def print_pd_game_result(player1, player2, stage1, stage2, stage3, stage4, save_folder):
    with print_result_lock:
        step = player1.scratch.curr_step
        print(f"Step: {step}")
        print("+" + "-" * (100 - 2) + "+")
        print("|" + " " * 38 + "**PD Game Result**" + " " * 38 + "|")
        print("+" + "-" * (100 - 2) + "+")

        width = 100

        # stage 1
        print("+" + "-" * (100 - 2) + "+")
        print("|" + "**Stage  1**" + " " * (width - 14) + "|")
        print("+" + "-" * (100 - 2) + "+")
        player1_line = f"| Player1: {player1.name}: decision {stage1['player1_decision']}"
        print("+" + "-" * (width - 2) + "+")
        print(player1_line + " " * (width - len(player1_line) - 1) + "|")
        player2_line = f"| Player2: {player2.name}: decision {stage1['player2_decision']}"
        print(player2_line + " " * (width - len(player2_line) - 1) + "|")
        print("+" + "-" * (width - 2) + "+")

        if "Refuse" in stage1["player1_decision"] or "Refuse" in stage1["player2_decision"]:
            print("+" + "-" * (width - 2) + "+")
            print("|" + " " * 40 + "End of PD Game " + " " * 40 + "|")
            print("+" + "-" * (width - 2) + "+")
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            with open(f"{save_folder}/pd_game_results_{player1.scratch.curr_step}.txt", "a") as f:
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write("|" + "**Stage  1**" + " " * (width - 14) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")
                player1_line = f"| Player1: {player1.name}: decision {stage1['player1_decision']}"
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
                player2_line = f"| Player2: {player2.name}: decision {stage1['player2_decision']}"
                f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")

                f.write("+" + "-" * (width - 2) + "+\n")
                f.write("|" + " " * 40 + "End of PD Game " + " " * 40 + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n\n\n")

            return

        # stage 2
        if stage2 is not None:
            print("+" + "-" * (100 - 2) + "+")
            print("|" + "**Stage  2**" + " " * (width - 14) + "|")
            print("+" + "-" * (100 - 2) + "+")
            player1_line = f"| Player1: {player1.name}: payoff {stage2['player1_payoff']}"
            print("+" + "-" * (width - 2) + "+")
            print(player1_line + " " * (width - len(player1_line) - 1) + "|")
            player2_line = f"| Player2: {player2.name}: payoff {stage2['player2_payoff']}"
            print(player2_line + " " * (width - len(player2_line) - 1) + "|")
            game_result_line = f"| Game Result: {stage2['game_result']}"
            print(game_result_line + " " * (width - len(game_result_line) - 1) + "|")
            print("+" + "-" * (width - 2) + "+")

        # stage 3
        if stage3 is not None:
            print("+" + "-" * (100 - 2) + "+")
            print("|" + "**Stage  3**" + " " * (width - 14) + "|")
            print("+" + "-" * (100 - 2) + "+")
            player1_line = f"| Player1: {player1.name}: evaluation {stage3['player1_evaluation']}"
            print("+" + "-" * (width - 2) + "+")
            print(player1_line + " " * (width - len(player1_line) - 1) + "|")
            player2_line = f"| Player2: {player2.name}: evaluation {stage3['player2_evaluation']}"
            print(player2_line + " " * (width - len(player2_line) - 1) + "|")
            print("+" + "-" * (width - 2) + "+")

        # stage 4
        if stage4 is not None:
            print("+" + "-" * (100 - 2) + "+")
            print("|" + "**Stage  4**" + " " * (width - 14) + "|")
            print("+" + "-" * (100 - 2) + "+")
            player1_line = f"| Player1: {player1.name}: gossip willing {stage4['player1_gossip_willing']}"
            print("+" + "-" * (width - 2) + "+")
            print(player1_line + " " * (width - len(player1_line) - 1) + "|")
            player2_line = f"| Player2: {player2.name}: gossip willing {stage4['player2_gossip_willing']}"
            print(player2_line + " " * (width - len(player2_line) - 1) + "|")
            print("+" + "-" * (width - 2) + "+")

        print("+" + "-" * (width - 2) + "+")
        print("|" + " " * 40 + "End of PD Game " + " " * 40 + "|")
        print("+" + "-" * (width - 2) + "+")

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        with open(f"{save_folder}/pd_game_results_{player1.scratch.curr_step}.txt", "a") as f:
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write("|" + "**Stage  1**" + " " * (width - 14) + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n")
            player1_line = f"| Player1: {player1.name}: decision {stage1['player1_decision']}"
            f.write("+" + "-" * (width - 2) + "+\n")
            f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
            player2_line = f"| Player2: {player2.name}: decision {stage1['player2_decision']}"
            f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n")

            if stage2 is not None:
                f.write("+" + "-" * (100 - 2) + "+\n")
                f.write("|" + "**Stage  2**" + " " * (width - 14) + "|\n")
                f.write("+" + "-" * (100 - 2) + "+\n")
                player1_line = f"| Player1: {player1.name}: payoff {stage2['player1_payoff']}"
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
                player2_line = f"| Player2: {player2.name}: payoff {stage2['player2_payoff']}"
                f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
                game_result_line = f"| Game Result: {stage2['game_result']}"
                f.write(game_result_line + " " * (width - len(game_result_line) - 1) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")

            if stage3 is not None:
                f.write("+" + "-" * (100 - 2) + "+\n")
                f.write("|" + "**Stage  3**" + " " * (width - 14) + "|\n")
                f.write("+" + "-" * (100 - 2) + "+\n")
                player1_line = f"| Player1: {player1.name}: evaluation {stage3['player1_evaluation']}"
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
                player2_line = f"| Player2: {player2.name}: evaluation {stage3['player2_evaluation']}"
                f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")

            if stage4 is not None:
                f.write("+" + "-" * (100 - 2) + "+\n")
                f.write("|" + "** gossip **" + " " * (width - 14) + "|\n")
                f.write("+" + "-" * (100 - 2) + "+\n")
                player1_line = f"| Player1: {player1.name}: gossip willing {stage4['player1_gossip_willing']}"
                f.write("+" + "-" * (width - 2) + "+\n")
                f.write(player1_line + " " * (width - len(player1_line) - 1) + "|\n")
                player2_line = f"| Player2: {player2.name}: gossip willing {stage4['player2_gossip_willing']}"
                f.write(player2_line + " " * (width - len(player2_line) - 1) + "|\n")
                f.write("+" + "-" * (width - 2) + "+\n")

            f.write("+" + "-" * (width - 2) + "+\n")
            f.write("|" + " " * 40 + "End of PD Game " + " " * 40 + "|\n")
            f.write("+" + "-" * (width - 2) + "+\n\n\n")
    return
