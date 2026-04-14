
import pandas as pd
import matplotlib.pyplot as plt
import os
import networkx as nx
import numpy as np
import matplotlib.cm as cm
from pathlib import Path
from collections import defaultdict
from threading import Lock
import traceback

class GameStatistics:
    def __init__(self, save_folder, autosave_every=1):
        self.lock = Lock()
        self.autosave_every = autosave_every
        self.save_folder = Path(save_folder)
        self.save_folder.mkdir(parents=True, exist_ok=True)

        # 1. 文件路径定义
        self.summary_csv_path = self.save_folder / "cooperation_rate.csv"
        self.summary_investment_csv_path = self.save_folder / "investment_success_rate.csv"
        self.summary_signup_csv_path = self.save_folder / "sign_up_stats.csv" 
        
        self.persona_dir = self.save_folder / "persona_details"
        self.persona_dir.mkdir(parents=True, exist_ok=True)
        
        # 网络图保存目录
        self.network_plots_dir = self.save_folder / "network_plots"
        self.network_plots_dir.mkdir(parents=True, exist_ok=True)

        # 2. 内存缓冲区
        self.data_buffer = defaultdict(lambda: defaultdict(dict))
        
        # 3. 统计变量
        self.player_decision_count = defaultdict(int)
        self.player_cooperate_count = defaultdict(int)
        self.player_signup_stats = defaultdict(lambda: {"count": 0, "sum": 0})
        self.player_stats = {} # 用于投资博弈的长期统计
        self.cooperate_rate = {} # 用于绘图的实时合作率
        self.last_saved_round = -1

        # 定义严格的列顺序
        self.summary_investment_cols = ["round", "version", "investment_success_rate", "probability_of_allocating_as_agreement", "avg_private_reputation", "avg_public_reputation"]
        self.summary_pd_cols = ["round", "version", "cooperation_rate", "avg_private_reputation", "avg_public_reputation"]
        self.summary_signup_cols = ["round", "version", "avg_sign_up", "avg_private_reputation", "avg_public_reputation"]

        self._init_csv_headers()

    def _init_csv_headers(self):
        if not self.summary_csv_path.exists():
            pd.DataFrame(columns=self.summary_pd_cols).to_csv(self.summary_csv_path, index=False)
        if not self.summary_investment_csv_path.exists():
            pd.DataFrame(columns=self.summary_investment_cols).to_csv(self.summary_investment_csv_path, index=False)
        if not self.summary_signup_csv_path.exists():
             pd.DataFrame(columns=self.summary_signup_cols).to_csv(self.summary_signup_csv_path, index=False)

    def _get_names_only(self, raw_list):
        if not raw_list: return "None"
        names = []
        for item in raw_list:
            if isinstance(item, (list, tuple)) and len(item) > 0:
                names.append(str(item[0])) 
            else:
                names.append(str(item))
        return "|".join(names)

    def log_cooperation_decision(self, round_idx, player_name, decision, version):
        with self.lock:
            self.player_decision_count[player_name] += 1
            if decision in [1, True, "C", "cooperate", "Cooperate"]:
                self.player_cooperate_count[player_name] += 1
            
            rate = self.player_cooperate_count[player_name] / self.player_decision_count[player_name]
            self.cooperate_rate[player_name] = rate

            self.data_buffer[round_idx][player_name].update({
                "round": round_idx,
                "version": version,
                "player": player_name,
                "decision": decision,
                "cooperation_rate": rate
            })

    def log_sign_up_decision(self, round_idx, player_name, sign_up_result, version):
        with self.lock:
            res_val = 1 if sign_up_result in [1, True, "Yes", "yes"] else 0
            stats = self.player_signup_stats[player_name]
            stats["count"] += 1
            stats["sum"] += res_val
            avg_sign_up = stats["sum"] / stats["count"]

            self.data_buffer[round_idx][player_name].update({
                "round": round_idx,
                "version": version,
                "player": player_name,
                "sign_up_result": res_val,
                "avg_sign_up": avg_sign_up
            })

    def log_player_context(self, round_idx, player_name, private_rep, public_rep, bind_list, black_list):
        with self.lock:
            self.data_buffer[round_idx][player_name].update({
                "player": player_name,
                "private_reputation": private_rep,
                "public_reputation": public_rep,
                "bind_list": self._get_names_only(bind_list),
                "black_list": self._get_names_only(black_list)
            })
            
    def log_player_relationships(self, round_idx, player_name, bind_list, black_list, private_rep, public_rep):
        self.log_player_context(round_idx, player_name, private_rep, public_rep, bind_list, black_list)



    # def log_player_investment(self, round_idx, player_name, success_num, total_num, version, target_persona_role, allocating_agreement, success_or_not):
    #     with self.lock:
    #         success_rate = success_num / total_num if total_num > 0 else 0.0

    #         if player_name not in self.player_stats:
    #             self.player_stats[player_name] = {"allocating_as_agreement": 0, "allocating_sum": 0}
        
    #         # 关键修复：确保只有数值类型才进行累加，避免 "None" + 1 报错
    #         if isinstance(allocating_agreement, (int, float)): 
    #             self.player_stats[player_name]["allocating_as_agreement"] += allocating_agreement
    #             self.player_stats[player_name]["allocating_sum"] += 1
            
    #         total_ok = self.player_stats[player_name]["allocating_as_agreement"]
    #         total_attempts = self.player_stats[player_name]["allocating_sum"]
    #         avg_allocating_agreement = total_ok / total_attempts if total_attempts > 0 else 0.0

    #         # 存储原始值用于CSV，None对象转为字符串"None"
    #         save_val = allocating_agreement if allocating_agreement is not None else "None"

    #         entry = self.data_buffer[round_idx][player_name]
    #         entry.update({
    #             "round": round_idx,
    #             "version": version,
    #             "player": player_name, 
    #             "role": target_persona_role,
    #             "success_or_not": success_or_not,
    #             "success_num": success_num, 
    #             "total_num": total_num, 
    #             "investment_success_rate": success_rate,
    #             "allocating_as_agreement": save_val, 
    #             "probability_of_allocating_as_agreement": avg_allocating_agreement,
    #         })

    def log_player_investment(self, round_idx, player_name, target_persona_role, version, 
                          success_or_not, total_success_num, total_num, 
                          stage3_agreement, was_stage3_reached):
        """
        更新后的记录逻辑：移除 Rate 计算，仅记录原始 0/1 标志位
        """
        with self.lock:
            # 直接获取 Buffer 中的条目
            entry = self.data_buffer[round_idx][player_name]
            
            entry.update({
                "round": round_idx,
                "version": version,
                "player": player_name, 
                "role": target_persona_role,
                "success_or_not": success_or_not,       # Stage 1 是否接受
                "total_success_num": total_success_num, # 累计成功数
                "total_num": total_num,                 # 累计总数
                "was_stage3_reached": was_stage3_reached, # 是否进入 Stage 3
                "stage3_agreement": stage3_agreement,     # 是否守约 (0/1)
            })

    def run_autosave(self, current_round):
        try:
            if current_round % self.autosave_every != 0 or current_round <= self.last_saved_round:
                return

            with self.lock:
                rounds_to_save = [r for r in self.data_buffer.keys() if r <= current_round and r > self.last_saved_round]
                all_new_rows = []

                for r in sorted(rounds_to_save):
                    for player_name, data in self.data_buffer[r].items():
                        all_new_rows.append(data)
                        
                        # 个人详情 CSV
                        persona_path = self.persona_dir / f"{player_name}.csv"
                        df_persona = pd.DataFrame([data])
                        preferred_order = [
                        "round", "version", "player", "role", 
                        "success_or_not", "total_success_num", "total_num", 
                        "was_stage3_reached", "stage3_agreement",
                        "private_reputation", "public_reputation", 
                        "bind_list", "black_list"
                    ]
                        
                        final_cols = [col for col in preferred_order if col in df_persona.columns]
                        remaining_cols = [col for col in df_persona.columns if col not in preferred_order]
                        final_cols += remaining_cols
                        
                        df_persona = df_persona[final_cols]
                        df_persona.to_csv(persona_path, mode='a', header=not persona_path.exists(), index=False)

                if not all_new_rows: return
                df_summary_raw = pd.DataFrame(all_new_rows)

                # 1. Sign Up Summary
                if "sign_up_result" in df_summary_raw.columns:
                    signup_data = df_summary_raw.dropna(subset=['sign_up_result'])
                    if not signup_data.empty:
                        # 确保 reputation 列转为数值，否则 mean() 会出错
                        for col in ['private_reputation', 'public_reputation']:
                            signup_data[col] = pd.to_numeric(signup_data[col], errors='coerce')
                            
                        summary_signup = signup_data.groupby(['round', 'version']).agg({
                            'sign_up_result': 'mean',
                            'private_reputation': 'mean',
                            'public_reputation': 'mean'
                        }).reset_index().rename(columns={
                            'sign_up_result': 'avg_sign_up',
                            'private_reputation': 'avg_private_reputation',
                            'public_reputation': 'avg_public_reputation'
                        })
                        summary_signup = summary_signup[self.summary_signup_cols]
                        summary_signup.to_csv(self.summary_signup_csv_path, mode='a', header=False, index=False)

                # 2. Investment Game Summary
                if "investment_success_rate" in df_summary_raw.columns:
                    invest_data = df_summary_raw.dropna(subset=['investment_success_rate'])
                    if not invest_data.empty:
                        # 确保数值转换
                        cols_to_numeric = [
                            'private_reputation', 'public_reputation', 
                            'investment_success_rate', 'probability_of_allocating_as_agreement',
                            'success_or_not', 'stage3_agreement' 
                        ]
                        for col in cols_to_numeric:
                            if col in invest_data.columns:
                                invest_data[col] = pd.to_numeric(invest_data[col], errors='coerce').fillna(0)

                        summary_invest = invest_data.groupby(['round', 'version']).agg({
                            'investment_success_rate': 'mean',
                            'probability_of_allocating_as_agreement': 'mean',
                            'success_or_not': 'mean',     # 如果你想看平均协商成功率
                            'stage3_agreement': 'mean',   # 如果你想看平均守约数
                            'private_reputation': 'mean',
                            'public_reputation': 'mean'
                        }).reset_index().rename(columns={
                            'private_reputation': 'avg_private_reputation',
                            'public_reputation': 'avg_public_reputation'
                        })
                        
                        # 确保 CSV 包含列，顺序对齐
                        summary_invest = summary_invest[self.summary_investment_cols]
                        summary_invest.to_csv(self.summary_investment_csv_path, mode='a', header=False, index=False)

                # 3. PD Cooperation Summary
                if "cooperation_rate" in df_summary_raw.columns:
                    pd_data = df_summary_raw.dropna(subset=['cooperation_rate']).copy()
                    if not pd_data.empty:
                        for col in ['private_reputation', 'public_reputation', 'cooperation_rate']:
                            pd_data[col] = pd.to_numeric(pd_data[col], errors='coerce')

                        summary_pd = pd_data.groupby(['round', 'version']).agg({
                            'cooperation_rate': 'mean',
                            'private_reputation': 'mean',
                            'public_reputation': 'mean'
                        }).reset_index().rename(columns={
                            'private_reputation': 'avg_private_reputation',
                            'public_reputation': 'avg_public_reputation'
                        })
                        
                        # 按照你要求的顺序重新排：version, round, cooperation_rate, ...
                        summary_pd = summary_pd[self.summary_pd_cols]
                        summary_pd.to_csv(self.summary_csv_path, mode='a', header=False, index=False)

                for r in rounds_to_save: del self.data_buffer[r]
                self.last_saved_round = current_round
                print(f" -> [Autosave] Round {current_round} PD stats saved.")

        except Exception as e:
            print(f"Autosave Error: {e}")
            traceback.print_exc()

    def draw_network(self, G: nx.DiGraph, title: str = "RepuNet Network", step: int = 0, save_every: int = 2):
        if step % save_every != 0 and step != 0: return
        with self.lock:
            coop_rates_dict = self.cooperate_rate.copy()
        
        for node in G.nodes():
            if node not in coop_rates_dict: coop_rates_dict[node] = 0.5
        
        coop_rates = np.array([coop_rates_dict[node] for node in G.nodes()])
        node_mutual_count = {node: len([nb for nb in G.successors(node) if G.has_edge(nb, node)]) for node in G.nodes()}
        node_sizes = [max(200 + 800 * node_mutual_count.get(node, 0), 200) for node in G.nodes()]

        pos = nx.spring_layout(G, k=1.8/np.sqrt(max(G.number_of_nodes(),1)), iterations=100, seed=42)
        plt.figure(figsize=(12, 10))
        plt.gcf().patch.set_facecolor('white')
        
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.3, edge_color='black', arrows=True)
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=cm.RdYlGn(coop_rates), edgecolors='black')
        nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')

        plt.title(f"{title} - Step {step}", fontsize=15)
        plt.axis('off')
        save_path = self.network_plots_dir / f"network_step_{step:04d}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

    def final_save_and_plot(self):
        max_round = max(self.data_buffer.keys()) if self.data_buffer else self.last_saved_round
        if max_round != -1:
            self.run_autosave(max_round)
        print("Final statistics completed.")

