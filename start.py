import os
import json
import shutil
import traceback
import errno
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import networkx as nx
from task.investment.investment import *
from task.investment_without_gossip.investment import *
from task.investment_without_reputation.investment import *
from task.investment_without_reputation_without_gossip.investment import *

from task.sign_up.sign_up import *
from task.sign_up_without_gossip.sign_up import *
from task.sign_up_without_reputation.sign_up import *
from task.sign_up_without_reputation_without_gossip.sign_up import *

from task.pd_game.pd_game import *
from task.pd_game_without_gossip.pd_game import *
from task.pd_game_without_reputation.pd_game import *
from task.pd_game_without_reputation_without_gossip.pd_game import *

from utils import *
from persona.persona import Persona
from public_reputation.SharedPublicReputationDB import init_public_reputation_db, publicreputationDB, restore_publicreputation_db_from_step

from pathlib import Path


from task.pd_game.game_statistics import *

class Creation:
    def __init__(
        self,
        sim_code,
        with_reputation,
        with_gossip,
        with_publicreputation,
        sim=None,
        
    ):
        self.sim_code = f"{sim_code}"
        sim_folder = sim_folder = f"{fs_storage}/{self.sim_code}"

        with open(f"{sim_folder}/reverie/meta.json") as json_file:
            reverie_meta = json.load(json_file)

        self.step = reverie_meta["step"]
        self.personas = dict()
        self.G = dict()
        self.with_reputation = "y" in with_reputation.lower() and "n" not in with_reputation.lower()
        self.with_publicreputation = "y" in with_publicreputation.lower() and "n" not in with_publicreputation.lower()
        self.with_gossip = "y" in with_gossip.lower() and "n" not in with_gossip.lower()


        # public_reputation_save_folder = Path(sim_folder).parent
        self.parent_sim_path = Path(sim_folder).parent
        visible_save_dir = os.path.join(self.parent_sim_path, "result_visible")
        
        self.stats_collector = GameStatistics(visible_save_dir)

        # publicreputationDB roll back
        if self.with_publicreputation and "step_" in self.sim_code:
            global_db_path = os.path.join(self.parent_sim_path, "public_reputation_database.json")
            
            print(f"Restoring PublicReputationDB from {sim_folder} to {global_db_path}...")
            restore_publicreputation_db_from_step(sim_folder, global_db_path)

        for persona_name in reverie_meta["persona_names"]:
            persona_folder = f"{sim_folder}/personas/{persona_name}"
            if sim == "investment":
                curr_persona = Persona(persona_name, persona_folder, self.with_reputation, self.with_publicreputation, investment=True)
            else:
                curr_persona = Persona(persona_name, persona_folder, self.with_reputation, self.with_publicreputation)
            self.personas[persona_name] = curr_persona

        init_public_reputation_db(f"{self.parent_sim_path}")
        if sim and "invest" in sim:
            self.set_graph_invest()
            role = "trustee"
            scenario = "invest"
            publicreputationDB.initialize_neutral_reputations(
            list(self.personas.values()), 
            role=role,
            scenario=scenario)
            role = "investor"
            scenario = "invest"
            publicreputationDB.add_initialize_neutral_reputations(
            list(self.personas.values()), 
            role=role,
            scenario=scenario)
        elif sim and "sign" in sim:
            self.set_graph_sign_up()
            role = "resident"
            scenario = "sign_up"
            publicreputationDB.initialize_neutral_reputations(
            list(self.personas.values()), 
            role=role,
            scenario=scenario)
        elif sim and "pd" in sim:
            self.set_graph_pd_game()
            role = "player"
            scenario = "pd_game"
            publicreputationDB.initialize_neutral_reputations(
            list(self.personas.values()), 
            role=role,
            scenario=scenario)

        
        

        # if self.with_publicreputation:
        #     init_public_reputation_db(f"{self.parent_sim_path}")
        #     publicreputationDB.initialize_neutral_reputations(
        #         list(self.personas.values()), 
        #         role="player",
        #         scenario=scenario
        #     )

    def set_graph_sign_up(self):
        self._set_graph_r()

    def set_graph_invest(self):
        self._set_graph_i()
        self._set_graph_t()

    def set_graph_pd_game(self):
        self._set_graph_p()

    def _set_graph_r(self):
        # resident graph
        G = nx.DiGraph()
        for _, persona in self.personas.items():
            if not G.has_node(persona.name):
                G.add_nodes_from([persona.name])
            black_list = list(persona.scratch.relationship["black_list"])
            bind_list = list(persona.scratch.relationship["bind_list"])
            for bind in bind_list:
                if bind[0] not in black_list:
                    if not G.has_node(bind[0]):
                        G.add_nodes_from([bind[0]])
                    G.add_edges_from([(persona.name, bind[0])])
        self.G["resident"] = G
        self.stats_collector.draw_network(G, title="RepuNet Network", step=self.step, save_every=2)

    def _set_graph_i(self):
        # investor graph
        G = nx.DiGraph()
        for _, persona in self.personas.items():
            if not G.has_node(persona.name):
                G.add_nodes_from([persona.name])
            black_list = list(persona.scratch.relationship["black_list"])
            bind_list = list(persona.scratch.relationship["bind_list"])
            for bind in bind_list:
                if bind[0] not in black_list and bind[1] != "trustee":
                    if not G.has_node(bind[0]):
                        G.add_nodes_from([bind[0]])
                    G.add_edges_from([(persona.name, bind[0])])
        self.G["investor"] = G

    def _set_graph_t(self):
        # trustee graph
        G = nx.DiGraph()
        for _, persona in self.personas.items():
            if not G.has_node(persona.name):
                G.add_nodes_from([persona.name])
            black_list = list(persona.scratch.relationship["black_list"])
            bind_list = list(persona.scratch.relationship["bind_list"])
            for bind in bind_list:
                if bind[0] not in black_list and bind[1] != "investor":
                    if not G.has_node(bind[0]):
                        G.add_nodes_from([bind[0]])
                    G.add_edges_from([(persona.name, bind[0])])
        self.G["trustee"] = G

    def _set_graph_p(self):
        # player graph for PD game
        G = nx.DiGraph()
        for _, persona in self.personas.items():
            if not G.has_node(persona.name):
                G.add_nodes_from([persona.name])
            black_list = list(persona.scratch.relationship["black_list"])
            bind_list = list(persona.scratch.relationship["bind_list"])
            for bind in bind_list:
                if bind[0] not in black_list:
                    if not G.has_node(bind[0]):
                        G.add_nodes_from([bind[0]])
                    G.add_edges_from([(persona.name, bind[0])])
        self.G["player"] = G
        
        self.stats_collector.draw_network(G, title="RepuNet Network", step=self.step, save_every=2)
        # if self.with_publicreputation and not self.with_gossip:
        #     stats_collector_with_publicreputation.draw_network(G, title="RepuNet Network", step=self.step, save_every=2)
        # if self.with_publicreputation and self.with_gossip:
        #     stats_collector_with_gossip_with_publicreputation.draw_network(G, title="RepuNet Network", step=self.step, save_every=2)


    def save(self):
        sim_folder = f"{fs_storage}/{self.sim_code}"
        reverie_meta = dict()
        reverie_meta["persona_names"] = list(self.personas.keys())
        reverie_meta["step"] = self.step
        reverie_meta_f = f"{sim_folder}/reverie/meta.json"
        with open(reverie_meta_f, "w") as outfile:
            outfile.write(json.dumps(reverie_meta, indent=2))

        # Save the personas.
        for persona_name, persona in self.personas.items():
            save_folder = f"{sim_folder}/personas/{persona_name}"
            persona.associativeMemory.base_path = f"{save_folder}/memory/associative_memory"
            persona.save(save_folder)
            # save reputation and gossip
            reputation_folder = f"{sim_folder}/personas/{persona_name}/reputation"
            if self.with_reputation:
                persona.reputationDB.save(reputation_folder)
            gossip_folder = f"{sim_folder}/personas/{persona_name}/reputation"
            persona.gossipDB.save(gossip_folder)

    def start_server_investment(self, int_counter):
        while True:
            self.stats_collector.final_save_and_plot()
            # Done with this iteration if <int_counter> reaches 0.
            if int_counter == 0:
                break

            self.step += 1
            for persona_name, persona in self.personas.items():
                persona.scratch.curr_step += 1
            origin_sim_folder = f"{fs_storage}/{self.sim_code}"
            new_sim_code = self.sim_code.split("/")[0] + f"/step_{self.step}"
            new_sim_folder = f"{fs_storage}/{new_sim_code}"
            self.sim_code = new_sim_code
            # copy the investment data to the new simulation folder
            shutil.copytree(
                f"{origin_sim_folder}",
                f"{new_sim_folder}",
            )

            if os.path.exists(f"{new_sim_folder}/investment results"):
                shutil.rmtree(f"{new_sim_folder}/investment results")
            self.set_graph_invest()
            print(f"sim_code: {self.sim_code}-----------------------------------------------")

            if self.with_reputation and self.with_gossip and not self.with_publicreputation:
                from task.investment.investment import update_knowns_reputation_observation, pair_each
                version = "with_gossip_repu_wo_pub"
                if self.step != 1 and (self.step - 1) % 5 == 0:
                    update_knowns_reputation_observation(self.personas, f"{fs_storage}/{self.sim_code}/investment results")
                
                from task.investment.investment import pair_each
                pairs = pair_each(self.personas, self.G, f"{self.parent_sim_path}/with_gossip_repu_wo_pub")
                for pair in pairs:
                    start_investment(
                        pair,
                        self.personas,
                        self.G,
                        self.stats_collector,
                        version,
                        f"{fs_storage}/{self.sim_code}/investment results",
                    )

            elif self.with_reputation and self.with_gossip and self.with_publicreputation:
                version = "with_reputation_publicreputation_gossip"
                if self.step != 1 and (self.step - 1) % 5 == 0:
                    update_knowns_reputation_observation_with_publicreputation(self.personas, f"{self.parent_sim_path}/investment_with_publicreputation")
                
                from task.investment.investment import pair_each_with_publicreputation
                pairs = pair_each_with_publicreputation(self.personas, self.G, f"{self.parent_sim_path}/investment_with_publicreputation")

                for pair in pairs:
                    start_investment_with_publicreputation(
                        pair,
                        self.personas,
                        self.G,
                        self.stats_collector,
                        version,
                        f"{fs_storage}/{self.sim_code}/investment results",
                    )

                sim_folder = f"{fs_storage}/{self.sim_code}"
                # Save the personas.
                for persona_name, persona in self.personas.items():
                    save_folder = f"{sim_folder}/personas/{persona_name}"
                    public_save_folder = f"{save_folder}/reputation/public_reputation.json"
                    persona.record_publicreputation_to_local(public_save_folder, persona.scratch.ID, role="investor")
                    persona.record_publicreputation_to_local(public_save_folder, persona.scratch.ID, role="trustee")

                # # 添加统计
                # for pair in pairs:
                #     investor = self.personas[pair[0]]
    
                #     investor_private_rep = get_reputation_score(investor, "investor", self.personas)
                #     investor_public_rep = get_public_reputation_score(investor, "investor")
                #     investor_bind_list = list(investor.scratch.relationship.get("bind_list", []))
                #     investor_black_list = list(investor.scratch.relationship.get("black_list", []))
                #     self.stats_collector.log_player_relationships(
                #         self.step, 
                #         investor.scratch.name, 
                #         investor_bind_list, 
                #         investor_black_list, 
                #         investor_private_rep, 
                #         investor_public_rep
                #     )

                #     trustee = self.personas[pair[1]]
                #     trustee_private_rep = get_reputation_score(trustee, "trustee", self.personas)
                #     trustee_public_rep = get_public_reputation_score(trustee, "trustee")
                #     trustee_bind_list = list(trustee.scratch.relationship.get("bind_list", []))
                #     trustee_black_list = list(trustee.scratch.relationship.get("black_list", []))
                #     self.stats_collector.log_player_relationships(
                #         self.step, 
                #         trustee.scratch.name, 
                #         trustee_bind_list, 
                #         trustee_black_list, 
                #         trustee_private_rep, 
                #         trustee_public_rep
                #     )
                # # C. 每一轮结束，统一执行保存
                # self.stats_collector.run_autosave(self.step)


            elif self.with_reputation and not self.with_gossip:
                pairs = pair_each_without_gossip(self.personas, self.G)

                for pair in pairs:
                    start_investment_without_gossip(
                        pair,
                        self.personas,
                        self.G,
                        f"{fs_storage}/{self.sim_code}/investment results",
                    )
            elif not self.with_reputation and self.with_gossip:
                pairs = pair_each_without_reputation(self.personas, self.G)

                for pair in pairs:
                    start_investment_without_reputation(
                        pair,
                        self.personas,
                        self.G,
                        f"{fs_storage}/{self.sim_code}/investment results",
                    )
            elif not self.with_reputation and not self.with_gossip:
                pairs = pair_each_without_reputation_without_gossip(self.personas, self.G)
                for pair in pairs:
                    start_investment_without_reputation_without_gossip(
                        pair,
                        self.personas,
                        self.G,
                        f"{fs_storage}/{self.sim_code}/investment results",
                    )

            self.save()
            int_counter -= 1

    def start_server_sign_up(self, int_counter):
        while True:
            # Done with this iteration if <int_counter> reaches 0.
            # self.stats_collector.final_save_and_plot()
            if int_counter == 0:
                break

            self.step += 1
            for _, persona in self.personas.items():
                persona.scratch.curr_step += 1
            origin_sim_folder = f"{fs_storage}/{self.sim_code}"
            new_sim_code = self.sim_code.split("/")[0] + f"/step_{self.step}"
            new_sim_folder = f"{fs_storage}/{new_sim_code}"
            self.sim_code = new_sim_code
            # copy the investment data to the new simulation folder
            shutil.copytree(
                f"{origin_sim_folder}",
                f"{new_sim_folder}",
            )

            if os.path.exists(f"{new_sim_folder}/sign up result"):
                shutil.rmtree(f"{new_sim_folder}/sign up result")

            # if self.step == 1:
            #     # persona reputation init
            #     for persona_name, persona in self.personas.items():
            #         reputation_init_sign_up(persona)

            self.set_graph_sign_up()
            print(f"sim_code: {self.sim_code}-----------------------------------------------")

            sign_up_flag = False
            if (self.step - 1) % 5 == 0:
                sign_up_flag = True
            # sign_up_flag = True

            if self.with_reputation and self.with_gossip and not self.with_publicreputation:
                start_sign_up(
                    self.personas,
                    self.G,
                    self.step,
                    self.stats_collector,
                    f"{new_sim_folder}/sign up result",
                    sign_up_flag,
                    # add
                )
                
                
            elif self.with_reputation and self.with_gossip and self.with_publicreputation:
                version = "with_gossip_with_reputation_with_publicreputation"
                start_sign_up_with_publicreputation(
                    self.personas,
                    self.G,
                    self.step,
                    # 记录sign up 结果
                    self.stats_collector,
                    version,
                    f"{new_sim_folder}/sign up result",
                    sign_up_flag,
                )
                sim_folder = f"{fs_storage}/{self.sim_code}"
                # Save the personas.
                for persona_name, persona in self.personas.items():
                    save_folder = f"{sim_folder}/personas/{persona_name}"
                    public_save_folder = f"{save_folder}/reputation/public_reputation.json"
                    persona.record_publicreputation_to_local(public_save_folder, persona.scratch.ID, role="resident")
                
                
                
                # for _, persona in self.personas.items():
                #     private_rep = get_reputation_score(persona, "resident", self.personas)
                #     public_rep = get_public_reputation_score(persona, "resident")
                #     bind_list = list(persona.scratch.relationship["bind_list"])
                #     black_list = list(persona.scratch.relationship["black_list"])
                #     # log_player_relationships(self, round_idx, player_name, bind_list, black_list, private_rep, public_rep):
                #     self.stats_collector.log_player_relationships(self.step, persona.scratch.name, bind_list, black_list, private_rep, public_rep)
                # self.stats_collector.run_autosave(self.step)

                
            elif self.with_reputation and not self.with_gossip and self.with_publicreputation:
                start_sign_up_without_gossip_with_publicreputation(
                    self.personas,
                    self.G,
                    self.step,
                    self.stats_collector,
                    f"{new_sim_folder}/sign up result",
                    sign_up_flag,
                )


            elif self.with_reputation and not self.with_gossip and not self.with_publicreputation:
                start_sign_up_without_gossip(
                    self.personas,
                    self.G,
                    self.step,
                    self.stats_collector,
                    f"{new_sim_folder}/sign up result",
                    sign_up_flag,
                )

            elif not self.with_reputation and self.with_gossip:
                start_sign_up_without_reputation(
                    self.personas,
                    self.G,
                    self.step,
                    self.stats_collector,
                    f"{new_sim_folder}/sign up result",
                    sign_up_flag,
                )

            elif not self.with_reputation and not self.with_gossip:
                start_sign_up_without_reputation_without_gossip(
                    self.personas,
                    self.G,
                    self.step,
                    self.stats_collector,
                    f"{new_sim_folder}/sign up result",
                    sign_up_flag,
                )

            self.save()
            int_counter -= 1

    def start_server_pd_game(self, int_counter):
        """启动PD游戏服务器"""
        print("Starting PD Game Server...")

        while True:
            # Done with this iteration if <int_counter> reaches 0.
            # self.stats_collector.final_save_and_plot()
            if int_counter == 0:
                break

            self.step += 1
            for persona_name, persona in self.personas.items():
                persona.scratch.curr_step += 1
            origin_sim_folder = f"{fs_storage}/{self.sim_code}"
            new_sim_code = self.sim_code.split("/")[0] + f"/step_{self.step}"
            new_sim_folder = f"{fs_storage}/{new_sim_code}"
            self.sim_code = new_sim_code
            # copy the PD game data to the new simulation folder
            shutil.copytree(
                f"{origin_sim_folder}",
                f"{new_sim_folder}",
            )

            if os.path.exists(f"{new_sim_folder}/pd_game results"):
                shutil.rmtree(f"{new_sim_folder}/pd_game results")
            self.set_graph_pd_game()
            print(f"sim_code: {self.sim_code}-----------------------------------------------")

            # 根据reputation和gossip设置选择相应的PD游戏版本
            # if self.with_reputation and self.with_gossip:
            if self.with_reputation and self.with_gossip and not self.with_publicreputation:

                # 原始版本：有reputation和gossip
                print("Using original PD game with reputation and gossip, without public reputation")
                # pairs = pair_each(self.personas, self.G, f"{self.parent_sim_path}/original")
                from task.pd_game.pd_game import pair_each
                pairs = pair_each(self.personas, self.G, f"{self.parent_sim_path}/original")
                # 设置gossip同步
                from task.pd_game.pd_game import set_gossip_sync

                set_gossip_sync(len(pairs))

                # 多线程执行PD游戏
                self.execute_pd_games_parallel(pairs, f"{fs_storage}/{self.sim_code}/pd_game results", "original")

                # 顺序执行gossip（如果有的话）
                from task.pd_game.pd_game import execute_gossip_sequential, gossip_queue

                if gossip_queue:
                    print("START EXECUTE Gossip!!!!!!!!!!!!!!!!!!!!!")
                    execute_gossip_sequential(self.personas, self.G, f"{self.parent_sim_path}/original", max_retries=3)
                # self.stats_collector.run_autosave(self.step)

            # 根据reputation和gossip设置选择相应的PD游戏版本
            elif self.with_reputation and self.with_gossip and self.with_publicreputation:
                # 原始版本：有reputation和gossip
                print("Using PD game with reputation and gossip and publicreputation")
                pairs = pair_each_with_publicreputation(self.personas, self.G, f"{self.parent_sim_path}/with_gossip_with_publicreputation")

                # 设置gossip同步
                from task.pd_game.pd_game import set_gossip_sync

                set_gossip_sync(len(pairs))

                # 多线程执行PD游戏
                self.execute_pd_games_parallel(pairs, f"{fs_storage}/{self.sim_code}/pd_game results", "with_gossip_with_publicreputation")

                # 图像绘制
                # print("All rounds completed. Generating plots...")
                # save_folder = "task/pd_game/output/results_visible"
                # stats_collector_with_gossip_with_publicreputation.run_autosave(self.step)

                # 顺序执行gossip（如果有的话）
                from task.pd_game.pd_game import execute_gossip_sequential, gossip_queue

                if gossip_queue:
                    print("START EXECUTE Gossip!!!!!!!!!!!!!!!!!!!!!")
                    execute_gossip_sequential_with_publicreputation(self.personas, self.G, f"{self.parent_sim_path}/with_gossip_with_publicreputation", max_retries=3)
                
                sim_folder = f"{fs_storage}/{self.sim_code}"
                # Save the personas.
                for persona_name, persona in self.personas.items():
                    save_folder = f"{sim_folder}/personas/{persona_name}"
                    public_save_folder = f"{save_folder}/reputation/public_reputation.json"
                    persona.record_publicreputation_to_local(public_save_folder, persona.scratch.ID, role="player")
                # for _, persona in self.personas.items():
                #     private_rep = get_reputation_score(persona, "player", self.personas)
                #     public_rep = get_public_reputation_score(persona, "player")
                #     bind_list = list(persona.scratch.relationship["bind_list"])
                #     black_list = list(persona.scratch.relationship["black_list"])
                #     # log_player_relationships(self, round_idx, player_name, bind_list, black_list, private_rep, public_rep):
                #     self.stats_collector.log_player_relationships(self.step, persona.scratch.name, bind_list, black_list, private_rep, public_rep)
                # self.stats_collector.run_autosave(self.step)

            elif self.with_reputation and not self.with_gossip:
                # without_gossip版本：有reputation，无gossip
                print("Using PD game without gossip (with reputation)")
                pairs = pair_each(self.personas, self.G)

                # 多线程执行PD游戏（无gossip）
                self.execute_pd_games_parallel(pairs, f"{fs_storage}/{self.sim_code}/pd_game results", "without_gossip")
                # 图像绘制
                print("All rounds completed. Generating plots...")
                # save_folder = "task/pd_game_without_gossip/output/results_visible"
                # stats_collector.run_autosave(self.step)


            elif not self.with_reputation and self.with_gossip:
                # without_reputation版本：无reputation，有gossip
                print("Using PD game without reputation (with gossip)")

                pairs = pair_each_without_reputation(self.personas, self.G)

                # 设置gossip同步
                from task.pd_game_without_reputation.pd_game import set_gossip_sync

                set_gossip_sync(len(pairs))

                # 多线程执行PD游戏
                self.execute_pd_games_parallel(pairs, f"{fs_storage}/{self.sim_code}/pd_game results", "without_reputation")

                # 顺序执行gossip（如果有的话）
                from task.pd_game_without_reputation.pd_game import execute_gossip_sequential_without_reputation, gossip_queue

                if gossip_queue:
                    print("START EXECUTE Gossip!!!!!!!!!!!!!!!!!!!!!")
                    execute_gossip_sequential_without_reputation(self.personas, self.G, max_retries=3)

            else:
                # without_reputation_without_gossip版本：无reputation，无gossip
                print("Using PD game without reputation and without gossip")

                pairs = pair_each_without_reputation_without_gossip(self.personas, self.G)

                # 多线程执行PD游戏（无reputation和gossip）
                self.execute_pd_games_parallel(pairs, f"{fs_storage}/{self.sim_code}/pd_game results", "without_reputation_without_gossip")

            self.save()
            int_counter -= 1
        
        

    def execute_pd_games_parallel(self, pairs, save_folder, version="original"):
        """并行执行PD游戏"""
        
        with ThreadPoolExecutor(max_workers=len(pairs)) as executor:
            # 根据版本选择相应的函数
            if version == "original":
                start_func = start_pd_game
            elif version == "without_gossip":
                start_func = start_pd_game_without_gossip  # 使用without_gossip模块的start_pd_game_without_gossip
            elif version == "with_gossip_with_publicreputation":
                start_func = start_pd_game_with_gossip_with_publicreputation  # 使用without_gossip模块的start_pd_game_without_gossip
            elif version == "without_reputation":
                start_func = start_pd_game_without_reputation
            elif version == "without_reputation_without_gossip":
                start_func = start_pd_game_without_reputation_without_gossip
            else:
                start_func = start_pd_game

            # 提交所有任务
            future_to_pair = {
                executor.submit(
                    start_func,
                    pair,
                    self.personas,
                    self.G,
                    save_folder,
                    self.stats_collector,
                    version,
                    max_retries=5,  # 设置最大重试次数
                ): pair
                for pair in pairs
            }

            # 等待所有任务完成
            for future in as_completed(future_to_pair):
                pair = future_to_pair[future]
                try:
                    result = future.result()
                    if result and result[0] is not None:
                        print(f"Completed PD game ({version}): {pair[0]} vs {pair[1]}")
                    else:
                        print(f"Failed PD game ({version}): {pair[0]} vs {pair[1]} (after all retries)")
                except Exception as e:
                    print(f"Error in PD game ({version}) {pair[0]} vs {pair[1]}: {e}")


    def open_server(self):
        """
        Open up an interactive terminal prompt that lets you run the simulation
        step by step and probe agent state.

        INPUT
          None
        OUTPUT
          None
        """
        print("Note: The agents in this simulation package are computational")
        print("constructs powered by generative agents architecture and LLM. We")
        print("clarify that these agents lack human-like agency, consciousness,")
        print("and independent decision-making.\n---")

        # <sim_folder> points to the current simulation folder.
        sim_folder = f"{fs_storage}/{self.sim_code}"

        while True:
            sim_folder = f"{fs_storage}/{self.sim_code}"
            sim_command = input("Enter option: ")
            sim_command = sim_command.strip()
            ret_str = ""

            try:
                if sim_command.lower() in ["f", "fin", "finish", "save and finish"]:
                    # Finishes the simulation environment and saves the progress.
                    # Example: fin
                    # self.save()
                    print("Simulation finished.")
                    break

                elif sim_command.lower() == "exit":
                    # Finishes the simulation environment but does not save the progress
                    # and erases all saved data from current simulation.
                    # Example: exit
                    shutil.rmtree(sim_folder)
                    break

                elif sim_command.lower() == "save":
                    # Saves the current simulation progress.
                    # Example: save
                    self.save()

                elif sim_command[:3].lower() == "run" and "invest" in sim_command.lower():
                    # Runs the number of steps specified in the prompt.
                    # Example: run 1000
                    int_count = int(sim_command.split()[-1])
                    server.start_server_investment(int_count)

                elif sim_command[:3].lower() == "run" and "sign" in sim_command.lower():
                    # Runs the number of steps specified in the prompt.
                    # Example: run 1000
                    int_count = int(sim_command.split()[-1])
                    server.start_server_sign_up(int_count)

                elif sim_command[:3].lower() == "run" and "pd" in sim_command.lower():
                    # Runs the number of steps specified in the prompt.
                    # Example: run 1000
                    int_count = int(sim_command.split()[-1])
                    server.start_server_pd_game(int_count)

                print(ret_str)

            except Exception as e:
                print(e)
                traceback.print_exc()
                print("Error.")
                pass


if __name__ == "__main__":
    origin = input("Enter the name of the forked simulation: ").strip()
    with_reputation = input("Whether to use reputation (y/n): ").strip()
    with_publicreputation = input("Whether to use public reputation (y/n): ").strip()
    with_gossip = input("Whether to use gossip (y/n): ").strip()
    game_type = input("Investment, Sign up, or PD game (i/s/p): ").strip()
    if "i" in game_type:
        sim = "investment"
    elif "s" in game_type:
        sim = "sign_up"
    elif "p" in game_type:
        sim = "pd_game"
    else:
        sim = "investment"  # default
    server = Creation(origin, with_reputation, with_gossip, with_publicreputation=with_publicreputation, sim=sim)
    server.open_server()
